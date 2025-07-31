# E-Commerce API

A RESTful API for e-commerce operations built with Python Flask, featuring comprehensive logging, error handling, and failure simulation capabilities.

## Features

- **Product Management**: List and retrieve products
- **Shopping Cart**: Add, remove, and manage cart items
- **Order Processing**: Create and retrieve orders
- **Comprehensive Logging**: Structured logging with rotation
- **Error Handling**: Graceful error handling with detailed logging
- **Failure Simulation**: Test application resilience with simulated failures
- **Health Monitoring**: Application health checks and monitoring
- **Docker Support**: Containerized deployment with Docker Compose

## API Endpoints

### Products
- `GET /api/products` - Get all products
- `GET /api/products/{id}` - Get specific product

### Cart
- `GET /api/cart` - Get current cart
- `POST /api/cart/add` - Add product to cart
- `DELETE /api/cart/remove/{id}` - Remove product from cart
- `DELETE /api/cart/clear` - Clear entire cart

### Orders
- `GET /api/orders` - Get all orders
- `GET /api/orders/{id}` - Get specific order with items
- `POST /api/orders` - Create new order

### System
- `GET /api/health` - Health check
- `GET /api/logs` - View application logs
- `GET /api/simulate/{type}` - Simulate failures
- `GET /api` - API information

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd e-commerce-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the API**
   - API Base URL: `http://localhost:8000/api`
   - Health Check: `http://localhost:8000/api/health`
   - API Info: `http://localhost:8000/api`

### Docker Deployment (Recommended)

1. **Deploy with Docker Compose**
   ```bash
   ./deploy.sh
   ```

2. **Manual Docker commands**
   ```bash
   # Build and start
   docker-compose up --build -d
   
   # View logs
   docker-compose logs -f
   
   # Stop the app
   docker-compose down
   ```

## API Usage Examples

### Get Products
```bash
curl http://localhost:8000/api/products
```

### Add to Cart
```bash
curl -X POST http://localhost:8000/api/cart/add \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'
```

### Get Cart
```bash
curl http://localhost:8000/api/cart
```

### Create Order
```bash
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "John Doe", "customer_email": "john@example.com"}'
```

### Health Check
```bash
curl http://localhost:8000/api/health
```

## Response Format

All API responses follow a standard format:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "timestamp": "2025-07-31T12:00:00",
  "data": {
    // Response data here
  }
}
```

## Logging

The application includes comprehensive logging with the following features:

- **Multiple log files**: `app.log`, `error.log`, `ecommerce.log`
- **Log rotation**: 1MB max file size with 5 backup files
- **Structured logging**: JSON-formatted log entries
- **Performance tracking**: Response time monitoring
- **User action tracking**: Detailed user interaction logs
- **Error logging**: Comprehensive error context

### Log Files
- `logs/app.log` - General application logs
- `logs/error.log` - Error-specific logs
- `logs/ecommerce.log` - E-commerce specific operations

## Testing

### Run Failure Tests
```bash
python test_failures.py
```

This script tests:
- Database failure simulation
- Slow response simulation
- Random error simulation
- Application recovery

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test failure simulations
curl http://localhost:8000/api/simulate/db-failure
curl http://localhost:8000/api/simulate/slow-response
curl http://localhost:8000/api/simulate/random-errors
```

## Project Structure

```
e-commerce-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose configuration
├── deploy.sh             # Deployment script
├── test_failures.py      # Failure testing script
├── .gitignore           # Git ignore rules
├── .dockerignore        # Docker ignore rules
├── README.md            # Project documentation
└── logs/                # Application logs (created at runtime)
    ├── app.log
    ├── error.log
    └── ecommerce.log
```

## Environment Variables

- `FLASK_ENV`: Set to `production` for Docker deployment
- `FLASK_APP`: Set to `app.py`

## Database

The application uses SQLite with the following tables:
- `products`: Product catalog
- `orders`: Customer orders
- `order_items`: Order line items

## Error Handling

The API includes comprehensive error handling:
- Standardized error responses
- Detailed error logging
- Graceful failure recovery
- Input validation
- Database error handling

## Monitoring

- Health check endpoint for monitoring
- Performance metrics logging
- Application status tracking
- Log file monitoring

## Security Features

- Input validation
- SQL injection prevention
- Error message sanitization
- Session management
- Non-root Docker user

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 