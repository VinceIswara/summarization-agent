# File: src/tasks.py
# Location: /summarization-agent/src/tasks.py

import logging
import asyncio
import os
from typing import Dict, Any, List

from src.email_ingestion.service import EmailService
from src.attachment_processor.converter import FileConverter
from src.ai_summarization.agent import SummarizationAgent
from src.report_generator.generator import ReportGenerator

logger = logging.getLogger(__name__)

async def process_emails_task():
    """
    Background task to process unread emails
    """
    logger.info("Starting email processing task")
    
    # Initialize services
    email_service = EmailService()
    
    # Fetch unread emails
    emails = email_service.get_unread_emails(limit=5)
    logger.info(f"Found {len(emails)} unread emails to process")
    
    # Process each email
    for email in emails:
        await process_single_email(email)
    
    # Clean up
    email_service.disconnect()
    logger.info("Email processing task completed")

async def process_single_email(email_data: Dict[str, Any]):
    """
    Process a single email and its attachments
    
    Args:
        email_data: Dictionary containing email metadata and content
    """
    try:
        logger.info(f"Processing email: {email_data['subject']}")
        
        # Process attachments
        converted_pdfs = []
        if email_data['attachments']:
            converted_pdfs = await process_attachments(email_data['attachments'])
            logger.info(f"Processed {len(converted_pdfs)} attachments")
        
        # For now, simulate AI processing
        logger.info("Simulating AI processing...")
        await asyncio.sleep(2)
        
        # Later we'll add the actual AI summarization here
        
        # Clean up temp files (in a real app, you might want to keep these until the entire process is complete)
        # file_converter = FileConverter()
        # file_converter.cleanup_temp_files([attachment['path'] for attachment in email_data['attachments']])
        # for pdf_path in converted_pdfs:
        #     if os.path.exists(pdf_path):
        #         os.remove(pdf_path)
        
        logger.info(f"Email processed successfully: {email_data['subject']}")
        
    except Exception as e:
        logger.error(f"Error processing email: {str(e)}")

async def process_attachments(attachments: List[Dict[str, Any]]) -> List[str]:
    """
    Process email attachments
    
    Args:
        attachments: List of attachment dictionaries
    
    Returns:
        List of paths to converted PDF files
    """
    converter = FileConverter()
    converted_pdfs = []
    
    for attachment in attachments:
        try:
            logger.info(f"Processing attachment: {attachment['filename']}")
            
            # Convert to PDF if needed
            pdf_path = converter.convert_to_pdf(
                attachment['path'], 
                attachment['filename']
            )
            
            if pdf_path:
                logger.info(f"Successfully converted to PDF: {attachment['filename']}")
                converted_pdfs.append(pdf_path)
            else:
                logger.warning(f"Failed to convert to PDF: {attachment['filename']}")
                
        except Exception as e:
            logger.error(f"Error processing attachment {attachment['filename']}: {str(e)}")
    
    return converted_pdfs