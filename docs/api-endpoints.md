# API Endpoints Documentation

This document provides detailed information about the API endpoints available in the Summarization Agent.

## Core Endpoints

### Health Check

```
GET /health
```

Returns the current health status of the service.

#### Response

```json
{
  "status": "ok"
}
```

### Root Endpoint

```
GET /
```

Returns a welcome message.

#### Response

```json
{
  "message": "Welcome to the Summarization Agent API"
}
```

### Process Emails

```
POST /api/process-emails
```

Triggers the processing of unread emails from the configured email account. The processing happens asynchronously in the background.

#### Response

```json
{
  "status": "processing",
  "message": "Email processing started in the background"
}
```

### Get Settings

```
GET /api/settings
```

Returns application settings information. Only available in debug mode.

#### Response

```json
{
  "debug": true,
  "log_level": "INFO",
  "email_server": "outlook.office365.com",
  "email_port": 993,
  "temp_dir": "./tmp",
  "max_attachment_size": 25000000
}
```

## Test Endpoints

These endpoints are primarily for testing and development purposes.

### Test Email Service

```
GET /test/email-service
```

Tests the email service by retrieving test emails in debug mode.

#### Response

```json
{
  "emails_found": 1,
  "emails": [
    {
      "id": "test_email_id",
      "subject": "Test Email Subject",
      "sender": "sender@example.com",
      "date": "Mon, 19 Aug 2023 12:00:00 +0000",
      "body": "This is a test email body with important information that needs to be summarized.",
      "attachments": [],
      "timestamp": "2023-08-19T12:00:00.123456"
    }
  ]
}
```

### Test Text Summarization

```
POST /test/summarize-text
```

Tests AI summarization with custom text.

#### Request

```json
{
  "subject": "Test Subject",
  "body": "This is the text content to summarize. It can be several paragraphs long...",
  "sender": "test@example.com",
  "date": "2023-08-30"
}
```

#### Response

```json
{
  "success": true,
  "summary": "Summary of the provided text content.",
  "metadata": {
    "subject": "Test Subject",
    "sender": "test@example.com",
    "date": "2023-08-30"
  }
}
```

### Test File Conversion

```
POST /test/convert-file
```

Tests file conversion by uploading a file (Office document or image).

#### Request

- Method: POST
- Content-Type: multipart/form-data
- Body: file (The file to convert)

#### Response

```json
{
  "success": true,
  "original_filename": "document.docx",
  "converted_path": "/app/tmp/converted_123456.pdf",
  "file_size": 152896,
  "message": "File successfully converted to PDF"
}
```

### Test PDF Summarization

```
POST /test/summarize-pdf
```

Tests PDF summarization by uploading a PDF file.

#### Request

- Method: POST
- Content-Type: multipart/form-data
- Body: file (PDF file)

#### Response

```json
{
  "success": true,
  "summary": "Summary of the PDF document.",
  "metadata": {
    "filename": "document.pdf"
  }
}
```

### Test Report Generation

```
POST /test/generate-report
```

Tests report generation with sample data.

#### Request

```json
{
  "email_data": {
    "subject": "Test Subject",
    "sender": "test@example.com",
    "date": "2023-08-30"
  },
  "summaries": [
    {
      "type": "email",
      "summary": {
        "success": true,
        "summary": "This is a test summary of an email.",
        "metadata": {
          "subject": "Test Subject",
          "sender": "test@example.com",
          "date": "2023-08-30"
        }
      }
    },
    {
      "type": "attachment",
      "summary": {
        "success": true,
        "summary": "This is a test summary of an attachment.",
        "metadata": {
          "filename": "document.pdf"
        }
      }
    }
  ]
}
```

#### Response

```json
{
  "report": {
    "report_id": "12345678-1234-5678-abcd-1234567890ab",
    "metadata": {
      "subject": "Test Subject",
      "sender": "test@example.com",
      "date": "2023-08-30",
      "generated_at": 1693396800
    },
    "email_summary": "This is a test summary of an email.",
    "attachment_summaries": [
      {
        "filename": "document.pdf",
        "summary": "This is a test summary of an attachment."
      }
    ]
  },
  "html_length": 1234,
  "html_sample": "<!DOCTYPE html><html><head><style>body { font-family: Arial, sans-serif; }</style></head><body><h1>Email Summary Report</h1>..."
}
```

### Test End-to-End Processing

```
POST /test/end-to-end
```

Tests the entire pipeline with a simulated email.

#### Response

```json
{
  "status": "processing",
  "message": "End-to-end test started in the background. Check the logs for details."
}
```

### Test Text Summarization with Real API

```
POST /test/summarize-text-real
```

Tests AI summarization with real OpenAI API (not simulated).

#### Request

```json
{
  "subject": "Test Subject",
  "body": "This is the text content to summarize. It can be several paragraphs long...",
  "sender": "test@example.com",
  "date": "2023-08-30"
}
```

#### Response

```json
{
  "success": true,
  "summary": "Summary generated by the real OpenAI API.",
  "metadata": {
    "subject": "Test Subject",
    "sender": "test@example.com",
    "date": "2023-08-30"
  }
}
```

### Test PDF Summarization with Real API

```
POST /test/summarize-pdf-real
```

Tests PDF summarization with real OpenAI API.

#### Request

- Method: POST
- Content-Type: multipart/form-data
- Body: file (PDF file)

#### Response

```json
{
  "success": true,
  "summary": "This is a detailed summary of the PDF content with bullet points and insights extracted by the real OpenAI API.",
  "metadata": {
    "filename": "document.pdf",
    "extracted_images_data": [
      {
        "page": 1,
        "index": 1,
        "format": "jpeg",
        "width": 800,
        "height": 600,
        "caption": "Description of the image generated by AI",
        "filepath": "/app/tmp/document_p1_img1_abc123.jpeg"
      }
    ]
  }
}
```

### Test End-to-End Processing with Real API

```
POST /test/end-to-end-real
```

Tests the entire pipeline with a simulated email using the real OpenAI API.

#### Response

```json
{
  "status": "processing",
  "message": "End-to-end test with real API started in the background. Check the logs for details."
}
```

## Error Responses

All endpoints may return the following error responses:

### 404 Not Found

```json
{
  "detail": "Not Found"
}
```

### 403 Forbidden

```json
{
  "detail": "This endpoint is only available in debug mode"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

## Authentication

Authentication is not currently implemented for these endpoints. Future versions may require API keys or other authentication mechanisms.