#!/usr/bin/env python3
"""
Database URL validation script for CortexAI
Tests different database configurations and validates connections
"""

import os
import sys
from dotenv import load_dotenv

def validate_database_url(db_url=None):
    """Validate a database URL and test connection"""
    
    if not db_url:
        load_dotenv()
        db_url = os.getenv('DATABASE_URL')
    
    print("🔍 Database URL Validation")
    print("=" * 40)
    
    if not db_url:
        print("❌ No DATABASE_URL found")
        print("\n📝 To set a DATABASE_URL, add it to your .env file:")
        print("   DATABASE_URL=postgresql://user:pass@host:5432/db")
        print("   DATABASE_URL=sqlite:///./conversations.db")
        return False
    
    print(f"📋 DATABASE_URL: {db_url}")
    print()
    
    # Parse URL
    try:
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        print(f"🔧 Protocol: {parsed.scheme}")
        print(f"🔧 Host: {parsed.hostname}")
        print(f"🔧 Port: {parsed.port}")
        print(f"🔧 Database: {parsed.path[1:] if parsed.path else 'N/A'}")
        print(f"🔧 Username: {parsed.username}")
        print()
    except Exception as e:
        print(f"❌ URL parsing error: {e}")
        return False
    
    # Test connection based on type
    if parsed.scheme == 'sqlite':
        return test_sqlite(db_url)
    elif parsed.scheme == 'postgresql':
        return test_postgresql(db_url)
    else:
        print(f"❌ Unsupported database type: {parsed.scheme}")
        print("   Supported types: sqlite, postgresql")
        return False

def test_sqlite(db_url):
    """Test SQLite connection"""
    print("🗄️  Testing SQLite connection...")
    
    try:
        import sqlite3
        from pathlib import Path
        
        # Extract file path from URL
        db_path = db_url.replace('sqlite:///', '')
        if db_path.startswith('./'):
            db_path = db_path[2:]
        
        # Create directory if it doesn't exist
        db_dir = Path(db_path).parent
        if not db_dir.exists():
            db_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {db_dir}")
        
        # Test connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        
        print("✅ SQLite connection successful!")
        print(f"📁 Database file: {db_path}")
        return True
        
    except Exception as e:
        print(f"❌ SQLite connection failed: {e}")
        return False

def test_postgresql(db_url):
    """Test PostgreSQL connection"""
    print("🐘 Testing PostgreSQL connection...")
    
    try:
        import psycopg
        
        # Test basic connection with GSSAPI disabled
        conn = psycopg.connect(db_url, gssencmode='disable')
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        
        print("✅ PostgreSQL connection successful!")
        
        # Test PostgresSaver setup
        print("🔧 Testing PostgresSaver setup...")
        try:
            from langgraph.checkpoint.postgres import PostgresSaver
            
            with PostgresSaver.from_conn_string(db_url) as checkpointer:
                checkpointer.setup()
                print("✅ PostgresSaver setup successful!")
                
        except Exception as e:
            print(f"⚠️  PostgresSaver setup warning: {e}")
            print("   This might be normal for some connection poolers")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ PostgreSQL connection failed: {error_msg}")
        
        # Handle specific GSSAPI error
        if "used_gssapi" in error_msg:
            print("\n🔧 This is a known psycopg issue. The connection might still work.")
            print("   CortexAI handles this automatically in production.")
            print("   Let's test with CortexAI directly...")
            return "gssapi_warning"
        
        print("\n🔧 Troubleshooting tips:")
        print("   - Check if the database server is running")
        print("   - Verify username, password, host, and port")
        print("   - Ensure the database exists")
        print("   - Check firewall settings")
        return False

def test_cortex_integration(db_url):
    """Test CortexAI integration with the database"""
    print("\n🧪 Testing CortexAI integration...")
    
    try:
        from cortex import Client
        
        # Initialize client with database
        api = Client(db_url=db_url)
        print("✅ CortexAI client initialized with database")
        
        # Test a simple operation
        response = api.create(
            input="Test message for database validation",
            model="gpt-4o-mini",
            store=True,
            temperature=0.1
        )
        
        print("✅ CortexAI database integration successful!")
        print(f"📝 Test response ID: {response['id']}")
        return True
        
    except Exception as e:
        print(f"❌ CortexAI integration failed: {e}")
        return False

def main():
    """Main validation function"""
    
    # Check command line arguments
    if len(sys.argv) > 1:
        db_url = sys.argv[1]
        print(f"🔍 Validating provided URL: {db_url}")
    else:
        db_url = None
    
    # Validate the database URL
    result = validate_database_url(db_url)
    if result == True:
        print("\n🎉 Database validation successful!")
        
        # Test CortexAI integration
        if test_cortex_integration(db_url):
            print("\n✅ Everything is working correctly!")
        else:
            print("\n⚠️  Database works but CortexAI integration has issues")
    elif result == "gssapi_warning":
        print("\n⚠️  GSSAPI warning detected - testing CortexAI integration directly...")
        
        # Test CortexAI integration despite GSSAPI warning
        if test_cortex_integration(db_url):
            print("\n✅ CortexAI integration successful despite GSSAPI warning!")
            print("   This is normal - CortexAI handles GSSAPI issues automatically.")
        else:
            print("\n❌ CortexAI integration failed")
    else:
        print("\n❌ Database validation failed")
        print("\n💡 Common DATABASE_URL formats:")
        print("   SQLite: sqlite:///./conversations.db")
        print("   PostgreSQL: postgresql://user:pass@localhost:5432/dbname")
        print("   Supabase: postgresql://user:pass@host:6543/postgres")

if __name__ == "__main__":
    main()
