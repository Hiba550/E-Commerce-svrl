"""
Products Blueprint
Handles product listing and detail views
"""
from flask import Blueprint, render_template, request, abort, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_, func
from models import Product, Category, ProductReview, ReviewLike, db, OrderItem, WishlistItem
from extensions import cache

products_bp = Blueprint('products', __name__)


@cache.memoize(timeout=600)
def get_price_bounds():
    """Return min and max price for active products."""
    stats = db.session.query(
        func.min(Product.price).label('min_price'),
        func.max(Product.price).label('max_price')
    ).filter(Product.is_active == True).first()

    if stats:
        min_price = float(stats.min_price or 0)
        max_price = float(stats.max_price or 0)
        return (min_price, max_price)
    return (0.0, 0.0)


@cache.memoize(timeout=300)
def _get_search_suggestions(term, limit):
    """Cached query for search suggestions."""
    search_term = f"%{term.lower()}%"
    products = Product.query.filter(
        Product.is_active == True,
        Product.name.ilike(search_term)
    ).order_by(Product.name.asc()).limit(limit).all()

    suggestions = []
    for product in products:
        # Build image URL: support both stored '/static/...' paths and relative paths
        if product.image_url:
            if product.image_url.startswith('/static/'):
                image_url = product.image_url
            else:
                image_url = url_for('static', filename=product.image_url)
        else:
            image_url = url_for('static', filename='images/product-placeholder.jpg')

        suggestions.append({
            'name': product.name,
            'slug': product.slug,
            'price': product.get_discounted_price(),
            'image': image_url
        })
    return suggestions


@products_bp.route('/')
def list_products():
    """List all products with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Get filter parameters
    category_slug = request.args.get('category')
    search_query = request.args.get('q')
    sort_by = request.args.get('sort', 'newest')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_rating = request.args.get('min_rating', type=int)
    availability = request.args.get('availability', 'all')

    if min_price is not None and max_price is not None and min_price > max_price:
        min_price, max_price = max_price, min_price

    # Rating aggregate subquery for filtering/sorting
    rating_subquery = db.session.query(
        ProductReview.product_id.label('product_id'),
        func.avg(ProductReview.rating).label('avg_rating'),
        func.count(ProductReview.id).label('review_count')
    ).group_by(ProductReview.product_id).subquery()
    
    # Base query
    query = Product.query.filter(Product.is_active == True).outerjoin(
        rating_subquery, rating_subquery.c.product_id == Product.id
    )
    
    # Apply category filter
    if category_slug:
        category = Category.query.filter_by(slug=category_slug, is_active=True).first()
        if category:
            query = query.filter(Product.category_id == category.id)

    # Apply price filters
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Apply search filter
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Product.features.ilike(search_term)
            )
        )

    # Availability filter
    if availability == 'in_stock':
        query = query.filter(Product.stock_quantity > 0)

    # Rating filter
    if min_rating:
        query = query.filter(func.coalesce(rating_subquery.c.avg_rating, 0) >= min_rating)
    
    # Apply sorting
    if sort_by == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'name':
        query = query.order_by(Product.name.asc())
    elif sort_by == 'rating':
        query = query.order_by(func.coalesce(rating_subquery.c.avg_rating, 0).desc(), Product.created_at.desc())
    else:  # newest
        query = query.order_by(Product.created_at.desc())
    
    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    # Pre-compute rating data
    rating_map = {}
    rating_counts = {}
    if products:
        product_ids = [product.id for product in products]
        rating_rows = db.session.query(
            ProductReview.product_id,
            func.avg(ProductReview.rating).label('avg_rating'),
            func.count(ProductReview.id).label('review_count')
        ).filter(ProductReview.product_id.in_(product_ids))
        rating_rows = rating_rows.group_by(ProductReview.product_id).all()

        for row in rating_rows:
            rating_map[row.product_id] = round(float(row.avg_rating or 0), 1)
            rating_counts[row.product_id] = row.review_count
    
    # Wishlist state for authenticated users
    wishlist_product_ids = set()
    if current_user.is_authenticated:
        wishlist_product_ids = {
            item.product_id for item in WishlistItem.query.filter_by(user_id=current_user.id).all()
        }

    # Get all categories for filter
    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
    
    return render_template('products/list.html',
                         products=products,
                         pagination=pagination,
                         categories=categories,
                         current_category=category_slug,
                         search_query=search_query,
                         sort_by=sort_by,
                         wishlist_product_ids=wishlist_product_ids,
                         min_price=min_price,
                         max_price=max_price,
                         min_rating=min_rating,
                         availability=availability,
                         rating_map=rating_map,
                         rating_counts=rating_counts,
                         price_bounds=get_price_bounds())


@products_bp.route('/<slug>')
def product_detail(slug):
    """Product detail page"""
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    # Get related products from the same category
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_active == True
    ).limit(4).all()
    
    # Get reviews ordered by creation date (newest first)
    reviews_list = ProductReview.query.filter_by(product_id=product.id).order_by(
        ProductReview.created_at.desc()
    ).all()
    
    is_in_wishlist = False
    if current_user.is_authenticated:
        is_in_wishlist = WishlistItem.query.filter_by(
            user_id=current_user.id,
            product_id=product.id
        ).first() is not None

    return render_template('products/detail.html',
                         product=product,
                         related_products=related_products,
                         reviews_list=reviews_list,
                         is_in_wishlist=is_in_wishlist)


@products_bp.route('/suggest')
def suggest_products():
    """Return search suggestions for auto-complete."""
    term = request.args.get('q', '').strip()
    limit = request.args.get('limit', 6, type=int)

    if not term:
        return jsonify([])

    limit = max(1, min(limit, 10))
    suggestions = _get_search_suggestions(term, limit)
    return jsonify(suggestions)


@products_bp.route('/review/add/<int:product_id>', methods=['GET', 'POST'])
@login_required
def add_review(product_id):
    """Add a review for a product"""
    product = Product.query.get_or_404(product_id)
    
    # Check if user already reviewed this product
    existing_review = ProductReview.query.filter_by(
        product_id=product_id,
        user_id=current_user.id
    ).first()
    
    if existing_review:
        flash('You have already reviewed this product', 'warning')
        return redirect(url_for('products.product_detail', slug=product.slug))
    
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        title = request.form.get('title', '').strip()
        comment = request.form.get('comment', '').strip()
        
        # Validate input
        if not rating or rating < 1 or rating > 5:
            flash('Please provide a rating between 1 and 5 stars', 'danger')
            return redirect(url_for('products.add_review', product_id=product_id))
        
        if not comment:
            flash('Please provide a review comment', 'danger')
            return redirect(url_for('products.add_review', product_id=product_id))
        
        # Check if this is a verified purchase
        has_purchased = OrderItem.query.join(OrderItem.order).filter(
            OrderItem.product_id == product_id,
            OrderItem.order.has(user_id=current_user.id),
            OrderItem.order.has(status='delivered')
        ).first() is not None
        
        # Create review
        review = ProductReview(
            product_id=product_id,
            user_id=current_user.id,
            rating=rating,
            title=title,
            comment=comment,
            is_verified_purchase=has_purchased
        )
        
        db.session.add(review)
        db.session.commit()
        
        flash('Thank you for your review!', 'success')
        return redirect(url_for('products.product_detail', slug=product.slug))
    
    return render_template('products/add_review.html', product=product)


@products_bp.route('/review/like/<int:review_id>', methods=['POST'])
@login_required
def toggle_review_like(review_id):
    """Toggle like on a review"""
    review = ProductReview.query.get_or_404(review_id)
    
    # Check if user already liked this review
    existing_like = ReviewLike.query.filter_by(
        review_id=review_id,
        user_id=current_user.id
    ).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        db.session.commit()
    else:
        # Like
        like = ReviewLike(
            review_id=review_id,
            user_id=current_user.id
        )
        db.session.add(like)
        db.session.commit()
    
    return redirect(url_for('products.product_detail', slug=review.product.slug))


@products_bp.route('/review/edit/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    """Edit a review"""
    review = ProductReview.query.get_or_404(review_id)
    
    # Check if user is the review author
    if review.user_id != current_user.id:
        flash('You can only edit your own reviews', 'danger')
        return redirect(url_for('products.product_detail', slug=review.product.slug))
    
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        title = request.form.get('title', '').strip()
        comment = request.form.get('comment', '').strip()
        
        # Validate input
        if not rating or rating < 1 or rating > 5:
            flash('Please provide a rating between 1 and 5 stars', 'danger')
            return redirect(url_for('products.edit_review', review_id=review_id))
        
        if not comment:
            flash('Please provide a review comment', 'danger')
            return redirect(url_for('products.edit_review', review_id=review_id))
        
        # Update review
        review.rating = rating
        review.title = title
        review.comment = comment
        db.session.commit()
        
        flash('Your review has been updated!', 'success')
        return redirect(url_for('products.product_detail', slug=review.product.slug))
    
    return render_template('products/edit_review.html', review=review, product=review.product)


@products_bp.route('/review/delete/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    """Delete a review"""
    review = ProductReview.query.get_or_404(review_id)
    product_slug = review.product.slug
    
    # Check if user is the review author or admin
    if review.user_id != current_user.id and not current_user.is_admin():
        flash('You can only delete your own reviews', 'danger')
        return redirect(url_for('products.product_detail', slug=product_slug))
    
    # Delete associated likes first
    ReviewLike.query.filter_by(review_id=review_id).delete()
    
    # Delete review
    db.session.delete(review)
    db.session.commit()
    
    flash('Your review has been deleted', 'success')
    return redirect(url_for('products.product_detail', slug=product_slug))
