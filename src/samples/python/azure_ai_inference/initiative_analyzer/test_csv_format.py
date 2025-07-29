#!/usr/bin/env python3
"""Test script to check CSV format compatibility."""

import csv
import sys
from pathlib import Path

def check_csv_format(file_path):
    """Check if CSV has required columns."""
    required_columns = ['category', 'title', 'goal', 'stream']
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            
            print(f"📁 File: {file_path}")
            print(f"📋 Headers found: {list(headers)}")
            print(f"📏 Number of columns: {len(headers)}")
            
            missing_columns = [col for col in required_columns if col not in headers]
            
            if missing_columns:
                print(f"❌ Missing required columns: {missing_columns}")
                return False
            else:
                print("✅ All required columns present")
                
                # Count rows
                row_count = sum(1 for row in reader)
                print(f"📊 Number of data rows: {row_count}")
                return True
                
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing CSV Format Compatibility\n")
    
    # Test sample file
    sample_file = "sample_backlog.csv"
    print("Testing sample file:")
    check_csv_format(sample_file)
    
    print("\n" + "="*50 + "\n")
    
    # Test user's file if provided
    user_file = "D:\\initiative_analyzer\\backlog.csv"
    if Path(user_file).exists():
        print("Testing user's backlog.csv file:")
        check_csv_format(user_file)
    else:
        print(f"User file not found: {user_file}")
