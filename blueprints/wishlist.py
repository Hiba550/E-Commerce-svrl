"""Wishlist Blueprint
Handles customer wishlist operations
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from models import db, Product, WishlistItem, CartItem


wishlist_bp = Blueprint('wishlist', __name__)


def _wants_json_response():
    """Determine if the current request expects a JSON response."""
    if request.is_json:
        return True
    accept_mimetypes = request.accept_mimetypes
    return accept_mimetypes['application/json'] >= accept_mimetypes['text/html'] or \
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def _json_response(success, message, status='info', **extra):
    """Utility to build a JSON response with standard fields."""
    payload = {
        'success': success,
        'message': message,
        'status': status,
        'wishlistCount': WishlistItem.query.filter_by(user_id=current_user.id).count(),
        'cartCount': CartItem.query.filter_by(user_id=current_user.id).count() if success else None,
    }
    payload.update({k: v for k, v in extra.items() if v is not None})
    return jsonify(payload)


@wishlist_bp.route('/')
@login_required
def view_wishlist():
    """Render wishlist page for current user."""
    items = (WishlistItem.query
             .filter_by(user_id=current_user.id)
             .join(Product)
             .order_by(WishlistItem.created_at.desc())
             .all())

    return render_template('wishlist/list.html', items=items)


@wishlist_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id):
    """Add a product to the user's wishlist."""
    product = Product.query.filter_by(id=product_id, is_active=True).first()

    if product is None:
        message = 'Product not found or inactive.'
        if _wants_json_response():
            return _json_response(False, message, status='danger')
        flash(message, 'danger')
        return redirect(request.referrer or url_for('products.list_products'))

    existing = WishlistItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if existing:
        message = 'Product already in your wishlist.'
        if _wants_json_response():
            return _json_response(False, message, status='info', action='exists')
        flash(message, 'info')
        return redirect(request.referrer or url_for('products.product_detail', slug=product.slug))

    try:
        wishlist_item = WishlistItem(user_id=current_user.id, product_id=product_id)
        db.session.add(wishlist_item)
        db.session.commit()
    except Exception:
        db.session.rollback()
        message = 'Could not add product to wishlist. Please try again.'
        if _wants_json_response():
            return _json_response(False, message, status='danger')
        flash(message, 'danger')
        return redirect(request.referrer or url_for('products.product_detail', slug=product.slug))

    message = f'{product.name} added to your wishlist.'

    if _wants_json_response():
        return _json_response(True, message, status='success', action='added')

    flash(message, 'success')
    return redirect(request.referrer or url_for('products.product_detail', slug=product.slug))


@wishlist_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_wishlist(item_id):
    """Remove a wishlist item."""
    wishlist_item = WishlistItem.query.filter_by(id=item_id, user_id=current_user.id).first()

    if wishlist_item is None:
        message = 'Wishlist item not found.'
        if _wants_json_response():
            return _json_response(False, message, status='warning')
        flash(message, 'warning')
        return redirect(request.referrer or url_for('wishlist.view_wishlist'))

    product_name = wishlist_item.product.name if wishlist_item.product else 'Item'

    try:
        db.session.delete(wishlist_item)
        db.session.commit()
    except Exception:
        db.session.rollback()
        message = 'Unable to remove item from wishlist. Please try again.'
        if _wants_json_response():
            return _json_response(False, message, status='danger')
        flash(message, 'danger')
        return redirect(request.referrer or url_for('wishlist.view_wishlist'))

    message = f'{product_name} removed from your wishlist.'

    if _wants_json_response():
        return _json_response(True, message, status='success', action='removed', removedId=item_id)

    flash(message, 'success')
    return redirect(request.referrer or url_for('wishlist.view_wishlist'))


@wishlist_bp.route('/move-to-cart/<int:item_id>', methods=['POST'])
@login_required
def move_to_cart(item_id):
    """Move an item from the wishlist to the cart."""
    wishlist_item = WishlistItem.query.filter_by(id=item_id, user_id=current_user.id).first()

    if wishlist_item is None:
        message = 'Wishlist item not found.'
        if _wants_json_response():
            return _json_response(False, message, status='warning')
        flash(message, 'warning')
        return redirect(request.referrer or url_for('wishlist.view_wishlist'))

    product = wishlist_item.product

    if product is None or not product.is_active or not product.is_in_stock():
        message = 'Product is currently unavailable to purchase.'
        if _wants_json_response():
            return _json_response(False, message, status='warning')
        flash(message, 'warning')
        return redirect(request.referrer or url_for('wishlist.view_wishlist'))

    try:
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()

        if cart_item:
            new_quantity = min(cart_item.quantity + 1, product.stock_quantity)
            cart_item.quantity = new_quantity
        else:
            cart_item = CartItem(
                user_id=current_user.id,
                product_id=product.id,
                quantity=1
            )
            db.session.add(cart_item)

        db.session.delete(wishlist_item)
        db.session.commit()
    except Exception:
        db.session.rollback()
        message = 'Could not move item to cart. Please try again.'
        if _wants_json_response():
            return _json_response(False, message, status='danger')
        flash(message, 'danger')
        return redirect(request.referrer or url_for('wishlist.view_wishlist'))

    message = f'{product.name} moved to your cart.'

    if _wants_json_response():
        return _json_response(True, message, status='success', action='moved', movedId=item_id)

    flash(message, 'success')
    return redirect(request.referrer or url_for('cart.view_cart'))


