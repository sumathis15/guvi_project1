#!/usr/bin/env python3
"""
Database Import Script - Setup Database on New Device
Clears existing database and imports from backup file
"""

import mysql.connector
from config import DB_CONFIG
import os
import sys

def import_database(backup_file):
    """Import database from SQL backup file"""
    print("IMPORTING DATABASE")
    print("=" * 50)
    
    if not os.path.exists(backup_file):
        print(f"Backup file not found: {backup_file}")
        return False
    
    try:
        # Connect to database
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print(f"Importing from: {backup_file}")
        print(f"File size: {os.path.getsize(backup_file) / 1024:.1f} KB")
        
        # Read and execute SQL file
        with open(backup_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        print(f"Executing {len(statements)} SQL statements...")
        
        for i, statement in enumerate(statements):
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    if i % 10 == 0:  # Progress every 10 statements
                        print(f"Progress: {i}/{len(statements)} statements")
                except Exception as e:
                    print(f"Warning: {str(e)}")
                    continue
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("Database imported successfully!")
        print("Ready to run the application!")
        
        return True
        
    except Exception as e:
        print(f"Import failed: {str(e)}")
        return False

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python import_database.py <backup_file.sql>")
        print("Example: python import_database.py cricket_database_backup_20250101_120000.sql")
        return
    
    backup_file = sys.argv[1]
    import_database(backup_file)

if __name__ == "__main__":
    main()
