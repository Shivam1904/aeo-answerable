"""
Base Reasoning Engine Module.

Defines the abstract interface for all reasoning engines.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Literal
from pydantic import BaseModel


class Reason(BaseModel):
    """
    A single reason explaining a metric result.
    
    Attributes:
        type: The type of reason (fact, issue, suggestion).
        message: Human-readable explanation.
        examples: Optional list of specific examples supporting this reason.
    """
    type: Literal["fact", "issue", "suggestion"]
    message: str
    examples: List[str] = []


class Explanation(BaseModel):
    """
    Complete explanation for a metric result.
    
    Attributes:
        severity: Overall severity based on score (success, warning, error).
        reasons: List of reasons explaining the score.
    """
    severity: Literal["success", "warning", "error"]
    reasons: List[Reason]


class ReasoningEngine(ABC):
    """
    Abstract base class for reasoning engines.
    
    A reasoning engine interprets raw metric diagnostic data and generates
    human-readable explanations. This allows the same diagnostic data to be
    used for both scoring and explanation generation.
    """
    
    @abstractmethod
    def explain(
        self,
        metric_name: str,
        metric_result: Dict[str, Any],
        score: float
    ) -> Explanation:
        """
        Generate human-readable explanations from metric diagnostic data.
        
        Args:
            metric_name: The name of the metric (e.g., 'dom_to_token_ratio').
            metric_result: The raw metric result dictionary from compute().
            score: The normalized score (0.0 to 1.0).
            
        Returns:
            Explanation object containing severity and list of reasons.
        """
        pass
    
    def _get_severity(self, score: float) -> Literal["success", "warning", "error"]:
        """
        Determine severity level based on score.
        
        Args:
            score: Normalized score (0.0 to 1.0).
            
        Returns:
            Severity level: success (≥0.8), warning (0.5-0.79), error (<0.5).
        """
        if score >= 0.8:
            return "success"
        elif score >= 0.5:
            return "warning"
        else:
            return "error"
