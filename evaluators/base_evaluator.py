"""
Base Evaluator Class for LLM Evaluation Framework
"""

from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any, Optional

class BaseEvaluator(ABC):
    """Abstract base class for all LLM evaluators"""
    
    def __init__(self, name: str, description: str, score_range: Tuple[float, float] = (0.0, 1.0)):
        self.name = name
        self.description = description
        self.score_range = score_range
    
    @abstractmethod
    def evaluate(self, query: str, answer: str, context: Optional[str] = None, 
                expected_answer: Optional[str] = None) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate the LLM response
        
        Args:
            query: The input query/question
            answer: The LLM's response to evaluate
            context: Optional context information
            expected_answer: Optional expected/reference answer
            
        Returns:
            Tuple of (score, evaluation_details)
        """
        pass
    
    def _normalize_score(self, raw_score: float, raw_range: Tuple[float, float] = None) -> float:
        """Normalize score to the evaluator's score range"""
        if raw_range is None:
            raw_range = self.score_range
        
        raw_min, raw_max = raw_range
        target_min, target_max = self.score_range
        
        # Normalize to 0-1 first
        normalized = (raw_score - raw_min) / (raw_max - raw_min)
        
        # Scale to target range
        scaled = normalized * (target_max - target_min) + target_min
        
        # Clamp to target range
        return max(target_min, min(target_max, scaled))
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate basic text similarity using word overlap"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _count_sentences(self, text: str) -> int:
        """Count sentences in text"""
        import re
        sentences = re.split(r'[.!?]+', text.strip())
        return len([s for s in sentences if s.strip()])
    
    def _count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())
