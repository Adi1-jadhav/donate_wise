import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# 📂 MySQL Configuration (Keep original for fallback/reference)
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'root'),
    'database': os.getenv('MYSQL_DATABASE', 'donation'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

# 🍃 MongoDB Configuration (Recommended for Vercel)
# Format: "mongodb+srv://<user>:<password>@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority"
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'donatewise')

# ☁️ Cloudinary Configuration (For persistent image storage on Vercel)
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

# 📧 Email Configuration
EMAIL_USER = os.getenv('EMAIL_USER', 'adityajadhav3117@gmail.com')
EMAIL_PASS = os.getenv('EMAIL_PASS', '') 
