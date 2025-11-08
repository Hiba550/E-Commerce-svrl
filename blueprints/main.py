"""
Main Blueprint
Handles home page and general routes
"""
from flask import Blueprint, render_template
from models import Product, Category

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page with featured products"""
    # Get featured products
    featured_products = Product.query.filter_by(is_featured=True, is_active=True).limit(8).all()
    
    # Get all active categories
    categories = Category.query.filter_by(is_active=True).order_by(Category.display_order).all()
    
    return render_template('main/index.html', 
                         featured_products=featured_products,
                         categories=categories)


@main_bp.route('/about')
def about():
    """About us page"""
    return render_template('main/about.html')


@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('main/contact.html')
