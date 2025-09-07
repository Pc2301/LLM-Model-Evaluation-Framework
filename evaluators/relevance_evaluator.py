"""
Relevance Evaluator - Evaluates how relevant the answer is to the query
"""

from typing import Tuple, Dict, Any, Optional
from .base_evaluator import BaseEvaluator
import re

class RelevanceEvaluator(BaseEvaluator):
    """Evaluates the relevance of an answer to the given query"""
    
    def __init__(self):
        super().__init__(
            name="Relevance Evaluator",
            description="Measures how well the answer addresses the specific query",
            score_range=(0.0, 1.0)
        )
    
    def evaluate(self, query: str, answer: str, context: Optional[str] = None, 
                expected_answer: Optional[str] = None) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate relevance of answer to query
        
        Returns:
            Tuple of (relevance_score, evaluation_details)
        """
        # Extract key terms from query
        query_terms = self._extract_key_terms(query)
        answer_terms = self._extract_key_terms(answer)
        
        # Calculate term overlap
        term_overlap_score = self._calculate_term_overlap(query_terms, answer_terms)
        
        # Check for direct question answering patterns
        direct_answer_score = self._check_direct_answer_patterns(query, answer)
        
        # Evaluate semantic relevance (simplified)
        semantic_score = self._evaluate_semantic_relevance(query, answer)
        
        # Calculate weighted final score
        relevance_score = (
            term_overlap_score * 0.4 +
            direct_answer_score * 0.3 +
            semantic_score * 0.3
        )
        
        evaluation_details = {
            "query_terms": list(query_terms),
            "answer_terms": list(answer_terms),
            "term_overlap_score": round(term_overlap_score, 3),
            "direct_answer_score": round(direct_answer_score, 3),
            "semantic_score": round(semantic_score, 3),
            "analysis": self._generate_relevance_analysis(query, answer, relevance_score)
        }
        
        return relevance_score, evaluation_details
    
    def _extract_key_terms(self, text: str) -> set:
        """Extract key terms from text (simplified approach)"""
        # Convert to lowercase and remove punctuation
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Common stop words to filter out
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'what', 'how', 'when', 'where', 'why',
            'who', 'which', 'that', 'this', 'these', 'those', 'i', 'you', 'he',
            'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        words = text.split()
        key_terms = {word for word in words if len(word) > 2 and word not in stop_words}
        
        return key_terms
    
    def _calculate_term_overlap(self, query_terms: set, answer_terms: set) -> float:
        """Calculate overlap between query and answer terms"""
        if not query_terms:
            return 0.0
        
        overlap = query_terms.intersection(answer_terms)
        return len(overlap) / len(query_terms)
    
    def _check_direct_answer_patterns(self, query: str, answer: str) -> float:
        """Check if answer directly addresses query patterns"""
        query_lower = query.lower()
        answer_lower = answer.lower()
        
        score = 0.0
        
        # Check for question-answer patterns
        if query_lower.startswith(('what', 'how', 'when', 'where', 'why', 'who')):
            # Look for direct answer indicators
            if any(phrase in answer_lower for phrase in [
                'the answer is', 'it is', 'this is', 'that is', 'because',
                'due to', 'as a result', 'therefore', 'consequently'
            ]):
                score += 0.3
            
            # Check if answer attempts to address the question type
            if query_lower.startswith('what') and any(word in answer_lower for word in ['is', 'are', 'means', 'refers']):
                score += 0.2
            elif query_lower.startswith('how') and any(word in answer_lower for word in ['by', 'through', 'using', 'via']):
                score += 0.2
            elif query_lower.startswith('when') and any(word in answer_lower for word in ['in', 'during', 'at', 'on']):
                score += 0.2
            elif query_lower.startswith('where') and any(word in answer_lower for word in ['in', 'at', 'on', 'near']):
                score += 0.2
            elif query_lower.startswith('why') and any(word in answer_lower for word in ['because', 'due', 'since']):
                score += 0.2
        
        # Check for imperative queries (commands/requests)
        if any(query_lower.startswith(word) for word in ['explain', 'describe', 'list', 'compare']):
            if len(answer.split()) > 10:  # Substantial response
                score += 0.4
        
        return min(score, 1.0)
    
    def _evaluate_semantic_relevance(self, query: str, answer: str) -> float:
        """Evaluate semantic relevance (simplified approach)"""
        # This is a simplified semantic evaluation
        # In a production system, you might use embeddings or more sophisticated NLP
        
        query_words = set(query.lower().split())
        answer_words = set(answer.lower().split())
        
        # Check for semantic indicators
        semantic_score = 0.0
        
        # Length appropriateness
        if 20 <= len(answer.split()) <= 200:
            semantic_score += 0.3
        elif len(answer.split()) < 5:
            semantic_score -= 0.2
        
        # Check if answer stays on topic
        common_words = query_words.intersection(answer_words)
        if len(common_words) > 0:
            semantic_score += 0.4
        
        # Check for coherent response structure
        if answer.strip() and not answer.lower().startswith(('i don\'t', 'i cannot', 'sorry')):
            semantic_score += 0.3
        
        return max(0.0, min(1.0, semantic_score))
    
    def _generate_relevance_analysis(self, query: str, answer: str, score: float) -> str:
        """Generate human-readable analysis of relevance"""
        if score >= 0.8:
            return "Highly relevant - Answer directly addresses the query with good term overlap"
        elif score >= 0.6:
            return "Moderately relevant - Answer addresses the query but could be more focused"
        elif score >= 0.4:
            return "Somewhat relevant - Answer partially addresses the query but lacks focus"
        else:
            return "Low relevance - Answer does not adequately address the query"
