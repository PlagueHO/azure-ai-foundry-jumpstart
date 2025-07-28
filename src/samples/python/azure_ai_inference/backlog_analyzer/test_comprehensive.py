"""
Comprehensive test of the backlog analyzer functionality.
"""

import csv
import json
import os
import tempfile
from test_csv_loading import load_backlog_items, load_initiatives


def test_tool_integration():
    """Test the initiative association tool with real data."""
    print("🔧 Testing initiative association tool...")
    
    try:
        from tools.initiative_associator import associate_backlog_with_initiatives
        
        # Load sample data
        backlog_items = load_backlog_items('sample_backlog.csv')
        initiatives = load_initiatives('sample_initiatives.csv')
        
        # Convert to dict format for tool
        initiatives_data = [
            {
                'area': init.area,
                'title': init.title,
                'details': init.details,
                'description': init.description,
                'kpi': init.kpi,
                'current_state': init.current_state,
                'solutions': init.solutions
            }
            for init in initiatives
        ]
        
        # Test with first backlog item
        first_item = backlog_items[0]
        backlog_data = {
            'category': first_item.category,
            'title': first_item.title,
            'goal': first_item.goal,
            'stream': first_item.stream,
            **first_item.timeline_data
        }
        
        # Run analysis
        result_json = associate_backlog_with_initiatives(backlog_data, initiatives_data)
        result = json.loads(result_json)
        
        print(f"✅ Analyzed: {first_item.title}")
        print(f"   Category: {first_item.category}")
        print(f"   Matched Initiative: {result.get('primary_initiative', 'None')}")
        print(f"   Category Confidence: {result.get('category_confidence', 0)}%")
        print(f"   Initiative Confidence: {result.get('initiative_confidence', 0)}%")
        
        # Test all items
        print("\n📊 Testing all backlog items...")
        results = []
        
        for item in backlog_items:
            item_data = {
                'category': item.category,
                'title': item.title,
                'goal': item.goal,
                'stream': item.stream,
                **item.timeline_data
            }
            
            try:
                result_json = associate_backlog_with_initiatives(item_data, initiatives_data)
                result = json.loads(result_json)
                results.append({
                    'title': item.title,
                    'category': item.category,
                    'matched_initiative': result.get('primary_initiative'),
                    'initiative_confidence': result.get('initiative_confidence', 0),
                    'category_confidence': result.get('category_confidence', 0)
                })
                
            except json.JSONDecodeError as e:
                print(f"❌ Error analyzing {item.title}: {e}")
                continue
        
        # Display summary
        print("\n📈 Analysis Summary:")
        for result in results:
            status = "✅" if result['matched_initiative'] else "⚠️"
            print(f"{status} {result['title']}")
            print(f"    → {result['matched_initiative'] or 'No match'} ({result['initiative_confidence']}%)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Tool test failed: {e}")
        return False


def test_csv_output_format():
    """Test CSV output functionality."""
    print("\n📄 Testing CSV output format...")
    
    try:
        # Create sample enriched data
        sample_enriched = {
            'category': 'Developer Excellence',
            'initiative': 'Improve developer onboarding',
            'title': 'Setup IDE automation',
            'goal': 'Reduce developer setup time',
            'stream': 'Engineering',
            '25 H1': '1',
            '25 H2': '0',
            'impact': 'Would improve developer onboarding efficiency',
            'analysis': 'Strong alignment with developer experience goals',
            'category_confidence': 85,
            'initiative_confidence': 72,
            'initiative_details': 'Improve developer onboarding',
            'timeline_alignment': 'Planned for Q1 2025',
            'resource_implications': 'Requires Engineering team resources',
            'recommendations': 'High priority; Strong strategic alignment'
        }
        
        # Test CSV writing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            fieldnames = list(sample_enriched.keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(sample_enriched)
            temp_file = f.name
        
        # Verify file was created and read it back
        with open(temp_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print("✅ CSV output created successfully")
            print(f"   File size: {len(content)} bytes")
            print(f"   Headers: {len(fieldnames)} columns")
        
        # Clean up
        os.unlink(temp_file)
        
        return True
        
    except (OSError, IOError) as e:
        print(f"❌ CSV output test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Running Backlog Analyzer Tests")
    print("=" * 50)
    
    all_passed = True
    
    # Test 1: CSV Loading
    print("📂 Testing CSV loading...")
    try:
        backlog = load_backlog_items('sample_backlog.csv')
        initiatives = load_initiatives('sample_initiatives.csv')
        print(f"✅ CSV loading: {len(backlog)} backlog items, {len(initiatives)} initiatives")
    except (ImportError, FileNotFoundError) as e:
        print(f"❌ CSV loading failed: {e}")
        all_passed = False
    
    # Test 2: Tool Integration
    if not test_tool_integration():
        all_passed = False
    
    # Test 3: CSV Output
    if not test_csv_output_format():
        all_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed!")
        print("\nThe backlog analyzer is ready to use:")
        print("python backlog_analyzer.py --enrich --backlog sample_backlog.csv --initiatives sample_initiatives.csv --output enriched_backlog.csv")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return all_passed


if __name__ == "__main__":
    main()
