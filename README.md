# Multi-Format Telegram Content Agent with Persistent Memory using Ollama and Google Sheets

## Overview

The **Multi-Format Telegram Content Agent** is an AI-powered backend application that receives content from users through Telegram, intelligently processes it using Large Language Models (LLMs), and stores structured results in Google Sheets.

Unlike basic Telegram bots that simply echo messages or save plain text, this project supports multiple content formats including:

- Plain Text
- Website URLs
- PDF Documents

The application extracts meaningful content, generates multiple platform-specific content drafts using LLMs (Ollama, Gemini, or Groq), remembers each user's writing style, prevents duplicate entries, and stores all generated outputs in Google Sheets.

The project has been designed with production-minded architecture, modular code organization, resilience against failures, and containerized deployment using Docker.

---

# Features

## Telegram Bot

- Responds to `/start`
- Supports `/setstyle`
- Receives plain text
- Receives website URLs
- Receives PDF files

---

## Multi-format Content Processing

### Plain Text

Processes user text directly.

Example:

```
Artificial Intelligence is transforming software engineering.
```

---

### Website URLs

Extracts the actual article from webpages using:

- trafilatura

Removes:

- advertisements
- navigation bars
- scripts
- sidebars
- boilerplate HTML

Only meaningful article content is sent to the LLM.

---

### PDF Documents

Downloads PDF files from Telegram.

Uses Microsoft MarkItDown to convert:

```
PDF
      ↓
Markdown
      ↓
Structured Text
```

The extracted Markdown preserves:

- headings
- lists
- tables
- formatting

which greatly improves LLM quality.

---

# AI Processing

Supports multiple LLM providers.

Primary:

- Ollama (Local)

Fallback:

- Gemini API

Optional:

- Groq API

The LLM generates structured JSON containing:

- Title
- Editorial rationale
- Category
- X (Twitter) post
- LinkedIn post

---

# Persistent Style Memory

Every Telegram user can define their preferred writing style.

Example:

```
/setstyle Write in a witty tone with emojis.
```

or

```
/setstyle Always include statistics.
```

The style preference is stored in SQLite.

Every future request automatically injects this style into the prompt before sending it to the LLM.

---

# Duplicate Prevention

The application performs idempotent writes.

Duplicate detection:

For URLs

- URL itself is used.

For Text

- SHA256 hash of the content.

For PDFs

- SHA256 hash of extracted markdown.

If identical content already exists in Google Sheets, no duplicate row is inserted.

---

# Google Sheets Integration

All processed content is automatically stored inside Google Sheets.

Columns:

| SourceIdentifier | SubmissionTimestamp | ContentType | LLMTitle | Rationale | Category | X_Variant | LinkedIn_Variant |

This provides a lightweight CMS for generated content.

---

# Docker Support

The entire project runs using Docker.

Single command:

```
docker-compose up --build
```

starts

- Telegram bot
- SQLite
- Application
- Health check

without manual setup.

---

# Project Architecture

```
Telegram User
        │
        ▼
 Telegram Bot
        │
        ▼
 Message Handler
        │
        ▼
 Content Router
   │      │      │
   │      │      │
 Text    URL    PDF
   │      │      │
   │      │      │
   │   Trafilatura
   │             │
   │      MarkItDown
   │             │
   └──────┬──────┘
          ▼
  Extracted Content
          │
          ▼
  Load User Style
      (SQLite)
          │
          ▼
  Prompt Builder
          │
          ▼
   Ollama / Gemini
          │
          ▼
 Structured JSON
          │
          ▼
 Duplicate Check
          │
          ▼
 Google Sheets
```

---

# Folder Structure

```
telegram-content-agent/

│
├── app/
│
├── handlers/
│     ├── start.py
│     ├── style.py
│     └── message.py
│
├── extractors/
│     ├── text.py
│     ├── url.py
│     └── pdf.py
│
├── llm/
│     ├── ollama.py
│     ├── gemini.py
│     └── orchestrator.py
│
├── services/
│     ├── duplicate.py
│     ├── prompt_builder.py
│     └── processor.py
│
├── storage/
│     ├── sheets.py
│     └── sqlite.py
│
├── utils/
│     ├── hash.py
│     ├── logger.py
│     └── retry.py
│
├── database/
│     └── style.db
│
├── temp/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── .env.example
└── .gitignore
```

---

# Technology Stack

| Component        | Technology           |
| ---------------- | -------------------- |
| Language         | Python               |
| Telegram         | python-telegram-bot  |
| LLM              | Ollama               |
| Fallback LLM     | Gemini               |
| Optional LLM     | Groq                 |
| URL Parsing      | trafilatura          |
| PDF Parsing      | Microsoft MarkItDown |
| Database         | SQLite               |
| Cloud Storage    | Google Sheets        |
| Containerization | Docker               |
| Orchestration    | Docker Compose       |

---

# Installation

## Clone Repository

```
git clone https://github.com/yourusername/telegram-content-agent.git

cd telegram-content-agent
```

---

## Create Virtual Environment

Windows

```
python -m venv venv

venv\Scripts\activate
```

Linux

```
python3 -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```
pip install -r requirements.txt
```

---

# Environment Variables

Create

```
.env
```

Example

```
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN

GOOGLE_SHEET_NAME=ContentAgent

GOOGLE_CREDENTIALS_FILE=credentials.json

OLLAMA_URL=http://localhost:11434

OLLAMA_MODEL=llama3.1

GEMINI_API_KEY=YOUR_API_KEY

GROQ_API_KEY=YOUR_API_KEY
```

---

# Telegram Bot Setup

1. Open Telegram

2. Search

```
BotFather
```

3. Create a new bot

```
/newbot
```

4. Copy the generated token.

5. Store it inside

```
.env
```

---

# Google Sheets Setup

## Step 1

Create a Google Cloud Project.

---

## Step 2

Enable

- Google Sheets API
- Google Drive API

---

## Step 3

Create a Service Account.

Download

```
credentials.json
```

---

## Step 4

Create a Google Sheet.

Name:

```
Content
```

---

## Step 5

Share the sheet with

```
your-service-account@project.iam.gserviceaccount.com
```

Give Editor permission.

---

# SQLite

Database:

```
style.db
```

Schema

```sql
CREATE TABLE styles(

user_id INTEGER PRIMARY KEY,

style_prompt TEXT

);
```

Stores user-specific writing styles.

---

# Running Ollama

Install Ollama.

Pull model.

```
ollama pull llama3.1
```

Run

```
ollama serve
```

Verify

```
http://localhost:11434
```

---

# Running the Application

Without Docker

```
python app/main.py
```

---

With Docker

```
docker-compose up --build
```

---

Detached

```
docker-compose up -d
```

---

# Health Check

Verify container

```
docker-compose ps
```

Expected

```
healthy
```

---

# Supported Commands

## /start

Returns

```
Welcome to the Content Agent!

Send me

• Text
• URL
• PDF

and I'll generate AI content.
```

---

## /setstyle

Example

```
/setstyle Write professionally with emojis.
```

Response

```
Style updated successfully.
```

---

# Processing Flow

## Plain Text

```
Telegram

↓

Text

↓

LLM

↓

Google Sheets
```

---

## URL

```
Telegram

↓

URL

↓

Trafilatura

↓

Article

↓

LLM

↓

Google Sheets
```

---

## PDF

```
Telegram

↓

PDF

↓

Download

↓

MarkItDown

↓

Markdown

↓

LLM

↓

Google Sheets
```

---

# Prompt Engineering

The application builds prompts using three parts.

```
System Prompt

+

User Style

+

Extracted Content
```

Example

```
You are an expert content strategist.

Return ONLY JSON.

Generate:

title

rationale

category

x_post

linkedin_post

User Style:

Write professionally.

Content:

<article>
```

---

# Retry Strategy

Sometimes LLMs return invalid JSON.

The application retries up to three times.

```
Attempt 1

↓

Invalid JSON

↓

Retry

↓

Invalid JSON

↓

Retry

↓

Valid JSON
```

---

# Idempotency

The application prevents duplicate entries.

URL

```
URL already exists

↓

Ignore
```

Text

```
Generate SHA256

↓

Compare

↓

Already Exists

↓

Ignore
```

PDF

```
Markdown Hash

↓

Compare

↓

Ignore Duplicate
```

---

# Error Handling

The application gracefully handles

- Invalid URLs
- Empty PDFs
- Google Sheets failures
- Telegram API failures
- Ollama connection failures
- Invalid JSON responses
- Network interruptions
- Rate limits
- Missing environment variables

---

# Rate Limiting

Exponential Backoff is implemented.

```
1 second

↓

2 seconds

↓

4 seconds
```

for

- Google Sheets API
- Ollama
- Gemini
- Groq

---

# Logging

Application logs include

- Incoming messages
- User ID
- Processing status
- LLM latency
- Google Sheets status
- Duplicate detection
- Exceptions

---

# Testing

## Plain Text

Send

```
Artificial Intelligence is changing software engineering.
```

Expected

New Google Sheet row.

---

## URL

Send

```
https://example.com/article
```

Expected

Article extracted and summarized.

---

## PDF

Upload

```
sample.pdf
```

Expected

Markdown extraction and AI-generated drafts.

---

## Duplicate

Send same URL twice.

Expected

Only one row.

---

## Style

```
/setstyle Write like Shakespeare.
```

Send same article again.

Expected

Different generated output.

---

# Core Requirements Checklist

- Dockerized application
- docker-compose support
- Health check
- Telegram bot
- Google Sheets integration
- SQLite style memory
- Ollama integration
- Gemini fallback
- URL extraction
- PDF extraction
- Prompt engineering
- Retry mechanism
- Duplicate prevention
- Structured JSON parsing
- Multi-platform content generation
- Logging
- Error handling

---

# Future Improvements

- PostgreSQL support
- Redis caching
- OCR support for scanned PDFs
- Multiple Google Sheets
- Scheduled content generation
- Slack integration
- Discord bot support
- Vector database for semantic duplicate detection
- User authentication dashboard
- REST API
- Admin analytics dashboard

---

# Author

Developed as part of the Backend Development AI Assignment.

Technologies Used:

- Python
- Telegram Bot API
- Ollama
- Gemini
- Google Sheets API
- SQLite
- Docker
- Microsoft MarkItDown
- Trafilatura
- Prompt Engineering
