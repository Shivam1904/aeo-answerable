"""
Deterministic Reasoning Engine.

Uses rule-based logic to generate explanations from metric diagnostic data.
"""
from typing import Dict, Any
from .base import ReasoningEngine, Explanation, Reason


class DeterministicReasoningEngine(ReasoningEngine):
    """
    Rule-based reasoning engine that interprets metric diagnostic data.
    
    For each metric, applies specific logic to generate human-readable
    explanations based on the diagnostic fields returned by compute().
    """
    
    def explain(
        self,
        metric_name: str,
        metric_result: Dict[str, Any],
        score: float
    ) -> Explanation:
        """
        Generate explanations using deterministic rules.
        
        Args:
            metric_name: The name of the metric.
            metric_result: The raw metric result dictionary.
            score: The normalized score (0.0 to 1.0).
            
        Returns:
            Explanation object with severity and reasons.
        """
        severity = self._get_severity(score)
        
        # Dispatch to metric-specific handler
        handler_name = f"_explain_{metric_name}"
        if hasattr(self, handler_name):
            handler = getattr(self, handler_name)
            reasons = handler(metric_result, score)
        else:
            # Generic fallback
            reasons = self._explain_generic(metric_result, score)
        
        return Explanation(severity=severity, reasons=reasons)
    
    # ===== Metric-Specific Handlers =====
    
    def _explain_dom_to_token_ratio(
        self, 
        result: Dict[str, Any], 
        score: float
    ) -> list[Reason]:
        """Explain DOM-to-token ratio results."""
        reasons = []
        
        ratio = result.get("ratio", 0)
        html_tokens = result.get("html_tokens", 0)
        text_tokens = result.get("text_tokens", 0)
        rating = result.get("efficiency_rating", "unknown")
        
        # Always explain the measurement
        reasons.append(Reason(
            type="fact",
            message=f"Content efficiency is {rating} ({ratio:.1%} of HTML is meaningful text)."
        ))
        
        if score < 0.8:
            gap = 0.5 - ratio
            reasons.append(Reason(
                type="issue",
                message=f"Your page has {html_tokens:,} HTML tokens but only {text_tokens:,} content tokens. Target is 50% efficiency (currently {ratio:.1%}).",
                examples=[f"Need to improve ratio by {gap:.1%} to reach target"]
            ))
            
            reasons.append(Reason(
                type="suggestion",
                message="Reduce HTML bloat by minimizing wrapper divs, removing unused scripts, and simplifying DOM structure."
            ))
        else:
            reasons.append(Reason(
                type="fact",
                message=f"Good balance: {text_tokens:,} content tokens out of {html_tokens:,} total HTML tokens."
            ))
        
        return reasons
    
    def _explain_heading_predictive_power(
        self,
        result: Dict[str, Any],
        score: float
    ) -> list[Reason]:
        """Explain heading predictive power results."""
        reasons = []
        
        headings_analyzed = result.get("headings_analyzed", 0)
        avg_similarity = result.get("avg_similarity", 0)
        low_sim_headings = result.get("low_similarity_headings", [])
        
        reasons.append(Reason(
            type="fact",
            message=f"Analyzed {headings_analyzed} headings with {avg_similarity:.0%} average semantic overlap with their content."
        ))
        
        if score < 0.8 and low_sim_headings:
            reasons.append(Reason(
                type="issue",
                message=f"{len(low_sim_headings)} heading(s) don't strongly predict their content, which hurts RAG retrieval accuracy.",
                examples=low_sim_headings[:5]
            ))
            
            reasons.append(Reason(
                type="suggestion",
                message="Use descriptive headings that include key terms from the content below them."
            ))
        elif score >= 0.8:
            reasons.append(Reason(
                type="fact",
                message="Headings are descriptive and semantically aligned with their content."
            ))
        
        return reasons
    
    def _explain_answer_first_compliance(
        self,
        result: Dict[str, Any],
        score: float
    ) -> list[Reason]:
        """Explain answer-first compliance results."""
        reasons = []
        
        sections_analyzed = result.get("sections_analyzed", 0)
        compliant_sections = result.get("compliant_sections", 0)
        compliance_rate = result.get("compliance_rate", 0)
        non_compliant = result.get("non_compliant_examples", [])
        
        reasons.append(Reason(
            type="fact",
            message=f"{compliant_sections}/{sections_analyzed} sections ({compliance_rate:.0%}) follow answer-first writing patterns."
        ))
        
        if score < 0.8 and non_compliant:
            reasons.append(Reason(
                type="issue",
                message="Some sections start with fluff or introductory text instead of direct answers.",
                examples=non_compliant[:3]
            ))
            
            reasons.append(Reason(
                type="suggestion",
                message="Start sections with direct answers (e.g., 'X is...', 'To do Y...') rather than 'In this article...' or 'Many people wonder...'"
            ))
        elif score >= 0.8:
            reasons.append(Reason(
                type="fact",
                message="Content follows answer-first best practices, making it easy for AI to extract direct answers."
            ))
        
        return reasons
    
    # ===== STRUCTURE METRICS =====
    
    def _explain_heading_hierarchy_validity(
        self,
        result: Dict[str, Any],
        score: float
    ) -> list[Reason]:
        """Explain heading hierarchy validity results."""
        reasons = []
        
        h1_count = result.get("h1_count", 0)
        total_headings = result.get("total_headings", 0)
        hierarchy_valid = result.get("hierarchy_valid", False)
        skipped_levels = result.get("skipped_levels", [])
        
        reasons.append(Reason(
            type="fact",
            message=f"Page has {h1_count} H1 tag(s) and {total_headings} total headings."
        ))
        
        if score < 0.8:
            if h1_count == 0:
                reasons.append(Reason(
                    type="issue",
                    message="Missing H1 tag. Every page needs exactly one H1 as the main title for SEO and AI crawlers."
                ))
            elif h1_count > 1:
                reasons.append(Reason(
                    type="issue",
                    message=f"Found {h1_count} H1 tags. Use only one H1 per page—it's the primary document title."
                ))
            
            if skipped_levels:
                reasons.append(Reason(
                    type="issue",
                    message="Heading hierarchy skips levels, which confuses screen readers and AI parsers.",
                    examples=skipped_levels[:3]
                ))
            
            reasons.append(Reason(
                type="suggestion",
                message="Use headings in order: H1 (page title) → H2 (main sections) → H3 (subsections). Never skip levels."
            ))
        else:
            reasons.append(Reason(
                type="fact",
                message="Heading structure is semantically valid and follows best practices."
            ))
        
        return reasons
    
    def _explain_semantic_tree_depth(
        self,
        result: Dict[str, Any],
        score: float
    ) -> list[Reason]:
        """Explain semantic tree depth results."""
        reasons = []
        
        max_depth = result.get("max_depth", 0)
        avg_depth = result.get("avg_depth", 0)
        deep_nodes = result.get("deep_nodes_count", 0)
        
        reasons.append(Reason(
            type="fact",
            message=f"DOM tree has max depth of {max_depth} levels (average: {avg_depth:.1f})."
        ))
        
        if score < 0.8:
            reasons.append(Reason(
                type="issue",
                message=f"Found {deep_nodes} nodes deeper than 10 levels. Deep nesting makes content extraction slow and error-prone for AI crawlers."
            ))
            
            reasons.append(Reason(
                type="suggestion",
                message="Flatten your HTML structure. Remove unnecessary wrapper divs and use CSS flexbox/grid instead of nested containers."
            ))
        else:
            reasons.append(Reason(
                type="fact",
                message="DOM structure is reasonably flat, making content easy to extract."
            ))
        
        return reasons
    
    def _explain_main_content_detectability(
        self,
        result: Dict[str, Any],
        score: float
    ) -> list[Reason]:
        """Explain main content detectability results."""
        reasons = []
        
        has_main = result.get("has_main_tag", False)
        has_article = result.get("has_article_tag", False)
        word_count = result.get("extractor_word_count", 0)
        extraction_quality = result.get("extraction_quality", "none")
        
        if has_main or has_article:
            tag = "<main>" if has_main else "<article>"
            reasons.append(Reason(
                type="fact",
                message=f"Page uses semantic {tag} tag, making content extraction reliable."
            ))
        else:
            reasons.append(Reason(
                type="fact",
                message="Page lacks semantic <main> or <article> tags."
            ))
        
        reasons.append(Reason(
            type="fact",
            message=f"Content extractor successfully extracted {word_count} words ({extraction_quality} quality)."
        ))
        
        if score < 0.8:
            if not has_main and not has_article:
                reasons.append(Reason(
                    type="issue",
                    message="Without <main> or <article> tags, AI crawlers must guess where your content starts and ends."
                ))
            
            if word_count < 100:
                reasons.append(Reason(
                    type="issue",
                    message=f"Only {word_count} words extracted. Content may be hidden in JavaScript or buried in navigation/ads."
                ))
            
            reasons.append(Reason(
                type="suggestion",
                message="Wrap your main content in a <main> tag. Ensure text is in the HTML, not dynamically loaded."
            ))
        else:
            reasons.append(Reason(
                type="fact",
                message="Main content is easily detectable and extractable."
            ))
        
        return reasons
    
    # ===== EFFICIENCY METRICS =====
    
    def _explain_liftable_units_density(
        self,
        result: Dict[str, Any],
        score: float
    ) -> list[Reason]:
        """Explain liftable units density results."""
        reasons = []
        
        lists = result.get("lists_count", 0)
        tables = result.get("tables_count", 0)
        faqs = result.get("faq_patterns", 0)
        total_units = result.get("total_units", 0)
        density = result.get("density_per_1k", 0)
        
        reasons.append(Reason(
            type="fact",
            message=f"Found {total_units} structured units: {lists} lists, {tables} tables, {faqs} FAQ patterns ({density:.1f} per 1000 words)."
        ))
        
        if score < 0.8:
            reasons.append(Reason(
                type="issue",
                message="Low structured content density. AI systems prefer scannable, quotable units like lists and FAQs."
            ))
            
            suggestions = []
            if lists == 0:
                suggestions.append("Add bulleted/numbered lists for steps, features, or benefits")
            if faqs == 0:
                suggestions.append("Include FAQ sections with question-answer pairs")
            if tables == 0 and "data" in result.get("note", "").lower():
                suggestions.append("Use tables for comparison data or specifications")
            
            if suggestions:
                reasons.append(Reason(
                    type="suggestion",
                    message="Improve structure: " + "; ".join(suggestions) + "."
                ))
        else:
            reasons.append(Reason(
                type="fact",
                message="Good density of structured, liftable content units."
            ))
        
        return reasons
    
    def _explain_duplicate_boilerplate_rate(
        self,
        result: Dict[str, Any],
        score: float
    ) -> list[Reason]:
        """Explain duplicate/boilerplate rate results."""
        reasons = []
        
        total_blocks = result.get("total_blocks", 0)
        duplicate_blocks = result.get("duplicate_blocks", 0)
        boilerplate_blocks = result.get("boilerplate_blocks", 0)
        duplicate_pct = result.get("duplicate_content_pct", 0)
        examples = result.get("duplicate_examples", [])
        
        reasons.append(Reason(
            type="fact",
            message=f"Analyzed {total_blocks} content blocks: {duplicate_blocks} duplicates, {boilerplate_blocks} boilerplate ({duplicate_pct:.0%} of content)."
        ))
        
        if score < 0.8 and (duplicate_blocks > 0 or boilerplate_blocks > 0):
            reasons.append(Reason(
                type="issue",
                message=f"{duplicate_pct:.0%} of your content is repetitive (navigation, footers, cookie notices). This pollutes AI embeddings and hurts retrieval precision.",
                examples=examples[:3]
            ))
            
            reasons.append(Reason(
                type="suggestion",
                message="Use semantic tags like <nav>, <footer>, <aside> to help crawlers ignore boilerplate. Remove duplicate text blocks."
            ))
        else:
            reasons.append(Reason(
                type="fact",
                message="Content is unique with minimal boilerplate repetition."
            ))
        
        return reasons
    
    # ===== RETRIEVAL METRICS =====
    
    def _explain_chunk_boundary_integrity(
        self,
        result: Dict[str, Any],
        score: float
    ) -> list[Reason]:
        """Explain chunk boundary integrity results."""
        reasons = []
        
        total_chunks = result.get("total_chunks", 0)
        clean_chunks = result.get("clean_boundary_chunks", 0)
        broken_chunks = total_chunks - clean_chunks if total_chunks > 0 else 0
        
        if total_chunks == 0:
            reasons.append(Reason(
                type="fact",
                message="No chunkable content detected (page may be too short)."
            ))
        else:
            reasons.append(Reason(
                type="fact",
                message=f"Analyzed {total_chunks} chunks: {clean_chunks} have clean boundaries, {broken_chunks} break mid-sentence."
            ))
            
            if score < 0.8 and broken_chunks > 0:
                reasons.append(Reason(
                    type="issue",
                    message=f"{broken_chunks} chunks break mid-sentence, causing incomplete context in RAG retrieval."
                ))
                
                reasons.append(Reason(
                    type="suggestion",
                    message="Ensure paragraphs are well-formed and sections end cleanly. Use semantic HTML (e.g., <p>, <section>) to define natural boundaries."
                ))
            else:
                reasons.append(Reason(
                    type="fact",
                    message="Content chunks respect natural sentence and paragraph boundaries."
                ))
        
        return reasons
    
    # ===== CONTENT QUALITY METRICS =====
    
    def _explain_anaphora_resolution(
        self,
        result: Dict[str, Any],
        score: float
    ) -> list[Reason]:
        """Explain anaphora resolution (pronoun clarity) results."""
        reasons = []
        
        pronoun_count = result.get("total_pronouns", 0)
        word_count = result.get("word_count", 0)
        pronoun_density = result.get("pronoun_density", 0)
        ambiguous_examples = result.get("ambiguous_examples", [])
        
        reasons.append(Reason(
            type="fact",
            message=f"Found {pronoun_count} pronouns in {word_count} words ({pronoun_density:.1%} density)."
        ))
        
        if score < 0.8:
            if pronoun_density > 0.05:
                reasons.append(Reason(
                    type="issue",
                    message=f"High pronoun density ({pronoun_density:.1%}). Pronouns like 'it', 'this', 'they' lose context when content is chunked for AI retrieval."
                ))
            
            if ambiguous_examples:
                reasons.append(Reason(
                    type="issue",
                    message="Found sentences starting with ambiguous pronouns:",
                    examples=ambiguous_examples[:3]
                ))
            
            reasons.append(Reason(
                type="suggestion",
                message="Replace vague pronouns with specific nouns. Instead of 'It offers...', write 'The platform offers...'."
            ))
        else:
            reasons.append(Reason(
                type="fact",
                message="Pronouns are used sparingly, ensuring clarity when content is chunked."
            ))
        
        return reasons
    
    # ===== SCHEMA METRICS =====
    
    def _explain_entity_schema_mapping(
        self,
        result: Dict[str, Any],
        score: float
    ) -> list[Reason]:
        """Explain entity-to-schema mapping results."""
        reasons = []
        
        entities_found = result.get("entities_found", 0)
        mapping_rate = result.get("mapping_rate", 0)
        unmapped = result.get("unmapped_entities", [])
        
        if isinstance(entities_found, list):
            entities_found = len(entities_found)
        if isinstance(unmapped, list):
            unmapped_count = len(unmapped)
        else:
            unmapped_count = unmapped
        
        reasons.append(Reason(
            type="fact",
            message=f"Detected {entities_found} entities on page, {mapping_rate:.0%} mapped to Schema.org types."
        ))
        
        if score < 0.8 and unmapped_count > 0:
            reasons.append(Reason(
                type="issue",
                message=f"{unmapped_count} important entities lack Schema.org markup, reducing AI understanding and rich snippet eligibility.",
                examples=unmapped[:5] if isinstance(unmapped, list) else []
            ))
            
            reasons.append(Reason(
                type="suggestion",
                message="Add JSON-LD schema for key entities (Person, Organization, Product, Event). Use schema.org markup generators."
            ))
        elif score >= 0.8:
            reasons.append(Reason(
                type="fact",
                message="Most entities are properly mapped to Schema.org types."
            ))
        
        return reasons
    
    def _explain_schema_coverage_by_intent(
        self,
        result: Dict[str, Any],
        score: float
    ) -> list[Reason]:
        """Explain schema coverage by intent results."""
        reasons = []
        
        detected_intent = result.get("detected_intent", "unknown")
        confidence = result.get("intent_confidence", 0)
        expected_schemas = result.get("expected_schema_types", [])
        
        if isinstance(expected_schemas, list):
            schema_count = len(expected_schemas)
        else:
            schema_count = expected_schemas
        
        reasons.append(Reason(
            type="fact",
            message=f"Detected page intent: '{detected_intent}' ({confidence:.0%} confidence). Expects {schema_count} schema type(s)."
        ))
        
        if score < 0.8:
            reasons.append(Reason(
                type="issue",
                message=f"Page appears to be a '{detected_intent}' page but lacks expected schema types.",
                examples=expected_schemas[:3] if isinstance(expected_schemas, list) else []
            ))
            
            intent_suggestions = {
                "how-to": "Add HowTo schema with step-by-step instructions",
                "article": "Add Article or BlogPosting schema with author and publish date",
                "product": "Add Product schema with name, price, and reviews",
                "faq": "Add FAQPage schema with Question/Answer pairs",
                "local-business": "Add LocalBusiness schema with address and hours"
            }
            
            suggestion = intent_suggestions.get(detected_intent, f"Add schema types appropriate for {detected_intent} content")
            reasons.append(Reason(
                type="suggestion",
                message=suggestion + "."
            ))
        else:
            reasons.append(Reason(
                type="fact",
                message="Page has appropriate schema coverage for its detected intent."
            ))
        
        return reasons
    
    def _explain_schema_quality_relationships(
        self,
        result: Dict[str, Any],
        score: float
    ) -> list[Reason]:
        """Explain schema relationship quality results."""
        reasons = []
        
        schema_blocks = result.get("schema_blocks", 0)
        completeness = result.get("completeness_score", 0)
        has_relationships = result.get("has_relationships", False)
        
        if schema_blocks == 0:
            reasons.append(Reason(
                type="fact",
                message="No JSON-LD schema found on page."
            ))
            
            if score < 0.8:
                reasons.append(Reason(
                    type="issue",
                    message="Missing structured data. AI engines rely on schema to understand relationships between entities."
                ))
                
                reasons.append(Reason(
                    type="suggestion",
                    message="Add JSON-LD schema linking related entities with @id properties (e.g., link Article → Author → Organization)."
                ))
        else:
            reasons.append(Reason(
                type="fact",
                message=f"Found {schema_blocks} schema block(s) with {completeness:.0%} relationship completeness."
            ))
            
            if score < 0.8:
                if not has_relationships:
                    reasons.append(Reason(
                        type="issue",
                        message="Schema blocks are isolated—no @id links connecting related entities (e.g., Article to Author)."
                    ))
                else:
                    reasons.append(Reason(
                        type="issue",
                        message="Schema relationships are incomplete or shallow."
                    ))
                
                reasons.append(Reason(
                    type="suggestion",
                    message="Use @id to create a knowledge graph: Article → author (@id) → Person → worksFor (@id) → Organization."
                ))
            else:
                reasons.append(Reason(
                    type="fact",
                    message="Schema entities are well-connected with @id relationships."
                ))
        
        return reasons
    
    # ===== TRUST METRICS =====
    
    def _explain_citation_source_density(
        self,
        result: Dict[str, Any],
        score: float
    ) -> list[Reason]:
        """Explain citation density results."""
        reasons = []
        
        claims_detected = result.get("factual_claims_detected", 0)
        text_citations = result.get("text_citations", 0)
        citation_links = result.get("citation_links", 0)
        
        if claims_detected == 0:
            reasons.append(Reason(
                type="fact",
                message="No factual claims detected (may be informational/navigational page)."
            ))
        else:
            reasons.append(Reason(
                type="fact",
                message=f"Detected {claims_detected} factual claim(s) with {text_citations} citation marker(s) and {citation_links} external links."
            ))
            
            if score < 0.8:
                reasons.append(Reason(
                    type="issue",
                    message="Claims lack authoritative citations. AI systems favor content with verifiable sources."
                ))
                
                reasons.append(Reason(
                    type="suggestion",
                    message="Link to authoritative sources (.gov, .edu, research papers) when making factual claims. Use citation formats like [1] or (Source)."
                ))
            else:
                reasons.append(Reason(
                    type="fact",
                    message="Good citation density with authoritative external links."
                ))
        
        return reasons
    
    def _explain_freshness_signal_strength(
        self,
        result: Dict[str, Any],
        score: float
    ) -> list[Reason]:
        """Explain freshness signal results."""
        reasons = []
        
        signal_count = result.get("signal_count", 0)
        dates_consistent = result.get("dates_consistent", True)
        has_signals = result.get("has_freshness_signals", False)
        
        if has_signals:
            reasons.append(Reason(
                type="fact",
                message=f"Found {signal_count} freshness signal(s) (published/updated dates)."
            ))
            
            if not dates_consistent:
                reasons.append(Reason(
                    type="issue",
                    message="Dates are inconsistent across visible text, schema, and meta tags."
                ))
        else:
            reasons.append(Reason(
                type="fact",
                message="No freshness signals detected (no published or updated dates)."
            ))
        
        if score < 0.8:
            if not has_signals:
                reasons.append(Reason(
                    type="issue",
                    message="Missing publication/update dates. AI systems prioritize fresh, timestamped content for queries like 'latest' or 'current'."
                ))
            
            reasons.append(Reason(
                type="suggestion",
                message="Add visible 'Last Updated' date at top of page. Include datePublished and dateModified in Article schema."
            ))
        else:
            reasons.append(Reason(
                type="fact",
                message="Page has clear, consistent freshness signals."
            ))
        
        return reasons
    
    def _explain_author_eeat_signals(
        self,
        result: Dict[str, Any],
        score: float
    ) -> list[Reason]:
        """Explain E-E-A-T (authorship) signal results."""
        reasons = []
        
        has_byline = result.get("has_author_byline", False)
        has_credentials = result.get("has_credentials", False)
        has_person_schema = result.get("has_person_schema", False)
        
        signals_found = sum([has_byline, has_credentials, has_person_schema])
        
        reasons.append(Reason(
            type="fact",
            message=f"Found {signals_found}/3 E-E-A-T signals: Author byline ({has_byline}), Credentials ({has_credentials}), Person schema ({has_person_schema})."
        ))
        
        if score < 0.8:
            missing = []
            if not has_byline:
                missing.append("visible author name/byline")
            if not has_credentials:
                missing.append("author bio or credentials")
            if not has_person_schema:
                missing.append("Person schema markup")
            
            reasons.append(Reason(
                type="issue",
                message=f"Missing E-E-A-T signals: {', '.join(missing)}. AI systems favor content with transparent authorship.",
                examples=missing
            ))
            
            reasons.append(Reason(
                type="suggestion",
                message="Add 'Written by [Name]' byline, link to author bio page, include Person schema with author's credentials/expertise."
            ))
        else:
            reasons.append(Reason(
                type="fact",
                message="Strong E-E-A-T signals with clear authorship and expertise indicators."
            ))
        
        return reasons
    
    # ===== ENHANCED GENERIC FALLBACK =====
    
    def _explain_generic(
        self,
        result: Dict[str, Any],
        score: float
    ) -> list[Reason]:
        """
        Enhanced generic fallback with maximum detail.
        
        Shows ALL diagnostic fields in a structured, informative way.
        """
        reasons = []
        
        # Add score context
        pct = int(score * 100)
        if score >= 0.8:
            reasons.append(Reason(
                type="fact",
                message=f"This metric scored {pct}% (passing threshold)."
            ))
        elif score >= 0.5:
            reasons.append(Reason(
                type="fact",
                message=f"This metric scored {pct}% (needs improvement)."
            ))
        else:
            reasons.append(Reason(
                type="fact",
                message=f"This metric scored {pct}% (critical issues detected)."
            ))
        
        # Extract ALL diagnostic fields
        standard_fields = {"metric", "score", "weight", "error", "note", "explanations"}
        diagnostic_fields = {
            k: v for k, v in result.items()
            if k not in standard_fields and v is not None and v != "" and v != []
        }
        
        if diagnostic_fields:
            # Group fields by type for better organization
            facts = []
            issues = []
            data_points = []
            
            for key, value in diagnostic_fields.items():
                label = key.replace("_", " ").title()
                
                # Format value appropriately
                if isinstance(value, bool):
                    val_str = "✓ Yes" if value else "✗ No"
                    fact_msg = f"{label}: {val_str}"
                    if not value and score < 0.8:
                        issues.append(f"Missing: {label}")
                    facts.append(fact_msg)
                    
                elif isinstance(value, (int, float)):
                    if isinstance(value, float):
                        val_str = f"{value:.3f}"
                    else:
                        val_str = f"{value:,}"
                    facts.append(f"{label}: {val_str}")
                    
                elif isinstance(value, list):
                    if len(value) > 0:
                        data_points.append((label, value))
                    else:
                        facts.append(f"{label}: None found")
                        
                elif isinstance(value, dict):
                    # Format dict as key-value pairs
                    dict_items = [f"{k}: {v}" for k, v in value.items()]
                    data_points.append((label, dict_items))
                    
                else:
                    facts.append(f"{label}: {value}")
            
            # Add facts as individual reasons
            for fact in facts:
                reasons.append(Reason(
                    type="fact",
                    message=fact
                ))
            
            # Add data points with examples
            for label, items in data_points:
                if isinstance(items, list) and len(items) > 0:
                    preview_items = items[:5]
                    message = f"{label} ({len(items)} items)" if len(items) > 5 else f"{label}"
                    reasons.append(Reason(
                        type="fact",
                        message=message,
                        examples=[str(item) for item in preview_items]
                    ))
            
            # Add issues if score is low
            if issues and score < 0.8:
                reasons.append(Reason(
                    type="issue",
                    message="Missing or failing checks:",
                    examples=issues
                ))
        
        # Add note if present
        if result.get("note"):
            reasons.append(Reason(
                type="fact",
                message=f"Note: {result['note']}"
            ))
        
        # Add generic suggestion for low scores
        if score < 0.5 and len(reasons) > 1:
            reasons.append(Reason(
                type="suggestion",
                message="This metric requires attention. Review the diagnostic details above to identify specific improvements needed."
            ))
        
        return reasons
