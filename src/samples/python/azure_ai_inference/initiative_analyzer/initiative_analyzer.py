"""
Initiative Analyzer - AI-powered backlog item analysis and initiative association.

This application analyzes CSV backlog items against organizational initiatives
using Azure AI Foundry's language models to generate comprehensive markdown reports
organized by initiative.

Features:
- CSV-based backlog and initiative processing
- AI-powered semantic analysis and initiative matching
- Confidence threshold filtering for high-quality associations
- Initiative-centric markdown report generation
- Detailed impact analysis and strategic recommendations
- Function tool calling for sophisticated initiative matching
- Configurable logging levels for debugging and monitoring
"""

import argparse
import csv
import json
import logging
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

from tools.initiative_associator import associate_backlog_with_initiatives

# Configure logging for debugging and monitoring (default configuration)
# This will be updated by configure_logging() function based on verbose setting
logger = logging.getLogger(__name__)


@dataclass
class BacklogItem:
    """Represents a single backlog item with its metadata."""
    
    category: str
    initiative: str
    title: str
    goal: str
    stream: str
    timeline_data: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert backlog item to dictionary format."""
        result = {
            'category': self.category,
            'initiative': self.initiative,
            'title': self.title,
            'goal': self.goal,
            'stream': self.stream
        }
        result.update(self.timeline_data)
        return result


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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert initiative to dictionary format."""
        return {
            'area': self.area,
            'title': self.title,
            'details': self.details,
            'description': self.description,
            'kpi': self.kpi,
            'current_state': self.current_state,
            'solutions': self.solutions
        }


@dataclass
class BacklogItemAssociation:
    """Represents a backlog item associated with an initiative."""
    
    backlog_item: BacklogItem
    confidence: int
    impact_analysis: str
    
    def get_timeline_summary(self) -> str:
        """Get a summary of the timeline for this backlog item."""
        active_periods = []
        for period, value in self.backlog_item.timeline_data.items():
            if value == '1' or value == 1:
                active_periods.append(period)
        
        if not active_periods:
            return "No specific timeline"
        elif len(active_periods) == 1:
            return active_periods[0]
        else:
            return f"{active_periods[0]}-{active_periods[-1]}"


@dataclass
class InitiativeReport:
    """Represents a complete initiative report with associated backlog items."""
    
    initiative: Initiative
    associated_items: List[BacklogItemAssociation]
    confidence_threshold: int
    collective_impact: str
    strategic_recommendations: str
    timeline_considerations: str


@dataclass 
class EnrichedBacklogItem:
    """Represents a backlog item enriched with AI analysis."""
    
    original_item: BacklogItem
    matched_initiative: Optional[str]
    secondary_initiatives: List[str]
    category_confidence: int
    initiative_confidence: int
    impact_analysis: str
    detailed_analysis: str
    timeline_alignment: str
    resource_implications: str
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert enriched backlog item to dictionary format for CSV output."""
        result = self.original_item.to_dict()
        result.update({
            'initiative': self.matched_initiative or self.original_item.initiative,
            'impact': self.impact_analysis,
            'analysis': self.detailed_analysis,
            'category_confidence': self.category_confidence,
            'initiative_confidence': self.initiative_confidence,
            'initiative_details': self.matched_initiative or '',
            'timeline_alignment': self.timeline_alignment,
            'resource_implications': self.resource_implications,
            'recommendations': '; '.join(self.recommendations)
        })
        return result


def configure_logging(verbose_level: str = 'ERROR') -> None:
    """
    Configure application logging based on verbosity level.

    Args:
        verbose_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Raises:
        ValueError: If invalid logging level provided
    """
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if verbose_level.upper() not in valid_levels:
        raise ValueError(f"Invalid logging level '{verbose_level}'. Valid options: {', '.join(valid_levels)}")

    log_level = getattr(logging, verbose_level.upper())
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True  # Override any existing configuration
    )

    # Set Azure SDK logging to WARNING to reduce noise unless DEBUG is selected
    if verbose_level.upper() != 'DEBUG':
        logging.getLogger('azure').setLevel(logging.WARNING)
        logging.getLogger('openai').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for the initiative analyzer."""
    parser = argparse.ArgumentParser(
        description="Initiative Analyzer - Analyze backlog items against organizational initiatives using AI",
        epilog="Example: python initiative_analyzer.py --backlog backlog.csv --initiatives initiatives.csv --output initiative_reports/",
    )
    parser.add_argument(
        "--backlog", 
        type=str, 
        required=True,
        help="Path to CSV file containing backlog items"
    )
    parser.add_argument(
        "--initiatives", 
        type=str, 
        required=True,
        help="Path to CSV file containing organizational initiatives"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        required=True,
        help="Output directory for initiative markdown reports"
    )
    parser.add_argument(
        "--confidence-threshold",
        type=int,
        default=60,
        help="Minimum confidence threshold for including backlog-initiative associations (default: 60)"
    )
    parser.add_argument(
        "--endpoint", 
        type=str, 
        help="Override PROJECT_ENDPOINT environment variable"
    )
    parser.add_argument(
        "--model", 
        type=str, 
        help="Override MODEL_DEPLOYMENT_NAME environment variable"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default=None,
        help="Set logging verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: ERROR"
    )
    parser.add_argument(
        "--filter-title",
        type=str,
        help="Filter backlog items by title using a regex pattern (e.g., 'onboard.*' to match titles containing 'onboard')"
    )
    return parser.parse_args()


def load_environment() -> None:
    """Load environment variables from .env file if available."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
        logger.info("Environment variables loaded from .env file")
    except ImportError:
        logger.info("python-dotenv not available, using system environment variables")


def initialize_client(endpoint: Optional[str] = None) -> AzureOpenAI:
    """
    Initialize and test the Azure AI Projects client and get Azure OpenAI client.

    Args:
        endpoint: Optional override for PROJECT_ENDPOINT

    Returns:
        Azure OpenAI client from AI Projects SDK

    Raises:
        SystemExit: If connection fails or required environment variables are missing
    """
    load_environment()

    # Get project endpoint from argument or environment
    project_endpoint = endpoint or os.environ.get("PROJECT_ENDPOINT")
    if not project_endpoint:
        logger.error(
            "PROJECT_ENDPOINT environment variable is required or must be provided via --endpoint argument"
        )
        print(
            "Error: PROJECT_ENDPOINT environment variable is required or must be provided via --endpoint argument"
        )
        sys.exit(1)

    # Configure authentication using DefaultAzureCredential
    credential = DefaultAzureCredential()

    try:
        # Create the Azure AI Projects client
        project_client = AIProjectClient(
            endpoint=project_endpoint,
            credential=credential
        )

        # Get Azure OpenAI client for inference operations
        client = project_client.inference.get_azure_openai_client(
            api_version="2024-10-21"
        )

        logger.info("Created Azure OpenAI client via AIProjectClient for endpoint: %s", project_endpoint)
        print(f"Connected to Azure AI Foundry project: {project_endpoint}")

        return client

    except Exception as e:
        logger.error("Failed to initialize client: %s", e)
        print(f"Connection failed: {e}")
        print("Please check your PROJECT_ENDPOINT and authentication.")
        sys.exit(1)


def load_backlog_items(file_path: str, title_filter: Optional[str] = None) -> List[BacklogItem]:
    """
    Load backlog items from CSV file.
    
    Args:
        file_path: Path to the backlog CSV file
        title_filter: Optional regex pattern to filter backlog items by title
        
    Returns:
        List of BacklogItem objects (filtered by title if pattern provided)
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If required columns are missing or regex pattern is invalid
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Backlog file not found: {file_path}")
    
    # Compile regex pattern if provided
    title_pattern = None
    if title_filter:
        try:
            title_pattern = re.compile(title_filter, re.IGNORECASE)
            logger.info("Using title filter pattern: %s", title_filter)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{title_filter}': {e}") from e
    
    required_columns = ['category', 'title', 'goal', 'stream']
    timeline_columns = ['25 H1', '25 H2', '26 H1', '26 H2', '27 H1', '27 H2', '28+']
    
    backlog_items = []
    filtered_count = 0
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Validate required columns
        missing_columns = [col for col in required_columns if col not in reader.fieldnames]
        if missing_columns:
            raise ValueError(f"Missing required columns in backlog CSV: {missing_columns}")
        
        for row_num, row in enumerate(reader, start=2):
            try:
                title = row['title'].strip()
                
                # Apply title filter if provided
                if title_pattern and not title_pattern.search(title):
                    filtered_count += 1
                    continue
                
                # Extract timeline data
                timeline_data = {}
                for col in timeline_columns:
                    if col in reader.fieldnames:
                        timeline_data[col] = row.get(col, '0')
                
                # Create backlog item
                item = BacklogItem(
                    category=row['category'].strip(),
                    initiative=row.get('initiative', '').strip(),
                    title=title,
                    goal=row['goal'].strip(),
                    stream=row['stream'].strip(),
                    timeline_data=timeline_data
                )
                
                backlog_items.append(item)
                
            except Exception as e:
                logger.warning("Error processing row %d in backlog CSV: %s", row_num, e)
                continue
    
    total_items = len(backlog_items) + filtered_count
    if title_pattern:
        logger.info("Loaded %d backlog items from %s (filtered %d items out of %d total)", 
                   len(backlog_items), file_path, filtered_count, total_items)
        print(f"Applied title filter '{title_filter}': {len(backlog_items)} items match (filtered out {filtered_count})")
    else:
        logger.info("Loaded %d backlog items from %s", len(backlog_items), file_path)
    
    return backlog_items


def load_initiatives(file_path: str) -> List[Initiative]:
    """
    Load initiatives from CSV file.
    
    Args:
        file_path: Path to the initiatives CSV file
        
    Returns:
        List of Initiative objects
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If required columns are missing
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Initiatives file not found: {file_path}")
    
    required_columns = ['area', 'title', 'details', 'description', 'kpi', 'current_state', 'solutions']
    
    initiatives = []
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Validate required columns
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
                logger.warning("Error processing row %d in initiatives CSV: %s", row_num, e)
                continue
    
    logger.info("Loaded %d initiatives from %s", len(initiatives), file_path)
    return initiatives


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be used as a filename.
    
    Args:
        filename: The string to sanitize
        
    Returns:
        str: A sanitized filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip('. ')
    # Limit length to avoid filesystem issues
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    return sanitized


def generate_initiative_markdown_report(initiative_report: InitiativeReport) -> str:
    """
    Generate a markdown report for a single initiative.
    
    Args:
        initiative_report: The initiative report data
        
    Returns:
        str: The markdown content for the report
    """
    initiative = initiative_report.initiative
    items = initiative_report.associated_items
    
    # Generate frontmatter
    markdown = f"""---
area: {initiative.area}
title: {initiative.title}
confidence_threshold: {initiative_report.confidence_threshold}
total_associated_items: {len(items)}
---

# {initiative.title}

## Initiative Overview

**Area:** {initiative.area}
**Current Status:** {initiative.current_state}

{initiative.details}

{initiative.description}

## Key Performance Indicators

{initiative.kpi}

## Proposed Solutions

{initiative.solutions}

## Associated Backlog Items

The following backlog items have been associated with this initiative based on semantic analysis and goal alignment:

| Title | Goal | Category | Stream | Timeline | Confidence | Impact Analysis |
|-------|------|----------|--------|----------|------------|-----------------|
"""

    # Add table rows for each associated backlog item
    for association in items:
        item = association.backlog_item
        timeline = association.get_timeline_summary()
        markdown += f"| {item.title} | {item.goal} | {item.category} | {item.stream} | {timeline} | {association.confidence}% | {association.impact_analysis} |\n"

    # Add collective impact assessment
    markdown += f"""
## Collective Impact Assessment

{initiative_report.collective_impact}

## Strategic Recommendations

{initiative_report.strategic_recommendations}

## Timeline and Resource Considerations

{initiative_report.timeline_considerations}
"""

    return markdown


def organize_backlog_by_initiative(
    enriched_items: List[EnrichedBacklogItem], 
    initiatives: List[Initiative],
    confidence_threshold: int
) -> List[InitiativeReport]:
    """
    Organize enriched backlog items by initiative and generate reports.
    
    Args:
        enriched_items: List of enriched backlog items
        initiatives: List of all initiatives
        confidence_threshold: Minimum confidence for including associations
        
    Returns:
        List[InitiativeReport]: Reports for initiatives with associated items
    """
    # Create a mapping of initiative titles to initiative objects
    initiative_map = {init.title: init for init in initiatives}
    
    # Group backlog items by their matched initiatives
    initiative_associations: Dict[str, List[BacklogItemAssociation]] = {}
    
    for enriched_item in enriched_items:
        # Only include items that meet the confidence threshold
        if (enriched_item.matched_initiative and 
            enriched_item.initiative_confidence >= confidence_threshold):
            
            initiative_title = enriched_item.matched_initiative
            
            if initiative_title not in initiative_associations:
                initiative_associations[initiative_title] = []
            
            association = BacklogItemAssociation(
                backlog_item=enriched_item.original_item,
                confidence=enriched_item.initiative_confidence,
                impact_analysis=enriched_item.impact_analysis
            )
            
            initiative_associations[initiative_title].append(association)
    
    # Generate reports for initiatives with associated items
    reports = []
    
    for initiative_title, associations in initiative_associations.items():
        if initiative_title in initiative_map:
            initiative = initiative_map[initiative_title]
            
            # Generate collective impact and recommendations using AI
            collective_impact = _generate_collective_impact_analysis(initiative, associations)
            strategic_recommendations = _generate_strategic_recommendations(initiative, associations)
            timeline_considerations = _generate_timeline_considerations(associations)
            
            report = InitiativeReport(
                initiative=initiative,
                associated_items=associations,
                confidence_threshold=confidence_threshold,
                collective_impact=collective_impact,
                strategic_recommendations=strategic_recommendations,
                timeline_considerations=timeline_considerations
            )
            
            reports.append(report)
    
    return reports


def _generate_collective_impact_analysis(
    initiative: Initiative, 
    associations: List[BacklogItemAssociation]
) -> str:
    """Generate collective impact analysis for multiple backlog items on an initiative."""
    if not associations:
        return "No associated backlog items meet the confidence threshold."
    
    # Basic analysis based on the number and types of items
    impact_text = (
        f"The {len(associations)} associated backlog items will collectively advance "
        f"this initiative through complementary approaches. "
    )
    
    # Analyze item categories
    categories = {assoc.backlog_item.category for assoc in associations}
    if len(categories) > 1:
        impact_text += (
            f"These items span {len(categories)} different categories "
            f"({', '.join(categories)}), providing a comprehensive approach to initiative advancement. "
        )
    
    # Analyze confidence levels
    avg_confidence = sum(assoc.confidence for assoc in associations) / len(associations)
    if avg_confidence > 75:
        impact_text += "The high confidence scores indicate strong strategic alignment across all items."
    elif avg_confidence > 60:
        impact_text += "The moderate to high confidence scores suggest good strategic fit for most items."
    else:
        impact_text += "The confidence scores suggest these items provide some strategic value but may need closer review."
    
    return impact_text


def _generate_strategic_recommendations(
    initiative: Initiative, 
    associations: List[BacklogItemAssociation]
) -> str:
    """Generate strategic recommendations for implementing associated backlog items."""
    if not associations:
        return "Consider identifying backlog items that could support this initiative."
    
    recommendations = (
        f"To maximize the success of the '{initiative.title}' initiative:\n\n"
        f"1. **Prioritize high-confidence items**: Focus on items with confidence scores above 70% for immediate impact.\n"
        f"2. **Coordinate implementation**: Ensure the {len(associations)} associated backlog items are implemented in a coordinated manner.\n"
        f"3. **Track KPI alignment**: Monitor progress against the initiative's KPIs: {initiative.kpi}\n"
    )
    
    # Add timeline-specific recommendations
    near_term_items = [
        assoc for assoc in associations 
        if any(assoc.backlog_item.timeline_data.get(period) in ['1', 1] 
               for period in ['25 H1', '25 H2'])
    ]
    
    if near_term_items:
        recommendations += f"4. **Near-term focus**: {len(near_term_items)} items are planned for the next year - ensure adequate resource allocation.\n"
    
    return recommendations


def _generate_timeline_considerations(associations: List[BacklogItemAssociation]) -> str:
    """Generate timeline and resource considerations for associated backlog items."""
    if not associations:
        return "No timeline considerations with current associations."
    
    # Analyze timeline distribution
    timeline_periods = ['25 H1', '25 H2', '26 H1', '26 H2', '27 H1', '27 H2', '28+']
    period_counts = {period: 0 for period in timeline_periods}
    
    for assoc in associations:
        for period in timeline_periods:
            if assoc.backlog_item.timeline_data.get(period) in ['1', 1]:
                period_counts[period] += 1
    
    # Find peak periods
    max_count = max(period_counts.values())
    peak_periods = [period for period, count in period_counts.items() if count == max_count and count > 0]
    
    if peak_periods:
        considerations = (
            f"Timeline analysis shows peak activity in {', '.join(peak_periods)} "
            f"with {max_count} concurrent items. "
        )
    else:
        considerations = "No specific timeline patterns identified across associated items. "
    
    # Analyze teams involved
    teams = {assoc.backlog_item.stream for assoc in associations}
    considerations += (
        f"Implementation will involve {len(teams)} team(s): {', '.join(teams)}. "
        f"Coordination across teams will be essential for initiative success."
    )
    
    return considerations


def save_initiative_reports(reports: List[InitiativeReport], output_dir: str) -> None:
    """
    Save initiative reports as markdown files.
    
    Args:
        reports: List of initiative reports to save
        output_dir: Directory to save the reports
        
    Raises:
        IOError: If unable to create directory or save files
    """
    if not reports:
        print("No initiative reports to save.")
        return
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    saved_count = 0
    
    for report in reports:
        try:
            # Generate filename from initiative title
            filename = sanitize_filename(f"{report.initiative.title}.md")
            file_path = output_path / filename
            
            # Generate markdown content
            markdown_content = generate_initiative_markdown_report(report)
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            saved_count += 1
            logger.info("Saved initiative report: %s", file_path)
            
        except Exception as e:
            logger.error("Failed to save report for initiative '%s': %s", 
                        report.initiative.title, e)
            continue
    
    print(f"✅ Saved {saved_count} initiative reports to {output_dir}")
    if saved_count < len(reports):
        print(f"⚠️  Failed to save {len(reports) - saved_count} reports")


def analyze_initiative_associations(
    backlog_file: str,
    initiatives_file: str,
    output_dir: str,
    client: AzureOpenAI,
    model_name: str,
    confidence_threshold: int = 60,
    title_filter: Optional[str] = None
) -> None:
    """
    Analyze backlog items against initiatives and generate initiative reports.
    
    Args:
        backlog_file: Path to backlog CSV file
        initiatives_file: Path to initiatives CSV file
        output_dir: Directory for output markdown reports
        client: Azure OpenAI client
        model_name: Model deployment name
        confidence_threshold: Minimum confidence for including associations
        title_filter: Optional regex pattern to filter backlog items by title
    """
    try:
        # Load data
        print("Loading backlog items...")
        backlog_items = load_backlog_items(backlog_file, title_filter)
        
        print("Loading initiatives...")
        initiatives = load_initiatives(initiatives_file)
        
        if not backlog_items:
            print("No backlog items found. Please check your backlog CSV file.")
            return
        
        if not initiatives:
            print("No initiatives found. Please check your initiatives CSV file.")
            return
        
        print(f"Analyzing {len(backlog_items)} backlog items against {len(initiatives)} initiatives...")
        print(f"Using confidence threshold: {confidence_threshold}%")
        
        # Process each backlog item
        enriched_items = []
        qualifying_items = 0
        
        for i, item in enumerate(backlog_items, 1):
            print(f"Analyzing item {i}/{len(backlog_items)}: {item.title}")
            
            try:
                enriched_item = analyze_backlog_item(client, item, initiatives, model_name)
                enriched_items.append(enriched_item)
                
                # Check if item qualifies for inclusion
                if (enriched_item.matched_initiative and 
                    enriched_item.initiative_confidence >= confidence_threshold):
                    qualifying_items += 1
                    print(f"  ✅ Matched: {enriched_item.matched_initiative} (confidence: {enriched_item.initiative_confidence}%)")
                else:
                    confidence = enriched_item.initiative_confidence
                    print(f"  ❌ No qualifying match (confidence: {confidence}% < {confidence_threshold}%)")
                
            except Exception as e:
                logger.error("Failed to analyze item '%s': %s", item.title, e)
                print(f"  ⚠️  Error analyzing item: {e}")
                continue
        
        print(f"\n📊 Analysis Summary:")
        print(f"   • Total items analyzed: {len(enriched_items)}")
        print(f"   • Items meeting threshold: {qualifying_items}")
        print(f"   • Confidence threshold: {confidence_threshold}%")
        
        # Generate initiative reports
        if enriched_items:
            print("\n📝 Generating initiative reports...")
            reports = organize_backlog_by_initiative(enriched_items, initiatives, confidence_threshold)
            
            if reports:
                print(f"Generated {len(reports)} initiative reports")
                save_initiative_reports(reports, output_dir)
                
                # Print summary of generated reports
                print(f"\n📋 Generated Reports:")
                for report in reports:
                    print(f"   • {report.initiative.title}: {len(report.associated_items)} items")
            else:
                print("❌ No initiative reports generated. Try lowering the confidence threshold.")
        else:
            print("❌ No items were successfully analyzed.")
            
    except Exception as e:
        logger.error("Error in initiative analysis: %s", e)
        print(f"Error processing analysis: {e}")
        sys.exit(1)


def create_initiative_association_tool() -> Dict[str, Any]:
    """
    Create the initiative association tool definition for the AI model.

    Returns:
        dict: Tool definition for initiative association in OpenAI format
    """
    return {
        "type": "function",
        "function": {
            "name": "associate_backlog_with_initiatives",
            "description": "Analyzes a backlog item against available initiatives to find the best matches. Performs semantic analysis to identify which initiatives would be most impacted by completing the backlog item, including goal alignment, category mapping, and impact assessment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "backlog_item": {
                        "type": "object",
                        "description": "Dictionary containing backlog item details including category, title, goal, stream, and timeline data",
                        "properties": {
                            "category": {"type": "string", "description": "High-level category of the backlog item"},
                            "title": {"type": "string", "description": "Title of the backlog item"},
                            "goal": {"type": "string", "description": "The goal or expected outcome"},
                            "stream": {"type": "string", "description": "Team responsible for the item"}
                        }
                    },
                    "initiatives": {
                        "type": "array",
                        "description": "List of available initiatives to match against",
                        "items": {
                            "type": "object",
                            "properties": {
                                "area": {"type": "string", "description": "Initiative area"},
                                "title": {"type": "string", "description": "Initiative title"},
                                "details": {"type": "string", "description": "Detailed description"},
                                "description": {"type": "string", "description": "Additional information"},
                                "kpi": {"type": "string", "description": "Key Performance Indicators"},
                                "current_state": {"type": "string", "description": "Current status"},
                                "solutions": {"type": "string", "description": "Proposed solutions"}
                            }
                        }
                    }
                },
                "required": ["backlog_item", "initiatives"]
            }
        }
    }


def get_backlog_analysis_system_prompt() -> str:
    """
    Get the system prompt for backlog analysis and initiative association.

    Returns:
        str: System prompt for the backlog analyzer
    """
    return """You are a Strategic Backlog Analyzer, designed to help organizations understand how their backlog items align with strategic initiatives. Your role is to:

**Core Responsibilities:**
1. Analyze backlog items for strategic alignment with organizational initiatives
2. Provide confidence scores for category classification and initiative matching
3. Generate actionable insights about impact and resource implications
4. Recommend priority and implementation approaches based on strategic fit

**Analysis Framework:**
- Use semantic analysis to match backlog goals with initiative objectives
- Evaluate category alignment between backlog items and initiative areas
- Assess timeline compatibility and resource requirements
- Consider both direct and indirect impacts on strategic goals

**Tool Usage:**
- Use the associate_backlog_with_initiatives tool to perform detailed semantic analysis
- Integrate tool results to provide comprehensive strategic recommendations
- Ensure confidence scores reflect the strength of semantic and strategic alignment

**Output Requirements:**
- Provide clear, actionable analysis for each backlog item
- Include specific confidence scores (0-100) for categorization and initiative matching
- Generate timeline alignment analysis and resource implications
- Offer strategic recommendations for prioritization and implementation

**Quality Standards:**
- Base analysis on factual alignment between goals and initiatives
- Provide transparent reasoning for all associations and confidence scores
- Consider organizational context and resource constraints
- Focus on maximizing strategic value through proper backlog prioritization

Remember: Your goal is to help organizations make data-driven decisions about backlog prioritization by clearly showing how each item contributes to strategic initiatives."""


def analyze_backlog_item(
    client: AzureOpenAI,
    backlog_item: BacklogItem,
    initiatives: List[Initiative],
    model_name: str
) -> EnrichedBacklogItem:
    """
    Analyze a single backlog item against available initiatives using AI.
    
    Args:
        client: The Azure OpenAI client
        backlog_item: The backlog item to analyze
        initiatives: List of available initiatives
        model_name: The model deployment name
        
    Returns:
        EnrichedBacklogItem with AI analysis results
        
    Raises:
        RuntimeError: If the AI analysis fails
    """
    try:
        # Create system prompt and conversation
        system_prompt = get_backlog_analysis_system_prompt()
        conversation = [{"role": "system", "content": system_prompt}]
        
        # Create user prompt for analysis
        user_prompt = f"""
        Please analyze the following backlog item against the provided initiatives:

        Backlog Item:
        - Category: {backlog_item.category}
        - Title: {backlog_item.title}
        - Goal: {backlog_item.goal}
        - Stream: {backlog_item.stream}
        - Timeline: {backlog_item.timeline_data}

        Use the associate_backlog_with_initiatives tool to perform detailed semantic analysis and provide:
        1. Primary initiative match (if any) with confidence score
        2. Secondary initiatives that may benefit
        3. Category confidence score (0-100)
        4. Initiative confidence score (0-100)
        5. Detailed impact analysis
        6. Strategic recommendations for implementation

        Focus on finding the strongest semantic and strategic alignment between the backlog item's goal and the available initiatives.
        """
        
        conversation.append({"role": "user", "content": user_prompt})
        
        # Create tool definition
        association_tool = create_initiative_association_tool()
        
        # Make the API call with tool support
        response = client.chat.completions.create(
            messages=conversation,
            model=model_name,
            tools=[association_tool],
            max_tokens=1000,
            temperature=0.1,  # Low temperature for consistent analysis
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        
        # Process tool calls if requested
        if response.choices[0].finish_reason == "tool_calls" and response.choices[0].message.tool_calls:
            logger.info("Processing initiative association tool call")
            
            # Add assistant's tool call message
            tool_call_message = {
                "role": "assistant",
                "content": response.choices[0].message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in response.choices[0].message.tool_calls
                ]
            }
            conversation.append(tool_call_message)
            
            # Execute tool call
            for tool_call in response.choices[0].message.tool_calls:
                if tool_call.function.name == "associate_backlog_with_initiatives":
                    try:
                        # Parse arguments and execute function
                        function_args = json.loads(tool_call.function.arguments)
                        
                        # Ensure we pass the initiatives as list of dictionaries
                        initiatives_data = [init.to_dict() for init in initiatives]
                        function_args["initiatives"] = initiatives_data
                        
                        # Execute the association function
                        tool_result = associate_backlog_with_initiatives(**function_args)
                        
                        # Add tool response to conversation
                        tool_message = {
                            "role": "tool",
                            "content": tool_result,
                            "tool_call_id": tool_call.id
                        }
                        conversation.append(tool_message)
                        
                    except Exception as e:
                        logger.error("Tool execution failed: %s", e)
                        error_result = json.dumps({
                            "error": f"Tool execution failed: {str(e)}"
                        })
                        tool_message = {
                            "role": "tool",
                            "content": error_result,
                            "tool_call_id": tool_call.id
                        }
                        conversation.append(tool_message)
            
            # Get final response with tool results
            final_response = client.chat.completions.create(
                messages=conversation,
                model=model_name,
                max_tokens=1000,
                temperature=0.1,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            final_content = final_response.choices[0].message.content or ""
            
        else:
            # Use direct response if no tools called
            final_content = response.choices[0].message.content or ""
        
        # Parse tool result to extract structured data
        tool_result_data = {}
        if conversation[-2]["role"] == "tool":
            try:
                tool_result_data = json.loads(conversation[-2]["content"])
            except json.JSONDecodeError:
                logger.warning("Failed to parse tool result JSON")
        
        # Create enriched backlog item
        enriched_item = EnrichedBacklogItem(
            original_item=backlog_item,
            matched_initiative=tool_result_data.get("primary_initiative"),
            secondary_initiatives=tool_result_data.get("secondary_initiatives", []),
            category_confidence=tool_result_data.get("category_confidence", 0),
            initiative_confidence=tool_result_data.get("initiative_confidence", 0),
            impact_analysis=tool_result_data.get("impact_analysis", ""),
            detailed_analysis=final_content,
            timeline_alignment=tool_result_data.get("timeline_alignment", ""),
            resource_implications=tool_result_data.get("resource_implications", ""),
            recommendations=tool_result_data.get("recommendations", [])
        )
        
        return enriched_item
        
    except Exception as e:
        logger.error("Failed to analyze backlog item '%s': %s", backlog_item.title, e)
        raise RuntimeError(f"Unable to analyze backlog item: {e}") from e


def main() -> None:
    """
    Main entry point for the Initiative Analyzer.
    """
    try:
        # Parse command-line arguments
        args = parse_arguments()

        # Configure logging based on verbose flag and environment variable
        verbose_level = args.verbose
        if verbose_level is None:
            verbose_level = os.environ.get('VERBOSE_LOGGING', 'ERROR').upper()

        try:
            configure_logging(verbose_level)
            logger.info("Logging configured at %s level", verbose_level)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

        # Get model deployment name from environment or command line
        model_deployment_name = args.model or os.environ.get(
            "MODEL_DEPLOYMENT_NAME", "gpt-4o"
        )

        # Initialize the client
        client = initialize_client(endpoint=args.endpoint)

        # Perform initiative analysis and generate reports
        analyze_initiative_associations(
            args.backlog,
            args.initiatives,
            args.output,
            client,
            model_deployment_name,
            getattr(args, 'confidence_threshold', 60),
            getattr(args, 'filter_title', None)
        )

    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error("Unexpected error in main: %s", e)
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
