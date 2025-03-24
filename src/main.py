from fastapi import FastAPI, BackgroundTasks
import logging
from src.email_ingestion.service import EmailService  # Update the import path as needed

app = FastAPI(
    title="Summarization Agent API",
    description="API for processing emails and generating summaries using AI",
    version="0.1.0",
)

email_service = EmailService()

@app.get("/")
async def root():
    return {"message": "Welcome to the Summarization Agent API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/process-emails")
async def process_emails(background_tasks: BackgroundTasks):
    """
    Trigger the processing of unread emails.
    The actual processing happens in the background.
    """
    # For now, just fetch emails but don't process them
    emails = email_service.get_unread_emails(limit=5)
    
    return {
        "status": "processing",
        "message": f"Processing {len(emails)} emails in the background",
        "email_count": len(emails)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 