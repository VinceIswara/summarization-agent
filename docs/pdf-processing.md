# PDF Processing

This document provides detailed information about the PDF processing capabilities in the Summarization Agent.

## Overview

The PDF processing module is a core component of the Summarization Agent that handles extraction, analysis, and summarization of PDF documents. It supports multimodal understanding by processing both text and images within PDFs, enabling comprehensive document analysis.

## Features

- **Text Extraction**: Extracts complete text content from PDF documents while preserving structure.
- **Image Extraction**: Identifies, extracts, and saves images embedded in PDF documents.
- **OCR Support**: Recognizes text within images using optical character recognition (future enhancement).
- **PDF Conversion**: Converts various document formats to PDF for consistent processing.
- **Multimodal Analysis**: Combines text and image analysis for comprehensive understanding.
- **Page Structure Analysis**: Preserves document structure including headers, paragraphs, and lists.
- **Image Captioning**: Generates descriptive captions for extracted images using AI.

## Implementation Details

### PDF Processing Pipeline

1. **Document Validation**: Verifies PDF integrity and structure.
2. **Text Extraction**: Extracts text content using PyMuPDF (fitz).
3. **Image Extraction**: Identifies and extracts images from the PDF.
4. **Image Processing**: Saves extracted images with unique filenames using UUID generation.
5. **Image Analysis**: Generates captions and descriptions for images using AI.
6. **Content Structuring**: Organizes extracted content into a structured format.
7. **Summarization**: Processes the structured content through the AI summarization agent.

### Image Extraction Process

Images are extracted from PDFs using the following process:

1. Iterate through each page of the PDF document.
2. Identify image objects within each page.
3. Extract each image and determine its format (JPEG, PNG, etc.).
4. Generate a unique filename using UUID for each image.
5. Save the image to the configured output directory.
6. Record metadata including page number, format, dimensions, and file path.
7. Generate AI-based captions for each image (when enabled).

### Key Code Sections

Below are the core functions for image extraction from PDFs:

```python
def extract_images_from_pdf(pdf_path, output_dir=None):
    """
    Extracts images from a PDF file and saves them to disk with unique filenames.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str, optional): Directory to save extracted images
        
    Returns:
        list: Information about extracted images including path and metadata
    """
    if output_dir is None:
        output_dir = "./tmp"
        
    os.makedirs(output_dir, exist_ok=True)
    
    extracted_images = []
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_num, page in enumerate(doc):
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                try:
                    # Extract image information
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_format = base_image["ext"]
                    
                    # Generate unique filename with UUID
                    unique_id = uuid.uuid4().hex[:8]
                    filename = f"page{page_num+1}_img{img_index+1}_{unique_id}.{image_format}"
                    image_path = os.path.join(output_dir, filename)
                    
                    # Save the image
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)
                    
                    # Get image dimensions
                    image = Image.open(io.BytesIO(image_bytes))
                    width, height = image.size
                    
                    # Add to extracted images list
                    image_info = {
                        "page": page_num + 1,
                        "index": img_index + 1,
                        "format": image_format,
                        "width": width,
                        "height": height,
                        "filepath": image_path,
                        "error": None
                    }
                    extracted_images.append(image_info)
                    
                except Exception as e:
                    # Record failed extraction with error
                    error_info = {
                        "page": page_num + 1,
                        "index": img_index + 1,
                        "format": "unknown",
                        "width": 0,
                        "height": 0,
                        "filepath": None,
                        "error": str(e)
                    }
                    extracted_images.append(error_info)
        
        return extracted_images
        
    except Exception as e:
        logger.error(f"Failed to extract images from PDF: {e}")
        return []
```

### Error Handling

The PDF processing module implements robust error handling:

- **Nested Error Handling**: Continues processing if individual image extraction fails.
- **Status Tracking**: Includes error status in image metadata.
- **Error Logging**: Detailed logging of processing errors for debugging.
- **Graceful Degradation**: Falls back to text-only processing if image extraction fails.

## Usage Examples

### Basic PDF Summarization

To process a PDF file using the test endpoint:

```bash
curl -X POST "http://localhost:8000/test/summarize-pdf" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf"
```

### PDF Summarization with Real API

For processing with the real OpenAI API:

```bash
curl -X POST "http://localhost:8000/test/summarize-pdf-real" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf"
```

### Programmatic Usage

Here's an example of how to use the PDF processing module programmatically:

```python
from src.document_processing.pdf_processor import PDFProcessor

# Initialize the processor
processor = PDFProcessor(output_dir="./tmp")

# Process a PDF file
result = processor.process_pdf("/path/to/document.pdf", extract_images=True)

# Access the extracted content
text_content = result["text"]
image_data = result["images"]
metadata = result["metadata"]

# Display information about extracted images
for img in image_data:
    print(f"Image on page {img['page']}: {img['filepath']}")
    
# Process with AI summarization
from src.ai_summarization.agent import SummarizationAgent

agent = SummarizationAgent()
summary = agent.summarize(
    text=text_content,
    images=image_data,
    document_metadata=metadata
)

print(f"Summary: {summary['summary']}")
```

## Configuration Options

The PDF processing module can be configured through environment variables or the settings API:

| Option | Description | Default Value |
|--------|-------------|---------------|
| `MAX_IMAGE_SIZE` | Maximum image size to process (in bytes) | 10485760 (10MB) |
| `OUTPUT_DIR` | Directory to store extracted images | ./tmp |
| `ENABLE_IMAGE_CAPTIONING` | Whether to generate captions for images | true |
| `IMAGE_QUALITY` | JPEG quality for saved images (1-100) | 85 |
| `MAX_PDF_SIZE` | Maximum PDF size to process (in bytes) | 25000000 (25MB) |
| `EXTRACT_IMAGES` | Whether to extract images by default | true |
| `IMAGE_FORMAT` | Default format for saving images | jpeg |

## Output Format

The PDF processing module produces structured output containing:

```json
{
  "success": true,
  "summary": "AI-generated summary of the PDF content",
  "metadata": {
    "filename": "original_document.pdf",
    "page_count": 5,
    "file_size": 1524000,
    "extracted_text_length": 15240,
    "processed_at": "2023-09-10T14:30:15.123456",
    "extracted_images_data": [
      {
        "page": 1,
        "index": 1,
        "format": "jpeg",
        "width": 800,
        "height": 600,
        "filepath": "/app/tmp/document_p1_img1_abc123.jpeg",
        "caption": "Description of the image generated by AI",
        "error": null
      },
      {
        "page": 2,
        "index": 1,
        "format": "png",
        "width": 1200,
        "height": 900,
        "filepath": "/app/tmp/document_p2_img1_def456.png",
        "caption": "Description of the image generated by AI",
        "error": null
      }
    ]
  }
}
```

## Technical Implementation

### Key Dependencies

- **PyMuPDF (fitz)**: Core library for PDF parsing and extraction
- **Pillow**: Image processing and manipulation
- **UUID**: Generation of unique identifiers for image files
- **OpenAI**: AI-based image captioning and content analysis

### Dependency Installation

Ensure you have the necessary dependencies installed:

```bash
pip install PyMuPDF pillow uuid python-magic
```

Or use the project's `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Code Structure

The PDF processing functionality is primarily implemented in:
- `src/document_processing/pdf_processor.py`: Core PDF processing logic
- `src/ai_summarization/agent.py`: AI summarization of extracted content
- `src/utils/image_utils.py`: Image handling utilities

### Performance Considerations

- PDF processing is resource-intensive and scales with document size and complexity
- Large documents with many images may require significant memory
- Image extraction increases processing time and storage requirements
- Consider implementing batch processing for large documents

#### Performance Optimization Tips

1. **Process images selectively**: Set `extract_images=False` for text-only processing when images aren't needed
2. **Limit page range**: Process specific page ranges for large documents
3. **Implement image size limits**: Skip very large images to conserve memory
4. **Use memory profiling**: Monitor memory usage with tools like `memory_profiler`
5. **Add pagination**: Process large documents in chunks of pages

## Limitations and Future Enhancements

### Current Limitations

- Maximum PDF size is limited to prevent resource exhaustion
- Complex document layouts may not be perfectly preserved
- PDF forms and interactive elements are not fully supported
- Some heavily protected PDFs may not be processable
- Image extraction may miss vector graphics or complex embedded content

### Planned Enhancements

- **Improved OCR**: Better text recognition in images
- **Table Extraction**: Structured extraction of tabular data
- **Content Classification**: Automatic categorization of document content
- **Incremental Processing**: Support for processing large documents in chunks
- **Layout Preservation**: Better preservation of complex document layouts
- **Language Detection**: Automatic detection and handling of multiple languages
- **Vector Graphics Support**: Improved handling of SVG and other vector content

## Troubleshooting

### Common Issues

1. **"Failed to extract images from PDF"**: Check if PDF contains extractable images and isn't protected
2. **"Error saving image to disk"**: Verify disk space and directory permissions
3. **"PDF too large"**: Reduce PDF size or increase MAX_PDF_SIZE setting
4. **Slow processing time**: Consider optimizing image extraction settings or disabling for large documents
5. **Memory errors**: Try processing fewer pages at once or disable image extraction

### Diagnostic Checklist

- [ ] Verify the PDF file isn't corrupted (try opening it in a PDF reader)
- [ ] Check if the PDF is password-protected or has security restrictions
- [ ] Ensure sufficient disk space for extracted images
- [ ] Verify directory permissions allow writing to the output directory
- [ ] Check system memory is sufficient for the PDF size
- [ ] Verify all dependencies are correctly installed

### Debugging

Enable detailed logging by setting the `LOG_LEVEL` environment variable to `DEBUG`.

```bash
export LOG_LEVEL=DEBUG
```

Or in your Docker environment:

```yaml
environment:
  - LOG_LEVEL=DEBUG
```

## References

- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/en/latest/)
- [PDF Specification Reference](https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Pillow (PIL Fork) Documentation](https://pillow.readthedocs.io/)
- [UUID Documentation](https://docs.python.org/3/library/uuid.html)
