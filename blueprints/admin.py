"""
Admin Blueprint
Handles admin dashboard and management operations
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func, or_

from models import db, User, Product, Category, Order, OrderItem, ProductImage
from blueprints.forms import ProductForm, CategoryForm
from werkzeug.utils import secure_filename
import os
import time

admin_bp = Blueprint('admin', __name__)

# File upload configuration
UPLOAD_FOLDER = 'static/images/products'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def _shift_month(reference: datetime, offset: int) -> datetime:
    """Return a new datetime representing the first day of the month offset from reference."""
    year = reference.year + ((reference.month - 1 + offset) // 12)
    month = (reference.month - 1 + offset) % 12 + 1
    return reference.replace(year=year, month=month, day=1)


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    # Core stats
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter(Order.status == 'pending').count()

    total_revenue = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).scalar() or 0
    avg_order_value = round(total_revenue / total_orders, 2) if total_orders else 0

    inventory_value = db.session.query(func.coalesce(func.sum(Product.price * Product.stock_quantity), 0)).scalar() or 0
    featured_products = Product.query.filter(Product.is_featured == True).count()

    customer_order_counts = dict(db.session.query(Order.user_id, func.count(Order.id)).group_by(Order.user_id).all())
    repeat_customers = sum(1 for count in customer_order_counts.values() if count > 1)
    total_customers = len(customer_order_counts)
    repeat_customer_rate = round((repeat_customers / total_customers) * 100, 1) if total_customers else 0

    # Monthly trend (last 6 months including current)
    reference_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_markers = [_shift_month(reference_month, offset) for offset in range(-5, 1)]
    monthly_summary = {marker.strftime('%b %Y'): {'revenue': 0.0, 'orders': 0} for marker in month_markers}

    orders_since = month_markers[0]
    recent_period_orders = Order.query.filter(Order.created_at >= orders_since).all()
    for order in recent_period_orders:
        if order.created_at:
            key = order.created_at.strftime('%b %Y')
            if key in monthly_summary:
                monthly_summary[key]['revenue'] += float(order.total_amount or 0)
                monthly_summary[key]['orders'] += 1

    monthly_labels = list(monthly_summary.keys())
    monthly_revenue = [round(monthly_summary[label]['revenue'], 2) for label in monthly_labels]
    monthly_orders = [monthly_summary[label]['orders'] for label in monthly_labels]

    # Order status distribution
    status_summary_query = db.session.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    status_summary = {status: count for status, count in status_summary_query}

    # Top performers
    top_products_query = db.session.query(
        Product.name.label('name'),
        func.coalesce(func.sum(OrderItem.quantity), 0).label('units'),
        func.coalesce(func.sum(OrderItem.subtotal), 0).label('revenue')
    ).join(OrderItem, OrderItem.product_id == Product.id)
    top_products_query = top_products_query.join(Order, OrderItem.order_id == Order.id)
    top_products_query = top_products_query.group_by(Product.id)
    top_products_query = top_products_query.order_by(func.sum(OrderItem.quantity).desc())
    top_products = [
        {
            'name': row.name,
            'units': int(row.units or 0),
            'revenue': round(float(row.revenue or 0), 2)
        }
        for row in top_products_query.limit(5).all()
    ]

    top_customers_query = db.session.query(
        User.id.label('user_id'),
        func.coalesce(User.full_name, User.username).label('name'),
        User.email.label('email'),
        func.coalesce(func.sum(Order.total_amount), 0).label('revenue'),
        func.count(Order.id).label('orders')
    ).join(Order, Order.user_id == User.id)
    top_customers_query = top_customers_query.group_by(User.id)
    top_customers_query = top_customers_query.order_by(func.sum(Order.total_amount).desc())
    top_customers = [
        {
            'name': row.name,
            'email': row.email,
            'orders': int(row.orders or 0),
            'revenue': round(float(row.revenue or 0), 2)
        }
        for row in top_customers_query.limit(5).all()
    ]

    # Recent activity
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    low_stock_products = Product.query.filter(
        Product.is_active == True,
        Product.stock_quantity <= Product.low_stock_threshold
    ).order_by(Product.stock_quantity.asc()).limit(6).all()

    dashboard_meta = {
        'inventory_value': round(float(inventory_value), 2),
        'featured_products': featured_products,
        'repeat_customer_rate': repeat_customer_rate,
        'avg_order_value': avg_order_value
    }

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_products=total_products,
        total_orders=total_orders,
        pending_orders=pending_orders,
        total_revenue=round(float(total_revenue), 2),
        monthly_labels=monthly_labels,
        monthly_revenue=monthly_revenue,
        monthly_orders=monthly_orders,
        status_summary=status_summary,
        top_products=top_products,
        top_customers=top_customers,
        recent_orders=recent_orders,
        low_stock_products=low_stock_products,
        dashboard_meta=dashboard_meta
    )


# Product Management
@admin_bp.route('/products')
@login_required
@admin_required
def products():
    """List all products"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    search_query = request.args.get('q', '').strip()
    status_filter = request.args.get('status', 'all')
    stock_filter = request.args.get('stock', 'all')
    category_filter = request.args.get('category', type=int)
    sort_by = request.args.get('sort', 'newest')

    query = Product.query

    if search_query:
        like_term = f"%{search_query}%"
        query = query.filter(or_(
            Product.name.ilike(like_term),
            Product.sku.ilike(like_term)
        ))

    if status_filter == 'active':
        query = query.filter(Product.is_active == True)
    elif status_filter == 'inactive':
        query = query.filter(Product.is_active == False)
    elif status_filter == 'featured':
        query = query.filter(Product.is_featured == True)

    if stock_filter == 'low':
        query = query.filter(Product.stock_quantity <= Product.low_stock_threshold, Product.stock_quantity > 0)
    elif stock_filter == 'out':
        query = query.filter(Product.stock_quantity == 0)
    elif stock_filter == 'in':
        query = query.filter(Product.stock_quantity > 0)

    if category_filter:
        query = query.filter(Product.category_id == category_filter)

    if sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'stock':
        query = query.order_by(Product.stock_quantity.asc())
    elif sort_by == 'name':
        query = query.order_by(Product.name.asc())
    else:
        query = query.order_by(Product.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    inventory_stats = {
        'active': Product.query.filter(Product.is_active == True).count(),
        'inactive': Product.query.filter(Product.is_active == False).count(),
        'featured': Product.query.filter(Product.is_featured == True).count(),
        'low_stock': Product.query.filter(Product.stock_quantity <= Product.low_stock_threshold, Product.is_active == True).count(),
        'total_value': round(float(db.session.query(func.coalesce(func.sum(Product.price * Product.stock_quantity), 0)).scalar() or 0), 2)
    }

    categories = Category.query.order_by(Category.name).all()

    return render_template(
        'admin/products.html',
        products=products,
        pagination=pagination,
        search_query=search_query,
        status_filter=status_filter,
        stock_filter=stock_filter,
        category_filter=category_filter,
        sort_by=sort_by,
        per_page=per_page,
        categories=categories,
        inventory_stats=inventory_stats
    )


@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    """Add new product"""
    form = ProductForm()
    
    # Populate category choices
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Generate slug from name
            slug = form.name.data.lower().replace(' ', '-')
            
            # Check if slug exists
            existing = Product.query.filter_by(slug=slug).first()
            if existing:
                slug = f"{slug}-{Product.query.count() + 1}"
            
            # Create product first (without images)
            product = Product(
                name=form.name.data,
                slug=slug,
                description=form.description.data,
                price=form.price.data,
                mrp=form.mrp.data,
                discount_percentage=form.discount_percentage.data,
                size=form.size.data,
                unit=form.unit.data,
                sku=form.sku.data,
                stock_quantity=form.stock_quantity.data,
                low_stock_threshold=form.low_stock_threshold.data,
                image_url=form.image_url.data if form.image_url.data else None,
                features=form.features.data,
                category_id=form.category_id.data,
                is_active=form.is_active.data,
                is_featured=form.is_featured.data
            )
            
            db.session.add(product)
            db.session.flush()  # Get product ID
            
            # Handle multiple file uploads
            uploaded_files = request.files.getlist('product_images')
            main_image_index = request.form.get('main_image', '0')
            
            if uploaded_files and uploaded_files[0].filename != '':
                # Create upload directory if it doesn't exist
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                for idx, file in enumerate(uploaded_files):
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        # Add timestamp to avoid conflicts
                        timestamp = str(int(time.time() * 1000))
                        filename = f"{product.id}_{timestamp}_{filename}"
                        filepath = os.path.join(UPLOAD_FOLDER, filename)
                        file.save(filepath)
                        
                        # Create ProductImage record
                        is_main = (str(idx) == main_image_index)
                        product_image = ProductImage(
                            product_id=product.id,
                            image_url=f'images/products/{filename}',
                            is_main=is_main,
                            display_order=idx,
                            alt_text=product.name
                        )
                        db.session.add(product_image)
                        
                        # Set first image as product's main image_url
                        if idx == 0 and not product.image_url:
                            product.image_url = f'images/products/{filename}'
            
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('admin.products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding product: {str(e)}', 'danger')
    
    return render_template('admin/product_form.html', form=form, action='Add')


@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    """Edit existing product"""
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    
    # Populate category choices
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            product.name = form.name.data
            product.description = form.description.data
            product.price = form.price.data
            product.mrp = form.mrp.data
            product.discount_percentage = form.discount_percentage.data
            product.size = form.size.data
            product.unit = form.unit.data
            product.sku = form.sku.data
            product.stock_quantity = form.stock_quantity.data
            product.low_stock_threshold = form.low_stock_threshold.data
            product.image_url = form.image_url.data if form.image_url.data else product.image_url
            product.features = form.features.data
            product.category_id = form.category_id.data
            product.is_active = form.is_active.data
            product.is_featured = form.is_featured.data
            
            # Handle new file uploads
            uploaded_files = request.files.getlist('product_images')
            main_image_index = request.form.get('main_image', '0')
            
            if uploaded_files and uploaded_files[0].filename != '':
                # Create upload directory if it doesn't exist
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                # Get current max display order
                existing_images = ProductImage.query.filter_by(product_id=product.id).all()
                max_order = max([img.display_order for img in existing_images], default=-1)
                
                for idx, file in enumerate(uploaded_files):
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        # Add timestamp to avoid conflicts
                        timestamp = str(int(time.time() * 1000))
                        filename = f"{product.id}_{timestamp}_{filename}"
                        filepath = os.path.join(UPLOAD_FOLDER, filename)
                        file.save(filepath)
                        
                        # Create ProductImage record
                        is_main = (str(idx) == main_image_index and len(existing_images) == 0)
                        product_image = ProductImage(
                            product_id=product.id,
                            image_url=f'images/products/{filename}',
                            is_main=is_main,
                            display_order=max_order + idx + 1,
                            alt_text=product.name
                        )
                        db.session.add(product_image)
                        
                        # Update product's main image_url if this is the first image
                        if idx == 0 and not product.image_url:
                            product.image_url = f'images/products/{filename}'
            
            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('admin.products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'danger')
    
    return render_template('admin/product_form.html', form=form, action='Edit', product=product)


@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    """Delete product"""
    product = Product.query.get_or_404(product_id)
    
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting product.', 'danger')
    
    return redirect(url_for('admin.products'))


# Order Management
@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    """List all orders"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status_filter = request.args.get('status')
    search_query = request.args.get('q', '').strip()
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = Order.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)

    if search_query:
        like_term = f"%{search_query}%"
        query = query.join(User, Order.user_id == User.id)
        query = query.filter(or_(
            Order.order_number.ilike(like_term),
            func.coalesce(User.full_name, User.username).ilike(like_term),
            User.email.ilike(like_term)
        ))

    if date_from:
        try:
            start_date = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Order.created_at >= start_date)
        except ValueError:
            flash('Invalid start date format. Use YYYY-MM-DD.', 'warning')

    if date_to:
        try:
            end_date = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Order.created_at < end_date)
        except ValueError:
            flash('Invalid end date format. Use YYYY-MM-DD.', 'warning')
    
    pagination = query.order_by(Order.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    orders = pagination.items
    
    status_counts_items = db.session.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    status_counts = {status: count for status, count in status_counts_items}
    status_total = sum(status_counts.values())

    return render_template(
        'admin/orders.html',
        orders=orders,
        pagination=pagination,
        status_filter=status_filter,
        search_query=search_query,
        date_from=date_from,
        date_to=date_to,
        status_counts=status_counts,
        status_total=status_total
    )


@admin_bp.route('/orders/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    """View order details"""
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)


@admin_bp.route('/orders/<int:order_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    """Update order status"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']
    
    if new_status not in valid_statuses:
        flash('Invalid status.', 'danger')
        return redirect(url_for('admin.order_detail', order_id=order_id))
    
    try:
        order.status = new_status
        db.session.commit()
        flash('Order status updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating order status.', 'danger')
    
    return redirect(url_for('admin.order_detail', order_id=order_id))


# User Management
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """List all users"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search_query = request.args.get('q', '').strip()
    role_filter = request.args.get('role', 'all')
    
    query = User.query

    if search_query:
        like_term = f"%{search_query}%"
        query = query.filter(or_(
            User.username.ilike(like_term),
            User.email.ilike(like_term),
            func.coalesce(User.full_name, '').ilike(like_term)
        ))

    if role_filter != 'all':
        query = query.filter(User.user_type == role_filter)

    pagination = query.order_by(User.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    users = pagination.items
    
    user_stats = {
        'total': User.query.count(),
        'admins': User.query.filter(User.user_type == 'admin').count(),
        'customers': User.query.filter(User.user_type == 'customer').count(),
        'active': User.query.filter(User.is_active == True).count()
    }

    return render_template('admin/users.html',
                         users=users,
                         pagination=pagination,
                         search_query=search_query,
                         role_filter=role_filter,
                         user_stats=user_stats)


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'warning')
        return redirect(url_for('admin.users'))
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        status = 'activated' if user.is_active else 'deactivated'
        flash(f'User {status} successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating user status.', 'danger')
    
    return redirect(url_for('admin.users'))


# Category Management
@admin_bp.route('/categories')
@login_required
@admin_required
def categories():
    """List all categories"""
    categories = Category.query.order_by(Category.display_order).all()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    """Add new category"""
    form = CategoryForm()
    
    if form.validate_on_submit():
        try:
            # Generate slug from name
            slug = form.name.data.lower().replace(' ', '-')
            
            category = Category(
                name=form.name.data,
                slug=slug,
                description=form.description.data,
                is_active=form.is_active.data
            )
            
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('admin.categories'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding category.', 'danger')
    
    return render_template('admin/category_form.html', form=form, action='Add')
