import os
try:
    from dotenv import load_dotenv
    # 📁 Load .env variables locally
    load_dotenv()
except ImportError:
    # 🌍 Silent fail: handled by Render env-vars in cloud
    pass

# 📂 Database Configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),  # Set this in Render's ENV
    'database': os.getenv('DB_NAME', 'donation'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# 📧 Email Configuration (Fetched from environment variables in cloud)
EMAIL_USER = os.getenv('EMAIL_USER', 'adityajadhav3117@gmail.com')
EMAIL_PASS = os.getenv('EMAIL_PASS', '')  # Set this in Render's ENV
