from flask import Flask
from routes.auth import auth
from routes.main import main
from routes.admin import admin_bp
from routes.food_rescue import food_rescue_bp
import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here')

    # Register custom filters
    @app.template_filter('urlencode')
    def urlencode_filter(s):
        if s:
            return urllib.parse.quote(str(s))
        return ""

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(food_rescue_bp)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
