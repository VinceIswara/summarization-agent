# Summarization Agent

An AI-powered application that automatically processes emails and documents to generate concise, insightful summaries.

## Overview

The Summarization Agent uses cutting-edge AI technology to analyze emails, PDFs, and various document types, extracting key information and presenting it in an easily digestible format. The system leverages OpenAI's GPT-4o model and Assistants API to provide high-quality summarization with support for both textual and visual content.

## Key Features

- **Email Processing**: Automatically retrieves and processes emails from Outlook
- **Document Analysis**: Extracts and analyzes text and images from PDFs and other document formats
- **Multimodal Understanding**: Processes both text and visual elements for comprehensive understanding
- **Intelligent Summarization**: Generates structured, bullet-point summaries focused on key information
- **Visual Content Analysis**: Extracts and describes images, charts, and diagrams from documents
- **Resource Efficiency**: Implements assistant caching and reuse for optimal performance
- **Docker Integration**: Runs in containerized environments for easy deployment

## Architecture

The system is built with a modular architecture:

- **Email Ingestion**: Connects to email servers to retrieve messages and attachments
- **Attachment Processing**: Converts documents to PDF and extracts content
- **AI Summarization**: Analyzes document content using OpenAI's Assistants API
- **Report Generation**: Creates formatted summaries with bullet points
- **Notification System**: Delivers summaries via email or other channels

## Technology Stack

- **Backend**: Python 3.11 with FastAPI
- **AI**: OpenAI GPT-4o and Assistants API
- **PDF Processing**: PyMuPDF for text and image extraction
- **Containerization**: Docker and Docker Compose
- **Data Storage**: Supabase (planned)
- **Notifications**: SendGrid and Twilio (planned)

## Getting Started

### Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Python 3.11+ (for local development)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/summarization-agent.git
   cd summarization-agent
   ```

2. Configure your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. Build and start the Docker containers:
   ```bash
   docker-compose up --build
   ```

4. The API will be available at `http://localhost:8000`

### Usage

#### API Endpoints

- `POST /api/process-emails`: Process unread emails from the configured account
- `GET /health`: Check service health status
- `POST /test/summarize-pdf-real`: Test PDF summarization with a direct file upload

See the [API documentation](docs/api-endpoints.md) for more details.

## Development

```bash
uvicorn src.main:app --reload
```

### Project Structure

summarization-agent/
├── src/
│ ├── ai_summarization/ # AI processing with OpenAI
│ ├── attachment_processor/ # File conversion utilities
│ ├── email_ingestion/ # Email fetching and parsing
│ ├── notifications/ # Email and WhatsApp notification
│ ├── report_generator/ # Report creation and formatting
│ ├── config.py # Configuration management
│ ├── main.py # FastAPI application
│ └── tasks.py # Background task handling
├── tests/ # Unit and integration tests
├── docker-compose.yml # Docker configuration
├── Dockerfile # Application container definition
└── requirements.txt # Python dependencies


### Running Tests

```bash
docker-compose exec app pytest
```

#### Local Development

If you prefer to run the application without Docker:

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn src.main:app --reload
```

## Documentation

- [Product Requirements Document (PRD)](docs/PRD.md) - Original project specifications and requirements
- [Implementation Plan](docs/Implementation-plan.md) - Step-by-step development plan with current status
- [API Endpoints](docs/api-endpoints.md) - Detailed API reference with request/response formats
- [PDF Processing](docs/pdf-processing.md) - PDF extraction and processing capabilities
- [Assistants API Integration](docs/assistants-api.md) - OpenAI Assistants API implementation details
- [Docker Setup](docs/docker-setup.md) - Container configuration and deployment guide
- [Architecture](docs/architecture.md) - System architecture, components, and data flow

## License

[MIT License](LICENSE)

