"""Check database contents"""
from app import create_app
from models import db, User, Category, Product

app = create_app()

with app.app_context():
    print("=== Users ===")
    users = User.query.all()
    for user in users:
        print(f"  - {user.username} ({user.user_type}) - {user.email}")
    
    print(f"\n=== Categories ({Category.query.count()}) ===")
    categories = Category.query.all()
    for cat in categories:
        print(f"  - {cat.name} (slug: {cat.slug}) - Active: {cat.is_active}")
    
    print(f"\n=== Products ({Product.query.count()}) ===")
    products = Product.query.all()
    for prod in products:
        print(f"  - {prod.name} (₹{prod.price}) - Stock: {prod.stock_quantity} - Active: {prod.is_active}")
