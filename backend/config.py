from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class Settings(BaseSettings):
    # MongoDB
    mongo_url: str = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name: str = os.environ.get('DB_NAME', 'bharat_biz_agent')
    
    # Sarvam AI
    sarvam_api_key: str = os.environ.get('SARVAM_API_KEY', '')
    
    # WhatsApp
    whatsapp_access_token: str = os.environ.get('WHATSAPP_ACCESS_TOKEN', '')
    whatsapp_phone_number_id: str = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')
    whatsapp_business_account_id: str = os.environ.get('WHATSAPP_BUSINESS_ACCOUNT_ID', '')
    whatsapp_verify_token: str = os.environ.get('WHATSAPP_VERIFY_TOKEN', '')
    whatsapp_api_version: str = os.environ.get('WHATSAPP_API_VERSION', 'v18.0')
    
    # Business Config
    business_name: str = os.environ.get('BUSINESS_NAME', 'Kapoor Textiles')
    business_address: str = os.environ.get('BUSINESS_ADDRESS', '')
    business_phone: str = os.environ.get('BUSINESS_PHONE', '')
    gst_number: str = os.environ.get('GST_NUMBER', '')
    business_state_code: str = os.environ.get('BUSINESS_STATE_CODE', '07')
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
