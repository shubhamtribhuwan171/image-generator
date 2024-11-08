from flask import Flask
from flask_cors import CORS
from models import db
from routes.image import image_bp
from routes.auth import auth_bp
from routes.sample import sample_bp
from flask_login import LoginManager
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///your_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
CORS(app)
db.init_app(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register blueprints
app.register_blueprint(image_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(sample_bp)

@app.route('/')
def home():
    return 'Server is running!'

if __name__ == '__main__':
    app.run()