# File: src/config.py
# Location: /summarization-agent/src/config.py

import os
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # Supabase Configuration (placeholders for now)
    supabase_url: str = Field("https://example.supabase.co", env="SUPABASE_URL")
    supabase_key: str = Field("your-supabase-key", env="SUPABASE_KEY")
    
    # OpenAI Configuration
    openai_api_key: str = Field("your-openai-api-key", env="OPENAI_API_KEY")
    
    # Email Configuration
    email_username: str = Field("email@example.com", env="EMAIL_USERNAME")
    email_password: str = Field("password", env="EMAIL_PASSWORD")
    email_server: str = Field("outlook.office365.com", env="EMAIL_SERVER")
    email_port: int = Field(993, env="EMAIL_PORT")
    
    # Sendgrid Configuration
    sendgrid_api_key: str = Field("your-sendgrid-key", env="SENDGRID_API_KEY")
    sendgrid_from_email: str = Field("noreply@example.com", env="SENDGRID_FROM_EMAIL")
    
    # Twilio Configuration
    twilio_account_sid: str = Field("your-twilio-sid", env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str = Field("your-twilio-token", env="TWILIO_AUTH_TOKEN")
    twilio_phone_number: str = Field("+1234567890", env="TWILIO_PHONE_NUMBER")
    
    # Application Configuration
    debug: bool = Field(True, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    max_attachment_size: int = Field(25000000, env="MAX_ATTACHMENT_SIZE")  # 25MB
    
    # Paths
    temp_dir: str = Field("./tmp", env="TEMP_DIR")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create a global settings object
settings = Settings() 