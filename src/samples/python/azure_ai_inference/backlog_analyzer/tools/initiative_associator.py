"""
Initiative Association Tool for Backlog Analysis.

This module provides functionality to match backlog items with relevant initiatives
based on semantic analysis, goal alignment, and impact assessment.
"""

import json
from typing import Any, Dict, List


def associate_backlog_with_initiatives(
    backlog_item: Dict[str, Any],
    initiatives: List[Dict[str, Any]]
) -> str:
    """
    Analyze a backlog item against available initiatives to find the best matches.
    
    This function performs semantic analysis to identify which initiatives would be
    most impacted by completing the given backlog item. It evaluates goal alignment,
    category mapping, and potential impact to provide detailed association analysis.
    
    Args:
        backlog_item: Dictionary containing backlog item details with keys:
            - category: High-level category of the backlog item
            - title: Title of the backlog item
            - goal: The goal or expected outcome
            - stream: Team responsible for the item
            - timeline data (25 H1, 25 H2, etc.)
        initiatives: List of initiative dictionaries with keys:
            - area: Initiative area (e.g., "Developer Excellence")
            - title: Initiative title
            - details: Detailed description
            - description: Additional information
            - kpi: Key Performance Indicators
            - current_state: Current status
            - solutions: Proposed solutions
    
    Returns:
        str: JSON string containing detailed analysis including:
            - primary_initiative: Best matching initiative (if any)
            - secondary_initiatives: Additional relevant initiatives
            - category_confidence: Confidence score for category match (0-100)
            - initiative_confidence: Confidence score for initiative match (0-100)
            - impact_analysis: Detailed impact assessment
            - reasoning: Explanation of matching logic
    
    Raises:
        ValueError: If required fields are missing from backlog_item or initiatives
    """
    # Check required fields in backlog item
    required_backlog_fields = ['category', 'title', 'goal', 'stream']
    missing_fields = [field for field in required_backlog_fields 
                     if field not in backlog_item]
    if missing_fields:
        raise ValueError(f"Missing required backlog fields: {missing_fields}")
    
    # Check required fields in initiatives
    required_initiative_fields = ['area', 'title', 'details', 'description', 
                                 'kpi', 'current_state', 'solutions']
    for i, initiative in enumerate(initiatives):
        missing_fields = [field for field in required_initiative_fields 
                         if field not in initiative]
        if missing_fields:
            raise ValueError(f"Initiative {i} missing required fields: {missing_fields}")
    
    # Initialize analysis result structure
    analysis_result = {
        "primary_initiative": None,
        "secondary_initiatives": [],
        "category_confidence": 0,
        "initiative_confidence": 0,
        "impact_analysis": "",
        "reasoning": "",
        "timeline_alignment": "",
        "resource_implications": "",
        "recommendations": []
    }
    
    # Extract backlog item information for analysis
    backlog_category = str(backlog_item.get('category', '')).lower()
    backlog_title = str(backlog_item.get('title', '')).lower()
    backlog_goal = str(backlog_item.get('goal', '')).lower()
    
    # Perform semantic analysis against each initiative
    initiative_scores = []
    
    for initiative in initiatives:
        # Extract initiative information
        initiative_area = str(initiative.get('area', '')).lower()
        initiative_title = str(initiative.get('title', '')).lower()
        initiative_details = str(initiative.get('details', '')).lower()
        initiative_description = str(initiative.get('description', '')).lower()
        initiative_solutions = str(initiative.get('solutions', '')).lower()
        
        # Calculate semantic similarity scores
        area_category_score = _calculate_semantic_similarity(
            backlog_category, initiative_area
        )
        
        goal_alignment_score = _calculate_goal_alignment(
            backlog_goal, initiative_details, initiative_description, initiative_solutions
        )
        
        title_relevance_score = _calculate_title_relevance(
            backlog_title, initiative_title, initiative_details
        )
        
        # Calculate composite score
        composite_score = (
            area_category_score * 0.3 +
            goal_alignment_score * 0.5 +
            title_relevance_score * 0.2
        )
        
        initiative_scores.append({
            'initiative': initiative,
            'score': composite_score,
            'area_category_score': area_category_score,
            'goal_alignment_score': goal_alignment_score,
            'title_relevance_score': title_relevance_score
        })
    
    # Sort initiatives by score
    initiative_scores.sort(key=lambda x: x['score'], reverse=True)
    
    # Determine primary and secondary initiatives
    if initiative_scores and initiative_scores[0]['score'] > 30:  # Minimum threshold
        primary = initiative_scores[0]
        analysis_result['primary_initiative'] = primary['initiative']['title']
        analysis_result['initiative_confidence'] = int(primary['score'])
        
        # Add secondary initiatives (score > 20 and not primary)
        secondary = []
        for item in initiative_scores[1:4]:  # Top 3 secondary
            if item['score'] > 20:
                secondary.append(item['initiative']['title'])
        analysis_result['secondary_initiatives'] = secondary
    
    # Calculate category confidence based on semantic alignment
    category_confidence = 0
    if initiative_scores:
        # Average of top 3 area-category scores
        top_area_scores = []
        for item in initiative_scores[:3]:
            top_area_scores.append(item['area_category_score'])
        
        if top_area_scores:
            category_confidence = int(sum(top_area_scores) / len(top_area_scores))
    
    analysis_result['category_confidence'] = category_confidence
    
    # Generate detailed analysis
    analysis_result['impact_analysis'] = _generate_impact_analysis(
        backlog_item, initiative_scores[:3] if initiative_scores else []
    )
    
    analysis_result['reasoning'] = _generate_reasoning(
        backlog_item, initiative_scores[:1] if initiative_scores else []
    )
    
    analysis_result['timeline_alignment'] = _analyze_timeline_alignment(
        backlog_item
    )
    
    analysis_result['resource_implications'] = _analyze_resource_implications(
        backlog_item, initiative_scores[:1] if initiative_scores else []
    )
    
    analysis_result['recommendations'] = _generate_recommendations(
        backlog_item, initiative_scores[:3] if initiative_scores else []
    )
    
    return json.dumps(analysis_result, indent=2)


def _calculate_semantic_similarity(text1: str, text2: str) -> float:
    """
    Calculate semantic similarity between two text strings using keyword overlap.
    
    Args:
        text1: First text string
        text2: Second text string
        
    Returns:
        float: Similarity score between 0 and 100
    """
    if not text1 or not text2:
        return 0.0
    
    # Simple keyword-based similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if not union:
        return 0.0
    
    # Jaccard similarity scaled to 0-100
    similarity = (len(intersection) / len(union)) * 100
    
    # Boost score for exact matches
    if text1.lower() in text2.lower() or text2.lower() in text1.lower():
        similarity = min(100, similarity * 1.5)
    
    return similarity


def _calculate_goal_alignment(
    backlog_goal: str, 
    initiative_details: str, 
    initiative_description: str, 
    initiative_solutions: str
) -> float:
    """
    Calculate how well a backlog goal aligns with initiative objectives.
    
    Args:
        backlog_goal: Goal of the backlog item
        initiative_details: Detailed description of the initiative
        initiative_description: Additional initiative description
        initiative_solutions: Proposed solutions for the initiative
        
    Returns:
        float: Alignment score between 0 and 100
    """
    # Combine all initiative text for comparison
    combined_initiative_text = f"{initiative_details} {initiative_description} {initiative_solutions}"
    
    # Calculate base similarity
    base_score = _calculate_semantic_similarity(backlog_goal, combined_initiative_text)
    
    # Look for specific goal-related keywords
    goal_keywords = [
        'improve', 'enhance', 'increase', 'reduce', 'optimize', 'streamline',
        'automate', 'simplify', 'accelerate', 'enable', 'implement', 'develop',
        'create', 'build', 'establish', 'deliver', 'achieve', 'ensure'
    ]
    
    goal_keyword_boost = 0
    for keyword in goal_keywords:
        if keyword in backlog_goal and keyword in combined_initiative_text:
            goal_keyword_boost += 10
    
    return min(100, base_score + goal_keyword_boost)


def _calculate_title_relevance(
    backlog_title: str, 
    initiative_title: str, 
    initiative_details: str
) -> float:
    """
    Calculate relevance between backlog title and initiative information.
    
    Args:
        backlog_title: Title of the backlog item
        initiative_title: Title of the initiative
        initiative_details: Detailed description of the initiative
        
    Returns:
        float: Relevance score between 0 and 100
    """
    # Calculate similarity with initiative title
    title_similarity = _calculate_semantic_similarity(backlog_title, initiative_title)
    
    # Calculate similarity with initiative details
    details_similarity = _calculate_semantic_similarity(backlog_title, initiative_details)
    
    # Weighted combination (title is more important)
    return title_similarity * 0.7 + details_similarity * 0.3


def _generate_impact_analysis(
    backlog_item: Dict[str, Any], 
    top_initiatives: List[Any]
) -> str:
    """
    Generate detailed impact analysis for the backlog item.
    
    Args:
        backlog_item: The backlog item being analyzed
        top_initiatives: Top matching initiatives with scores
        
    Returns:
        str: Detailed impact analysis text
    """
    if not top_initiatives:
        return (
            f"The backlog item '{backlog_item.get('title', 'Unknown')}' "
            f"does not strongly align with any of the provided initiatives. "
            f"This may indicate a gap in the current initiative framework or "
            f"suggest that this item addresses a unique organizational need."
        )
    
    primary = top_initiatives[0]
    impact_text = (
        f"Completing '{backlog_item.get('title', 'Unknown')}' would have "
        f"significant impact on the '{primary['initiative']['title']}' initiative "
        f"(confidence: {int(primary['score'])}%). "
    )
    
    # Add specific impact details based on the initiative area
    initiative_area = primary['initiative'].get('area', '')
    if 'developer' in initiative_area.lower():
        impact_text += (
            "This would improve developer productivity and experience, "
            "potentially reducing onboarding time and increasing code quality. "
        )
    elif 'user' in initiative_area.lower() or 'experience' in initiative_area.lower():
        impact_text += (
            "This would enhance user experience and satisfaction, "
            "likely improving user retention and engagement metrics. "
        )
    elif 'performance' in initiative_area.lower():
        impact_text += (
            "This would optimize system performance and efficiency, "
            "potentially reducing costs and improving user satisfaction. "
        )
    
    # Add information about secondary impacts
    if len(top_initiatives) > 1:
        secondary_titles = [init['initiative']['title'] for init in top_initiatives[1:]]
        impact_text += (
            f"Additionally, it may provide secondary benefits to: "
            f"{', '.join(secondary_titles)}."
        )
    
    return impact_text


def _generate_reasoning(
    backlog_item: Dict[str, Any], 
    primary_initiative: List[Any]
) -> str:
    """
    Generate reasoning for the initiative association.
    
    Args:
        backlog_item: The backlog item being analyzed
        primary_initiative: Primary matching initiative with score details
        
    Returns:
        str: Detailed reasoning text
    """
    if not primary_initiative:
        return (
            "No strong initiative match found. The backlog item may address "
            "a unique need not covered by current initiatives, or may require "
            "initiative framework expansion."
        )
    
    primary = primary_initiative[0]
    reasoning = (
        f"The association is based on strong alignment between the backlog goal "
        f"'{backlog_item.get('goal', 'Unknown')}' and the initiative focus on "
        f"'{primary['initiative'].get('details', 'Unknown')}'. "
    )
    
    # Add specific reasoning based on score components
    if primary['area_category_score'] > 50:
        reasoning += (
            f"The category '{backlog_item.get('category', 'Unknown')}' "
            f"strongly aligns with the initiative area "
            f"'{primary['initiative'].get('area', 'Unknown')}'. "
        )
    
    if primary['goal_alignment_score'] > 60:
        reasoning += (
            "The goals show high semantic similarity, indicating that "
            "completing this backlog item would directly advance the initiative. "
        )
    
    if primary['title_relevance_score'] > 40:
        reasoning += (
            "The titles demonstrate clear topical relevance, suggesting "
            "aligned strategic intent. "
        )
    
    return reasoning


def _analyze_timeline_alignment(backlog_item: Dict[str, Any]) -> str:
    """
    Analyze timeline implications of the backlog item.
    
    Args:
        backlog_item: The backlog item with timeline data
        
    Returns:
        str: Timeline alignment analysis
    """
    timeline_fields = ['25 H1', '25 H2', '26 H1', '26 H2', '27 H1', '27 H2', '28+']
    active_periods = []
    
    for period in timeline_fields:
        if backlog_item.get(period) == '1' or backlog_item.get(period) == 1:
            active_periods.append(period)
    
    if not active_periods:
        return "No specific timeline indicated for this backlog item."
    
    if len(active_periods) == 1:
        return f"Planned for implementation in {active_periods[0]}."
    
    return f"Planned for implementation across multiple periods: {', '.join(active_periods)}."


def _analyze_resource_implications(
    backlog_item: Dict[str, Any], 
    primary_initiative: List[Any]
) -> str:
    """
    Analyze resource implications of implementing the backlog item.
    
    Args:
        backlog_item: The backlog item being analyzed
        primary_initiative: Primary matching initiative with details
        
    Returns:
        str: Resource implications analysis
    """
    stream = backlog_item.get('stream', 'Unknown')
    
    implications = f"Implementation will require resources from the {stream} team. "
    
    if primary_initiative:
        initiative = primary_initiative[0]['initiative']
        current_state = initiative.get('current_state', '').lower()
        
        if 'low adoption' in current_state or 'available' in current_state:
            implications += (
                "The related initiative has low adoption, so this backlog item "
                "could serve as a catalyst for broader initiative success. "
            )
        elif 'in progress' in current_state:
            implications += (
                "The related initiative is already in progress, so this item "
                "should integrate well with existing efforts. "
            )
    
    implications += (
        "Consider coordination with other teams working on related initiatives "
        "to maximize synergy and avoid resource conflicts."
    )
    
    return implications


def _generate_recommendations(
    backlog_item: Dict[str, Any], 
    top_initiatives: List[Any]
) -> List[str]:
    """
    Generate actionable recommendations based on the analysis.
    
    Args:
        backlog_item: The backlog item being analyzed
        top_initiatives: Top matching initiatives with scores
        
    Returns:
        List[str]: List of recommendation strings
    """
    recommendations = []
    
    if not top_initiatives:
        recommendations.extend([
            "Consider creating a new initiative to cover this backlog area",
            "Evaluate if this item addresses a genuine gap in strategic planning",
            "Review initiative framework completeness"
        ])
        return recommendations
    
    primary = top_initiatives[0]
    
    if primary['score'] > 70:
        recommendations.append(
            "Strong initiative alignment - prioritize for implementation"
        )
    elif primary['score'] > 50:
        recommendations.append(
            "Good initiative alignment - consider for next planning cycle"
        )
    else:
        recommendations.append(
            "Moderate alignment - review initiative fit before proceeding"
        )
    
    # Timeline-based recommendations
    timeline_fields = ['25 H1', '25 H2', '26 H1', '26 H2', '27 H1', '27 H2', '28+']
    near_term = any(backlog_item.get(period) == '1' or backlog_item.get(period) == 1 
                   for period in timeline_fields[:2])
    
    if near_term:
        recommendations.append(
            "Near-term implementation planned - ensure resource availability"
        )
    
    # KPI-based recommendations
    if primary['initiative'].get('kpi'):
        recommendations.append(
            f"Track progress against KPI: {primary['initiative']['kpi']}"
        )
    
    return recommendations
