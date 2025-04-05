import logging
import json
from typing import Dict, Any, List
import time
import uuid

from src.config import settings

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Service to generate summary reports from AI processing results"""
    
    def generate_report(self, email_data: Dict[str, Any], summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a comprehensive report from email and attachment summaries
        
        Args:
            email_data: Original email data
            summaries: List of summaries for email and attachments
            
        Returns:
            Dictionary containing the formatted report
        """
        try:
            # Extract email metadata
            subject = email_data.get("subject", "No subject")
            sender = email_data.get("sender", "Unknown sender")
            date = email_data.get("date", "Unknown date")
            
            # Find email summary
            email_summary = "Email content could not be summarized."
            attachment_summaries = []
            
            for item in summaries:
                if item["type"] == "email" and item["summary"]["success"]:
                    email_summary = item["summary"]["summary"]
                elif item["type"] == "attachment" and item["summary"]["success"]:
                    attachment_summaries.append({
                        "filename": item["summary"]["metadata"]["filename"],
                        "summary": item["summary"]["summary"]
                    })
            
            # Generate a unique report ID
            report_id = str(uuid.uuid4())
            
            # Create the report
            report = {
                "report_id": report_id,
                "metadata": {
                    "subject": subject,
                    "sender": sender,
                    "date": date,
                    "generated_at": time.time()
                },
                "email_summary": email_summary,
                "attachment_summaries": attachment_summaries
            }
            
            # In a real app, you would store this report in a database
            logger.info(f"Generated report {report_id} for email: {subject}")
            
            return {
                "success": True,
                "report": report
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def format_for_email(self, report: Dict[str, Any]) -> str:
        """Format report for email delivery"""
        try:
            if not report.get("success", False) or "report" not in report:
                return "Error generating report."
            
            report_data = report["report"]
            metadata = report_data.get("metadata", {})
            email_summary = report_data.get("email_summary", "No email summary available")
            attachment_summaries = report_data.get("attachment_summaries", [])
            
            # Build HTML content
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    h1 {{ color: #2c3e50; }}
                    h2 {{ color: #3498db; margin-top: 20px; }}
                    .metadata {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                    .summary {{ margin-bottom: 30px; }}
                    .attachment {{ margin-bottom: 25px; background-color: #f1f1f1; padding: 15px; border-radius: 5px; }}
                    .attachment h3 {{ margin-top: 0; color: #2c3e50; }}
                </style>
            </head>
            <body>
                <h1>Email Summary Report</h1>
                
                <div class="metadata">
                    <strong>Subject:</strong> {metadata.get("subject", "Unknown")}<br>
                    <strong>From:</strong> {metadata.get("sender", "Unknown")}<br>
                    <strong>Date:</strong> {metadata.get("date", "Unknown")}<br>
                </div>
                
                <h2>Email Summary</h2>
                <div class="summary">
                    {email_summary}
                </div>
            """
            
            if attachment_summaries:
                html_content += "<h2>Attachments</h2>"
                
                for attachment in attachment_summaries:
                    html_content += f"""
                    <div class="attachment">
                        <h3>{attachment.get("filename", "Unknown file")}</h3>
                        <div>{attachment.get("summary", "No summary available")}</div>
                    </div>
                    """
            
            html_content += """
                <hr>
                <p style="color: #7f8c8d; font-size: 0.8em;">This report was generated automatically by the Summarization Agent.</p>
            </body>
            </html>
            """
            
            return html_content
            
        except Exception as e:
            logger.error(f"Error formatting report for email: {str(e)}")
            return "Error formatting report for email."
