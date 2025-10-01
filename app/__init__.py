from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from logging.handlers import RotatingFileHandler
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
cache = Cache()
jwt = JWTManager()
mail = Mail()
scheduler = BackgroundScheduler()

def create_app(config_name='default'):
    """Application factory pattern"""
    from config import config

    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    cache.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app, supports_credentials=True)

    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        try:
            uid = int(user_id) if isinstance(user_id, str) else user_id
            return User.query.get(uid)
        except (ValueError, TypeError):
            return None

    # JWT user loader
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        from app.models import User
        identity = jwt_data["sub"]
        try:
            uid = int(identity) if isinstance(identity, str) else identity
            return User.query.get(uid)
        except (ValueError, TypeError):
            return None

    # Register blueprints
    from app.routes import auth, stock, portfolio, watchlist, screener, alerts, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(stock.bp)
    app.register_blueprint(portfolio.bp)
    app.register_blueprint(watchlist.bp)
    app.register_blueprint(screener.bp)
    app.register_blueprint(alerts.bp)
    app.register_blueprint(main.bp)

    # Setup logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/stockanalyzer.log',
                                           maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Stock Analyzer startup')

    # Start scheduler for background jobs (disabled for now to avoid errors)
    # if not app.testing:
    #     from jobs.scheduler import setup_jobs
    #     setup_jobs(app, scheduler)
    #     scheduler.start()

    # Create database tables (only if not using migrations)
    # with app.app_context():
    #     db.create_all()

    return app