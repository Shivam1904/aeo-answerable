"""
Page-Level Metrics Module.

Contains all metrics computed on individual pages for extractability
and structure scoring.
"""
from typing import List, Type

from ..base import BaseMetric

# Import all page-level metric classes
from .heading_hierarchy_validity import HeadingHierarchyValidityMetric
from .liftable_units_density import LiftableUnitsDensityMetric
from .semantic_tree_depth import SemanticTreeDepthMetric
from .dom_to_token_ratio import DOMToTokenRatioMetric
from .main_content_detectability import MainContentDetectabilityMetric
from .chunk_boundary_integrity import ChunkBoundaryIntegrityMetric
from .duplicate_boilerplate_rate import DuplicateBoilerplateRateMetric
from .answer_first_compliance import AnswerFirstComplianceMetric
from .anaphora_resolution import AnaphoraResolutionMetric
from .heading_predictive_power import HeadingPredictivePowerMetric
from .entity_schema_mapping import EntitySchemaMappingMetric
from .schema_coverage_by_intent import SchemaCoverageByIntentMetric
from .schema_quality_relationships import SchemaQualityRelationshipsMetric
from .citation_source_density import CitationSourceDensityMetric
from .freshness_signal_strength import FreshnessSignalStrengthMetric
from .author_eeat_signals import AuthorEEATSignalsMetric


# Ordered list of all page-level metrics
PAGE_LEVEL_METRICS: List[Type[BaseMetric]] = [
    # Structure metrics
    HeadingHierarchyValidityMetric,
    SemanticTreeDepthMetric,
    MainContentDetectabilityMetric,
    
    # Efficiency metrics
    DOMToTokenRatioMetric,
    LiftableUnitsDensityMetric,
    DuplicateBoilerplateRateMetric,
    
    # Retrieval metrics
    ChunkBoundaryIntegrityMetric,
    
    # Content quality metrics
    AnswerFirstComplianceMetric,
    AnaphoraResolutionMetric,
    
    # Semantic metrics
    HeadingPredictivePowerMetric,
    
    # Schema metrics
    EntitySchemaMappingMetric,
    SchemaCoverageByIntentMetric,
    SchemaQualityRelationshipsMetric,
    
    # Trust metrics
    CitationSourceDensityMetric,
    FreshnessSignalStrengthMetric,
    AuthorEEATSignalsMetric,
]

__all__ = [
    "PAGE_LEVEL_METRICS",
    "HeadingHierarchyValidityMetric",
    "LiftableUnitsDensityMetric",
    "SemanticTreeDepthMetric",
    "DOMToTokenRatioMetric",
    "MainContentDetectabilityMetric",
    "ChunkBoundaryIntegrityMetric",
    "DuplicateBoilerplateRateMetric",
    "AnswerFirstComplianceMetric",
    "AnaphoraResolutionMetric",
    "HeadingPredictivePowerMetric",
    "EntitySchemaMappingMetric",
    "SchemaCoverageByIntentMetric",
    "SchemaQualityRelationshipsMetric",
    "CitationSourceDensityMetric",
    "FreshnessSignalStrengthMetric",
    "AuthorEEATSignalsMetric",
]
