#!/usr/bin/env python3
"""
Mock test for initiative analyzer with simulated Azure responses.
This tests the complete workflow without requiring Azure SDK dependencies.
"""

import json
from typing import Dict, Any

def mock_associate_backlog_with_initiatives(backlog_item: Dict[str, Any], initiatives: list) -> str:
    """
    Mock function that simulates the initiative association analysis.
    Returns a JSON string with analysis results.
    """
    # Simulate AI analysis based on backlog item content
    backlog_title = backlog_item.get('title', '').lower()
    backlog_category = backlog_item.get('category', '').lower()
    
    # Find best matching initiative
    best_match = None
    best_confidence = 0
    
    for initiative in initiatives:
        initiative_title = initiative.get('title', '').lower()
        initiative_area = initiative.get('area', '').lower()
        
        confidence = 30  # Base confidence
        
        # Check for keyword matches
        if 'onboard' in backlog_title and 'onboard' in initiative_title:
            confidence += 40
        if 'mobile' in backlog_title and 'mobile' in initiative_title:
            confidence += 40
        if 'database' in backlog_title and 'database' in initiative_title:
            confidence += 40
        if 'auth' in backlog_title and ('auth' in initiative_title or 'mfa' in initiative_title):
            confidence += 40
        
        # Category matching
        if 'user experience' in backlog_category and 'user experience' in initiative_area:
            confidence += 20
        if 'developer excellence' in backlog_category and 'developer excellence' in initiative_area:
            confidence += 20
        if 'performance' in backlog_category and 'performance' in initiative_area:
            confidence += 20
        if 'security' in backlog_category and 'security' in initiative_area:
            confidence += 20
        
        if confidence > best_confidence:
            best_confidence = confidence
            best_match = initiative['title']
    
    # Generate mock analysis result
    result = {
        "primary_initiative": best_match if best_confidence >= 60 else None,
        "secondary_initiatives": [],
        "category_confidence": min(best_confidence + 10, 95),
        "initiative_confidence": best_confidence,
        "impact_analysis": f"Completing '{backlog_item['title']}' would directly support the initiative goals by {backlog_item['goal'].lower()}.",
        "detailed_analysis": f"This backlog item aligns well with organizational objectives in the {backlog_item['category']} area.",
        "timeline_alignment": "The planned timeline supports initiative delivery goals.",
        "resource_implications": f"Implementation will require coordination with the {backlog_item['stream']} team.",
        "recommendations": [
            "High priority based on strategic alignment",
            "Consider for next planning cycle",
            f"Track progress against initiative KPIs"
        ]
    }
    
    return json.dumps(result, indent=2)

def main():
    """Test the mock analysis function."""
    print("🧪 Testing Mock Initiative Analysis\n")
    
    # Sample backlog item
    backlog_item = {
        "category": "Developer Excellence",
        "title": "Improve developer onboarding",
        "goal": "Streamline new developer setup",
        "stream": "Engineering Team"
    }
    
    # Sample initiatives
    initiatives = [
        {
            "area": "Developer Excellence",
            "title": "Improve developer onboarding",
            "details": "Streamline the onboarding process for new developers using GitHub Copilot",
            "description": "Create a comprehensive onboarding guide for GitHub Copilot",
            "kpi": "Time to onboard new developers",
            "current_state": "GitHub Copilot available, but low adoption",
            "solutions": "GitHub Copilot bootcamp, workshops, and documentation"
        },
        {
            "area": "User Experience",
            "title": "Mobile-first design strategy",
            "details": "Focus on mobile user experience improvements",
            "description": "Ensure all applications are optimized for mobile devices",
            "kpi": "Mobile user satisfaction score",
            "current_state": "Current applications have basic mobile support",
            "solutions": "Responsive design implementation, mobile usability testing"
        }
    ]
    
    # Run mock analysis
    print(f"Analyzing: {backlog_item['title']}")
    print(f"Category: {backlog_item['category']}")
    print(f"Goal: {backlog_item['goal']}")
    print()
    
    result = mock_associate_backlog_with_initiatives(backlog_item, initiatives)
    print("Analysis Result:")
    print(result)
    
    # Parse and display key metrics
    result_data = json.loads(result)
    print(f"\n📊 Key Metrics:")
    print(f"   Primary Initiative: {result_data['primary_initiative']}")
    print(f"   Initiative Confidence: {result_data['initiative_confidence']}%")
    print(f"   Category Confidence: {result_data['category_confidence']}%")
    
    if result_data['initiative_confidence'] >= 60:
        print("   ✅ Meets confidence threshold (≥60%)")
    else:
        print("   ❌ Below confidence threshold (<60%)")

if __name__ == "__main__":
    main()
