from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database initialization
def init_db():
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
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    
    if str(product_id) in session['cart']:
        session['cart'][str(product_id)] += 1
    else:
        session['cart'][str(product_id)] = 1
    
    flash('Product added to cart!')
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    if 'cart' not in session or not session['cart']:
        return render_template('cart.html', cart_items=[], total=0)
    
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
                'id': product[0],
                'name': product[1],
                'price': product[3],
                'quantity': quantity,
                'total': item_total
            })
            total += item_total
    
    conn.close()
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session and str(product_id) in session['cart']:
        del session['cart'][str(product_id)]
        flash('Product removed from cart!')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        customer_email = request.form['customer_email']
        
        if not customer_name or not customer_email:
            flash('Please fill in all fields!')
            return render_template('checkout.html')
        
        conn = sqlite3.connect('ecommerce.db')
        cursor = conn.cursor()
        
        # Calculate total
        total = 0
        for product_id, quantity in session['cart'].items():
            cursor.execute('SELECT price FROM products WHERE id = ?', (product_id,))
            product = cursor.fetchone()
            if product:
                total += product[0] * quantity
        
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
        session.pop('cart', None)
        
        flash('Order placed successfully!')
        return redirect(url_for('index'))
    
    return render_template('checkout.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=8000) 