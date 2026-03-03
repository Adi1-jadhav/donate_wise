from flask import Flask
from routes.auth import auth
from routes.main import main
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key_here'

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
