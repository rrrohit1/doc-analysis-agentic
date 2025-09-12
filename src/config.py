from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the API key
google_api_key = os.getenv("GOOGLE_API_KEY")