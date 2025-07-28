#!/usr/bin/env python3
"""
Simplified Backlog Analyzer Demo - works without Azure AI client.
This demonstrates the core functionality with mock AI responses.
"""

import argparse
import csv
import json
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from pathlib import Path
import os
import sys

# Add tools to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from initiative_associator import associate_backlog_with_initiatives


@dataclass
class BacklogItem:
    """Represents a backlog item."""
    category: str
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


@dataclass
class EnrichedBacklogItem:
    """Represents an enriched backlog item with AI analysis."""
    category: str
    initiative: str
    title: str
    goal: str
    stream: str
    timeline_data: Dict[str, str]
    impact: str
    analysis: str
    category_confidence: int
    initiative_confidence: int
    initiative_details: str
    timeline_alignment: str
    resource_implications: str
    recommendations: str


def load_backlog_items(file_path: str, title_filter: Optional[str] = None) -> List[BacklogItem]:
    """Load backlog items from CSV file with optional title filtering."""
    items = []
    filtered_count = 0
    
    # Compile regex pattern if provided
    title_pattern = None
    if title_filter:
        try:
            title_pattern = re.compile(title_filter, re.IGNORECASE)
            print(f"Using title filter pattern: {title_filter}")
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{title_filter}': {e}") from e
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row['title'].strip()
            
            # Apply title filter if provided
            if title_pattern and not title_pattern.search(title):
                filtered_count += 1
                continue
                
            # Extract timeline columns
            timeline_data = {}
            for key, value in row.items():
                if key not in ['category', 'title', 'goal', 'stream']:
                    timeline_data[key] = value
            
            items.append(BacklogItem(
                category=row['category'],
                title=title,
                goal=row['goal'],
                stream=row['stream'],
                timeline_data=timeline_data
            ))
    
    if title_pattern:
        print(f"Applied title filter '{title_filter}': {len(items)} items match (filtered out {filtered_count})")
    
    return items


def load_initiatives(file_path: str) -> List[Initiative]:
    """Load initiatives from CSV file."""
    initiatives = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            initiatives.append(Initiative(**row))
    return initiatives


def enrich_backlog_items(backlog_items: List[BacklogItem], initiatives: List[Initiative]) -> List[EnrichedBacklogItem]:
    """Enrich backlog items with AI analysis (using local tools)."""
    enriched_items = []
    
    # Convert initiatives to dict format for tool
    initiatives_data = [asdict(init) for init in initiatives]
    
    for item in backlog_items:
        print(f"Analyzing: {item.title}")
        
        # Prepare item data for analysis
        item_data = {
            'category': item.category,
            'title': item.title,
            'goal': item.goal,
            'stream': item.stream,
            **item.timeline_data
        }
        
        try:
            # Call local analysis tool
            result_json = associate_backlog_with_initiatives(item_data, initiatives_data)
            result = json.loads(result_json)
            
            # Create enriched item
            enriched = EnrichedBacklogItem(
                category=item.category,
                initiative=result.get('primary_initiative', 'No match found'),
                title=item.title,
                goal=item.goal,
                stream=item.stream,
                timeline_data=item.timeline_data,
                impact=result.get('impact_analysis', 'No impact analysis available'),
                analysis=result.get('detailed_analysis', 'No detailed analysis available'),
                category_confidence=result.get('category_confidence', 0),
                initiative_confidence=result.get('initiative_confidence', 0),
                initiative_details=result.get('initiative_details', ''),
                timeline_alignment=result.get('timeline_alignment', ''),
                resource_implications=result.get('resource_implications', ''),
                recommendations=result.get('recommendations', '')
            )
            
            enriched_items.append(enriched)
            print(f"  → Matched to: {enriched.initiative} ({enriched.initiative_confidence}% confidence)")
            
        except Exception as e:
            print(f"  ❌ Error analyzing {item.title}: {e}")
            # Create a fallback enriched item
            enriched = EnrichedBacklogItem(
                category=item.category,
                initiative='Analysis failed',
                title=item.title,
                goal=item.goal,
                stream=item.stream,
                timeline_data=item.timeline_data,
                impact='Analysis unavailable due to error',
                analysis=f'Error during analysis: {str(e)}',
                category_confidence=0,
                initiative_confidence=0,
                initiative_details='',
                timeline_alignment='',
                resource_implications='',
                recommendations='Manual review required'
            )
            enriched_items.append(enriched)
    
    return enriched_items


def save_enriched_backlog(enriched_items: List[EnrichedBacklogItem], output_path: str):
    """Save enriched backlog items to CSV file."""
    if not enriched_items:
        print("No enriched items to save.")
        return
    
    # Get all field names from the first item
    first_item = enriched_items[0]
    fieldnames = ['category', 'initiative', 'title', 'goal', 'stream']
    
    # Add timeline fields
    for key in first_item.timeline_data:
        fieldnames.append(key)
    
    # Add analysis fields
    fieldnames.extend([
        'impact', 'analysis', 'category_confidence', 'initiative_confidence',
        'initiative_details', 'timeline_alignment', 'resource_implications', 'recommendations'
    ])
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in enriched_items:
            row = {
                'category': item.category,
                'initiative': item.initiative,
                'title': item.title,
                'goal': item.goal,
                'stream': item.stream,
                'impact': item.impact,
                'analysis': item.analysis,
                'category_confidence': item.category_confidence,
                'initiative_confidence': item.initiative_confidence,
                'initiative_details': item.initiative_details,
                'timeline_alignment': item.timeline_alignment,
                'resource_implications': item.resource_implications,
                'recommendations': item.recommendations
            }
            # Add timeline data
            row.update(item.timeline_data)
            
            writer.writerow(row)
    
    print(f"Enriched backlog saved to: {output_path}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Backlog Analyzer - AI-powered backlog item analysis')
    parser.add_argument('--backlog', required=True, help='Path to backlog CSV file')
    parser.add_argument('--initiatives', required=True, help='Path to initiatives CSV file')
    parser.add_argument('--output', required=True, help='Path for output enriched CSV file')
    parser.add_argument('--enrich', action='store_true', help='Enable AI enrichment (using local tools)')
    parser.add_argument('--filter-title', type=str, help='Filter backlog items by title using a regex pattern')
    
    args = parser.parse_args()
    
    # Validate input files
    if not Path(args.backlog).exists():
        print(f"Backlog file not found: {args.backlog}")
        return 1
    
    if not Path(args.initiatives).exists():
        print(f"Initiatives file not found: {args.initiatives}")
        return 1
    
    try:
        # Load data
        print(f"Loading backlog from: {args.backlog}")
        backlog_items = load_backlog_items(args.backlog, getattr(args, 'filter_title', None))
        print(f"Loaded {len(backlog_items)} backlog items")
        
        print(f"Loading initiatives from: {args.initiatives}")
        initiatives = load_initiatives(args.initiatives)
        print(f"Loaded {len(initiatives)} initiatives")
        
        if args.enrich:
            print("\nStarting AI enrichment...")
            enriched_items = enrich_backlog_items(backlog_items, initiatives)
            save_enriched_backlog(enriched_items, args.output)
            
            # Display summary
            print("\nEnrichment Summary:")
            matched_count = sum(1 for item in enriched_items if item.initiative_confidence > 0)
            print(f"   Total items: {len(enriched_items)}")
            print(f"   Successfully matched: {matched_count}")
            print(f"   Match rate: {(matched_count / len(enriched_items) * 100):.1f}%")
            
        else:
            print("\nAI enrichment disabled. Use --enrich flag to enable analysis.")
            print("File validation completed successfully.")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
