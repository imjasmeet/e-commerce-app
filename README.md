# E-Commerce Store

A simple e-commerce application built with Python Flask that allows users to browse products, add them to cart, and place orders.

## Features

- **Product Catalog**: Browse available products with descriptions and prices
- **Shopping Cart**: Add/remove products from cart with quantity tracking
- **Checkout Process**: Complete orders with customer information
- **Order Management**: Store orders in SQLite database
- **Responsive Design**: Modern UI with Bootstrap and Font Awesome icons

## Sample Products

The application comes with 5 sample products:
- Laptop ($999.99)
- Smartphone ($699.99)
- Headphones ($199.99)
- Tablet ($399.99)
- Smartwatch ($299.99)

## Installation

### Option 1: Local Development

1. **Clone or download the project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the application**:
   Open your browser and go to `http://localhost:8000`

### Option 2: Docker Deployment (Recommended)

1. **Deploy with Docker Compose**:
   ```bash
   # Quick deployment
   ./deploy.sh
   
   # Or manually
   docker-compose up --build -d
   ```

2. **Access the application**:
   Open your browser and go to `http://localhost:8000`

3. **View logs**:
   ```bash
   docker-compose logs -f
   ```

4. **Stop the application**:
   ```bash
   docker-compose down
   ```

## Usage

1. **Browse Products**: View the product catalog on the home page
2. **Add to Cart**: Click "Add to Cart" on any product
3. **View Cart**: Click the cart icon in the navigation to see your items
4. **Remove Items**: Use the "Remove" button in the cart to delete items
5. **Checkout**: Click "Proceed to Checkout" to place your order
6. **Complete Order**: Fill in your name and email, then click "Place Order"

## Database

The application uses SQLite with three main tables:
- `products`: Product information (name, description, price, stock)


- `orders`: Customer orders (name, email, total amount, date)
- `order_items`: Individual items in each order

The database is automatically created when you first run the application.

## Project Structure

```
e-commerce-app/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose configuration
├── deploy.sh          # Deployment script
├── .dockerignore      # Docker ignore file
├── templates/         # HTML templates
│   ├── base.html      # Base template with navigation
│   ├── index.html     # Product listing page
│   ├── cart.html      # Shopping cart page
│   └── checkout.html  # Checkout page
└── static/            # Static files (CSS, images)
```

## Technologies Used

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML, Bootstrap 5, Font Awesome
- **Session Management**: Flask sessions for cart functionality

## Demo Features

- Session-based shopping cart
- Product catalog with pricing
- Order placement with customer details
- Responsive design for mobile and desktop
- Flash messages for user feedback

This is a demo application for educational purposes. No real payment processing is implemented. 