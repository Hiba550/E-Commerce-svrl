"""
Restore minimal sample categories and products directly into the SQLite `app.db` without importing the Flask app.
This is safe to run locally and will only insert sample rows if the tables are empty.
"""
import sqlite3
from datetime import datetime

DB = 'app.db'

CATEGORIES = [
    ('Refined Rice Bran Oil', 'refined-rbo', 'Premium quality refined rice bran oil for everyday cooking', 1),
    ('Cold Pressed Oil', 'cold-pressed', 'Traditionally extracted cold pressed oils', 2),
    ('Premium Oil', 'premium', 'Premium range of cooking oils', 3),
]

PRODUCTS = [
    {
        'name': 'Refined Rice Bran Oil - 1L',
        'slug': 'rbo-1l',
        'sku': 'RBO-1L-001',
        'description': 'Premium quality refined rice bran oil. Rich in Oryzanol and Vitamin E.',
        'price': 180.00,
        'mrp': 200.00,
        'discount_percentage': 10,
        'size': '1',
        'unit': 'Litre',
        'stock_quantity': 500,
        'low_stock_threshold': 50,
        'image_url': 'images/products/rbo-1l.jpg',
        'features': 'High smoke point, Rich in Oryzanol, Heart healthy, No cholesterol',
        'is_active': 1,
        'is_featured': 1,
        'category_slug': 'refined-rbo'
    },
    {
        'name': 'Refined Rice Bran Oil - 5L',
        'slug': 'rbo-5l',
        'sku': 'RBO-5L-001',
        'description': 'Family pack refined rice bran oil. Economical and healthy choice.',
        'price': 850.00,
        'mrp': 950.00,
        'discount_percentage': 11,
        'size': '5',
        'unit': 'Litre',
        'stock_quantity': 300,
        'low_stock_threshold': 30,
        'image_url': 'images/products/rbo-5l.jpg',
        'features': 'Value pack, High smoke point, Rich in Oryzanol, Heart healthy',
        'is_active': 1,
        'is_featured': 1,
        'category_slug': 'refined-rbo'
    },
    {
        'name': 'Cold Pressed Rice Bran Oil - 1L',
        'slug': 'cold-pressed-rbo-1l',
        'sku': 'CP-RBO-1L-001',
        'description': 'Traditionally extracted cold pressed rice bran oil.',
        'price': 250.00,
        'mrp': 280.00,
        'discount_percentage': 11,
        'size': '1',
        'unit': 'Litre',
        'stock_quantity': 150,
        'low_stock_threshold': 20,
        'image_url': 'images/products/cold-pressed-rbo-1l.jpg',
        'features': 'Cold pressed, Natural extraction, Rich nutrients, Traditional method',
        'is_active': 1,
        'is_featured': 1,
        'category_slug': 'cold-pressed'
    }
]


def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Ensure foreign keys on/off as needed
    try:
        cur.execute('PRAGMA foreign_keys = OFF')
    except Exception:
        pass

    # Categories
    cur.execute("SELECT COUNT(1) FROM categories")
    cats_count = cur.fetchone()[0]
    print('Existing categories:', cats_count)
    if cats_count == 0:
        print('Inserting sample categories...')
        for name, slug, desc, order in CATEGORIES:
            cur.execute(
                'INSERT INTO categories (name, slug, description, is_active, display_order, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                (name, slug, desc, 1, order, datetime.utcnow().isoformat())
            )
        conn.commit()
    else:
        print('Categories exist, skipping insert')

    # Build mapping slug -> id
    cur.execute('SELECT id, slug FROM categories')
    mapping = {slug: cid for cid, slug in cur.fetchall()}

    # Products
    cur.execute('SELECT COUNT(1) FROM products')
    prod_count = cur.fetchone()[0]
    print('Existing products:', prod_count)
    if prod_count == 0:
        print('Inserting sample products...')
        for p in PRODUCTS:
            cat_id = mapping.get(p['category_slug'])
            cur.execute(
                '''INSERT INTO products (name, slug, description, price, mrp, discount_percentage, size, unit, sku, stock_quantity, low_stock_threshold, image_url, features, is_active, is_featured, category_id, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    p['name'], p['slug'], p['description'], p['price'], p.get('mrp'), p.get('discount_percentage'), p.get('size'), p.get('unit'), p.get('sku'),
                    p.get('stock_quantity', 0), p.get('low_stock_threshold', 0), p.get('image_url'), p.get('features'), p.get('is_active', 1), p.get('is_featured', 0),
                    cat_id, datetime.utcnow().isoformat(), datetime.utcnow().isoformat()
                )
            )
        conn.commit()
        print('Inserted', len(PRODUCTS), 'sample products')
    else:
        print('Products exist, skipping insert')

    conn.close()

if __name__ == '__main__':
    main()
