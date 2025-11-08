"""
Checkout Blueprint
Handles order checkout and payment processing
"""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, CartItem, Order, OrderItem
from blueprints.forms import CheckoutForm
import uuid

checkout_bp = Blueprint('checkout', __name__)


@checkout_bp.route('/', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page"""
    # Get cart items
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('products.list_products'))
    
    # Calculate totals
    subtotal = sum(item.get_subtotal() for item in cart_items)
    tax_rate = 0.05  # 5% tax
    tax_amount = round(subtotal * tax_rate, 2)
    shipping_cost = 0 if subtotal > 500 else 50  # Free shipping over ₹500
    total_amount = subtotal + tax_amount + shipping_cost
    
    form = CheckoutForm()
    
    # Pre-fill form with user data
    if request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.phone.data = current_user.phone
        form.address_line1.data = current_user.address_line1
        form.address_line2.data = current_user.address_line2
        form.city.data = current_user.city
        form.state.data = current_user.state
        form.pincode.data = current_user.pincode
    
    if form.validate_on_submit():
        try:
            # Generate unique order number
            order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
            
            # Create order
            order = Order(
                order_number=order_number,
                user_id=current_user.id,
                status='confirmed',
                payment_method='razorpay_mock',
                payment_status='paid',
                payment_id=f"pay_{uuid.uuid4().hex[:16]}",
                subtotal=subtotal,
                tax_amount=tax_amount,
                shipping_cost=shipping_cost,
                total_amount=total_amount,
                shipping_full_name=form.full_name.data,
                shipping_phone=form.phone.data,
                shipping_address_line1=form.address_line1.data,
                shipping_address_line2=form.address_line2.data,
                shipping_city=form.city.data,
                shipping_state=form.state.data,
                shipping_pincode=form.pincode.data,
                notes=form.notes.data
            )
            db.session.add(order)
            db.session.flush()  # Get order ID
            
            # Create order items
            for cart_item in cart_items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=cart_item.product_id,
                    product_name=cart_item.product.name,
                    product_size=cart_item.product.size,
                    product_sku=cart_item.product.sku,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product.get_discounted_price(),
                    subtotal=cart_item.get_subtotal()
                )
                db.session.add(order_item)
                
                # Update product stock
                cart_item.product.stock_quantity -= cart_item.quantity
            
            # Clear cart
            CartItem.query.filter_by(user_id=current_user.id).delete()
            
            # Commit transaction
            db.session.commit()
            
            flash('Order placed successfully!', 'success')
            return redirect(url_for('checkout.order_confirmation', order_number=order_number))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your order. Please try again.', 'danger')
            return redirect(url_for('checkout.checkout'))
    
    return render_template('checkout/checkout.html',
                         form=form,
                         cart_items=cart_items,
                         subtotal=subtotal,
                         tax_amount=tax_amount,
                         shipping_cost=shipping_cost,
                         total_amount=total_amount)


@checkout_bp.route('/confirmation/<order_number>')
@login_required
def order_confirmation(order_number):
    """Order confirmation page"""
    order = Order.query.filter_by(
        order_number=order_number,
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('checkout/confirmation.html', order=order)


@checkout_bp.route('/orders')
@login_required
def my_orders():
    """User's order history"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    pagination = Order.query.filter_by(user_id=current_user.id)\
        .order_by(Order.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    orders = pagination.items
    
    return render_template('checkout/orders.html',
                         orders=orders,
                         pagination=pagination)


@checkout_bp.route('/orders/<order_number>')
@login_required
def order_detail(order_number):
    """Order detail page"""
    order = Order.query.filter_by(
        order_number=order_number,
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('checkout/order_detail.html', order=order)
