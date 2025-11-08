"""
Seed Database Script
Populates the database with sample data for Shree Vinayaga Rice Bran Oil products
Run this script after creating the database: python seed_data.py
"""
import sys
from app import create_app
from models import db, User, Category, Product

def seed_database():
    """Seed the database with initial data"""
    
    app = create_app()
    
    with app.app_context():
        print("🌱 Starting database seeding...")
        
        # Clear existing data (optional - comment out if you want to preserve existing data)
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create Admin User
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@shreevinayaga.com',
            full_name='Administrator',
            phone='+91 9876543210',
            user_type='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create Test Customer
        print("Creating test customer...")
        customer = User(
            username='customer',
            email='customer@example.com',
            full_name='Test Customer',
            phone='+91 9876543211',
            user_type='customer',
            address_line1='123 Test Street',
            city='Chennai',
            state='Tamil Nadu',
            pincode='600001',
            is_active=True
        )
        customer.set_password('customer123')
        db.session.add(customer)
        
        db.session.commit()
        print("✅ Users created")
        
        # Create Categories
        print("Creating categories...")
        categories_data = [
            {
                'name': 'Retail Pack',
                'slug': 'retail-pack',
                'description': 'Perfect for home use - small convenient packs',
                'is_active': True,
                'display_order': 1
            },
            {
                'name': 'Family Pack',
                'slug': 'family-pack',
                'description': 'Value packs for regular family cooking',
                'is_active': True,
                'display_order': 2
            },
            {
                'name': 'Bulk Pack',
                'slug': 'bulk-pack',
                'description': 'Large packs for restaurants and institutions',
                'is_active': True,
                'display_order': 3
            }
        ]
        
        categories = {}
        for cat_data in categories_data:
            category = Category(**cat_data)
            db.session.add(category)
            categories[cat_data['slug']] = category
        
        db.session.commit()
        print("✅ Categories created")
        
        # Create Products - Rice Bran Oil variants
        print("Creating products...")
        products_data = [
            {
                'name': 'Shree Vinayaga Rice Bran Oil 1L',
                'slug': 'rice-bran-oil-1l',
                'description': 'Premium quality refined rice bran oil perfect for everyday cooking. Rich in Oryzanol, promotes heart health and has a high smoke point ideal for all types of cooking including deep frying.',
                'price': 180.00,
                'mrp': 200.00,
                'discount_percentage': 10,
                'size': '1',
                'unit': 'Litre',
                'sku': 'RBO-1L-001',
                'stock_quantity': 500,
                'low_stock_threshold': 50,
                'image_url': '/static/images/rbo-1l.jpg',
                'features': 'Heart Healthy, High Smoke Point, Rich in Oryzanol, Low Cholesterol, Ideal for Frying',
                'category_id': categories['retail-pack'].id,
                'is_active': True,
                'is_featured': True,
                'meta_title': 'Buy Rice Bran Oil 1L - Shree Vinayaga Pure RBO',
                'meta_description': 'Buy premium quality rice bran oil 1L pack. FSSAI certified, heart healthy cooking oil.'
            },
            {
                'name': 'Shree Vinayaga Rice Bran Oil 5L',
                'slug': 'rice-bran-oil-5l',
                'description': 'Family pack rice bran oil for regular home cooking. FSSAI certified, physically refined using steam-based deacidification process ensuring maximum purity and nutritional value.',
                'price': 850.00,
                'mrp': 950.00,
                'discount_percentage': 10.5,
                'size': '5',
                'unit': 'Litre',
                'sku': 'RBO-5L-001',
                'stock_quantity': 300,
                'low_stock_threshold': 30,
                'image_url': '/static/images/rbo-5l.jpg',
                'features': 'Value Pack, FSSAI Certified, Physically Refined, High Nutritional Value, Best for Family Use',
                'category_id': categories['family-pack'].id,
                'is_active': True,
                'is_featured': True,
                'meta_title': 'Rice Bran Oil 5L Family Pack - Shree Vinayaga',
                'meta_description': 'Buy 5 litre rice bran oil family pack. Premium quality, FSSAI certified cooking oil.'
            },
            {
                'name': 'Shree Vinayaga Rice Bran Oil 15L',
                'slug': 'rice-bran-oil-15l',
                'description': 'Bulk pack rice bran oil ideal for restaurants, hotels, and institutional buyers. Sourced from fresh rice bran from local mills within 100-150 km radius, ensuring freshness and quality.',
                'price': 2400.00,
                'mrp': 2700.00,
                'discount_percentage': 11.1,
                'size': '15',
                'unit': 'Litre',
                'sku': 'RBO-15L-001',
                'stock_quantity': 200,
                'low_stock_threshold': 20,
                'image_url': '/static/images/rbo-15l.jpg',
                'features': 'Bulk Pack, Restaurant Grade, Fresh from Local Mills, Low FFA, High Oil Content',
                'category_id': categories['bulk-pack'].id,
                'is_active': True,
                'is_featured': True,
                'meta_title': 'Buy Rice Bran Oil 15L Bulk Pack - Wholesale RBO',
                'meta_description': '15 litre rice bran oil bulk pack for restaurants and institutions. Best wholesale prices.'
            },
            {
                'name': 'Shree Vinayaga Premium RBO 1L (Oryzanol Rich)',
                'slug': 'premium-rbo-1l-oryzanol',
                'description': 'Premium segment rice bran oil with enhanced Oryzanol content. Specifically processed to retain maximum Oryzanol (up to 28% more) for superior heart health benefits. Perfect for health-conscious consumers.',
                'price': 220.00,
                'mrp': 250.00,
                'discount_percentage': 12,
                'size': '1',
                'unit': 'Litre',
                'sku': 'PRBO-1L-001',
                'stock_quantity': 250,
                'low_stock_threshold': 30,
                'image_url': '/static/images/premium-rbo-1l.jpg',
                'features': 'Enhanced Oryzanol, Premium Quality, Heart Health, Cholesterol Management, Antioxidant Rich',
                'category_id': categories['retail-pack'].id,
                'is_active': True,
                'is_featured': True,
                'meta_title': 'Premium Oryzanol Rich Rice Bran Oil 1L - Shree Vinayaga',
                'meta_description': 'Premium quality rice bran oil with enhanced Oryzanol for heart health. Buy now!'
            },
            {
                'name': 'Shree Vinayaga Rice Bran Oil 2L',
                'slug': 'rice-bran-oil-2l',
                'description': 'Convenient 2 litre pack of pure rice bran oil. Healthy n Enhancing Taste - our tagline reflects our commitment to both health and flavor. Perfect size for small families.',
                'price': 350.00,
                'mrp': 390.00,
                'discount_percentage': 10.3,
                'size': '2',
                'unit': 'Litre',
                'sku': 'RBO-2L-001',
                'stock_quantity': 400,
                'low_stock_threshold': 40,
                'image_url': '/static/images/rbo-2l.jpg',
                'features': 'Convenient Size, Pure Quality, Taste Enhancer, Healthy Cooking, Value for Money',
                'category_id': categories['retail-pack'].id,
                'is_active': True,
                'is_featured': False,
                'meta_title': 'Rice Bran Oil 2L Pack - Shree Vinayaga Pure RBO',
                'meta_description': '2 litre rice bran oil pack. Perfect size for small families. Buy online now!'
            },
            {
                'name': 'Shree Vinayaga Rice Bran Oil 10L',
                'slug': 'rice-bran-oil-10l',
                'description': 'Economic 10 litre pack suitable for small restaurants, cafeterias, and food processing units. Dindigul, Tamil Nadu made with 100 TPD capacity ensuring consistent quality and supply.',
                'price': 1650.00,
                'mrp': 1850.00,
                'discount_percentage': 10.8,
                'size': '10',
                'unit': 'Litre',
                'sku': 'RBO-10L-001',
                'stock_quantity': 150,
                'low_stock_threshold': 15,
                'image_url': '/static/images/rbo-10l.jpg',
                'features': 'Economic Pack, Food Service Grade, Consistent Quality, B2B Friendly, Dindigul Made',
                'category_id': categories['bulk-pack'].id,
                'is_active': True,
                'is_featured': False,
                'meta_title': 'Rice Bran Oil 10L Economic Pack - B2B Wholesale',
                'meta_description': '10 litre rice bran oil for restaurants and food service. Wholesale rates available.'
            }
        ]
        
        for product_data in products_data:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()
        print("✅ Products created")
        
        print("\n🎉 Database seeding completed successfully!")
        print("\n📊 Summary:")
        print(f"   - Users: {User.query.count()}")
        print(f"   - Categories: {Category.query.count()}")
        print(f"   - Products: {Product.query.count()}")
        print("\n🔐 Login Credentials:")
        print("   Admin - Username: admin | Password: admin123")
        print("   Customer - Username: customer | Password: customer123")
        print("\n✨ You can now run the application: python app.py")


if __name__ == '__main__':
    seed_database()
