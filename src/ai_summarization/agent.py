import os
import base64
import asyncio
import logging
import json
import uuid
from typing import List, Dict, Any, Optional

import fitz  # PyMuPDF
import openai
from openai import OpenAI
from src.ai_summarization.assistant_profiles import get_assistant_profile

from src.config import settings

logger = logging.getLogger(__name__)

class SummarizationAgent:
    """Agent for processing documents and generating summaries using OpenAI's Assistants API."""

    def __init__(self, force_real_api=False):
        api_key = settings.openai_api_key
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"
        self.force_real_api = force_real_api
        self._assistant = None

    def get_or_create_assistant(self, profile: str = "default"):
        """Creates or retrieves a reusable assistant based on the profile."""
        profile_config = get_assistant_profile(profile, self.model)
        version_key = {
            "model": profile_config["model"],
            "tools": profile_config["tools"]
        }
        cache_file = f".cached_assistant_id_{profile}.json"

        if self._assistant:
            return self._assistant

        assistant_data = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    assistant_data = json.load(f)
                if assistant_data.get("version") == version_key:
                    assistant_id = assistant_data.get("id")
                    assistant = self.client.beta.assistants.retrieve(assistant_id)
                    self._assistant = assistant
                    return assistant
            except Exception as e:
                logger.warning(f"Failed to load or use cached assistant: {e}")

        try:
            assistant = self.client.beta.assistants.create(
                name=profile_config["name"],
                description=profile_config["description"],
                model=profile_config["model"],
                tools=profile_config["tools"]
            )
            with open(cache_file, "w") as f:
                json.dump({"id": assistant.id, "version": version_key}, f, indent=2)
            self._assistant = assistant
            return assistant
        except Exception as e:
            logger.error(f"Failed to create assistant: {e}")
            raise

    # Add/Modify in extract_images_from_pdf method:
    def extract_images_from_pdf(self, pdf_path: str, output_dir: str = "/app/tmp/") -> List[Dict[str, Any]]: # Add output_dir arg
        """
        Extract images from a PDF file using PyMuPDF, save them to disk,
        and return metadata including Base64 encoding and file path.
        """
        images = []
        try:
            # Ensure the output directory exists
            os.makedirs(output_dir, exist_ok=True) # Create dir if needed
            logger.info(f"Ensured image output directory exists: {output_dir}")

            doc = fitz.open(pdf_path)
            # Get PDF name without extension for unique filenames
            pdf_basename = os.path.splitext(os.path.basename(pdf_path))[0]

            for page_num, page in enumerate(doc, start=1):
                for img_index, img in enumerate(page.get_images(full=True), start=1):
                    xref = img[0]
                    try: # Add inner try/except for individual image robustness
                        base_image = doc.extract_image(xref)
                        if not base_image: # Skip if image extraction failed
                            logger.warning(f"Could not extract image index {img_index} on page {page_num}")
                            continue
                        image_bytes = base_image["image"]
                        img_format = base_image["ext"]

                        # *** START: Code to save image file ***
                        unique_suffix = uuid.uuid4().hex[:6]
                        filename = f"{pdf_basename}_p{page_num}_img{img_index}_{unique_suffix}.{img_format}"
                        output_path = os.path.join(output_dir, filename)
                        try:
                            with open(output_path, "wb") as img_file:
                                img_file.write(image_bytes)
                            logger.debug(f"Saved image to: {output_path}")
                        except OSError as e:
                            logger.warning(f"Failed to save image {filename} to {output_dir}: {e}")
                            output_path = None # Indicate saving failed
                        # *** END: Code to save image file ***

                        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                        images.append({
                            "page": page_num,
                            "index": img_index,
                            "format": img_format,
                            "width": base_image.get("width", 0),
                            "height": base_image.get("height", 0),
                            "base64": image_base64,
                            "filepath": output_path # Add the saved file path
                        })
                    except Exception as e_inner:
                        logger.warning(f"Error processing image index {img_index} on page {page_num}: {e_inner}")

        except Exception as e:
            # Log the main exception for the whole function
            logger.error(f"Failed during image extraction process for PDF {pdf_path}: {e}", exc_info=True)
        return images

    async def process_pdf_document(self, pdf_path: str, document_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a PDF document by extracting its content and generating a summary using OpenAI's Assistants API.

        Args:
            pdf_path: Path to the PDF file.
            document_metadata: Metadata associated with the document.

        Returns:
            A dictionary containing the success status, summary, and metadata.
        """
        try:
            # Extract images from the PDF
            extracted_images = self.extract_images_from_pdf(pdf_path, output_dir="/app/tmp/")

            # Generate image descriptions using GPT
            for image_data in extracted_images:
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/{image_data['format']};base64,{image_data['base64']}"
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": "Describe the image. It may contain charts or figures relevant to business or scientific contexts."
                                }
                            ]
                        }
                    ],
                    temperature=0.5,
                        max_tokens=150
                    )
                    description = response.choices[0].message.content.strip()
                    # Add caption directly to the dict in extracted_images
                    image_data["caption"] = description
                except Exception as e:
                    logger.warning(f"Error generating caption for image {image_data['index']} on page {image_data['page']}: {e}")
                    # Add error caption directly to the dict in extracted_images
                    image_data["caption"] = "Error generating caption"

            # Upload the PDF file to OpenAI
            with open(pdf_path, "rb") as file:
                file_response = self.client.files.create(file=file, purpose="assistants")
            file_id = file_response.id

            assistant = self.get_or_create_assistant(profile="pdf_summarizer")
            # Attach the file to the assistant run context

            # Create a thread and send a message to the assistant
            thread = self.client.beta.threads.create()
            image_captions_text = "\n".join(
                f"- Page {d['page']} Image {d['index']} (Saved: {d.get('filepath', 'No') or 'No'}): {d.get('caption', 'N/A')}" 
                for d in extracted_images
            )
            full_prompt = (
                "Please analyze the uploaded PDF document and generate a concise summary with bullet points, "
                "highlighting key information and insights. The summary should be readable in under 10 minutes.\n\n"
                "The following are captions of images extracted from the PDF. Use them as supplemental context for the summary, "
                "since the assistant cannot directly see images embedded in the PDF:\n"
                f"{image_captions_text}"
            )
            message = self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=full_prompt, # Just the text prompt
                attachments=[        # Use the attachments parameter
                    {
                        "file_id": file_id,
                        "tools": [{"type": "file_search"}]
                    }
                ]
            )

            # Run the assistant and wait for completion
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id,
                # Remove file_ids and tools override
                additional_instructions="Use the attached PDF (via file search) and provided image captions to summarize concisely."
            )
            while run.status not in ["completed", "failed", "cancelled", "expired"]:
                await asyncio.sleep(1)
                run = self.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            if run.status != "completed":
                logger.error(f"PDF processing run failed with status: {run.status}, error: {run.last_error}")
                return {"success": False, "error": f"Processing failed with status: {run.status}, Last error: {run.last_error}"}

            # Retrieve the assistant's response
            messages = self.client.beta.threads.messages.list(thread_id=thread.id, order="desc", limit=1)
            summary_text = "Assistant response not found or invalid format."
            if messages.data and messages.data[0].role == "assistant": 
                if messages.data[0].content and isinstance(messages.data[0].content[0], openai.types.beta.threads.TextContentBlock):  
                    summary_text = messages.data[0].content[0].text.value

            # Return Success

            return {
                "success": True,
                "summary": summary_text,
                "metadata": {
                    "filename": os.path.basename(pdf_path),
                    "extracted_images_data": extracted_images,
                }
            }

        except Exception as e:
            logger.error(f"Error processing PDF with OpenAI: {e}", exc_info=True)
            return {"success": False, "error": str(e), "metadata": {"filename": os.path.basename(pdf_path)}}

        finally:
            # Cleanup Thread (Optional but Recommended)
            if thread:
                try:
                    logger.info(f"Deleting thread {thread.id}")
                    self.client.beta.threads.delete(thread.id)
                except Exception as e_del_thread:
                    logger.warning(f"Failed to delete thread {thread.id}: {e_del_thread}")
            # Cleanup File (Essential)
            if file_id:
                try:
                    logger.info(f"Deleting file {file_id}")
                    self.client.files.delete(file_id)
                except Exception as e_del_file:
                    logger.warning(f"Failed to delete file {file_id}: {e_del_file}")
