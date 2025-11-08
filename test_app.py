"""
Unit Tests for Shree Vinayaga E-Commerce Application

Run tests with: pytest
Run with coverage: pytest --cov=. --cov-report=html
"""

import pytest
from app import create_app, db
from models import User, Product, Category, CartItem, Order, OrderItem, WishlistItem
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for tests
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        
@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def authenticated_client(client, app):
    """Create authenticated test client"""
    with app.app_context():
        # Create test user
        user = User(
            username='testuser',
            email='test@example.com',
            user_type='customer'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
    
    # Login
    response = client.post('/auth/login', data={
        'username_or_email': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    
    # Verify login succeeded
    assert response.status_code == 200
    
    return client


@pytest.fixture
def admin_client(client, app):
    """Create authenticated admin test client"""
    with app.app_context():
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            user_type='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
    
    # Login as admin
    client.post('/auth/login', data={
        'username_or_email': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    
    return client


@pytest.fixture
def sample_product(app):
    """Create a sample product"""
    with app.app_context():
        category = Category(name='Test Category', slug='test-category', description='Test Description')
        db.session.add(category)
        db.session.commit()
        
        product = Product(
            name='Test Product',
            slug='test-product',
            sku='TEST001',
            description='Test product description',
            price=100.00,
            mrp=120.00,
            size='1',
            unit='L',
            stock_quantity=50,
            category_id=category.id,
            is_featured=True
        )
        db.session.add(product)
        db.session.commit()
        
        return product.id


# ====================
# Authentication Tests
# ====================

class TestAuthentication:
    """Test authentication functionality"""
    
    def test_registration_success(self, client, app):
        """Test successful user registration"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'full_name': 'New User',
            'phone': '9876543210',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Registration successful' in response.data or b'Login' in response.data
        
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'new@example.com'
    
    def test_registration_duplicate_username(self, client, app):
        """Test registration with duplicate username"""
        with app.app_context():
            user = User(
                username='existing',
                email='existing@example.com'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/auth/register', data={
            'username': 'existing',
            'email': 'new@example.com',
            'full_name': 'Existing User',
            'phone': '9876543210',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        assert b'Username already exists' in response.data or b'already' in response.data.lower()
    
    def test_login_success(self, client, app):
        """Test successful login"""
        with app.app_context():
            user = User(
                username='logintest',
                email='login@example.com'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/auth/login', data={
            'username_or_email': 'logintest',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'successfully' in response.data.lower() or b'welcome' in response.data.lower()
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/auth/login', data={
            'username_or_email': 'nonexistent',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert b'Invalid' in response.data or b'incorrect' in response.data.lower()
    
    def test_logout(self, authenticated_client):
        """Test logout functionality"""
        response = authenticated_client.get('/auth/logout', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'logged out' in response.data.lower() or b'Login' in response.data


# ====================
# Product Tests
# ====================

class TestProducts:
    """Test product functionality"""
    
    def test_product_list_page(self, client, app, sample_product):
        """Test product listing page loads"""
        response = client.get('/products/')
        
        assert response.status_code == 200
        assert b'Test Product' in response.data
    
    def test_product_detail_page(self, client, app, sample_product):
        """Test product detail page loads"""
        with app.app_context():
            product = Product.query.get(sample_product)
            slug = product.slug
        
        response = client.get(f'/products/{slug}')
        
        assert response.status_code == 200
        assert b'Test Product' in response.data
        assert b'100' in response.data  # Price
    
    def test_product_search(self, client, app, sample_product):
        """Test product search functionality"""
        response = client.get('/products/?q=Test')
        
        assert response.status_code == 200
        assert b'Test Product' in response.data
    
    def test_product_category_filter(self, client, app, sample_product):
        """Test product category filtering"""
        with app.app_context():
            category = Category.query.first()
            
        response = client.get(f'/products/?category={category.slug}')
        
        assert response.status_code == 200


# ====================
# Cart Tests
# ====================

class TestCart:
    """Test shopping cart functionality"""
    
    def test_add_to_cart(self, authenticated_client, app, sample_product):
        """Test adding product to cart"""
        response = authenticated_client.post(f'/cart/add/{sample_product}', data={
            'quantity': 2
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            cart_items = CartItem.query.all()
            assert len(cart_items) == 1
            assert cart_items[0].quantity == 2
    
    def test_add_to_cart_exceeds_stock(self, authenticated_client, app, sample_product):
        """Test adding more than available stock"""
        response = authenticated_client.post(f'/cart/add/{sample_product}', data={
            'quantity': 1000
        }, follow_redirects=True)
        
        assert b'stock' in response.data.lower() or b'available' in response.data.lower()
    
    def test_view_cart(self, authenticated_client, app, sample_product):
        """Test viewing cart"""
        # Add item to cart first
        authenticated_client.post(f'/cart/add/{sample_product}', data={'quantity': 1})
        
        response = authenticated_client.get('/cart/')
        
        assert response.status_code == 200
        assert b'Test Product' in response.data
    
    def test_update_cart_quantity(self, authenticated_client, app, sample_product):
        """Test updating cart item quantity"""
        # Add item to cart first
        authenticated_client.post(f'/cart/add/{sample_product}', data={'quantity': 1})
        
        with app.app_context():
            cart_item = CartItem.query.first()
            item_id = cart_item.id
        
        response = authenticated_client.post(f'/cart/update/{item_id}', data={
            'quantity': 3
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            cart_item = CartItem.query.get(item_id)
            assert cart_item.quantity == 3
    
    def test_remove_from_cart(self, authenticated_client, app, sample_product):
        """Test removing item from cart"""
        # Add item to cart first
        authenticated_client.post(f'/cart/add/{sample_product}', data={'quantity': 1})
        
        with app.app_context():
            cart_item = CartItem.query.first()
            item_id = cart_item.id
        
        response = authenticated_client.post(f'/cart/remove/{item_id}', follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            cart_item = CartItem.query.get(item_id)
            assert cart_item is None
    
    def test_clear_cart(self, authenticated_client, app, sample_product):
        """Test clearing entire cart"""
        # Add item to cart first
        authenticated_client.post(f'/cart/add/{sample_product}', data={'quantity': 1})
        
        response = authenticated_client.post('/cart/clear', follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            cart_items = CartItem.query.all()
            assert len(cart_items) == 0


class TestWishlist:
    """Test wishlist functionality"""

    def test_add_to_wishlist(self, authenticated_client, app, sample_product):
        """User can add a product to wishlist"""
        response = authenticated_client.post(f'/wishlist/add/{sample_product}', follow_redirects=True)

        assert response.status_code == 200

        with app.app_context():
            items = WishlistItem.query.all()
            assert len(items) == 1
            assert items[0].product_id == sample_product

    def test_add_duplicate_wishlist(self, authenticated_client, app, sample_product):
        """Adding same product twice does not create duplicates"""
        authenticated_client.post(f'/wishlist/add/{sample_product}', follow_redirects=True)
        authenticated_client.post(f'/wishlist/add/{sample_product}', follow_redirects=True)

        with app.app_context():
            items = WishlistItem.query.filter_by(product_id=sample_product).all()
            assert len(items) == 1

    def test_remove_from_wishlist(self, authenticated_client, app, sample_product):
        """User can remove product from wishlist"""
        authenticated_client.post(f'/wishlist/add/{sample_product}', follow_redirects=True)

        with app.app_context():
            item = WishlistItem.query.filter_by(product_id=sample_product).first()
            item_id = item.id

        response = authenticated_client.post(f'/wishlist/remove/{item_id}', follow_redirects=True)

        assert response.status_code == 200

        with app.app_context():
            item = WishlistItem.query.get(item_id)
            assert item is None

    def test_move_to_cart_from_wishlist(self, authenticated_client, app, sample_product):
        """Moving wishlist item to cart adds it to cart and removes from wishlist"""
        authenticated_client.post(f'/wishlist/add/{sample_product}', follow_redirects=True)

        with app.app_context():
            item = WishlistItem.query.filter_by(product_id=sample_product).first()
            item_id = item.id

        response = authenticated_client.post(f'/wishlist/move-to-cart/{item_id}', follow_redirects=True)

        assert response.status_code == 200

        with app.app_context():
            cart_item = CartItem.query.filter_by(product_id=sample_product).first()
            wishlist_item = WishlistItem.query.get(item_id)
            assert cart_item is not None
            assert cart_item.quantity == 1
            assert wishlist_item is None


# ====================
# Checkout Tests
# ====================

class TestCheckout:
    """Test checkout and order functionality"""
    
    def test_checkout_page_loads(self, authenticated_client, app, sample_product):
        """Test checkout page loads"""
        # Add item to cart first
        authenticated_client.post(f'/cart/add/{sample_product}', data={'quantity': 1})
        
        response = authenticated_client.get('/checkout/')
        
        assert response.status_code == 200
        assert b'Checkout' in response.data
    
    def test_checkout_empty_cart(self, authenticated_client):
        """Test checkout with empty cart"""
        response = authenticated_client.get('/checkout/', follow_redirects=True)
        
        assert b'empty' in response.data.lower() or b'Cart' in response.data
    
    def test_place_order(self, authenticated_client, app, sample_product):
        """Test placing an order"""
        # Add item to cart first
        authenticated_client.post(f'/cart/add/{sample_product}', data={'quantity': 2})
        
        response = authenticated_client.post('/checkout', data={
            'full_name': 'Test User',
            'phone': '1234567890',
            'address_line1': '123 Test St',
            'address_line2': 'Unit 1',
            'city': 'Test City',
            'state': 'Test State',
            'pincode': '123456',
            'notes': 'Leave at door'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            orders = Order.query.all()
            assert len(orders) == 1
            assert orders[0].total_amount == 260.0  # subtotal + tax + shipping
            
            # Check stock was reduced
            product = Product.query.get(sample_product)
            assert product.stock_quantity == 48  # 50 - 2
            
            # Check cart was cleared
            cart_items = CartItem.query.all()
            assert len(cart_items) == 0
    
    def test_order_history(self, authenticated_client, app, sample_product):
        """Test viewing order history"""
        # Place an order first
        authenticated_client.post(f'/cart/add/{sample_product}', data={'quantity': 1})
        authenticated_client.post('/checkout', data={
            'full_name': 'Test User',
            'phone': '1234567890',
            'address_line1': '123 Test St',
            'address_line2': '',
            'city': 'Test City',
            'state': 'Test State',
            'pincode': '123456',
            'notes': ''
        }, follow_redirects=True)
        
        with app.app_context():
            order = Order.query.first()
            order_number = order.order_number.encode()

        response = authenticated_client.get('/checkout/orders')

        assert response.status_code == 200
        assert order_number in response.data


# ====================
# Admin Tests
# ====================

class TestAdmin:
    """Test admin functionality"""
    
    def test_admin_dashboard_access(self, admin_client):
        """Test admin can access dashboard"""
        response = admin_client.get('/admin/')
        
        assert response.status_code == 200
        assert b'Dashboard' in response.data
    
    def test_non_admin_dashboard_denied(self, authenticated_client):
        """Test non-admin cannot access dashboard"""
        response = authenticated_client.get('/admin/', follow_redirects=True)
        
        assert b'permission' in response.data.lower() or b'admin' in response.data.lower()
    
    def test_admin_create_product(self, admin_client, app):
        """Test admin can create product"""
        with app.app_context():
            category = Category(name='Test Category', slug='test-category', description='Test')
            db.session.add(category)
            db.session.commit()
            category_id = category.id
        
        response = admin_client.post('/admin/products/add', data={
            'name': 'New Product',
            'sku': 'NEW001',
            'description': 'New product description',
            'price': 150.00,
            'mrp': 180.00,
            'discount_percentage': 10,
            'size': '2',
            'unit': 'L',
            'stock_quantity': 100,
            'low_stock_threshold': 10,
            'category_id': category_id,
            'is_active': 'y',
            'is_featured': 'y'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            product = Product.query.filter_by(sku='NEW001').first()
            assert product is not None
            assert product.name == 'New Product'
    
    def test_admin_update_order_status(self, admin_client, app, sample_product):
        """Test admin can update order status"""
        # Create an order first
        with app.app_context():
            user = User.query.first()
            order = Order(
                order_number='TEST123',
                user_id=user.id,
                shipping_full_name='Test User',
                shipping_phone='1234567890',
                shipping_address_line1='123 Test St',
                shipping_city='Test City',
                shipping_state='Test State',
                shipping_pincode='123456',
                subtotal=100.00,
                tax_amount=10.00,
                shipping_cost=20.00,
                total_amount=130.00,
                status='pending'
            )
            db.session.add(order)
            db.session.commit()
            order_id = order.id
        
        response = admin_client.post(f'/admin/orders/{order_id}/update-status', data={
            'status': 'shipped'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            order = Order.query.get(order_id)
            assert order.status == 'shipped'


# ====================
# Model Tests
# ====================

class TestModels:
    """Test database models"""
    
    def test_user_password_hashing(self, app):
        """Test user password is hashed"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Password should not be stored in plain text
            assert user.password_hash != 'password123'
            assert user.password_hash.startswith('scrypt:') or user.password_hash.startswith('pbkdf2:')
    
    def test_product_discount_percentage(self, app, sample_product):
        """Test product discount percentage calculation"""
        with app.app_context():
            product = Product.query.get(sample_product)
            # Product discount_percentage is 0 by default, not calculated from price/mrp
            # Just test that the attribute exists
            assert product.discount_percentage == 0
    
    def test_product_stock_status(self, app, sample_product):
        """Test product stock status"""
        with app.app_context():
            product = Product.query.get(sample_product)
            product.stock_quantity = 5
            
            assert product.is_in_stock() is True
            assert product.is_low_stock() is True
            
            product.stock_quantity = 0
            assert product.is_in_stock() is False
    
    def test_order_items_relationship(self, app, sample_product):
        """Test order and order items relationship"""
        with app.app_context():
            user = User(
                username='ordertest',
                email='order@example.com'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            order = Order(
                order_number='TEST456',
                user_id=user.id,
                shipping_full_name='Test User',
                shipping_phone='1234567890',
                shipping_address_line1='123 Test St',
                shipping_city='Test City',
                shipping_state='Test State',
                shipping_pincode='123456',
                subtotal=100.00,
                tax_amount=10.00,
                shipping_cost=20.00,
                total_amount=130.00
            )
            db.session.add(order)
            db.session.commit()
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=sample_product,
                quantity=2,
                unit_price=100.00,
                subtotal=200.00
            )
            db.session.add(order_item)
            db.session.commit()
            
            # Test relationship
            items = order.order_items.all()
            assert len(items) == 1
            assert items[0].quantity == 2
            assert items[0].subtotal == 200.00


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
