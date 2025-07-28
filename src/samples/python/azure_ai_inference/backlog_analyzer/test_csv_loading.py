"""
Test CSV loading functionality without dependencies.
"""

import csv
import os
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class BacklogItem:
    """Represents a single backlog item with its metadata."""
    
    category: str
    initiative: str
    title: str
    goal: str
    stream: str
    timeline_data: Dict[str, str]


@dataclass
class Initiative:
    """Represents an organizational initiative."""
    
    area: str
    title: str
    details: str
    description: str
    kpi: str
    current_state: str
    solutions: str


def load_backlog_items(file_path: str) -> List[BacklogItem]:
    """Load backlog items from CSV file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Backlog file not found: {file_path}")
    
    required_columns = ['category', 'title', 'goal', 'stream']
    timeline_columns = ['25 H1', '25 H2', '26 H1', '26 H2', '27 H1', '27 H2', '28+']
    
    backlog_items = []
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Validate required columns
        if reader.fieldnames:
            missing_columns = [col for col in required_columns if col not in reader.fieldnames]
            if missing_columns:
                raise ValueError(f"Missing required columns in backlog CSV: {missing_columns}")
        
        for row_num, row in enumerate(reader, start=2):
            try:
                # Extract timeline data
                timeline_data = {}
                for col in timeline_columns:
                    if reader.fieldnames and col in reader.fieldnames:
                        timeline_data[col] = row.get(col, '0')
                
                # Create backlog item
                item = BacklogItem(
                    category=row['category'].strip(),
                    initiative=row.get('initiative', '').strip(),
                    title=row['title'].strip(),
                    goal=row['goal'].strip(),
                    stream=row['stream'].strip(),
                    timeline_data=timeline_data
                )
                
                backlog_items.append(item)
                
            except Exception as e:
                print(f"Warning: Error processing row {row_num} in backlog CSV: {e}")
                continue
    
    return backlog_items


def load_initiatives(file_path: str) -> List[Initiative]:
    """Load initiatives from CSV file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Initiatives file not found: {file_path}")
    
    required_columns = ['area', 'title', 'details', 'description', 'kpi', 'current_state', 'solutions']
    
    initiatives = []
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Validate required columns
        if reader.fieldnames:
            missing_columns = [col for col in required_columns if col not in reader.fieldnames]
            if missing_columns:
                raise ValueError(f"Missing required columns in initiatives CSV: {missing_columns}")
        
        for row_num, row in enumerate(reader, start=2):
            try:
                initiative = Initiative(
                    area=row['area'].strip(),
                    title=row['title'].strip(),
                    details=row['details'].strip(),
                    description=row['description'].strip(),
                    kpi=row['kpi'].strip(),
                    current_state=row['current_state'].strip(),
                    solutions=row['solutions'].strip()
                )
                
                initiatives.append(initiative)
                
            except Exception as e:
                print(f"Warning: Error processing row {row_num} in initiatives CSV: {e}")
                continue
    
    return initiatives


if __name__ == "__main__":
    print("Testing CSV loading...")
    
    # Test backlog loading
    try:
        backlog = load_backlog_items('sample_backlog.csv')
        print(f"✅ Loaded {len(backlog)} backlog items")
        
        for i, item in enumerate(backlog[:2]):  # Show first 2 items
            print(f"  {i+1}. {item.title} ({item.category}) - {item.goal}")
            
    except Exception as e:
        print(f"❌ Error loading backlog: {e}")
    
    # Test initiatives loading
    try:
        initiatives = load_initiatives('sample_initiatives.csv')
        print(f"✅ Loaded {len(initiatives)} initiatives")
        
        for i, init in enumerate(initiatives[:2]):  # Show first 2 initiatives
            print(f"  {i+1}. {init.title} ({init.area}) - {init.details}")
            
    except Exception as e:
        print(f"❌ Error loading initiatives: {e}")
    
    print("\n✅ CSV loading test complete!")
