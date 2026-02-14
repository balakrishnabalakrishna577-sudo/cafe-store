import os
import environ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False)
)

# Take environment variables from .env file
environ.Env.read_env(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=True)

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'jazzmin',  # Beautiful admin theme - must be before django.contrib.admin
    'django.contrib.admin',  # Django Admin Panel
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap5',
    'cafe.apps.CafeConfig',  # Use app config to ensure signals are loaded
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'cafe.middleware.AdminSessionSeparationMiddleware',
    'cafe.middleware.CouponValidationMiddleware',
    'cafe.middleware.NoCacheMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cafe_delivery.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cafe.context_processors.cart_count',
                'cafe.context_processors.notifications_context',
                'cafe.context_processors.admin_session_context',
                'cafe.context_processors.advertisements_context',
            ],
            'builtins': [
                'cafe.templatetags.django_compat',
            ],
        },
    },
]

WSGI_APPLICATION = 'cafe_delivery.wsgi.application'
# ASGI_APPLICATION = 'cafe_delivery.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Use PostgreSQL in production
if not DEBUG:
    try:
        import dj_database_url
        DATABASES['default'] = dj_database_url.parse(env('DATABASE_URL'))
    except ImportError:
        # dj_database_url not available, keep SQLite
        pass

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Razorpay Configuration (Test Mode with Dummy Credentials)
RAZORPAY_KEY_ID = env('RAZORPAY_KEY_ID', default='rzp_test_dummy_key_id_12345')
RAZORPAY_KEY_SECRET = env('RAZORPAY_KEY_SECRET', default='dummy_secret_key_67890')

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'info@chang.spicesofindiacuisine.com'

# Security Settings for Production (commented out for development)
# if not DEBUG:
#     SECURE_BROWSER_XSS_FILTER = True
#     SECURE_CONTENT_TYPE_NOSNIFF = True
#     SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#     SECURE_HSTS_SECONDS = 31536000
#     SECURE_REDIRECT_EXEMPT = []
#     SECURE_SSL_REDIRECT = True
#     SESSION_COOKIE_SECURE = True
#     CSRF_COOKIE_SECURE = True


# REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# CORS Settings for Mobile App
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8081",  # React Native
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8081",
]

CORS_ALLOW_CREDENTIALS = True

# Allow all origins in development (change in production)
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True


# ============================================
# JAZZMIN ADMIN THEME CONFIGURATION
# ============================================

JAZZMIN_SETTINGS = {
    # Title on the login screen and header
    "site_title": "Spices of India Cuisine Admin",
    "site_header": "Spices of India Cuisine",
    "site_brand": "Spices of India Cuisine Management",
    "site_logo": None,  # Add your logo path here if you have one
    "login_logo": None,
    "site_logo_classes": "img-circle",
    "site_icon": None,
    
    # Welcome text on the login screen
    "welcome_sign": "Welcome to Spices of India Cuisine Admin Panel",
    
    # Copyright on the footer
    "copyright": "Spices of India Cuisine",
    
    # The model admin to search from the search bar, search bar omitted if excluded
    "search_model": "cafe.MenuItem",
    
    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": None,
    
    ############
    # Top Menu #
    ############
    
    # Links to put along the top menu
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:custom_dashboard", "permissions": ["auth.view_user"]},
        {"name": "Analytics", "url": "admin:custom_analytics", "permissions": ["auth.view_user"]},
        {"name": "Normal Admin", "url": "/django-admin/", "new_window": True},
        {"name": "View Site", "url": "/", "new_window": True},
    ],
    
    #############
    # User Menu #
    #############
    
    # Additional links to include in the user menu on the top right ("app" url type is not allowed)
    "usermenu_links": [
        {"name": "View Site", "url": "/", "new_window": True},
        {"model": "auth.user"},
    ],
    
    #############
    # Side Menu #
    #############
    
    # Whether to display the side menu
    "show_sidebar": True,
    
    # Whether to aut expand the menu
    "navigation_expanded": True,
    
    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],
    
    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],
    
    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["cafe", "auth"],
    
    # Custom links to append to app groups, keyed on app name
    "custom_links": {
        "cafe": [
            {
                "name": "📈 Analytics",
                "url": "admin:custom_analytics",
                "icon": "fas fa-chart-line",
                "permissions": ["cafe.view_order"]
            }
        ]
    },
    
    # Custom app and model ordering
    "apps_order": [
        "cafe",
        "auth",
    ],
    
    # Custom icons for side menu apps/models
    "icons": {
        # Auth app
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        
        # Cafe app - organized by category
        "cafe": "fas fa-store",
        
        # Menu Management
        "cafe.MenuItem": "fas fa-utensils",
        "cafe.Category": "fas fa-th-large",
        
        # Order Management
        "cafe.Order": "fas fa-shopping-cart",
        "cafe.OrderItem": "fas fa-shopping-basket",
        "cafe.OrderTracking": "fas fa-truck",
        
        # Customer Management
        "cafe.UserProfile": "fas fa-id-card",
        "cafe.DeliveryAddress": "fas fa-map-marker-alt",
        
        # Shopping Features
        "cafe.Cart": "fas fa-cart-plus",
        "cafe.Wishlist": "fas fa-heart",
        
        # Marketing & Engagement
        "cafe.Coupon": "fas fa-ticket-alt",
        "cafe.Notification": "fas fa-bell",
        "cafe.Review": "fas fa-star",
        "cafe.Rating": "fas fa-star-half-alt",
    },
    
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": False,
    
    #############
    # UI Tweaks #
    #############
    
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": "css/admin_custom.css",
    "custom_js": "js/admin_custom.js",
    
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": False,
    
    ###############
    # Change view #
    ###############
    
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    
    # Override change forms on a per modeladmin basis
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-danger",  # Changed to match custom admin red theme
    "accent": "accent-danger",  # Changed to match custom admin red theme
    "navbar": "navbar-white navbar-light",  # Light navbar to match custom admin
    "no_navbar_border": False,
    "navbar_fixed": True,  # Fixed navbar for better UX
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,  # Fixed sidebar to match custom admin
    "sidebar": "sidebar-light-danger",  # Light sidebar with danger accent
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": True,  # Disable sidebar expand/collapse
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,  # Flat style to match custom admin
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-danger",  # Changed to red to match custom admin
        "secondary": "btn-warning",  # Changed to orange to match custom admin
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    # Custom CSS variables to match custom admin panel
    "actions_sticky_top": False,
}


# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# CORS Configuration (for mobile app)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React Native
    "http://localhost:8081",  # Expo
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8081",
]

CORS_ALLOW_CREDENTIALS = True

# For development, allow all origins (remove in production)
CORS_ALLOW_ALL_ORIGINS = DEBUG
