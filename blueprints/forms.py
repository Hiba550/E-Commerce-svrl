"""
WTForms for user input validation
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, FloatField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange


class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(max=120)
    ])
    phone = StringField('Phone Number', validators=[
        DataRequired(),
        Length(min=10, max=20, message='Please enter a valid phone number')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])


class LoginForm(FlaskForm):
    """User login form"""
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')


class CheckoutForm(FlaskForm):
    """Checkout form for shipping information"""
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(max=120)
    ])
    phone = StringField('Phone Number', validators=[
        DataRequired(),
        Length(min=10, max=20)
    ])
    address_line1 = StringField('Address Line 1', validators=[
        DataRequired(),
        Length(max=200)
    ])
    address_line2 = StringField('Address Line 2', validators=[
        Optional(),
        Length(max=200)
    ])
    city = StringField('City', validators=[
        DataRequired(),
        Length(max=100)
    ])
    state = StringField('State', validators=[
        DataRequired(),
        Length(max=100)
    ])
    pincode = StringField('PIN Code', validators=[
        DataRequired(),
        Length(min=6, max=10)
    ])
    notes = TextAreaField('Order Notes (Optional)', validators=[Optional()])


class ProductForm(FlaskForm):
    """Admin form for adding/editing products"""
    name = StringField('Product Name', validators=[
        DataRequired(),
        Length(max=200)
    ])
    description = TextAreaField('Description', validators=[Optional()])
    price = FloatField('Price (₹)', validators=[
        DataRequired(),
        NumberRange(min=0, message='Price must be positive')
    ])
    mrp = FloatField('MRP (₹)', validators=[
        Optional(),
        NumberRange(min=0, message='MRP must be positive')
    ])
    discount_percentage = FloatField('Discount %', validators=[
        Optional(),
        NumberRange(min=0, max=100, message='Discount must be between 0 and 100')
    ])
    size = StringField('Size', validators=[DataRequired()])
    unit = StringField('Unit', validators=[Optional()])
    sku = StringField('SKU', validators=[
        DataRequired(),
        Length(max=50)
    ])
    stock_quantity = IntegerField('Stock Quantity', validators=[
        DataRequired(),
        NumberRange(min=0)
    ])
    low_stock_threshold = IntegerField('Low Stock Threshold', validators=[
        Optional(),
        NumberRange(min=0)
    ])
    image_url = StringField('Image URL', validators=[Optional()])
    features = TextAreaField('Features', validators=[Optional()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    is_active = BooleanField('Active')
    is_featured = BooleanField('Featured')


class CategoryForm(FlaskForm):
    """Admin form for adding/editing categories"""
    name = StringField('Category Name', validators=[
        DataRequired(),
        Length(max=100)
    ])
    description = TextAreaField('Description', validators=[Optional()])
    is_active = BooleanField('Active', default=True)
