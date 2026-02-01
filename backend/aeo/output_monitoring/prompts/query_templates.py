"""
Query Templates for Automated Query Generation.

These templates are used to generate test queries based on
extracted topics from page content. Each category contains
multiple template variations to test different query styles.
"""

# =============================================================================
# QUERY TEMPLATES BY CATEGORY
# =============================================================================
# Each key is a query category, and the value is a list of template strings.
# Use {topic} as a placeholder for the extracted topic name.

QUERY_TEMPLATES = {
    # Definition/explanation queries
    "definition": [
        "What is {topic}?",
        "Can you explain {topic}?",
        "Tell me about {topic}",
    ],
    
    # How-to/tutorial queries
    "how_to": [
        "How does {topic} work?",
        "How to use {topic}?",
        "How can I get started with {topic}?",
    ],
    
    # Benefits/value proposition queries
    "benefits": [
        "What are the benefits of {topic}?",
        "Why should I use {topic}?",
        "What makes {topic} good?",
    ],
    
    # Comparison/competitive queries
    "comparison": [
        "How does {topic} compare to alternatives?",
        "{topic} vs competitors",
        "Is {topic} better than other options?",
    ],
    
    # Pricing/cost queries
    "pricing": [
        "How much does {topic} cost?",
        "What is the pricing for {topic}?",
        "{topic} pricing plans",
    ],
    
    # Features/capabilities queries
    "features": [
        "What features does {topic} have?",
        "What can {topic} do?",
        "{topic} capabilities",
    ],
    
    # Review/reputation queries
    "reviews": [
        "Is {topic} any good?",
        "{topic} reviews",
        "What do people think about {topic}?",
    ],
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_all_template_categories() -> list:
    """Return list of all available template categories."""
    return list(QUERY_TEMPLATES.keys())


def get_templates_for_category(category: str) -> list:
    """Get templates for a specific category."""
    return QUERY_TEMPLATES.get(category, [])


def format_template(template: str, topic: str) -> str:
    """Format a template string with the given topic."""
    return template.format(topic=topic)
