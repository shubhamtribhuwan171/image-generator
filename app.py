from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from flask_login import LoginManager
from routes.auth import auth_bp
from routes.image import image_bp
from routes.sample import sample_bp

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS
    
# Load configuration
app.config.from_object(Config)
    
# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
    
# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(image_bp, url_prefix='/image')
app.register_blueprint(sample_bp, url_prefix='/api')
    
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
    
if __name__ == '__main__':
    app.run()