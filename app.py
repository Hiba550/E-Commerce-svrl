"""
Main Application Entry Point
Initializes Flask app, database, and registers all blueprints
"""
import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from config import config
from models import db, User
from extensions import cache


def create_app(config_name='development'):
    """Application factory pattern"""
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    cache.init_app(app)
    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        return User.query.get(int(user_id))
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from blueprints.auth import auth_bp
    from blueprints.main import main_bp
    from blueprints.products import products_bp
    from blueprints.cart import cart_bp
    from blueprints.checkout import checkout_bp
    from blueprints.admin import admin_bp
    from blueprints.wishlist import wishlist_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(checkout_bp, url_prefix='/checkout')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(wishlist_bp, url_prefix='/wishlist')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Context processors
    @app.context_processor
    def inject_user_counts():
        """Inject cart item count into all templates"""
        from flask_login import current_user
        if current_user.is_authenticated:
            from models import CartItem, WishlistItem
            cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
            wishlist_count = WishlistItem.query.filter_by(user_id=current_user.id).count()
            return dict(cart_count=cart_count, wishlist_count=wishlist_count)
        return dict(cart_count=0, wishlist_count=0)
    
    return app


if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=True)
