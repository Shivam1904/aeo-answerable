"""
Schema Suggestions Module.

Analyzes content and recommends Schema.org structured data
to improve AI engine understanding and citability.
"""
from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel
import re


class SchemaSuggestion(BaseModel):
    """
    A single schema.org markup suggestion.
    
    Attributes:
        schema_type: The Schema.org type (e.g., "FAQPage", "HowTo")
        name: Human-readable name
        reason: Why this schema is recommended
        implementation_priority: How important this is
        example_json_ld: Example JSON-LD markup
        applicable_pages: Types of pages this applies to
        impact_on_ai: How this helps AI engines
    """
    schema_type: str
    name: str
    reason: str
    implementation_priority: Literal["critical", "recommended", "nice_to_have"]
    example_json_ld: Dict[str, Any]
    applicable_pages: List[str]
    impact_on_ai: str


class SchemaAnalysisReport(BaseModel):
    """
    Complete schema suggestion report.
    
    Attributes:
        url: The analyzed URL
        total_suggestions: Number of schema suggestions
        critical_count: Number of critical suggestions
        suggestions: List of schema suggestions
        general_tips: General schema implementation tips
    """
    url: str
    total_suggestions: int
    critical_count: int
    suggestions: List[SchemaSuggestion]
    general_tips: List[str]


# =============================================================================
# SCHEMA TEMPLATES
# =============================================================================

SCHEMA_TEMPLATES = {
    "Organization": {
        "name": "Organization",
        "description": "Basic organization information",
        "priority": "critical",
        "impact": "Helps AI engines identify and describe your company accurately",
        "applicable_to": ["homepage", "about page"],
        "template": {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Your Company Name",
            "url": "https://yourcompany.com",
            "logo": "https://yourcompany.com/logo.png",
            "description": "Brief description of your company",
            "foundingDate": "2020",
            "sameAs": [
                "https://twitter.com/yourcompany",
                "https://linkedin.com/company/yourcompany"
            ]
        }
    },
    "FAQPage": {
        "name": "FAQ Page",
        "description": "Frequently Asked Questions markup",
        "priority": "critical",
        "impact": "AI engines can directly cite Q&A pairs from your content",
        "applicable_to": ["faq page", "support page", "product page"],
        "template": {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": "What is your product?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Our product is a comprehensive solution that..."
                    }
                }
            ]
        }
    },
    "HowTo": {
        "name": "How-To Guide",
        "description": "Step-by-step instructions markup",
        "priority": "recommended",
        "impact": "AI engines can extract and cite specific steps from your guides",
        "applicable_to": ["tutorial", "guide", "documentation"],
        "template": {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": "How to Use Our Product",
            "description": "Learn how to get started with our product",
            "step": [
                {
                    "@type": "HowToStep",
                    "name": "Step 1: Sign Up",
                    "text": "Create an account at ourwebsite.com"
                },
                {
                    "@type": "HowToStep",
                    "name": "Step 2: Configure Settings",
                    "text": "Navigate to settings and configure your preferences"
                }
            ]
        }
    },
    "Product": {
        "name": "Product",
        "description": "Product information markup",
        "priority": "critical",
        "impact": "AI engines can accurately cite product features, pricing, and reviews",
        "applicable_to": ["product page", "pricing page"],
        "template": {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Product Name",
            "description": "Product description",
            "brand": {
                "@type": "Brand",
                "name": "Your Brand"
            },
            "offers": {
                "@type": "Offer",
                "price": "99.00",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock"
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.5",
                "reviewCount": "100"
            }
        }
    },
    "Article": {
        "name": "Article",
        "description": "Blog post or article markup",
        "priority": "recommended",
        "impact": "Improves content attribution and authorship signals",
        "applicable_to": ["blog post", "news article", "thought leadership"],
        "template": {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Article Title",
            "description": "Article description",
            "author": {
                "@type": "Person",
                "name": "Author Name"
            },
            "datePublished": "2024-01-01",
            "dateModified": "2024-01-15",
            "publisher": {
                "@type": "Organization",
                "name": "Your Company"
            }
        }
    },
    "SoftwareApplication": {
        "name": "Software Application",
        "description": "Software/SaaS product markup",
        "priority": "critical",
        "impact": "AI engines understand your software's purpose and features",
        "applicable_to": ["software product page", "app landing page"],
        "template": {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "App Name",
            "description": "What your software does",
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "Web, iOS, Android",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.7",
                "ratingCount": "500"
            }
        }
    },
    "WebSite": {
        "name": "WebSite with Search",
        "description": "Website-level markup with search action",
        "priority": "recommended",
        "impact": "Helps AI engines understand site structure and search capability",
        "applicable_to": ["homepage"],
        "template": {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Your Website",
            "url": "https://yourwebsite.com",
            "potentialAction": {
                "@type": "SearchAction",
                "target": "https://yourwebsite.com/search?q={search_term_string}",
                "query-input": "required name=search_term_string"
            }
        }
    },
    "BreadcrumbList": {
        "name": "Breadcrumb Navigation",
        "description": "Page hierarchy markup",
        "priority": "nice_to_have",
        "impact": "Helps AI understand your site structure and page relationships",
        "applicable_to": ["all pages except homepage"],
        "template": {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home",
                    "item": "https://yourwebsite.com"
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Products",
                    "item": "https://yourwebsite.com/products"
                }
            ]
        }
    },
}


def analyze_content_for_schema(
    content: str,
    url: str,
    page_title: str = "",
    industry: str = "",
) -> List[SchemaSuggestion]:
    """
    Analyze page content and suggest appropriate schemas.
    
    Args:
        content: The page content text
        url: The page URL
        page_title: The page title
        industry: Optional industry context
        
    Returns:
        List of schema suggestions
    """
    suggestions = []
    content_lower = content.lower()
    title_lower = page_title.lower()
    url_lower = url.lower()
    
    # Always recommend Organization for main site
    if _is_homepage(url) or "about" in url_lower:
        suggestions.append(_create_suggestion("Organization"))
    
    # Check for FAQ content
    if _has_faq_content(content_lower, title_lower):
        suggestions.append(_create_suggestion("FAQPage"))
    
    # Check for How-To content
    if _has_howto_content(content_lower, title_lower):
        suggestions.append(_create_suggestion("HowTo"))
    
    # Check for Product content
    if _has_product_content(content_lower, url_lower, industry):
        suggestions.append(_create_suggestion("Product"))
    
    # Check for Article/Blog content
    if _has_article_content(url_lower, title_lower):
        suggestions.append(_create_suggestion("Article"))
    
    # Check for Software content
    if _has_software_content(content_lower, industry):
        suggestions.append(_create_suggestion("SoftwareApplication"))
    
    # Homepage gets WebSite schema
    if _is_homepage(url):
        suggestions.append(_create_suggestion("WebSite"))
    
    # Most pages benefit from breadcrumbs
    if not _is_homepage(url):
        suggestions.append(_create_suggestion("BreadcrumbList"))
    
    return suggestions


def _create_suggestion(schema_type: str) -> SchemaSuggestion:
    """Create a schema suggestion from template."""
    template = SCHEMA_TEMPLATES[schema_type]
    return SchemaSuggestion(
        schema_type=schema_type,
        name=template["name"],
        reason=template["description"],
        implementation_priority=template["priority"],
        example_json_ld=template["template"],
        applicable_pages=template["applicable_to"],
        impact_on_ai=template["impact"],
    )


def _is_homepage(url: str) -> bool:
    """Check if URL is the homepage."""
    # Remove protocol
    path = url.split("//")[-1]
    # Remove domain
    path = "/".join(path.split("/")[1:])
    return path == "" or path == "/" or path == "index.html"


def _has_faq_content(content: str, title: str) -> bool:
    """Check if content has FAQ patterns."""
    faq_patterns = [
        "frequently asked",
        "faq",
        "common questions",
        "q&a",
        "q & a",
    ]
    question_pattern = r'\?.*\n.*[A-Z]'  # Questions followed by answers
    
    has_faq_keyword = any(p in content or p in title for p in faq_patterns)
    has_qa_pattern = len(re.findall(question_pattern, content)) >= 3
    
    return has_faq_keyword or has_qa_pattern


def _has_howto_content(content: str, title: str) -> bool:
    """Check if content has how-to patterns."""
    howto_patterns = [
        "how to",
        "step by step",
        "step 1",
        "tutorial",
        "guide",
        "getting started",
        "instructions",
    ]
    return any(p in content or p in title for p in howto_patterns)


def _has_product_content(content: str, url: str, industry: str) -> bool:
    """Check if content is product-related."""
    product_patterns = [
        "pricing",
        "buy now",
        "add to cart",
        "product",
        "features",
        "plans",
        "$",
        "per month",
        "/mo",
    ]
    return any(p in content or p in url for p in product_patterns)


def _has_article_content(url: str, title: str) -> bool:
    """Check if content is article/blog."""
    article_patterns = [
        "blog",
        "article",
        "post",
        "news",
        "/blog/",
        "/articles/",
        "/posts/",
    ]
    return any(p in url or p in title for p in article_patterns)


def _has_software_content(content: str, industry: str) -> bool:
    """Check if content is software-related."""
    software_patterns = [
        "software",
        "saas",
        "platform",
        "app",
        "application",
        "tool",
        "api",
        "integration",
        "dashboard",
    ]
    return any(p in content for p in software_patterns) or industry.lower() in ["software", "saas", "tech"]


def generate_schema_report(
    url: str,
    content: str = "",
    page_title: str = "",
    industry: str = "",
) -> SchemaAnalysisReport:
    """
    Generate a complete schema suggestion report.
    
    Args:
        url: The page URL
        content: Page content (optional)
        page_title: Page title (optional)
        industry: Industry context (optional)
        
    Returns:
        Complete schema analysis report
    """
    suggestions = analyze_content_for_schema(content, url, page_title, industry)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        if s.schema_type not in seen:
            seen.add(s.schema_type)
            unique_suggestions.append(s)
    
    critical_count = sum(1 for s in unique_suggestions if s.implementation_priority == "critical")
    
    general_tips = [
        "Always validate your JSON-LD using Google's Rich Results Test",
        "Include schema markup in the <head> section or at the end of <body>",
        "Keep schema data consistent with visible page content",
        "Update dateModified when content changes",
        "Use specific schema types over generic ones when possible",
        "Test schema implementation in Google Search Console",
    ]
    
    return SchemaAnalysisReport(
        url=url,
        total_suggestions=len(unique_suggestions),
        critical_count=critical_count,
        suggestions=unique_suggestions,
        general_tips=general_tips,
    )
