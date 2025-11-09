"""
Database Models
Defines all database tables and relationships for the e-commerce platform
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication and customer information"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    
    # User type: 'customer', 'admin', 'distributor'
    user_type = db.Column(db.String(20), default='customer', nullable=False)
    
    # Address Information
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    
    # Account Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy='dynamic', cascade='all, delete-orphan')
    cart_items = db.relationship('CartItem', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    wishlist_items = db.relationship('WishlistItem', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user has admin privileges"""
        return self.user_type == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    """Product category model"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    """Product model for rice bran oil variants"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Pricing
    price = db.Column(db.Float, nullable=False)
    mrp = db.Column(db.Float)  # Maximum Retail Price
    discount_percentage = db.Column(db.Float, default=0)
    
    # Product Details
    size = db.Column(db.String(50))  # e.g., "1L", "5L", "15L"
    unit = db.Column(db.String(20), default='Litre')
    sku = db.Column(db.String(50), unique=True, index=True)
    
    # Inventory
    stock_quantity = db.Column(db.Integer, default=0)
    low_stock_threshold = db.Column(db.Integer, default=10)
    
    # Images
    image_url = db.Column(db.String(255))
    image_url_2 = db.Column(db.String(255))
    image_url_3 = db.Column(db.String(255))
    # Optional 3D model file (relative path under static/, e.g. 'models/product123.glb')
    model_url = db.Column(db.String(255))
    
    # SEO & Marketing
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.Text)
    features = db.Column(db.Text)  # JSON or comma-separated features
    
    # Product Status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cart_items = db.relationship('CartItem', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    images = db.relationship('ProductImage', backref='product', lazy='dynamic', cascade='all, delete-orphan', order_by='ProductImage.display_order')
    reviews = db.relationship('ProductReview', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    wishlist_items = db.relationship('WishlistItem', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock_quantity > 0
    
    def is_low_stock(self):
        """Check if product stock is low"""
        return 0 < self.stock_quantity <= self.low_stock_threshold
    
    def get_discounted_price(self):
        """Calculate and return discounted price"""
        if self.discount_percentage > 0:
            return round(self.price * (1 - self.discount_percentage / 100), 2)
        return self.price
    
    def get_average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)
    
    def get_rating_distribution(self):
        """Get rating distribution (5 star, 4 star, etc.)"""
        distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        for review in self.reviews.all():
            distribution[review.rating] += 1
        return distribution
    
    def __repr__(self):
        return f'<Product {self.name}>'


class ProductImage(db.Model):
    """Product image model for multiple product images"""
    __tablename__ = 'product_images'
    
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    is_main = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    alt_text = db.Column(db.String(200))
    
    # Foreign Keys
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProductImage {self.image_url}>'


class ProductReview(db.Model):
    """Product review and rating model"""
    __tablename__ = 'product_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(200))
    comment = db.Column(db.Text)
    is_verified_purchase = db.Column(db.Boolean, default=False)
    
    # Foreign Keys
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    likes = db.relationship('ReviewLike', backref='review', lazy='dynamic', cascade='all, delete-orphan')
    user = db.relationship('User', backref='reviews')
    
    def get_likes_count(self):
        """Get number of likes"""
        return self.likes.count()
    
    def is_liked_by_user(self, user_id):
        """Check if user liked this review"""
        return self.likes.filter_by(user_id=user_id).first() is not None
    
    def __repr__(self):
        return f'<ProductReview {self.id}>'


class ReviewLike(db.Model):
    """Review like model"""
    __tablename__ = 'review_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    review_id = db.Column(db.Integer, db.ForeignKey('product_reviews.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('review_id', 'user_id', name='unique_review_user_like'),
    )
    
    def __repr__(self):
        return f'<ReviewLike {self.id}>'


class WishlistItem(db.Model):
    """Wishlist item model for users"""
    __tablename__ = 'wishlist_items'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

    # Constraints
    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='unique_wishlist_user_product'),
    )

    def __repr__(self):
        return f'<WishlistItem user={self.user_id} product={self.product_id}>'


class CartItem(db.Model):
    """Shopping cart item model"""
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='unique_user_product'),
    )
    
    def get_subtotal(self):
        """Calculate subtotal for this cart item"""
        return round(self.product.get_discounted_price() * self.quantity, 2)
    
    def __repr__(self):
        return f'<CartItem user={self.user_id} product={self.product_id}>'


class Order(db.Model):
    """Order model for tracking purchases"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Order Status: 'pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled'
    status = db.Column(db.String(20), default='pending', nullable=False)
    
    # Payment Information
    payment_method = db.Column(db.String(50))  # 'razorpay', 'cod', etc.
    payment_status = db.Column(db.String(20), default='pending')  # 'pending', 'paid', 'failed'
    payment_id = db.Column(db.String(100))  # External payment gateway ID
    
    # Pricing
    subtotal = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0)
    shipping_cost = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False)
    
    # Shipping Address
    shipping_full_name = db.Column(db.String(120))
    shipping_phone = db.Column(db.String(20))
    shipping_address_line1 = db.Column(db.String(200))
    shipping_address_line2 = db.Column(db.String(200))
    shipping_city = db.Column(db.String(100))
    shipping_state = db.Column(db.String(100))
    shipping_pincode = db.Column(db.String(10))
    
    # Additional Information
    notes = db.Column(db.Text)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'


class OrderItem(db.Model):
    """Order item model for individual products in an order"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    
    # Product snapshot (in case product changes later)
    product_name = db.Column(db.String(200))
    product_size = db.Column(db.String(50))
    product_sku = db.Column(db.String(50))
    
    # Foreign Keys
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    
    def __repr__(self):
        return f'<OrderItem order={self.order_id} product={self.product_name}>'
