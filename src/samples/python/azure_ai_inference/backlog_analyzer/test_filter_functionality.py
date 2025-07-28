#!/usr/bin/env python3
"""
Test the new --filter-title functionality in backlog_analyzer.py and backlog_analyzer_demo.py
"""

import subprocess
import os
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"\n🧪 {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print(f"✅ Success")
            # Show filtered output for clarity
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if any(keyword in line for keyword in ['Applied title filter', 'items match', 'Successfully matched', 'Match rate']):
                    print(f"   {line}")
            return True
        else:
            print(f"❌ Failed (exit code: {result.returncode})")
            print(f"   Error: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def main():
    """Test the filter-title functionality."""
    print("🔍 Testing --filter-title functionality")
    print("=" * 60)
    
    # Change to the backlog analyzer directory
    backlog_dir = Path(__file__).parent
    os.chdir(backlog_dir)
    
    tests = [
        {
            "command": 'python backlog_analyzer_demo.py --enrich --backlog sample_backlog.csv --initiatives sample_initiatives.csv --output test1.csv --filter-title ".*onboard.*"',
            "description": "Filter items containing 'onboard' (should match 2 items)"
        },
        {
            "command": 'python backlog_analyzer_demo.py --enrich --backlog sample_backlog.csv --initiatives sample_initiatives.csv --output test2.csv --filter-title "^Mobile.*"',
            "description": "Filter items starting with 'Mobile' (should match 1 item)"
        },
        {
            "command": 'python backlog_analyzer_demo.py --enrich --backlog sample_backlog.csv --initiatives sample_initiatives.csv --output test3.csv --filter-title ".*security.*"',
            "description": "Filter items containing 'security' (should match 1 item)"
        },
        {
            "command": 'python backlog_analyzer_demo.py --enrich --backlog sample_backlog.csv --initiatives sample_initiatives.csv --output test4.csv --filter-title "(database|query)"',
            "description": "Filter items with 'database' or 'query' (should match 1 item)"
        },
        {
            "command": 'python backlog_analyzer_demo.py --enrich --backlog sample_backlog.csv --initiatives sample_initiatives.csv --output test5.csv --filter-title "^NoMatch.*"',
            "description": "Filter with pattern that matches nothing (should match 0 items)"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if run_command(test["command"], test["description"]):
            passed += 1
        else:
            failed += 1
    
    # Test error handling
    print(f"\n🧪 Testing invalid regex pattern (should fail gracefully)")
    print(f"Command: python backlog_analyzer_demo.py --filter-title '['")
    
    try:
        result = subprocess.run(
            'python backlog_analyzer_demo.py --enrich --backlog sample_backlog.csv --initiatives sample_initiatives.csv --output test_error.csv --filter-title "["',
            shell=True, capture_output=True, text=True, cwd=os.getcwd()
        )
        
        if result.returncode != 0 and "Invalid regex pattern" in result.stderr:
            print("✅ Error handling works correctly")
            passed += 1
        else:
            print("❌ Error handling failed")
            failed += 1
    except Exception as e:
        print(f"❌ Exception during error test: {e}")
        failed += 1
    
    # Clean up test files
    test_files = ['test1.csv', 'test2.csv', 'test3.csv', 'test4.csv', 'test5.csv', 'test_error.csv']
    for file in test_files:
        if Path(file).exists():
            Path(file).unlink()
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The --filter-title functionality is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
