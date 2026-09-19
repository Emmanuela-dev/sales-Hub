# 🚀 Quick Start Guide

Get the Sales Intelligence Hub running in 5 minutes!

## Prerequisites

- ✅ Python 3.9 or higher installed
- ✅ MySQL 8.0 or higher running locally
- ✅ Git (or download as ZIP)

## Step 1: Install Python Dependencies (1 minute)

```bash
# Navigate to project directory
cd "Sales Intelligence Hub"

# Install all required packages
pip install -r requirements.txt
```

**Expected output**: Successfully installed all packages without errors

## Step 2: Set Up MySQL Database (2 minutes)

### For Windows Users:

```bash
# Option 1: Using Command Prompt
mysql -u root -p < database\schema.sql
mysql -u root -p < database\triggers.sql
mysql -u root -p < database\sample_data.sql

# When prompted for password, enter your MySQL root password
```

### For Mac/Linux Users:

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/triggers.sql
mysql -u root -p < database/sample_data.sql
```

**Expected output**: No errors, all commands complete

### Verify Database Setup:

```bash
# Connect to MySQL
mysql -u root -p

# In MySQL, type:
USE sales_intelligence_hub;
SHOW TABLES;

# You should see 4 tables:
# - users
# - branches  
# - customer_sales
# - payment_splits

EXIT;
```

## Step 3: Configure Database Connection (1 minute)

Edit `db_connection.py` and update the `DB_CONFIG`:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_MYSQL_PASSWORD',  # ← CHANGE THIS!
    'database': 'sales_intelligence_hub',
    'raise_on_warnings': True,
    'autocommit': True
}
```

Replace `YOUR_MYSQL_PASSWORD` with your actual MySQL root password.

## Step 4: Run the Application (1 minute)

```bash
streamlit run app.py
```

**Expected output**:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

The app will automatically open in your default browser!

## Step 5: Login and Explore

Use these credentials to login:

### Super Admin (Full Access)
- **Username**: `superadmin`
- **Password**: `admin123`

### Branch Admin (NY Branch)
- **Username**: `ny_admin`  
- **Password**: `admin123`

### First Time Steps:
1. Login with superadmin credentials
2. Browse the Dashboard to see KPI metrics
3. Go to Sales → View Sales to see sample data
4. Check Payments → Payment History
5. Explore Reports for analytics

---

## ✅ You're Done! 

Your Sales Intelligence Hub is now running! 🎉

### What's Next?

- 📊 **Explore Dashboard**: View real-time metrics
- 💰 **Add Sales**: Try creating a new sale
- 💳 **Record Payments**: Record a payment and watch status update
- 📈 **View Reports**: See advanced analytics
- 🔧 **Customize**: Modify colors in app.py or add branches

---

## 🆘 Quick Troubleshooting

### Problem: "Access denied for user 'root'@'localhost'"
```bash
# Check MySQL password is correct in db_connection.py
# Re-enter password when running SQL scripts
```

### Problem: "Database doesn't exist"
```bash
# Run schema setup again
mysql -u root -p < database/schema.sql
```

### Problem: "Streamlit port already in use"
```bash
# Run on different port
streamlit run app.py --server.port 8502
```

### Problem: "Module not found"
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

---

## 📚 Full Documentation

- 📖 [README.md](README.md) - Complete project overview
- ⚙️ [CONFIG.md](CONFIG.md) - Advanced configuration
- 🗄️ [database/schema.sql](database/schema.sql) - Database structure
- 🔄 [database/triggers.sql](database/triggers.sql) - Automation triggers

---

## 🎯 Demo Data Included

The sample data includes:
- 6 branches (NY, LA, Chicago, Boston, San Francisco, Miami)
- 29 sales transactions
- 24 payment records
- 3 months of historical data

Perfect for exploring all features!

---

**Questions?** Check the README.md or CONFIG.md files for more details.

Happy analyzing! 📊
