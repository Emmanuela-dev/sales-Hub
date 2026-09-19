# Sales Intelligence Hub - Technical Architecture

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        STREAMLIT UI LAYER                        │
│  (Pages: Dashboard, Sales, Payments, Reports, Authentication)   │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────────────┐
│                    APPLICATION LOGIC LAYER                       │
│  ├─ auth.py (Authentication & RBAC)                              │
│  ├─ db_connection.py (Connection pooling)                        │
│  ├─ sql_queries.py (Query definitions)                           │
│  └─ pages/* (Feature modules)                                    │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────────────┐
│                     DATA ACCESS LAYER                            │
│  Connection pooling, Query execution, Result mapping             │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────────────┐
│                      MYSQL DATABASE                              │
│  ├─ users (Authentication)                                       │
│  ├─ branches (Organization)                                      │
│  ├─ customer_sales (Transactions)                                │
│  └─ payment_splits (Payments)                                    │
│  ├─ Triggers (Automation)                                        │
│  └─ Indexes (Performance)                                        │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Component Architecture

### 1. Authentication & Authorization (auth.py)

**Responsibilities:**
- User authentication against database
- Password hashing using bcrypt
- Session management
- Role-based access control

**Key Classes:**
```
AuthenticationManager
├─ authenticate_user()
├─ login()
├─ logout()
├─ is_logged_in()
├─ require_role()
└─ apply_branch_filter()
```

**Security Features:**
- Bcrypt password hashing (cost factor: 12)
- Secure session storage in st.session_state
- Login time tracking
- Timeout handling (future enhancement)

### 2. Database Connection (db_connection.py)

**Responsibilities:**
- MySQL connection pooling
- Query execution
- Result mapping
- Error handling

**Key Classes:**
```
DatabaseConnection
├─ initialize_pool()        # Create connection pool
├─ get_connection()         # Get from pool
├─ execute_query()          # INSERT, UPDATE, DELETE
├─ fetch_query()            # SELECT (multiple rows)
├─ fetch_dataframe()        # SELECT as DataFrame
├─ fetch_one()              # SELECT (single row)
└─ test_connection()        # Connection verification
```

**Performance Features:**
- Connection pooling (size: 5 default)
- Session reset between requests
- Parameterized queries (SQL injection prevention)
- Automatic connection closure

### 3. SQL Queries (sql_queries.py)

**Organization:**
```
SQL Queries Module
├─ Dashboard Queries (5)
├─ Branch Analytics (3)
├─ Payment Analysis (3)
├─ Sales Status (2)
├─ Trends (2)
├─ Collections (3)
├─ Revenue Analysis (3)
├─ Customer Insights (3)
├─ Category Analysis (2)
├─ Performance Metrics (3)
└─ User/Insert/Update (8)
```

**Query Types:**
- Aggregate queries (SUM, COUNT, AVG)
- Trend queries (Monthly, yearly)
- Filter queries (By branch, date range)
- Window functions (LAG, ROW_NUMBER)

## 📊 Data Model

### Entity Relationship Diagram

```
users
├─ PK: user_id
├─ FK: branch_id → branches
├─ Role-based access
└─ Password hash storage

branches
├─ PK: branch_id
├─ Unique: branch_code
├─ Location info
└─ Contact details

customer_sales
├─ PK: sale_id
├─ FK: branch_id → branches
├─ Generated: received_amount
├─ Generated: pending_amount
├─ Status: Open/Partial/Closed
└─ Indexed: branch_id, sale_date, payment_status

payment_splits
├─ PK: payment_id
├─ FK: sale_id → customer_sales
├─ FK: branch_id → branches
├─ Payment method enum
└─ Indexed: sale_id, branch_id, payment_date
```

### Database Normalization

**Level 3NF (Third Normal Form)**
- No redundant data
- All non-key columns depend on primary key
- No transitive dependencies
- Foreign key relationships enforce referential integrity

## 🔄 Workflow Patterns

### Authentication Flow

```
User Input (Login)
    ↓
Validate Credentials
    ↓
Query Database
    ↓
Verify Password (bcrypt)
    ↓
Create Session
    ↓
Grant Access
```

### Sales Creation Flow

```
User Form Input
    ↓
Validate Input
    ↓
Check Permissions (Branch filter)
    ↓
INSERT into customer_sales
    ↓
Set Status = 'Open'
    ↓
Success Notification
```

### Payment Recording Flow

```
User Selects Sale
    ↓
Validate Payment Amount
    ↓
INSERT into payment_splits
    ↓
TRIGGER: payment_splits_after_insert
    ├─ Calculate total_received
    ├─ Update pending_amount
    ├─ Determine new status
    └─ UPDATE customer_sales
    ↓
Success Notification
```

## 🎨 UI/UX Architecture

### Page Structure

Each page follows this structure:

```
Page Module (e.g., dashboard.py)
├─ Authentication check
├─ Apply styling
├─ Render header
├─ Fetch data
├─ Render components
│  ├─ Metric cards
│  ├─ Charts
│  ├─ Tables
│  └─ Forms
└─ Error handling
```

### Component Hierarchy

```
Streamlit App
├─ Sidebar (Navigation + User Info)
├─ Main Content Area
│  ├─ Page Header (Title + Description)
│  ├─ Filters (Optional)
│  ├─ Tabs or Sections
│  │  ├─ Cards/Metrics
│  │  ├─ Charts (Plotly)
│  │  ├─ Tables (DataFrames)
│  │  └─ Forms
│  └─ Footer Info
└─ CSS Styling
```

## 🚀 Performance Optimization

### Database Level

1. **Indexes**
   ```sql
   -- Primary key indexes (automatic)
   -- Foreign key indexes (automatic)
   -- Search indexes:
   CREATE INDEX idx_username ON users(username);
   CREATE INDEX idx_branch_code ON branches(branch_code);
   CREATE INDEX idx_cs_branch_date ON customer_sales(branch_id, sale_date);
   CREATE INDEX idx_ps_branch_date ON payment_splits(branch_id, payment_date);
   ```

2. **Query Optimization**
   - Use SELECT * only when necessary
   - Filter early (WHERE clause)
   - Use LIMIT for large results
   - Aggregate at database level

3. **Connection Pooling**
   - Reduces connection overhead
   - Maintains session state
   - Configurable pool size

### Application Level

1. **Streamlit Caching**
   ```python
   @st.cache_data
   def get_expensive_data():
       return fetch_dataframe(query)
   ```

2. **Lazy Loading**
   - Load data only when accessed
   - Progressive refinement
   - On-demand calculations

3. **Data Filtering**
   - Filter early in queries
   - Reduce dataset size
   - Minimize memory usage

## 🔒 Security Architecture

### Authentication

- **Password Storage**: bcrypt with cost factor 12
- **Session Management**: Streamlit session state
- **Timeout**: 24 hours (future enhancement)

### Authorization

- **Role-Based Access Control (RBAC)**
  - Super Admin: Full system access
  - Admin: Branch-level access
  - User: Read-only access

- **Data Isolation**
  - Users see only their branch data
  - Enforced at query level
  - Query parameters validated

### Data Protection

- **SQL Injection Prevention**
  - Parameterized queries only
  - Type-safe parameter binding

- **Encryption**
  - HTTPS recommended for production
  - SSL for database connections

## 🧪 Testing Strategy

### Unit Tests
```python
test_authentication.py
├─ test_password_hashing()
├─ test_login_valid()
├─ test_login_invalid()
└─ test_role_permissions()

test_database.py
├─ test_connection()
├─ test_query_execution()
└─ test_connection_pool()
```

### Integration Tests
```python
test_sales_workflow.py
├─ test_create_sale()
├─ test_record_payment()
└─ test_status_updates()
```

### UI Tests
```python
test_ui.py
├─ test_dashboard_loads()
├─ test_form_validation()
└─ test_navigation()
```

## 📈 Scalability Considerations

### Current Configuration
- Pool size: 5 connections
- Suitable for: < 20 concurrent users

### Scaling Strategies

1. **Database Level**
   - Increase connection pool size
   - Add read replicas
   - Implement caching (Redis)
   - Archive old data

2. **Application Level**
   - Load balancing
   - Multi-instance deployment
   - Async processing
   - Queue systems (Celery)

3. **Infrastructure**
   - Container deployment (Docker)
   - Kubernetes orchestration
   - CDN for static assets
   - Monitoring & logging

## 🔄 Deployment Options

### Local Development
```bash
streamlit run app.py
# http://localhost:8501
```

### Docker Container
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py"]
```

### Cloud Deployment
- **Streamlit Cloud**: Minimal setup
- **AWS EC2**: Full control
- **Heroku**: Simplified deployment
- **Google Cloud Run**: Serverless option

## 📋 Code Quality Standards

### Style Guide
- PEP 8 compliance
- 80-character line length (soft limit)
- Type hints for critical functions
- Comprehensive docstrings

### Documentation
- Module-level docstrings
- Function-level docstrings
- Inline comments for complex logic
- README and architecture docs

### Version Control
- Meaningful commit messages
- .gitignore for sensitive files
- Feature branches
- Pull request reviews

## 🛠️ Maintenance & Monitoring

### Logging
```python
import logging
logger = logging.getLogger(__name__)
logger.info("User login: %s", username)
```

### Monitoring Metrics
- Response time
- Database query performance
- Error rates
- User activity
- Storage usage

### Backup Strategy
```bash
# Daily backup
mysqldump -u root -p sales_intelligence_hub > backup_$(date +%Y%m%d).sql

# Monthly archival
aws s3 cp backup_*.sql s3://backups/
```

---

## 📚 Technology Stack Details

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Frontend | Streamlit | 1.28.1 | Web UI framework |
| Backend | Python | 3.9+ | Application logic |
| Database | MySQL | 8.0+ | Data persistence |
| ORM/Query | mysql-connector | 8.2.0 | Database driver |
| Data Processing | Pandas | 2.1.3 | Data manipulation |
| Visualization | Plotly | 5.17.0 | Interactive charts |
| Security | bcrypt | 4.1.2 | Password hashing |

---

**Last Updated**: 2026
**Architecture Version**: 1.0
