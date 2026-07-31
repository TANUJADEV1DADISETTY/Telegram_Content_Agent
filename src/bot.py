import urllib.parse
import os
import time
import tempfile
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from src.config import validate_config, TELEGRAM_BOT_TOKEN, logger
from src.db import init_db, get_user_style, set_user_style, is_duplicate, mark_processed
from src.extractors import extract_from_url, extract_from_pdf, compute_hash
from src.llm import generate_drafts
from src.sheets import get_worksheet, check_identifier_in_sheet, append_content_row
from src.health import start_health_server


# ── Helpers ───────────────────────────────────────────────────────────────────

def is_url(text: str) -> bool:
    text = text.strip()
    if not (text.startswith("http://") or text.startswith("https://")):
        return False
    try:
        parsed = urllib.parse.urlparse(text)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False


def _esc(text: str) -> str:
    """Escape all MarkdownV2 special characters in user-supplied text."""
    special = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in special else c for c in text)


# ── Command handlers ──────────────────────────────────────────────────────────

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "👋 Welcome to the *Multi\\-Format Telegram Content Agent\\!*\n\n"
        "I am your automated content team\\. Send me articles, links, PDFs, or "
        "raw text and I will generate optimised social\\-media drafts and log them "
        "to your Google Sheet\\.\n\n"
        "🛠 *Commands:*\n"
        "`/start` \\— this message\n"
        "`/setstyle <description>` \\— set your personal tone "
        "\\(e\\.g\\. `/setstyle witty with emojis`\\)\n\n"
        "📬 *Send me any content to get started\\!*"
    )
    await update.message.reply_text(text, parse_mode="MarkdownV2")


async def setstyle_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not context.args:
        current = get_user_style(user_id)
        if current:
            body = f"Your current style is:\n_{_esc(current)}_"
        else:
            body = "You have no style set yet\\."
        await update.message.reply_text(
            "ℹ️ Please specify a style\\.\n"
            "Usage: `/setstyle <description>`\n"
            "Example: `/setstyle write like a pirate`\n\n"
            + body,
            parse_mode="MarkdownV2",
        )
        return

    style_prompt = " ".join(context.args)
    set_user_style(user_id, style_prompt)
    await update.message.reply_text(
        f"✅ *Style saved\\!*\n\nYour tone is now:\n_{_esc(style_prompt)}_",
        parse_mode="MarkdownV2",
    )


# ── Main message handler ──────────────────────────────────────────────────────

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message:
        return

    user_id = update.effective_user.id

    # Validate config on every call so we give clear error messages even if
    # credentials were missing at startup but the process is still alive.
    try:
        validate_config()
    except Exception as exc:
        logger.error(f"Config validation failed: {exc}")
        await message.reply_text(
            f"⚠️ Bot is not fully configured. Please check the server.\n\n{exc}"
        )
        return

    # ── Route by content type ─────────────────────────────────────────────────
    content_type = ""
    content = ""
    source_identifier = ""

    if message.document:
        # Only accept PDFs
        if message.document.mime_type != "application/pdf":
            await message.reply_text(
                "⚠️ Only PDF documents are supported. Please send a .pdf file."
            )
            return

        content_type = "pdf"
        status_msg = await message.reply_text("📥 Downloading PDF…")
        try:
            file_info = await context.bot.get_file(message.document.file_id)
            tmp_dir = tempfile.gettempdir()
            safe_name = f"{message.document.file_id}_{message.document.file_name or 'doc.pdf'}"
            local_path = os.path.join(tmp_dir, safe_name)
            await file_info.download_to_drive(local_path)

            await status_msg.edit_text("🔍 Converting PDF to Markdown…")
            content = extract_from_pdf(local_path)
            source_identifier = compute_hash(content)

            try:
                os.remove(local_path)
            except OSError:
                pass

        except Exception as exc:
            logger.error(f"PDF processing error: {exc}")
            await status_msg.edit_text(f"❌ PDF processing failed: {exc}")
            return

    elif message.text:
        raw = message.text.strip()
        if is_url(raw):
            content_type = "url"
            status_msg = await message.reply_text("🌐 Fetching article content…")
            try:
                content = extract_from_url(raw)
                source_identifier = raw  # URL is the canonical identifier
            except Exception as exc:
                logger.error(f"URL extraction error: {exc}")
                await status_msg.edit_text(f"❌ Article extraction failed: {exc}")
                return
        else:
            content_type = "text"
            status_msg = await message.reply_text("📝 Processing text…")
            content = raw
            source_identifier = compute_hash(content)
    else:
        await message.reply_text(
            "⚠️ Unsupported format. Send plain text, a URL, or a PDF file."
        )
        return

    # ── Ingestion pipeline ────────────────────────────────────────────────────
    try:
        user_style = get_user_style(user_id)

        await status_msg.edit_text("📊 Connecting to Google Sheets…")
        worksheet = get_worksheet()

        await status_msg.edit_text("🛡️ Checking for duplicates…")
        dup_sheet = check_identifier_in_sheet(worksheet, source_identifier)
        dup_db    = is_duplicate(user_id, source_identifier, user_style)

        if dup_sheet and dup_db:
            logger.info("Duplicate detected — skipping.")
            await status_msg.edit_text(
                "⚠️ Duplicate detected!\n\n"
                "This content was already processed with your current style.\n"
                "No new row was added."
            )
            return

        await status_msg.edit_text("🤖 Generating drafts via LLM… (may take ~30 s)")
        llm_data = generate_drafts(content, user_style)

        await status_msg.edit_text("💾 Writing to Google Sheets…")
        append_content_row(worksheet, source_identifier, content_type, llm_data)
        mark_processed(user_id, source_identifier, user_style)

        title    = llm_data.get("title", "")
        category = llm_data.get("category", "")
        rationale = llm_data.get("rationale", "")
        x_post   = llm_data.get("variants", {}).get("x_post", "")
        li_post  = llm_data.get("variants", {}).get("linkedin_post", "")

        reply = (
            f"✅ Logged to Google Sheets!\n\n"
            f"📌 Title: {title}\n"
            f"🏷 Category: {category}\n"
            f"💡 Rationale: {rationale}\n\n"
            f"{'─'*30}\n"
            f"𝕏 Draft ({len(x_post)} chars):\n{x_post}\n\n"
            f"{'─'*30}\n"
            f"💼 LinkedIn Draft:\n{li_post}"
        )
        if len(reply) > 4096:
            reply = reply[:4090] + "…"

        await status_msg.edit_text(reply)

    except Exception as exc:
        logger.error(f"Pipeline failed: {exc}")
        try:
            await status_msg.edit_text(f"❌ Processing failed: {exc}")
        except Exception:
            pass


# ── Entry-point ───────────────────────────────────────────────────────────────

def main() -> None:
    # 1. Initialise SQLite
    init_db()

    # 2. Start health-check server on :8000/health (daemon thread)
    start_health_server(port=8000)

    # 3. Validate config — if invalid we still keep the process alive for
    #    Docker health-checks, but we don't start polling.
    try:
        validate_config()
    except Exception as exc:
        logger.critical(f"Config invalid — bot will not poll: {exc}")
        while True:
            time.sleep(3600)

    # 4. Build and start the Telegram application (long-polling)
    logger.info("Building Telegram application…")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",    start_command))
    app.add_handler(CommandHandler("setstyle", setstyle_command))

    # Handle text messages AND PDF document messages
    app.add_handler(
        MessageHandler(
            (filters.TEXT & ~filters.COMMAND) | filters.Document.MimeType("application/pdf"),
            message_handler,
        )
    )

    logger.info("Bot polling started.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
