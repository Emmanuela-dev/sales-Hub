"""
Database Connection Module
Handles MySQL database connectivity with connection pooling and error handling
"""

import os
import mysql.connector
from mysql.connector import Error, pooling
import streamlit as st
from typing import Optional, List, Tuple, Dict
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'Emmanuela@20'),
    'database': os.getenv('DB_NAME', 'glamour_hub'),
    'raise_on_warnings': False,
    'autocommit': True
}



class DatabaseConnection:
    """
    Manages MySQL database connections with connection pooling
    Provides methods for executing queries and retrieving data
    """
    
    _pool = None
    
    @staticmethod
    def initialize_pool(config: Dict = None) -> None:
        """Initialize connection pool"""
        if DatabaseConnection._pool is None:
            try:
                cfg = config or DB_CONFIG
                DatabaseConnection._pool = pooling.MySQLConnectionPool(
                    pool_name="sales_hub_pool",
                    pool_size=5,
                    pool_reset_session=True,
                    **cfg
                )
                st.success("✓ Database connection pool initialized")
            except Error as err:
                st.error(f"Error initializing connection pool: {err}")
                raise
    
    @staticmethod
    def get_connection():
        """Get connection from pool"""
        try:
            if DatabaseConnection._pool is None:
                DatabaseConnection.initialize_pool()
            return DatabaseConnection._pool.get_connection()
        except Error as err:
            st.error(f"Error getting connection: {err}")
            return None
    
    @staticmethod
    def execute_query(query: str, params: Tuple = None) -> bool:
        """
        Execute INSERT, UPDATE, DELETE queries
        
        Args:
            query: SQL query to execute
            params: Query parameters for parameterized queries
            
        Returns:
            bool: True if successful, False otherwise
        """
        connection = None
        cursor = None
        try:
            connection = DatabaseConnection.get_connection()
            if not connection:
                st.error("Failed to establish database connection")
                return False
            
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            connection.commit()
            return True
            
        except Error as err:
            st.error(f"Database error: {err}")
            if connection:
                connection.rollback()
            return False
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @staticmethod
    def fetch_query(query: str, params: Tuple = None) -> Optional[List[Tuple]]:
        """
        Execute SELECT query and return all results
        
        Args:
            query: SQL SELECT query
            params: Query parameters
            
        Returns:
            List of tuples or None if error
        """
        connection = None
        cursor = None
        try:
            connection = DatabaseConnection.get_connection()
            if not connection:
                return None
            
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            return cursor.fetchall()
            
        except Error as err:
            st.error(f"Database error: {err}")
            return None
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @staticmethod
    def fetch_dataframe(query: str, params: Tuple = None) -> Optional[pd.DataFrame]:
        """
        Execute SELECT query and return as pandas DataFrame
        
        Args:
            query: SQL SELECT query
            params: Query parameters
            
        Returns:
            DataFrame or None if error
        """
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            if not connection:
                return None
            
            df = pd.read_sql(query, connection, params=params)
            return df
            
        except Error as err:
            st.error(f"Database error: {err}")
            return None
            
        finally:
            if connection:
                connection.close()
    
    @staticmethod
    def fetch_one(query: str, params: Tuple = None) -> Optional[Tuple]:
        """
        Execute SELECT query and return single result
        
        Args:
            query: SQL SELECT query
            params: Query parameters
            
        Returns:
            Single tuple or None
        """
        connection = None
        cursor = None
        try:
            connection = DatabaseConnection.get_connection()
            if not connection:
                return None
            
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            return cursor.fetchone()
            
        except Error as err:
            st.error(f"Database error: {err}")
            return None
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @staticmethod
    def test_connection() -> bool:
        """
        Test database connection
        
        Returns:
            bool: True if connection successful
        """
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            if connection and connection.is_connected():
                db_info = connection.get_server_info()
                return True
            return False
        except Error as err:
            st.error(f"Connection test failed: {err}")
            return False
        finally:
            if connection and connection.is_connected():
                connection.close()


def verify_db_connection():
    """
    Verify database connection on app startup
    Displays error message if connection fails
    """
    if not DatabaseConnection.test_connection():
        st.error("""
        ❌ **Database Connection Failed**
        
        Please ensure:
        1. MySQL server is running
        2. Database credentials in `db_connection.py` are correct
        3. Database `sales_intelligence_hub` exists
        4. Run the SQL scripts in `/database/` folder first:
           - schema.sql
           - triggers.sql
           - sample_data.sql
        """)
        st.stop()
