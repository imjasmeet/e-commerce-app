from flask import Flask, request, jsonify, session
import sqlite3
from datetime import datetime
import os
import random
import time
import logging
import json
from logging.handlers import RotatingFileHandler
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Global failure simulation flags
SIMULATE_DB_FAILURE = False
SIMULATE_SLOW_RESPONSE = False
SIMULATE_RANDOM_ERRORS = False
SIMULATE_NULL_POINTER = False

# Configure logging
def setup_logging():
    """Setup comprehensive logging configuration"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler with rotation
            RotatingFileHandler(
                'logs/app.log',
                maxBytes=1024 * 1024,  # 1MB
                backupCount=5
            ),
            # Error file handler
            RotatingFileHandler(
                'logs/error.log',
                maxBytes=1024 * 1024,  # 1MB
                backupCount=5
            )
        ]
    )
    
    # Set specific loggers
    app.logger.setLevel(logging.INFO)
    
    # Create custom loggers
    logger = logging.getLogger('ecommerce')
    logger.setLevel(logging.INFO)
    
    # Add handlers to custom logger
    file_handler = RotatingFileHandler('logs/ecommerce.log', maxBytes=1024*1024, backupCount=5)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)
    
    return logger

# Initialize logger
logger = setup_logging()

def log_request_info():
    """Log request information"""
    logger.info(f"API Request: {request.method} {request.url} - IP: {request.remote_addr} - User-Agent: {request.headers.get('User-Agent', 'Unknown')}")

def log_user_action(action, details=None):
    """Log user actions"""
    user_info = {
        'action': action,
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'session_id': session.get('_id', 'No Session'),
        'timestamp': datetime.now().isoformat()
    }
    if details:
        user_info.update(details)
    
    logger.info(f"User Action: {json.dumps(user_info)}")

def log_error(error, context=None):
    """Log errors with context"""
    error_info = {
        'error': str(error),
        'error_type': type(error).__name__,
        'ip': request.remote_addr,
        'url': request.url,
        'method': request.method,
        'timestamp': datetime.now().isoformat()
    }
    if context:
        error_info.update(context)
    
    logger.error(f"Application Error: {json.dumps(error_info)}")

def log_performance(operation, duration, details=None):
    """Log performance metrics"""
    perf_info = {
        'operation': operation,
        'duration_ms': round(duration * 1000, 2),
        'timestamp': datetime.now().isoformat()
    }
    if details:
        perf_info.update(details)
    
    logger.info(f"Performance: {json.dumps(perf_info)}")

def api_response(data=None, message="Success", status_code=200, error=None):
    """Standard API response format"""
    response = {
        "success": status_code < 400,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    if error:
        response["error"] = error
    
    return jsonify(response), status_code

def handle_errors(f):
    """Decorator to handle API errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            log_error(e, {'operation': f.__name__})
            return api_response(
                message="Internal server error",
                status_code=500,
                error=str(e)
            )
    return decorated_function

# Database initialization
def init_db():
    try:
        start_time = time.time()
        logger.info("Starting database initialization...")
        
        conn = sqlite3.connect('ecommerce.db')
        cursor = conn.cursor()
        
        # Create products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                image_url TEXT,
                stock INTEGER DEFAULT 0
            )
        ''')
        
        # Create orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                total_amount REAL NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create order_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                price REAL,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Insert sample products if they don't exist
        cursor.execute('SELECT COUNT(*) FROM products')
        if cursor.fetchone()[0] == 0:
            sample_products = [
                ('Laptop', 'High-performance laptop with latest specs', 999.99, '/static/laptop.jpg', 10),
                ('Smartphone', 'Latest smartphone with great camera', 699.99, '/static/phone.jpg', 15),
                ('Headphones', 'Wireless noise-cancelling headphones', 199.99, '/static/headphones.jpg', 20),
                ('Tablet', '10-inch tablet perfect for work and play', 399.99, '/static/tablet.jpg', 8),
                ('Smartwatch', 'Fitness tracking smartwatch', 299.99, '/static/watch.jpg', 12)
            ]
            cursor.executemany('INSERT INTO products (name, description, price, image_url, stock) VALUES (?, ?, ?, ?, ?)', sample_products)
            logger.info(f"Inserted {len(sample_products)} sample products")
        
        conn.commit()
        conn.close()
        
        duration = time.time() - start_time
        log_performance("database_initialization", duration)
        logger.info("✅ Database initialized successfully")
        
    except Exception as e:
        log_error(e, {'operation': 'database_initialization'})
        print(f"❌ Database initialization failed: {e}")
        raise

def simulate_failures():
    """Simulate various failure scenarios"""
    if SIMULATE_DB_FAILURE:
        logger.warning("Simulating database failure")
        raise Exception("Simulated database connection failure")
    
    if SIMULATE_SLOW_RESPONSE:
        logger.warning("Simulating slow response (5 seconds)")
        time.sleep(5)  # Simulate slow response
    
    if SIMULATE_RANDOM_ERRORS and random.random() < 0.3:
        logger.warning("Simulating random application error")
        raise Exception("Random application error")
    
    if SIMULATE_NULL_POINTER:
        logger.warning("Simulating null pointer exception")
        # Create a null reference and try to access it
        null_obj = None
        null_obj.some_attribute  # This will raise AttributeError (Python's equivalent of NullPointerException)

# API Routes

@app.route('/api/products', methods=['GET'])
@handle_errors
def get_products():
    """Get all products"""
    start_time = time.time()
    log_request_info()
    
    simulate_failures()
    
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products_data = cursor.fetchall()
    conn.close()
    
    products = []
    for product in products_data:
        products.append({
            'id': product[0],
            'name': product[1],
            'description': product[2],
            'price': product[3],
            'image_url': product[4],
            'stock': product[5]
        })
    
    duration = time.time() - start_time
    log_performance("get_products", duration, {'products_count': len(products)})
    log_user_action('get_products', {'products_count': len(products)})
    
    return api_response(
        data={'products': products, 'total': len(products)},
        message="Products retrieved successfully"
    )

@app.route('/api/products/<int:product_id>', methods=['GET'])
@handle_errors
def get_product(product_id):
    """Get a specific product"""
    start_time = time.time()
    log_request_info()
    
    simulate_failures()
    
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product_data = cursor.fetchone()
    conn.close()
    
    if not product_data:
        return api_response(
            message="Product not found",
            status_code=404
        )
    
    product = {
        'id': product_data[0],
        'name': product_data[1],
        'description': product_data[2],
        'price': product_data[3],
        'image_url': product_data[4],
        'stock': product_data[5]
    }
    
    duration = time.time() - start_time
    log_performance("get_product", duration, {'product_id': product_id})
    log_user_action('get_product', {'product_id': product_id})
    
    return api_response(
        data={'product': product},
        message="Product retrieved successfully"
    )

@app.route('/api/cart', methods=['GET'])
@handle_errors
def get_cart():
    """Get current cart"""
    start_time = time.time()
    log_request_info()
    
    simulate_failures()
    
    if 'cart' not in session or not session['cart']:
        log_user_action('get_empty_cart')
        return api_response(
            data={'items': [], 'total': 0, 'item_count': 0},
            message="Cart is empty"
        )
    
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    cart_items = []
    total = 0
    
    for product_id, quantity in session['cart'].items():
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        if product:
            item_total = product[3] * quantity
            cart_items.append({
                'product_id': product[0],
                'name': product[1],
                'price': product[3],
                'quantity': quantity,
                'total': item_total
            })
            total += item_total
    
    conn.close()
    
    duration = time.time() - start_time
    log_performance("get_cart", duration, {
        'cart_items_count': len(cart_items),
        'cart_total': total
    })
    log_user_action('get_cart', {
        'cart_items_count': len(cart_items),
        'cart_total': total
    })
    
    return api_response(
        data={
            'items': cart_items,
            'total': total,
            'item_count': len(cart_items)
        },
        message="Cart retrieved successfully"
    )

@app.route('/api/cart/add', methods=['POST'])
@handle_errors
def add_to_cart():
    """Add product to cart"""
    start_time = time.time()
    log_request_info()
    
    simulate_failures()
    
    data = request.get_json()
    if not data or 'product_id' not in data:
        return api_response(
            message="Product ID is required",
            status_code=400
        )
    
    product_id = data['product_id']
    quantity = data.get('quantity', 1)
    
    # Validate product exists
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        return api_response(
            message="Product not found",
            status_code=404
        )
    
    if 'cart' not in session:
        session['cart'] = {}
    
    if str(product_id) in session['cart']:
        session['cart'][str(product_id)] += quantity
        action = 'increment_cart_item'
    else:
        session['cart'][str(product_id)] = quantity
        action = 'add_new_cart_item'
    
    duration = time.time() - start_time
    log_performance("add_to_cart", duration, {'product_id': product_id})
    log_user_action(action, {
        'product_id': product_id,
        'quantity': quantity,
        'cart_total_items': sum(session['cart'].values())
    })
    
    return api_response(
        data={
            'product_id': product_id,
            'quantity': session['cart'][str(product_id)],
            'cart_total_items': sum(session['cart'].values())
        },
        message="Product added to cart successfully"
    )

@app.route('/api/cart/remove/<int:product_id>', methods=['DELETE'])
@handle_errors
def remove_from_cart(product_id):
    """Remove product from cart"""
    start_time = time.time()
    log_request_info()
    
    simulate_failures()
    
    if 'cart' not in session or str(product_id) not in session['cart']:
        return api_response(
            message="Product not in cart",
            status_code=404
        )
    
    quantity = session['cart'][str(product_id)]
    del session['cart'][str(product_id)]
    
    duration = time.time() - start_time
    log_performance("remove_from_cart", duration, {'product_id': product_id})
    log_user_action('remove_from_cart', {
        'product_id': product_id,
        'removed_quantity': quantity,
        'cart_total_items': sum(session['cart'].values())
    })
    
    return api_response(
        data={
            'product_id': product_id,
            'removed_quantity': quantity,
            'cart_total_items': sum(session['cart'].values())
        },
        message="Product removed from cart successfully"
    )

@app.route('/api/cart/clear', methods=['DELETE'])
@handle_errors
def clear_cart():
    """Clear entire cart"""
    start_time = time.time()
    log_request_info()
    
    simulate_failures()
    
    if 'cart' in session:
        cart_items = sum(session['cart'].values())
        session.pop('cart', None)
        
        duration = time.time() - start_time
        log_performance("clear_cart", duration)
        log_user_action('clear_cart', {'cleared_items': cart_items})
        
        return api_response(
            data={'cleared_items': cart_items},
            message="Cart cleared successfully"
        )
    
    return api_response(
        message="Cart is already empty"
    )

@app.route('/api/orders', methods=['POST'])
@handle_errors
def create_order():
    """Create a new order"""
    start_time = time.time()
    log_request_info()
    
    simulate_failures()
    
    if 'cart' not in session or not session['cart']:
        log_user_action('create_order_empty_cart')
        return api_response(
            message="Cannot create order with empty cart",
            status_code=400
        )
    
    data = request.get_json()
    if not data or 'customer_name' not in data or 'customer_email' not in data:
        return api_response(
            message="Customer name and email are required",
            status_code=400
        )
    
    customer_name = data['customer_name']
    customer_email = data['customer_email']
    
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # Calculate total
    total = 0
    cart_items = []
    for product_id, quantity in session['cart'].items():
        cursor.execute('SELECT price FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        if product:
            total += product[0] * quantity
            cart_items.append({'product_id': product_id, 'quantity': quantity, 'price': product[0]})
    
    # Create order
    cursor.execute('INSERT INTO orders (customer_name, customer_email, total_amount) VALUES (?, ?, ?)',
                  (customer_name, customer_email, total))
    order_id = cursor.lastrowid
    
    # Add order items
    for product_id, quantity in session['cart'].items():
        cursor.execute('SELECT price FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        if product:
            cursor.execute('INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)',
                         (order_id, product_id, quantity, product[0]))
    
    conn.commit()
    conn.close()
    
    # Clear cart
    cart_total_items = sum(session['cart'].values())
    session.pop('cart', None)
    
    duration = time.time() - start_time
    log_performance("create_order", duration, {
        'order_id': order_id,
        'total_amount': total,
        'items_count': len(cart_items)
    })
    log_user_action('create_order', {
        'order_id': order_id,
        'customer_name': customer_name,
        'customer_email': customer_email,
        'total_amount': total,
        'items_count': len(cart_items)
    })
    
    return api_response(
        data={
            'order_id': order_id,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'total_amount': total,
            'items_count': len(cart_items),
            'items': cart_items
        },
        message="Order created successfully"
    )

@app.route('/api/orders', methods=['GET'])
@handle_errors
def get_orders():
    """Get all orders"""
    start_time = time.time()
    log_request_info()
    
    simulate_failures()
    
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders ORDER BY order_date DESC')
    orders_data = cursor.fetchall()
    conn.close()
    
    orders = []
    for order in orders_data:
        orders.append({
            'id': order[0],
            'customer_name': order[1],
            'customer_email': order[2],
            'total_amount': order[3],
            'order_date': order[4]
        })
    
    duration = time.time() - start_time
    log_performance("get_orders", duration, {'orders_count': len(orders)})
    log_user_action('get_orders', {'orders_count': len(orders)})
    
    return api_response(
        data={'orders': orders, 'total': len(orders)},
        message="Orders retrieved successfully"
    )

@app.route('/api/orders/<int:order_id>', methods=['GET'])
@handle_errors
def get_order(order_id):
    """Get specific order with items"""
    start_time = time.time()
    log_request_info()
    
    simulate_failures()
    
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # Get order details
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    order_data = cursor.fetchone()
    
    if not order_data:
        return api_response(
            message="Order not found",
            status_code=404
        )
    
    # Get order items
    cursor.execute('''
        SELECT oi.*, p.name, p.description 
        FROM order_items oi 
        JOIN products p ON oi.product_id = p.id 
        WHERE oi.order_id = ?
    ''', (order_id,))
    items_data = cursor.fetchall()
    
    conn.close()
    
    order = {
        'id': order_data[0],
        'customer_name': order_data[1],
        'customer_email': order_data[2],
        'total_amount': order_data[3],
        'order_date': order_data[4],
        'items': []
    }
    
    for item in items_data:
        order['items'].append({
            'product_id': item[2],
            'name': item[5],
            'description': item[6],
            'quantity': item[3],
            'price': item[4],
            'total': item[3] * item[4]
        })
    
    duration = time.time() - start_time
    log_performance("get_order", duration, {'order_id': order_id})
    log_user_action('get_order', {'order_id': order_id})
    
    return api_response(
        data={'order': order},
        message="Order retrieved successfully"
    )

# Failure simulation routes
@app.route('/api/simulate/db-failure', methods=['GET'])
def simulate_db_failure():
    global SIMULATE_DB_FAILURE
    SIMULATE_DB_FAILURE = not SIMULATE_DB_FAILURE
    status = "enabled" if SIMULATE_DB_FAILURE else "disabled"
    logger.warning(f"Database failure simulation {status}")
    return api_response(
        data={'simulation': 'db_failure', 'status': status},
        message=f"Database failure simulation {status}"
    )

@app.route('/api/simulate/slow-response', methods=['GET'])
def simulate_slow_response():
    global SIMULATE_SLOW_RESPONSE
    SIMULATE_SLOW_RESPONSE = not SIMULATE_SLOW_RESPONSE
    status = "enabled" if SIMULATE_SLOW_RESPONSE else "disabled"
    logger.warning(f"Slow response simulation {status}")
    return api_response(
        data={'simulation': 'slow_response', 'status': status},
        message=f"Slow response simulation {status}"
    )

@app.route('/api/simulate/random-errors', methods=['GET'])
def simulate_random_errors():
    global SIMULATE_RANDOM_ERRORS
    SIMULATE_RANDOM_ERRORS = not SIMULATE_RANDOM_ERRORS
    status = "enabled" if SIMULATE_RANDOM_ERRORS else "disabled"
    logger.warning(f"Random error simulation {status}")
    return api_response(
        data={'simulation': 'random_errors', 'status': status},
        message=f"Random error simulation {status}"
    )

@app.route('/api/simulate/null-pointer', methods=['GET'])
def simulate_null_pointer():
    global SIMULATE_NULL_POINTER
    SIMULATE_NULL_POINTER = not SIMULATE_NULL_POINTER
    status = "enabled" if SIMULATE_NULL_POINTER else "disabled"
    logger.warning(f"Null pointer exception simulation {status}")
    return api_response(
        data={'simulation': 'null_pointer', 'status': status},
        message=f"Null pointer exception simulation {status}"
    )

@app.route('/api/health', methods=['GET'])
def health_check():
    start_time = time.time()
    try:
        conn = sqlite3.connect('ecommerce.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products')
        product_count = cursor.fetchone()[0]
        conn.close()
        
        duration = time.time() - start_time
        log_performance("health_check", duration)
        
        return api_response(
            data={
                "status": "healthy",
                "database": "connected",
                "products": product_count,
                "simulations": {
                    "db_failure": SIMULATE_DB_FAILURE,
                    "slow_response": SIMULATE_SLOW_RESPONSE,
                    "random_errors": SIMULATE_RANDOM_ERRORS,
                    "null_pointer": SIMULATE_NULL_POINTER
                }
            },
            message="Application is healthy"
        )
    except Exception as e:
        duration = time.time() - start_time
        log_error(e, {'operation': 'health_check', 'duration_ms': round(duration * 1000, 2)})
        return api_response(
            data={
                "status": "unhealthy",
                "error": str(e)
            },
            message="Application is unhealthy",
            status_code=500
        )

@app.route('/api/logs', methods=['GET'])
def view_logs():
    """View application logs (for debugging)"""
    try:
        log_files = {}
        log_dir = 'logs'
        
        if os.path.exists(log_dir):
            for filename in os.listdir(log_dir):
                if filename.endswith('.log'):
                    filepath = os.path.join(log_dir, filename)
                    with open(filepath, 'r') as f:
                        # Get last 50 lines
                        lines = f.readlines()
                        log_files[filename] = lines[-50:] if len(lines) > 50 else lines
        
        return api_response(
            data={
                "log_files": log_files,
                "timestamp": datetime.now().isoformat()
            },
            message="Logs retrieved successfully"
        )
    except Exception as e:
        log_error(e, {'operation': 'view_logs'})
        return api_response(
            message="Error retrieving logs",
            status_code=500,
            error=str(e)
        )

@app.route('/api', methods=['GET'])
def api_info():
    """API information and available endpoints"""
    return api_response(
        data={
            "name": "E-Commerce API",
            "version": "1.0.0",
            "description": "RESTful API for e-commerce operations",
            "endpoints": {
                "products": {
                    "GET /api/products": "Get all products",
                    "GET /api/products/{id}": "Get specific product"
                },
                "cart": {
                    "GET /api/cart": "Get current cart",
                    "POST /api/cart/add": "Add product to cart",
                    "DELETE /api/cart/remove/{id}": "Remove product from cart",
                    "DELETE /api/cart/clear": "Clear entire cart"
                },
                "orders": {
                    "GET /api/orders": "Get all orders",
                    "GET /api/orders/{id}": "Get specific order",
                    "POST /api/orders": "Create new order"
                },
                "system": {
                    "GET /api/health": "Health check",
                    "GET /api/logs": "View application logs",
                    "GET /api/simulate/{type}": "Simulate failures (db-failure, slow-response, random-errors, null-pointer)"
                }
            }
        },
        message="API information"
    )

if __name__ == '__main__':
    logger.info("Starting E-Commerce API...")
    init_db()
    logger.info("API startup complete")
    app.run(debug=False, host='0.0.0.0', port=8000) 