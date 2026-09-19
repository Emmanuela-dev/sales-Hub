# Sales Intelligence Hub

**Professional Business Intelligence & Sales Management Platform**

A production-grade, enterprise-ready Sales Management and Financial Tracking System built with Python, MySQL, and Streamlit. Features professional analytics, real-time dashboards, and intelligent financial automation.

---

## 🎯 Features

### Core Modules
- **📊 Dashboard** - Real-time KPI metrics with professional visualizations
- **💰 Sales Management** - Create and track sales entries with branch-specific permissions
- **💳 Payment Management** - Record split payments and track collection status
- **📈 Advanced Reports** - Comprehensive analytics and business intelligence

### Key Capabilities
- ✅ Role-based access control (Super Admin, Admin, User)
- ✅ Real-time financial metrics and collections tracking
- ✅ Automated payment status updates via SQL triggers
- ✅ Branch-wise performance analytics
- ✅ Payment method breakdown and analysis
- ✅ Advanced KPI visualizations with Plotly
- ✅ Responsive professional UI with modern design
- ✅ Secure authentication with bcrypt hashing
- ✅ Multi-branch support with data isolation
- ✅ Normalized relational database schema

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python 3.9+
- **Database**: MySQL 8.0+
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly
- **Security**: bcrypt, session management
- **Authentication**: Role-based access control (RBAC)

---

## 📋 Project Structure

```
sales_intelligence_hub/
│
├── app.py                      # Main application entry point
├── db_connection.py            # Database connection & pooling
├── auth.py                     # Authentication & RBAC
├── sql_queries.py              # All SQL queries
├── requirements.txt            # Python dependencies
│
├── database/
│   ├── schema.sql              # Database schema & tables
│   ├── triggers.sql            # Automated triggers
│   └── sample_data.sql         # Demo data
│
├── pages/
│   ├── dashboard.py            # KPI Dashboard
│   ├── sales.py                # Sales Management
│   ├── payments.py             # Payment Management
│   └── reports.py              # Advanced Reports
│
└── assets/                     # Static assets (future)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### 1. Clone or Download the Project

```bash
cd "Sales Intelligence Hub"
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up MySQL Database

#### Step 1: Create Database and Tables
```bash
# Connect to MySQL
mysql -u root -p

# Run schema script
mysql -u root -p < database/schema.sql

# Run triggers script
mysql -u root -p < database/triggers.sql

# Run sample data script
mysql -u root -p < database/sample_data.sql
```

#### Step 2: Configure Database Connection
Edit `db_connection.py` and update the `DB_CONFIG` dictionary:

```python
DB_CONFIG = {
    'host': 'localhost',           # Your MySQL host
    'user': 'root',                # Your MySQL username
    'password': 'your_password',   # Your MySQL password (CHANGE THIS!)
    'database': 'sales_intelligence_hub',
    'raise_on_warnings': True,
    'autocommit': True
}
```

### 4. Run the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

---

## 🔐 Demo Credentials

After running the setup scripts, use these credentials to login:

| Username | Password | Role |
|----------|----------|------|
| superadmin | admin123 | Super Admin (full access) |
| ny_admin | admin123 | Admin (NY branch access) |
| la_admin | admin123 | Admin (LA branch access) |
| ch_admin | admin123 | Admin (Chicago branch access) |
| user1 | admin123 | User (read-only access) |

---

## 📊 Dashboard Features

### KPI Metrics (Last 30 Days)
- Total Sales amount
- Total Received amount
- Total Pending amount
- Collection Percentage

### Analytics Tabs
1. **Sales Trends** - Monthly sales and revenue visualization
2. **Branch Analytics** - Branch-wise performance comparison
3. **Payment Methods** - Revenue breakdown by payment type (Cash, UPI, Card)
4. **Status Distribution** - Open vs Partial vs Closed sales

### Supporting Tables
- Top performing branches
- Highest pending collections

---

## 💰 Sales Management

### Features
- Create new sales entries
- Capture customer details (name, phone, email)
- Assign product categories (Standard, Professional Services, Enterprise)
- Track payment status (Open, Partial, Closed)
- View and filter all sales records
- Branch-specific permissions

### Access Control
- **Super Admin**: Can view and manage all branches
- **Admin**: Can only view and manage their assigned branch
- **User**: Read-only access to branch sales

---

## 💳 Payment Management

### Record Payments
- Select open/partial sales
- Record split payments
- Support for multiple payment methods (Cash, UPI, Card)
- Transaction reference tracking
- Payment notes

### Payment Automation
- SQL triggers automatically update sale payment status
- Pending amounts calculated automatically
- Collection metrics updated in real-time
- Financial consistency maintained

### Payment History
- Filter by payment method
- Filter by date range
- Sort by amount or date
- View transaction references
- Track payment statistics

---

## 📈 Reports & Analytics

### Available Reports

1. **Revenue Analysis**
   - Total sales and received
   - Total pending amount
   - Collection rate percentage

2. **Branch Performance**
   - Sales by branch
   - Collection efficiency
   - Closing percentage
   - Average days to close

3. **Collection Efficiency**
   - Branch-wise collection metrics
   - Collection percentage
   - Average payment days

4. **Top Sales & Customers**
   - Highest value sales
   - Top customers by purchase amount
   - Purchase frequency

5. **Payment Method Analysis**
   - Revenue by payment method
   - Transaction count breakdown
   - Percentage distribution

6. **Product Category Analysis**
   - Sales by category
   - Collection rate by category
   - Category-wise revenue

7. **Overdue Collections**
   - Sales pending >30 days
   - Total overdue amount
   - Customer details

---

## 🗄️ Database Schema

### Tables

#### users
- Authentication and role management
- Stores user credentials (bcrypt hashed)
- Role-based access control

#### branches
- Store branch information
- Branch managers and contact details
- Location tracking

#### customer_sales
- Sales transactions
- Customer information
- Payment status tracking
- Generated columns for received/pending amounts

#### payment_splits
- Individual payment records
- Multiple payments per sale
- Payment method tracking
- Transaction references

### Key Features
- ✅ Primary & Foreign Keys
- ✅ Relational Integrity
- ✅ Generated Columns for auto-calculations
- ✅ SQL Triggers for automation
- ✅ Indexes for performance

---

## 🔄 SQL Triggers

### Trigger: payment_splits_after_insert
Automatically updates sale payment status and amounts when a payment is recorded.

```sql
- Recalculates total received amount
- Updates payment status (Open → Partial → Closed)
- Maintains financial consistency
```

### Trigger: payment_splits_after_update
Handles updates to existing payment records.

### Trigger: payment_splits_after_delete
Updates status when a payment is deleted.

---

## 🔒 Security Features

- **Password Hashing**: bcrypt encryption for all passwords
- **Session Management**: Secure session-based authentication
- **Role-Based Access Control**: Three-tier access system
- **Data Isolation**: Users can only see their branch data (except Super Admin)
- **SQL Injection Prevention**: Parameterized queries throughout
- **Connection Pooling**: Secure database connection management

---

## 🎨 UI/UX Design

### Design Philosophy
- **Professional**: Corporate color palette (blue, slate gray, white)
- **Minimal**: Clean layouts with subtle shadows
- **Responsive**: Fully responsive grid system
- **Accessible**: Clear typography and contrast ratios
- **Consistent**: Unified design system across all pages

### Color Palette
- Primary: #1e293b (Dark Blue)
- Secondary: #64748b (Slate Gray)
- Accent: #3b82f6 (Blue)
- Success: #10b981 (Green)
- Warning: #f59e0b (Amber)
- Danger: #ef4444 (Red)
- Light: #f8fafc (Off-White)

---

## 📊 SQL Queries (15+ Analytics)

The `sql_queries.py` module includes:

1. QUERY_TOTAL_SALES - Total sales amount
2. QUERY_TOTAL_RECEIVED - Total received payments
3. QUERY_TOTAL_PENDING - Total pending amount
4. QUERY_COLLECTION_PERCENTAGE - Collection rate %
5. QUERY_BRANCH_WISE_SALES - Sales by branch
6. QUERY_TOP_BRANCHES - Top performing branches
7. QUERY_PAYMENT_METHOD_BREAKDOWN - Payment method analysis
8. QUERY_PAYMENT_STATUS_DISTRIBUTION - Status distribution
9. QUERY_MONTHLY_SALES_TREND - Monthly trends
10. QUERY_MONTHLY_REVENUE_TREND - Revenue trends
11. QUERY_PENDING_COLLECTIONS - Pending collections analysis
12. QUERY_OVERDUE_COLLECTIONS - Overdue >30 days
13. QUERY_TOTAL_REVENUE_ANALYSIS - Revenue overview
14. QUERY_HIGHEST_SALES - Top sales records
15. QUERY_TOP_CUSTOMERS - Customer analysis
16. QUERY_OPEN_CLOSED_RATIO - Status ratio
17. QUERY_BRANCH_EFFICIENCY - Branch performance
18. QUERY_REVENUE_GROWTH - Growth analysis
19. QUERY_PRODUCT_CATEGORY_BREAKDOWN - Category analysis
20. QUERY_COLLECTION_EFFICIENCY - Collection metrics

---

## 🐛 Troubleshooting

### Database Connection Failed
1. Ensure MySQL is running: `mysql -u root -p`
2. Check credentials in `db_connection.py`
3. Verify database exists: `SHOW DATABASES;`
4. Check database contents: `USE sales_intelligence_hub; SHOW TABLES;`

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Clear cache
rm -rf __pycache__
streamlit cache clear
```

### Port Already in Use
```bash
# Run on different port
streamlit run app.py --server.port 8502
```

### MySQL Connection Issues
```bash
# Check MySQL service status
net start MySQL80

# Or verify connection
mysql -h localhost -u root -p
```

---

## 📈 Performance Optimization

- **Connection Pooling**: Reuses MySQL connections
- **Query Optimization**: Indexes on frequently used columns
- **Data Caching**: Streamlit caches visualization computations
- **Lazy Loading**: Pages load data on-demand

---

## 🔄 Workflow Example

### Complete Sales-to-Payment Flow

1. **Create Sale**
   - Navigate to Sales → Add New Sale
   - Enter customer details and sale amount
   - System creates sale record with "Open" status

2. **Payment Received**
   - Navigate to Payments → Record Payment
   - Select the sale from open sales list
   - Enter payment amount and method
   - System automatically updates sale status

3. **Track Progress**
   - Dashboard shows updated pending amount
   - Payment status changes (Open → Partial → Closed)
   - Reports reflect new financial metrics

4. **Generate Reports**
   - View collection efficiency by branch
   - Analyze payment method breakdown
   - Identify overdue collections
   - Export data for further analysis

---

## 🚀 Future Enhancements (v2.0)

- User management interface
- Email notifications for overdue collections
- PDF report export
- Data import/export functionality
- API integration with accounting software
- Mobile app version
- Advanced forecasting models
- Webhook integrations
- Custom report builder
- Bulk operations

---

## 📝 License

This project is proprietary business software. All rights reserved.

---

## 👥 Support & Maintenance

For issues, questions, or feature requests, please contact the development team.

---

## 📖 Additional Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **Plotly Documentation**: https://plotly.com/python/
- **MySQL Documentation**: https://dev.mysql.com/doc/
- **bcrypt Documentation**: https://github.com/pyca/bcrypt

---

**Built with ❤️ for modern business intelligence.**

Sales Intelligence Hub v1.0 © 2026
