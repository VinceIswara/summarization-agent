import os
import subprocess
import tempfile
import logging
import uuid
from typing import Dict, Any, Optional, List

from src.config import settings

logger = logging.getLogger(__name__)

class FileConverter:
    """Service to convert various file formats to PDF"""
    
    def __init__(self):
        self.temp_dir = settings.temp_dir
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def convert_to_pdf(self, file_path: str, original_filename: str) -> Optional[str]:
        """
        Convert a file to PDF format
        
        Args:
            file_path: Path to the original file
            original_filename: Original filename with extension
            
        Returns:
            Path to the converted PDF file, or None if conversion failed
        """
        try:
            file_extension = os.path.splitext(original_filename)[1].lower()
            
            # Check if file is already a PDF
            if file_extension == '.pdf':
                logger.info(f"File is already a PDF: {original_filename}")
                return file_path
            
            # In debug mode, just return a mock PDF path
            if settings.debug:
                logger.info(f"Debug mode: Simulating conversion of {original_filename} to PDF")
                return os.path.join(self.temp_dir, f"{uuid.uuid4()}.pdf")
            
            # Handle Office documents (DOC, DOCX, XLS, XLSX, PPT, PPTX)
            if file_extension in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
                return self._convert_office_to_pdf(file_path)
            
            # Handle images (JPG, PNG, etc.)
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif']:
                return self._convert_image_to_pdf(file_path)
            
            # Unsupported format
            logger.warning(f"Unsupported file format: {file_extension}")
            return None
            
        except Exception as e:
            logger.error(f"Error converting file to PDF: {str(e)}")
            return None
    
    def _convert_office_to_pdf(self, file_path: str) -> Optional[str]:
        """Convert Office documents to PDF using LibreOffice"""
        try:
            output_dir = tempfile.mkdtemp(dir=self.temp_dir)
            
            # Use LibreOffice to convert
            process = subprocess.run([
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', output_dir,
                file_path
            ], capture_output=True, text=True, timeout=60)
            
            if process.returncode != 0:
                logger.error(f"LibreOffice conversion failed: {process.stderr}")
                return None
            
            # Find the generated PDF
            for file in os.listdir(output_dir):
                if file.endswith('.pdf'):
                    return os.path.join(output_dir, file)
            
            logger.error("PDF output not found after conversion")
            return None
            
        except subprocess.TimeoutExpired:
            logger.error("LibreOffice conversion timed out")
            return None
        except Exception as e:
            logger.error(f"Error in Office to PDF conversion: {str(e)}")
            return None
    
    def _convert_image_to_pdf(self, file_path: str) -> Optional[str]:
        """Convert image to PDF using Pillow"""
        try:
            from PIL import Image
            from reportlab.pdfgen import canvas
            from reportlab.lib.utils import ImageReader
            
            output_pdf = os.path.join(self.temp_dir, f"{uuid.uuid4()}.pdf")
            
            # Open image
            img = Image.open(file_path)
            
            # Create PDF
            c = canvas.Canvas(output_pdf, pagesize=(img.width, img.height))
            c.drawImage(ImageReader(img), 0, 0, width=img.width, height=img.height)
            c.save()
            
            return output_pdf
            
        except Exception as e:
            logger.error(f"Error in image to PDF conversion: {str(e)}")
            return None
    
    def cleanup_temp_files(self, file_paths: List[str]):
        """Clean up temporary files after processing"""
        for path in file_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    logger.debug(f"Removed temporary file: {path}")
            except Exception as e:
                logger.error(f"Error cleaning up temp file {path}: {str(e)}")
