"""
Database Initialization Script
Creates initial database tables and populates with sample data
"""
import os
from app import create_app
from models import db, User, Category, Product

def init_database():
    """Initialize database with tables and sample data"""
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate (careful in production!)
        print("Creating database tables...")
        db.create_all()
        
        # Check if admin exists
        admin_exists = User.query.filter_by(username='admin').first()
        if admin_exists:
            print("Admin user already exists!")
        
        # Check if products exist
        products_exist = Product.query.count() > 0
        if products_exist:
            print("Products already exist!")
        
        if admin_exists and products_exist:
            return
        
        if not admin_exists:
            print("Creating admin user...")
            # Create admin user
            admin = User(
                username='admin',
                email='admin@shreevinayaga.com',
                full_name='Admin User',
                user_type='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create test customer
            customer = User(
                username='customer',
                email='customer@example.com',
                full_name='Test Customer',
                user_type='customer'
            )
            customer.set_password('customer123')
            db.session.add(customer)
            
            db.session.commit()
            print("✓ Admin user created (username: admin, password: admin123)")
            print("✓ Test customer created (username: customer, password: customer123)")
        else:
            print("✓ Admin user already exists")
        
        print("\nCreating product categories...")
        # Create categories
        categories_data = [
            {
                'name': 'Refined Rice Bran Oil',
                'slug': 'refined-rbo',
                'description': 'Premium quality refined rice bran oil for everyday cooking',
                'is_active': True,
                'display_order': 1
            },
            {
                'name': 'Cold Pressed Oil',
                'slug': 'cold-pressed',
                'description': 'Traditionally extracted cold pressed oils',
                'is_active': True,
                'display_order': 2
            },
            {
                'name': 'Premium Oil',
                'slug': 'premium',
                'description': 'Premium range of cooking oils',
                'is_active': True,
                'display_order': 3
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            category = Category(**cat_data)
            db.session.add(category)
            categories.append(category)
        
        db.session.commit()
        print(f"✓ Created {len(categories)} categories")
        
        print("\nCreating products...")
        # Create products
        products_data = [
            {
                'name': 'Refined Rice Bran Oil - 1L',
                'slug': 'rbo-1l',
                'sku': 'RBO-1L-001',
                'description': 'Premium quality refined rice bran oil. Rich in Oryzanol and Vitamin E. Perfect for all types of cooking - frying, sautéing, and baking.',
                'price': 180.00,
                'mrp': 200.00,
                'discount_percentage': 10,
                'size': '1',
                'unit': 'Litre',
                'stock_quantity': 500,
                'low_stock_threshold': 50,
                'image_url': 'images/products/rbo-1l.jpg',
                'features': 'High smoke point, Rich in Oryzanol, Heart healthy, No cholesterol',
                'is_active': True,
                'is_featured': True,
                'category_id': 1
            },
            {
                'name': 'Refined Rice Bran Oil - 5L',
                'slug': 'rbo-5l',
                'sku': 'RBO-5L-001',
                'description': 'Family pack refined rice bran oil. Economical and healthy choice for daily cooking needs.',
                'price': 850.00,
                'mrp': 950.00,
                'discount_percentage': 11,
                'size': '5',
                'unit': 'Litre',
                'stock_quantity': 300,
                'low_stock_threshold': 30,
                'image_url': 'images/products/rbo-5l.jpg',
                'features': 'Value pack, High smoke point, Rich in Oryzanol, Heart healthy',
                'is_active': True,
                'is_featured': True,
                'category_id': 1
            },
            {
                'name': 'Refined Rice Bran Oil - 15L',
                'slug': 'rbo-15l',
                'sku': 'RBO-15L-001',
                'description': 'Commercial pack refined rice bran oil. Perfect for restaurants and bulk users.',
                'price': 2400.00,
                'mrp': 2700.00,
                'discount_percentage': 11,
                'size': '15',
                'unit': 'Litre',
                'stock_quantity': 200,
                'low_stock_threshold': 20,
                'image_url': 'images/products/rbo-15l.jpg',
                'features': 'Bulk pack, Cost effective, High smoke point, Commercial use',
                'is_active': True,
                'is_featured': False,
                'category_id': 1
            },
            {
                'name': 'Cold Pressed Rice Bran Oil - 1L',
                'slug': 'cold-pressed-rbo-1l',
                'sku': 'CP-RBO-1L-001',
                'description': 'Traditionally extracted cold pressed rice bran oil. Retains natural nutrients and flavor.',
                'price': 250.00,
                'mrp': 280.00,
                'discount_percentage': 11,
                'size': '1',
                'unit': 'Litre',
                'stock_quantity': 150,
                'low_stock_threshold': 20,
                'image_url': 'images/products/cold-pressed-rbo-1l.jpg',
                'features': 'Cold pressed, Natural extraction, Rich nutrients, Traditional method',
                'is_active': True,
                'is_featured': True,
                'category_id': 2
            },
            {
                'name': 'Premium Rice Bran Oil - 1L',
                'slug': 'premium-rbo-1l',
                'sku': 'PREM-RBO-1L-001',
                'description': 'Premium grade refined rice bran oil with extra filtration for superior quality.',
                'price': 220.00,
                'mrp': 250.00,
                'discount_percentage': 12,
                'size': '1',
                'unit': 'Litre',
                'stock_quantity': 250,
                'low_stock_threshold': 30,
                'image_url': 'images/products/premium-rbo-1l.jpg',
                'features': 'Extra refined, Premium quality, Clear oil, Superior taste',
                'is_active': True,
                'is_featured': True,
                'category_id': 3
            },
            {
                'name': 'Rice Bran Oil Gift Pack - 2x1L',
                'slug': 'rbo-gift-pack',
                'sku': 'RBO-GIFT-001',
                'description': 'Premium gift pack with 2 bottles of 1L refined rice bran oil. Perfect for gifting.',
                'price': 380.00,
                'mrp': 420.00,
                'discount_percentage': 10,
                'size': '2',
                'unit': 'Litre',
                'stock_quantity': 100,
                'low_stock_threshold': 10,
                'image_url': 'images/products/rbo-gift-pack.jpg',
                'features': 'Gift packaging, Premium quality, Festival special, Value for money',
                'is_active': True,
                'is_featured': True,
                'category_id': 3
            },
            {
                'name': 'Refined Rice Bran Oil - 500ml',
                'slug': 'rbo-500ml',
                'sku': 'RBO-500ML-001',
                'description': 'Compact 500ml pack of refined rice bran oil. Ideal for small families and trial.',
                'price': 95.00,
                'mrp': 110.00,
                'discount_percentage': 14,
                'size': '0.5',
                'unit': 'Litre',
                'stock_quantity': 400,
                'low_stock_threshold': 50,
                'image_url': 'images/products/rbo-500ml.jpg',
                'features': 'Compact size, Trial pack, Easy to handle, Perfect for small families',
                'is_active': True,
                'is_featured': False,
                'category_id': 1
            }
        ]
        
        for prod_data in products_data:
            product = Product(**prod_data)
            db.session.add(product)
        
        db.session.commit()
        print(f"✓ Created {len(products_data)} products")
        
        print("\n" + "="*50)
        print("Database initialization complete!")
        print("="*50)
        print("\nYou can now login with:")
        print("  Admin: username='admin', password='admin123'")
        print("  Customer: username='customer', password='customer123'")
        print("\nRun the application with: python app.py")


if __name__ == '__main__':
    init_database()
