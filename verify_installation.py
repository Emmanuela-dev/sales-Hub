"""Verify the Glamour Hub internal operations installation."""

import sys
import os

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def check_python_version():
    """Check Python version"""
    print("✓ Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} (Required: 3.9+)")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (Required: 3.9+)")
        return False

def check_required_packages():
    """Check if all required packages are installed"""
    print("✓ Checking required packages...")
    
    packages = {
        'streamlit': 'Streamlit',
        'mysql.connector': 'MySQL Connector',
        'pandas': 'Pandas',
        'plotly': 'Plotly',
        'bcrypt': 'bcrypt'
    }
    
    all_installed = True
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - NOT INSTALLED")
            all_installed = False
    
    return all_installed

def check_project_files():
    """Check if all required project files exist"""
    print("✓ Checking project files...")
    
    required_files = [
        'app.py',
        'db_connection.py',
        'auth.py',
        'sql_queries.py',
        'requirements.txt',
        'README.md',
        'database/schema.sql',
        'database/triggers.sql',
        'database/sample_data.sql',
        'pages/dashboard.py',
        'pages/sales.py',
        'pages/inventory.py',
        'pages/expenses.py',
        'pages/reports.py'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            all_exist = False
    
    return all_exist

def check_database_connection():
    """Check if database can be connected"""
    print("✓ Checking database connection...")
    
    try:
        from db_connection import DatabaseConnection
        if DatabaseConnection.test_connection():
            print("  ✅ Database connection successful")
            return True
        else:
            print("  ❌ Database connection failed")
            return False
    except Exception as e:
        print(f"  ❌ Database connection error: {e}")
        return False

def check_database_structure():
    """Check if all required tables exist"""
    print("✓ Checking database structure...")
    
    try:
        from db_connection import DatabaseConnection
        
        tables = [
            'users', 'product_categories', 'products', 'sales',
            'sale_items', 'stock_movements', 'expenses', 'staff_attendance'
        ]
        
        all_exist = True
        for table in tables:
            result = DatabaseConnection.fetch_one(
                f"SELECT 1 FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'glamour_hub' AND TABLE_NAME = '{table}'"
            )
            if result:
                print(f"  ✅ {table}")
            else:
                print(f"  ❌ {table} - MISSING")
                all_exist = False
        
        return all_exist
    except Exception as e:
        print(f"  ❌ Database check error: {e}")
        return False

def check_triggers():
    """Check if SQL triggers are installed"""
    print("✓ Checking SQL triggers...")
    
    try:
        from db_connection import DatabaseConnection
        
        result = DatabaseConnection.fetch_one(
            "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TRIGGERS WHERE TRIGGER_SCHEMA = 'glamour_hub'"
        )
        
        trigger_count = result[0] if result else 0
        
        if trigger_count >= 1:
            print(f"  ✅ {trigger_count} triggers installed")
            return True
        else:
            print(f"  ❌ Only {trigger_count} triggers found (expected: 1 or more)")
            return False
    except Exception as e:
        print(f"  ❌ Trigger check error: {e}")
        return False

def check_sample_data():
    """Check if sample data exists"""
    print("✓ Checking sample data...")
    
    try:
        from db_connection import DatabaseConnection
        
        result = DatabaseConnection.fetch_one("SELECT COUNT(*) FROM products")
        products_count = result[0] if result else 0
        
        # Check sales
        result = DatabaseConnection.fetch_one("SELECT COUNT(*) FROM sales")
        sales_count = result[0] if result else 0
        
        # Check payments
        print(f"  ✅ Products: {products_count}")
        print(f"  ✅ Sales: {sales_count}")
        
        return products_count > 0 and sales_count > 0
    except Exception as e:
        print(f"  ⚠️  Data check error: {e}")
        return False

def print_summary(results):
    """Print summary of checks"""
    print_header("VERIFICATION SUMMARY")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    
    if failed == 0:
        print("\n🎉 All checks passed! Your installation is ready.")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Login with superadmin / admin123")
        print("3. Explore the dashboard and features")
        return True
    else:
        print("\n⚠️  Some checks failed. Please review the errors above.")
        print("\nCommon fixes:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Check MySQL password in db_connection.py")
        print("3. Run database setup: mysql -u root -p < database/schema.sql")
        return False

def main():
    """Run all verification checks"""
    
    print_header("GLAMOUR HUB - INSTALLATION VERIFICATION")
    
    results = {
        'Python Version': check_python_version(),
        'Required Packages': check_required_packages(),
        'Project Files': check_project_files(),
        'Database Connection': check_database_connection(),
        'Database Structure': check_database_structure(),
        'SQL Triggers': check_triggers(),
        'Sample Data': check_sample_data()
    }
    
    success = print_summary(results)
    
    return 0 if success else 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
