"""
Cart Blueprint
Handles shopping cart operations
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Product, CartItem

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('/')
@login_required
def view_cart():
    """View shopping cart"""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    # Calculate totals
    subtotal = sum(item.get_subtotal() for item in cart_items)
    
    return render_template('cart/view.html',
                         cart_items=cart_items,
                         subtotal=subtotal)


@cart_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """Add product to cart"""
    product = Product.query.get_or_404(product_id)
    
    if not product.is_active or not product.is_in_stock():
        flash('Product is currently unavailable.', 'warning')
        return redirect(request.referrer or url_for('products.list_products'))
    
    # Get quantity from form
    quantity = request.form.get('quantity', 1, type=int)
    
    if quantity < 1:
        flash('Invalid quantity.', 'danger')
        return redirect(request.referrer or url_for('products.list_products'))
    
    # Check stock availability
    if quantity > product.stock_quantity:
        flash(f'Only {product.stock_quantity} items available in stock.', 'warning')
        return redirect(request.referrer or url_for('products.list_products'))
    
    # Check if item already in cart
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()
    
    try:
        if cart_item:
            # Update quantity
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock_quantity:
                flash(f'Cannot add more. Only {product.stock_quantity} items available.', 'warning')
                return redirect(request.referrer or url_for('products.list_products'))
            cart_item.quantity = new_quantity
            message = f'Updated {product.name} quantity in cart.'
        else:
            # Add new item
            cart_item = CartItem(
                user_id=current_user.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
            message = f'Added {product.name} to cart.'
        
        db.session.commit()
        flash(message, 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error adding item to cart.', 'danger')
    
    return redirect(request.referrer or url_for('cart.view_cart'))


@cart_bp.route('/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart_item(item_id):
    """Update cart item quantity"""
    cart_item = CartItem.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first_or_404()
    
    quantity = request.form.get('quantity', 1, type=int)
    
    if quantity < 1:
        flash('Invalid quantity.', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    # Check stock availability
    if quantity > cart_item.product.stock_quantity:
        flash(f'Only {cart_item.product.stock_quantity} items available in stock.', 'warning')
        return redirect(url_for('cart.view_cart'))
    
    try:
        cart_item.quantity = quantity
        db.session.commit()
        flash('Cart updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating cart.', 'danger')
    
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    """Remove item from cart"""
    cart_item = CartItem.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first_or_404()
    
    try:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error removing item from cart.', 'danger')
    
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/clear', methods=['POST'])
@login_required
def clear_cart():
    """Clear all items from cart"""
    try:
        CartItem.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash('Cart cleared successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error clearing cart.', 'danger')
    
    return redirect(url_for('cart.view_cart'))
