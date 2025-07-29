#!/usr/bin/env python3
"""
Test script to validate core functionality of the initiative analyzer
without requiring Azure dependencies.
"""

import csv
import sys
from pathlib import Path

def test_csv_loading():
    """Test loading CSV files."""
    print("Testing CSV file loading...")
    
    # Test backlog loading
    try:
        with open('sample_backlog.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            backlog_items = list(reader)
            print(f"✅ Loaded {len(backlog_items)} backlog items")
            for item in backlog_items:
                print(f"   - {item['title']} ({item['category']})")
    except Exception as e:
        print(f"❌ Error loading backlog: {e}")
        return False
    
    # Test initiatives loading
    try:
        with open('sample_initiatives.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            initiatives = list(reader)
            print(f"✅ Loaded {len(initiatives)} initiatives")
            for initiative in initiatives:
                print(f"   - {initiative['title']} ({initiative['area']})")
    except Exception as e:
        print(f"❌ Error loading initiatives: {e}")
        return False
    
    return True

def test_file_structure():
    """Test that required files and directories exist."""
    print("\nTesting file structure...")
    
    required_files = [
        'sample_backlog.csv',
        'sample_initiatives.csv',
        'initiative_analyzer.py',
        'tools/initiative_associator.py',
        'tools/__init__.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def test_output_directory_creation():
    """Test creating output directory."""
    print("\nTesting output directory creation...")
    
    try:
        output_dir = Path("test_output")
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Output directory created: {output_dir.absolute()}")
        return True
    except Exception as e:
        print(f"❌ Error creating output directory: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Running Initiative Analyzer Core Functionality Tests\n")
    
    tests = [
        ("File Structure", test_file_structure),
        ("CSV Loading", test_csv_loading),
        ("Output Directory Creation", test_output_directory_creation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
    print("TEST RESULTS:")
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All core functionality tests passed!")
        print("The CSV files and basic structure are ready for the initiative analyzer.")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
