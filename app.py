# app.py

from flask import Flask, render_template
from config import Config
from models import db
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, current_user
from routes.auth import auth_bp
from routes.sample import sample_bp
from routes.image import image_bp  # Import the Image Blueprint
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirect to login page if not authenticated

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(sample_bp, url_prefix='/api')
    app.register_blueprint(image_bp, url_prefix='/image')  # Register the Image Blueprint

    # Import User model for login manager
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Home route (Landing Page)
    @app.route('/')
    def landing():
        return render_template('landing.html')

    # Dashboard route
    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html', user=current_user)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
