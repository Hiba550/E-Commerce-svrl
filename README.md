## Project Structure

```
ecommerce/
│
├── app.py                      # Main application entry point
├── config.py                   # Configuration settings
├── models.py                   # Database models
├── seed_data.py               # Database seeding script
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
├── .env                       # Environment variables
├── .gitignore                # Git ignore rules
│
├── blueprints/               # Application blueprints (modules)
│   ├── __init__.py
│   ├── auth.py              # Authentication routes
│   ├── main.py              # Main/home routes
│   ├── products.py          # Product routes
│   ├── cart.py              # Shopping cart routes
│   ├── checkout.py          # Checkout & orders routes
│   ├── admin.py             # Admin panel routes
│   └── forms.py             # WTForms definitions
│
├── templates/               # Jinja2 templates
│   ├── base.html           # Base template
│   ├── main/               # Home, about, contact pages
│   ├── auth/               # Login, register, profile
│   ├── products/           # Product listing & details
│   ├── cart/               # Shopping cart
│   ├── checkout/           # Checkout & order pages
│   ├── admin/              # Admin dashboard
│   └── errors/             # Error pages (404, 500)
│
└── static/                 # Static assets
    ├── css/
    │   └── theme.css       # Main stylesheet
    ├── js/
    │   └── main.js         # JavaScript functionality
    └── images/             # Product images, logos
```# E-Commerce-svrl
