# Sales Intelligence Hub - Configuration Guide

## ⚙️ Configuration Setup

### Step 1: MySQL Database Configuration

Edit the `DB_CONFIG` in `db_connection.py`:

```python
DB_CONFIG = {
    'host': 'localhost',                    # MySQL server hostname
    'user': 'root',                         # MySQL username
    'password': 'your_password',            # MySQL password - CHANGE THIS!
    'database': 'sales_intelligence_hub',   # Database name
    'raise_on_warnings': True,              # Show SQL warnings
    'autocommit': True                      # Auto-commit transactions
}
```

### Step 2: Environment Variables (Optional)

Create a `.env` file in the project root for sensitive credentials:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_secure_password
DB_NAME=sales_intelligence_hub
DB_PORT=3306

STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
```

Then update `db_connection.py` to use environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'sales_intelligence_hub'),
    'raise_on_warnings': True,
    'autocommit': True
}
```

### Step 3: MySQL Setup

#### Option A: Using Command Line

```bash
# Connect to MySQL
mysql -u root -p

# Within MySQL CLI, run:
SOURCE database/schema.sql
SOURCE database/triggers.sql
SOURCE database/sample_data.sql
```

#### Option B: Using Individual Commands

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/triggers.sql
mysql -u root -p < database/sample_data.sql
```

#### Option C: Using MySQL Workbench
1. Open MySQL Workbench
2. Create new query tab
3. Open and run each SQL file sequentially

### Step 4: Verify Installation

Check that everything is installed correctly:

```bash
# Check Python version
python --version
# Should be 3.9 or higher

# Check pip packages
pip list | grep streamlit
pip list | grep mysql-connector

# Test database connection
python -c "from db_connection import DatabaseConnection; print(DatabaseConnection.test_connection())"
# Should print: True
```

## 🔐 Security Best Practices

### Password Management
1. **Never commit passwords** to version control
2. **Use environment variables** for sensitive data
3. **Use strong passwords** for MySQL user
4. **Change default demo passwords** in production

### User Management
1. Create individual MySQL accounts for different environments
2. Use restricted permissions for production users
3. Rotate authentication tokens regularly
4. Enable MySQL audit logging

### Database Security
1. **Enable SSL** for MySQL connections:
   ```python
   DB_CONFIG = {
       ...
       'ssl_disabled': False,
       'ssl_ca': '/path/to/ca.pem',
       'ssl_cert': '/path/to/client-cert.pem',
       'ssl_key': '/path/to/client-key.pem'
   }
   ```

2. **Restrict access** to database server
3. **Regular backups** and testing restore procedures
4. **Monitor** database access logs

## 📊 Database Maintenance

### Regular Backups

```bash
# Weekly backup
mysqldump -u root -p sales_intelligence_hub > backup_$(date +%Y%m%d).sql

# Restore from backup
mysql -u root -p sales_intelligence_hub < backup_20260115.sql
```

### Performance Optimization

```sql
-- Analyze tables for query optimization
ANALYZE TABLE users;
ANALYZE TABLE branches;
ANALYZE TABLE customer_sales;
ANALYZE TABLE payment_splits;

-- Check table status
SHOW TABLE STATUS FROM sales_intelligence_hub;
```

### Monitor Database

```sql
-- Check current connections
SHOW PROCESSLIST;

-- Monitor slow queries
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

## 🚀 Deployment Configuration

### Development
```python
ENVIRONMENT = 'development'
DEBUG = True
SQLALCHEMY_ECHO = True
```

### Production
```python
ENVIRONMENT = 'production'
DEBUG = False
SQLALCHEMY_ECHO = False
CACHE_ENABLED = True
```

### Streamlit Configuration (`.streamlit/config.toml`)

```toml
[theme]
primaryColor = "#3b82f6"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8fafc"
textColor = "#1e293b"
font = "sans serif"

[server]
port = 8501
headless = true
runOnSave = true

[client]
toolbarMode = "minimal"
showErrorDetails = false

[logger]
level = "info"
```

## 🔄 Connection Pooling

The application uses MySQL connection pooling for better performance:

```python
# Pool configuration in db_connection.py
pool_name="sales_hub_pool"
pool_size=5              # Number of connections
pool_reset_session=True  # Reset session before reuse
```

Adjust based on expected concurrent users:
- Small deployment (< 10 users): pool_size = 5
- Medium deployment (10-50 users): pool_size = 10
- Large deployment (> 50 users): pool_size = 20

## 📝 Logging

Enable application logging for monitoring:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
```

## 🧪 Testing Configuration

### Unit Tests
```bash
pytest tests/ -v
```

### Integration Tests
```bash
pytest tests/integration/ -v --cov
```

### Load Testing
```bash
locust -f loadtest.py --host=http://localhost:8501
```

## 📦 Docker Deployment (Optional)

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      DB_HOST: mysql
      DB_USER: root
      DB_PASSWORD: ${DB_PASSWORD}
    depends_on:
      - mysql
  
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/schema.sql:/docker-entrypoint-initdb.d/schema.sql

volumes:
  mysql_data:
```

## ✅ Checklist

Before deploying to production:

- [ ] MySQL database created and populated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Database connection tested
- [ ] Environment variables configured
- [ ] All SQL triggers verified
- [ ] Sample data loaded
- [ ] Login credentials changed from demo defaults
- [ ] SSL certificates configured (if using remote MySQL)
- [ ] Backup procedures tested
- [ ] Monitoring and logging configured
- [ ] User roles and permissions verified
- [ ] Performance tuning completed

## 🆘 Troubleshooting

### Issue: "Access denied for user 'root'@'localhost'"
**Solution**: Check MySQL password in DB_CONFIG matches your MySQL setup

### Issue: "Database 'sales_intelligence_hub' doesn't exist"
**Solution**: Run database setup scripts: `SOURCE database/schema.sql`

### Issue: "Connection pool exhausted"
**Solution**: Increase pool_size in db_connection.py

### Issue: "Trigger doesn't exist"
**Solution**: Run triggers setup: `SOURCE database/triggers.sql`

---

For more information, see README.md
