import imaplib
import email
from email.header import decode_header
import os
import logging
from datetime import datetime
import tempfile
from typing import List, Dict, Any

from src.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.email_username = settings.email_username
        self.email_password = settings.email_password
        self.email_server = settings.email_server
        self.email_port = settings.email_port
        self.temp_dir = settings.temp_dir
        self.conn = None
        
        # Ensure temp directory exists
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def connect(self) -> bool:
        """Connect to the email server"""
        try:
            if settings.debug:
                logger.info("Debug mode: Simulating email connection")
                return True
                
            self.conn = imaplib.IMAP4_SSL(self.email_server, self.email_port)
            self.conn.login(self.email_username, self.email_password)
            logger.info("Successfully connected to email server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to email server: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from the email server"""
        if not settings.debug and self.conn:
            try:
                self.conn.close()
                self.conn.logout()
            except Exception as e:
                logger.error(f"Error disconnecting from email server: {str(e)}")
    
    def get_unread_emails(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch unread emails from the inbox"""
        if settings.debug:
            # Return a test email in debug mode
            logger.info("Debug mode: Returning test email")
            return [{
                "id": "test_email_id",
                "subject": "Test Email Subject",
                "sender": "sender@example.com",
                "date": "Mon, 19 Aug 2023 12:00:00 +0000",
                "body": "This is a test email body with important information that needs to be summarized.",
                "attachments": [],
                "timestamp": datetime.now().isoformat()
            }]
        
        emails = []
        
        if not self.conn and not self.connect():
            return emails
        
        try:
            self.conn.select("INBOX")
            status, data = self.conn.search(None, "UNSEEN")
            
            if status != "OK" or not data[0]:
                logger.info("No unread emails found")
                return emails
            
            email_ids = data[0].split()
            count = 0
            
            for email_id in email_ids:
                if count >= limit:
                    break
                
                status, data = self.conn.fetch(email_id, "(RFC822)")
                if status != "OK":
                    logger.warning(f"Failed to fetch email with ID {email_id}")
                    continue
                
                raw_email = data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                # Extract email metadata
                subject, encoding = decode_header(email_message["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")
                
                sender, encoding = decode_header(email_message["From"])[0]
                if isinstance(sender, bytes):
                    sender = sender.decode(encoding if encoding else "utf-8", errors="ignore")
                
                date = email_message["Date"]
                
                # Process email body and attachments
                body = ""
                attachments = []
                
                if email_message.is_multipart():
                    for part in email_message.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        
                        # Get email body
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            try:
                                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            except Exception as e:
                                logger.error(f"Error decoding email body: {str(e)}")
                                body = "Error decoding email body"
                        
                        # Get attachments
                        if "attachment" in content_disposition:
                            filename = part.get_filename()
                            if filename:
                                # Clean filename to avoid path traversal
                                filename = os.path.basename(filename)
                                attachment_data = part.get_payload(decode=True)
                                
                                # Save attachment to temp file
                                with tempfile.NamedTemporaryFile(delete=False, dir=self.temp_dir) as temp_file:
                                    temp_file.write(attachment_data)
                                    temp_path = temp_file.name
                                
                                attachments.append({
                                    "filename": filename,
                                    "content_type": content_type,
                                    "path": temp_path,
                                    "size": len(attachment_data)
                                })
                else:
                    # Handle non-multipart email
                    try:
                        body = email_message.get_payload(decode=True).decode("utf-8", errors="ignore")
                    except Exception as e:
                        logger.error(f"Error decoding email body: {str(e)}")
                        body = "Error decoding email body"
                
                # Create email object
                email_obj = {
                    "id": email_id.decode(),
                    "subject": subject,
                    "sender": sender,
                    "date": date,
                    "body": body,
                    "attachments": attachments,
                    "timestamp": datetime.now().isoformat()
                }
                
                emails.append(email_obj)
                count += 1
            
            return emails
        
        except Exception as e:
            logger.error(f"Error retrieving emails: {str(e)}")
            return emails