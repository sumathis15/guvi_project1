#!/usr/bin/env python3
"""
Database Export Script - Backup Current Working Database
Exports all tables with data to SQL dump file
"""

import mysql.connector
from config import DB_CONFIG
import os
from datetime import datetime

def export_database():
    """Export entire database to SQL dump file"""
    print("EXPORTING DATABASE")
    print("=" * 50)
    
    try:
        # Connect to database
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Get database name
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        print(f"Database: {db_name}")
        
        # Create export filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = f"cricket_database_backup_{timestamp}.sql"
        
        print(f"Export file: {export_file}")
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"Tables to export: {len(tables)}")
        
        with open(export_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("-- Cricket Analytics Database Backup\n")
            f.write(f"-- Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Database: {db_name}\n")
            f.write("-- Contains all working data for 23/25 SQL queries\n\n")
            
            # Disable foreign key checks
            f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")
            
            for table in tables:
                print(f"Exporting table: {table}")
                
                # Drop table if exists
                f.write(f"DROP TABLE IF EXISTS `{table}`;\n")
                
                # Get table structure
                cursor.execute(f"SHOW CREATE TABLE `{table}`")
                create_table = cursor.fetchone()[1]
                f.write(f"{create_table};\n\n")
                
                # Get table data
                cursor.execute(f"SELECT * FROM `{table}`")
                rows = cursor.fetchall()
                
                if rows:
                    # Get column names
                    cursor.execute(f"DESCRIBE `{table}`")
                    columns = [col[0] for col in cursor.fetchall()]
                    
                    # Write INSERT statements
                    for row in rows:
                        values = []
                        for value in row:
                            if value is None:
                                values.append('NULL')
                            elif isinstance(value, str):
                                # Escape single quotes
                                escaped = value.replace("'", "\\'")
                                values.append(f"'{escaped}'")
                            else:
                                values.append(str(value))
                        
                        f.write(f"INSERT INTO `{table}` (`{'`, `'.join(columns)}`) VALUES ({', '.join(values)});\n")
                    
                    f.write(f"\n-- {len(rows)} rows exported from {table}\n\n")
                else:
                    f.write(f"-- No data in {table}\n\n")
            
            # Re-enable foreign key checks
            f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
        
        cursor.close()
        connection.close()
        
        print(f"Database exported successfully!")
        print(f"File: {export_file}")
        print(f"Size: {os.path.getsize(export_file) / 1024:.1f} KB")
        
        return export_file
        
    except Exception as e:
        print(f"Export failed: {str(e)}")
        return None

if __name__ == "__main__":
    export_database()
