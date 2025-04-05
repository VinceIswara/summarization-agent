# File: src/main.py
# Location: /summarization-agent/src/main.py

import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException, File, UploadFile
import asyncio
import os
import tempfile
from typing import Optional

from src.config import settings
from src.tasks import process_emails_task
from src.email_ingestion.service import EmailService
from src.attachment_processor.converter import FileConverter
from src.ai_summarization.agent import SummarizationAgent
from src.report_generator.generator import ReportGenerator

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Summarization Agent API",
    description="API for processing emails and generating summaries using AI",
    version="0.1.0",
)

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
    background_tasks.add_task(process_emails_task)
    
    return {
        "status": "processing",
        "message": "Email processing started in the background"
    }

@app.get("/api/settings")
async def get_settings():
    """Get application settings (development mode only)"""
    if not settings.debug:
        raise HTTPException(status_code=403, detail="This endpoint is only available in debug mode")
    
    # Return a sanitized version of settings (without sensitive data)
    return {
        "debug": settings.debug,
        "log_level": settings.log_level,
        "email_server": settings.email_server,
        "email_port": settings.email_port,
        "temp_dir": settings.temp_dir,
        "max_attachment_size": settings.max_attachment_size
    }

# ---- TEST ENDPOINTS ----

@app.get("/test/email-service")
async def test_email_service():
    """Test the email service (retrieve test emails in debug mode)"""
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Test endpoints are only available in debug mode")
    
    email_service = EmailService()
    emails = email_service.get_unread_emails(limit=2)
    
    return {
        "emails_found": len(emails),
        "emails": emails
    }

@app.post("/test/summarize-text")
async def test_summarize_text(content: dict):
    """
    Test AI summarization with custom text
    
    Example request body:
    {
        "subject": "Test Subject",
        "body": "This is the text content to summarize. It can be several paragraphs long...",
        "sender": "test@example.com",
        "date": "2023-08-30"
    }
    """
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Test endpoints are only available in debug mode")
    
    agent = SummarizationAgent()
    result = await agent.process_email_content(content)
    
    return result

@app.post("/test/convert-file")
async def test_file_conversion(file: UploadFile = File(...)):
    """Test file conversion by uploading a file (Office document or image)"""
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Test endpoints are only available in debug mode")
    
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, dir=settings.temp_dir) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        # Convert file
        converter = FileConverter()
        pdf_path = converter.convert_to_pdf(temp_path, file.filename)
        
        if not pdf_path:
            return {"success": False, "message": "Conversion failed"}
        
        # Get file size
        pdf_size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0
        
        return {
            "success": True,
            "original_filename": file.filename,
            "converted_path": pdf_path,
            "file_size": pdf_size,
            "message": "File successfully converted to PDF"
        }
    except Exception as e:
        logger.error(f"Error in file conversion test: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/test/summarize-pdf")
async def test_summarize_pdf(file: UploadFile = File(...)):
    """Test PDF summarization by uploading a PDF file"""
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Test endpoints are only available in debug mode")
    
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, dir=settings.temp_dir, suffix=".pdf") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        # Process the PDF
        agent = SummarizationAgent()
        result = await agent.process_pdf_document(temp_path, {"filename": file.filename})
        
        return result
    except Exception as e:
        logger.error(f"Error in PDF summarization test: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/test/generate-report")
async def test_report_generation(data: dict):
    """
    Test report generation with sample data
    
    Example request body:
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
    """
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Test endpoints are only available in debug mode")
    
    try:
        generator = ReportGenerator()
        report = generator.generate_report(data.get("email_data", {}), data.get("summaries", []))
        
        # Also test email formatting
        html_report = generator.format_for_email(report)
        
        return {
            "report": report,
            "html_length": len(html_report),
            "html_sample": html_report[:500] + "..." if len(html_report) > 500 else html_report
        }
    except Exception as e:
        logger.error(f"Error in report generation test: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/test/end-to-end")
async def test_end_to_end(background_tasks: BackgroundTasks):
    """
    Test the entire pipeline with a simulated email
    This will process a test email with an attachment through all components
    """
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Test endpoints are only available in debug mode")
    
    async def process_test_email():
        try:
            logger.info("Starting end-to-end test processing")
            
            # 1. Simulate retrieving an email
            email_service = EmailService()
            emails = email_service.get_unread_emails(limit=1)
            
            if not emails:
                logger.error("No test emails available")
                return
            
            email_data = emails[0]
            logger.info(f"Processing test email: {email_data['subject']}")
            
            # 2. Process the email content with AI
            agent = SummarizationAgent()
            email_summary = await agent.process_email_content(email_data)
            
            # 3. Process attachments if any
            attachment_summaries = []
            
            for attachment in email_data.get('attachments', []):
                logger.info(f"Processing attachment: {attachment['filename']}")
                
                # Convert if needed
                converter = FileConverter()
                pdf_path = converter.convert_to_pdf(attachment['path'], attachment['filename'])
                
                if pdf_path:
                    # Summarize the PDF
                    pdf_summary = await agent.process_pdf_document(pdf_path, {"filename": attachment['filename']})
                    attachment_summaries.append({
                        "type": "attachment",
                        "summary": pdf_summary
                    })
            
            # 4. Generate the report
            summaries = [{"type": "email", "summary": email_summary}] + attachment_summaries
            generator = ReportGenerator()
            report = generator.generate_report(email_data, summaries)
            
            # 5. Format for email (just generate, don't send)
            html_report = generator.format_for_email(report)
            
            logger.info("End-to-end test processing completed successfully")
        except Exception as e:
            logger.error(f"Error in end-to-end test: {str(e)}")
    
    background_tasks.add_task(process_test_email)
    
    return {
        "status": "processing",
        "message": "End-to-end test started in the background. Check the logs for details."
    }

@app.post("/test/summarize-text-real")
async def test_summarize_text_real(content: dict):
    """
    Test AI summarization with real OpenAI API
    
    Example request body:
    {
        "subject": "Test Subject",
        "body": "This is the text content to summarize. It can be several paragraphs long...",
        "sender": "test@example.com",
        "date": "2023-08-30"
    }
    """
    try:
        agent = SummarizationAgent(force_real_api=True)
        result = await agent.process_email_content(content)
        
        return result
    except Exception as e:
        logger.error(f"Error in real API summarization test: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/test/end-to-end-real")
async def test_end_to_end_real(background_tasks: BackgroundTasks):
    """
    Test the entire pipeline with a simulated email using the real OpenAI API
    """
    async def process_test_email_real():
        try:
            logger.info("Starting end-to-end test with real API processing")
            
            # 1. Simulate retrieving an email
            email_service = EmailService()
            emails = email_service.get_unread_emails(limit=1)
            
            if not emails:
                logger.error("No test emails available")
                return
            
            email_data = emails[0]
            logger.info(f"Processing test email with real API: {email_data['subject']}")
            
            # 2. Process the email content with AI (using real API)
            agent = SummarizationAgent(force_real_api=True)
            email_summary = await agent.process_email_content(email_data)
            logger.info(f"Email summary generated with real API: {email_summary['summary'][:100]}...")
            
            # 3. Process attachments if any
            attachment_summaries = []
            
            for attachment in email_data.get('attachments', []):
                logger.info(f"Processing attachment with real API: {attachment['filename']}")
                
                # Convert if needed
                converter = FileConverter()
                pdf_path = converter.convert_to_pdf(attachment['path'], attachment['filename'])
                
                if pdf_path:
                    # Summarize the PDF with real API
                    pdf_summary = await agent.process_pdf_document(pdf_path, {"filename": attachment['filename']})
                    attachment_summaries.append({
                        "type": "attachment",
                        "summary": pdf_summary
                    })
                    logger.info(f"Attachment summary generated with real API: {pdf_summary['summary'][:100]}...")
            
            # 4. Generate the report
            summaries = [{"type": "email", "summary": email_summary}] + attachment_summaries
            generator = ReportGenerator()
            report = generator.generate_report(email_data, summaries)
            
            # 5. Format for email (just generate, don't send)
            html_report = generator.format_for_email(report)
            
            logger.info("End-to-end test with real API completed successfully")
        except Exception as e:
            logger.error(f"Error in end-to-end test with real API: {str(e)}")
    
    background_tasks.add_task(process_test_email_real)
    
    return {
        "status": "processing",
        "message": "End-to-end test with real API started in the background. Check the logs for details."
    }

@app.post("/test/summarize-pdf-real")
async def test_summarize_pdf_real(file: UploadFile = File(...)):
    """Test PDF summarization with real OpenAI API by uploading a PDF file"""
    
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, dir=settings.temp_dir, suffix=".pdf") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        # Process the PDF with real API
        agent = SummarizationAgent(force_real_api=True)
        result = await agent.process_pdf_document(temp_path, {"filename": file.filename})
        
        return result
    except Exception as e:
        logger.error(f"Error in PDF summarization with real API: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)