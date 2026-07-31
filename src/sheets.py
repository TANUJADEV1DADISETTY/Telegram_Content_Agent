import os
import json
import time
from datetime import datetime, timezone
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from src.config import (
    GOOGLE_SHEETS_CREDENTIALS_JSON, GOOGLE_SHEET_NAME, GOOGLE_SHEET_ID, logger
)

SHEET_HEADERS = [
    "SourceIdentifier",
    "SubmissionTimestamp",
    "ContentType",
    "LLMTitle",
    "Rationale",
    "Category",
    "X_Variant",
    "LinkedIn_Variant",
]


def get_sheets_client():
    if not GOOGLE_SHEETS_CREDENTIALS_JSON:
        raise ValueError("GOOGLE_SHEETS_CREDENTIALS_JSON environment variable is not set")

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    # Try parsing as inline JSON string first
    try:
        creds_dict = json.loads(GOOGLE_SHEETS_CREDENTIALS_JSON)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        logger.info("Loaded Google credentials from environment JSON string.")
    except json.JSONDecodeError:
        # Fall back to treating the value as a file path
        if os.path.exists(GOOGLE_SHEETS_CREDENTIALS_JSON):
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                GOOGLE_SHEETS_CREDENTIALS_JSON, scope
            )
            logger.info(f"Loaded Google credentials from file: {GOOGLE_SHEETS_CREDENTIALS_JSON}")
        else:
            raise FileNotFoundError(
                f"GOOGLE_SHEETS_CREDENTIALS_JSON is not valid JSON and no file exists at: "
                f"{GOOGLE_SHEETS_CREDENTIALS_JSON}"
            )

    return gspread.authorize(creds)


def get_worksheet() -> gspread.Worksheet:
    client = get_sheets_client()

    try:
        if GOOGLE_SHEET_ID:
            logger.info(f"Opening spreadsheet by ID: {GOOGLE_SHEET_ID}")
            spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        else:
            logger.info(f"Opening spreadsheet by name: {GOOGLE_SHEET_NAME}")
            spreadsheet = client.open(GOOGLE_SHEET_NAME)
    except Exception as e:
        logger.error(f"Error opening Google Sheet: {str(e)}")
        raise

    # Get or create the 'Content' worksheet
    try:
        worksheet = spreadsheet.worksheet("Content")
        logger.info("Found existing 'Content' worksheet.")
    except gspread.WorksheetNotFound:
        logger.info("'Content' worksheet not found — creating it.")
        try:
            worksheet = spreadsheet.add_worksheet(title="Content", rows="1000", cols="8")
        except Exception as e:
            logger.warning(
                f"Could not create 'Content' worksheet ({e}). Falling back to first sheet."
            )
            worksheet = spreadsheet.get_worksheet(0)

    # Ensure headers are in place
    _ensure_headers(worksheet)
    return worksheet


def _ensure_headers(worksheet: gspread.Worksheet) -> None:
    try:
        first_row = worksheet.row_values(1)
    except Exception as e:
        logger.warning(f"Could not read row 1 for header check: {e}")
        first_row = []

    if first_row[:len(SHEET_HEADERS)] == SHEET_HEADERS:
        return  # Headers already correct

    logger.info("Writing required headers to row 1.")
    try:
        if not first_row:
            worksheet.insert_row(SHEET_HEADERS, 1)
        else:
            for idx, h in enumerate(SHEET_HEADERS, start=1):
                worksheet.update_cell(1, idx, h)
    except Exception as e:
        logger.error(f"Failed to write headers: {e}")
        raise


def check_identifier_in_sheet(worksheet: gspread.Worksheet, identifier: str) -> bool:
    """Return True if *identifier* is already present in the SourceIdentifier column."""
    try:
        col_values = worksheet.col_values(1)  # Column A = SourceIdentifier
        return identifier in col_values[1:]   # skip the header row
    except Exception as e:
        logger.error(f"Error querying sheet for duplicates: {e}")
        return False  # conservative: let it proceed rather than block forever


def append_content_row(
    worksheet: gspread.Worksheet,
    source_identifier: str,
    content_type: str,
    llm_data: dict,
) -> None:
    """Append a single structured row; retry up to 3 times on transient errors."""
    timestamp = datetime.now(timezone.utc).isoformat()
    row = [
        source_identifier,
        timestamp,
        content_type,
        llm_data.get("title", ""),
        llm_data.get("rationale", ""),
        llm_data.get("category", ""),
        llm_data.get("variants", {}).get("x_post", ""),
        llm_data.get("variants", {}).get("linkedin_post", ""),
    ]

    logger.info(f"Appending row — identifier: {source_identifier[:60]}")

    retries = 3
    for attempt in range(retries):
        try:
            worksheet.append_row(row, value_input_option="USER_ENTERED")
            logger.info("Row appended successfully.")
            return
        except Exception as e:
            wait = 2 ** attempt  # exponential back-off: 1s, 2s, 4s
            logger.warning(
                f"Append attempt {attempt + 1}/{retries} failed: {e}. "
                f"Retrying in {wait}s…"
            )
            if attempt < retries - 1:
                time.sleep(wait)
            else:
                raise
