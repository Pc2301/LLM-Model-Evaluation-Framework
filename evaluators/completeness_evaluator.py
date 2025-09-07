"""
Completeness Evaluator - Evaluates how comprehensive the answer is
"""

from typing import Tuple, Dict, Any, Optional
from .base_evaluator import BaseEvaluator
import re

class CompletenessEvaluator(BaseEvaluator):
    """Evaluates the completeness and comprehensiveness of an answer"""
    
    def __init__(self):
        super().__init__(
            name="Completeness Evaluator",
            description="Measures how thoroughly the answer addresses all aspects of the query",
            score_range=(0.0, 1.0)
        )
    
    def evaluate(self, query: str, answer: str, context: Optional[str] = None, 
                expected_answer: Optional[str] = None) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate completeness of answer
        
        Returns:
            Tuple of (completeness_score, evaluation_details)
        """
        # Analyze query complexity and requirements
        query_aspects = self._analyze_query_aspects(query)
        
        # Evaluate coverage of query aspects
        coverage_score = self._evaluate_aspect_coverage(query, answer, query_aspects)
        
        # Evaluate depth of response
        depth_score = self._evaluate_response_depth(answer)
        
        # Check for comprehensive elements
        comprehensive_score = self._evaluate_comprehensiveness(answer)
        
        # Compare with expected answer if available
        if expected_answer:
            expected_coverage_score = self._compare_with_expected(answer, expected_answer)
        else:
            expected_coverage_score = 0.7  # Neutral score when no expected answer
        
        # Calculate weighted completeness score
        completeness_score = (
            coverage_score * 0.3 +
            depth_score * 0.25 +
            comprehensive_score * 0.25 +
            expected_coverage_score * 0.2
        )
        
        evaluation_details = {
            "query_aspects": query_aspects,
            "coverage_score": round(coverage_score, 3),
            "depth_score": round(depth_score, 3),
            "comprehensive_score": round(comprehensive_score, 3),
            "expected_coverage_score": round(expected_coverage_score, 3),
            "response_length": len(answer.split()),
            "completeness_indicators": self._identify_completeness_indicators(answer),
            "analysis": self._generate_completeness_analysis(answer, completeness_score, query_aspects)
        }
        
        return completeness_score, evaluation_details
    
    def _analyze_query_aspects(self, query: str) -> Dict[str, Any]:
        """Analyze different aspects that the query might be asking for"""
        query_lower = query.lower()
        
        aspects = {
            "question_type": self._identify_question_type(query),
            "complexity": self._assess_query_complexity(query),
            "multiple_parts": self._has_multiple_parts(query),
            "requires_examples": self._requires_examples(query),
            "requires_explanation": self._requires_explanation(query),
            "requires_comparison": self._requires_comparison(query),
            "key_topics": self._extract_key_topics(query)
        }
        
        return aspects
    
    def _identify_question_type(self, query: str) -> str:
        """Identify the type of question being asked"""
        query_lower = query.lower().strip()
        
        if query_lower.startswith('what'):
            return 'definition/explanation'
        elif query_lower.startswith('how'):
            return 'process/method'
        elif query_lower.startswith('why'):
            return 'reasoning/cause'
        elif query_lower.startswith('when'):
            return 'temporal'
        elif query_lower.startswith('where'):
            return 'location'
        elif query_lower.startswith('who'):
            return 'person/entity'
        elif query_lower.startswith(('compare', 'contrast')):
            return 'comparison'
        elif query_lower.startswith(('list', 'enumerate')):
            return 'enumeration'
        elif query_lower.startswith(('explain', 'describe')):
            return 'explanation'
        else:
            return 'general'
    
    def _assess_query_complexity(self, query: str) -> str:
        """Assess the complexity of the query"""
        word_count = len(query.split())
        
        # Check for complex indicators
        complex_indicators = [
            'and', 'or', 'but', 'however', 'also', 'additionally',
            'compare', 'contrast', 'analyze', 'evaluate', 'discuss'
        ]
        
        complex_count = sum(1 for indicator in complex_indicators if indicator in query.lower())
        
        if word_count > 20 or complex_count > 2:
            return 'high'
        elif word_count > 10 or complex_count > 0:
            return 'medium'
        else:
            return 'low'
    
    def _has_multiple_parts(self, query: str) -> bool:
        """Check if query has multiple parts or sub-questions"""
        multi_part_indicators = [
            r'\band\b', r'\bor\b', r'\balso\b', r'\badditionally\b',
            r'\?.*\?', r'[;,].*[?]', r'\b(first|second|third)\b'
        ]
        
        query_lower = query.lower()
        return any(re.search(pattern, query_lower) for pattern in multi_part_indicators)
    
    def _requires_examples(self, query: str) -> bool:
        """Check if query likely requires examples"""
        example_indicators = [
            'example', 'examples', 'instance', 'such as', 'like',
            'demonstrate', 'illustrate', 'show'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in example_indicators)
    
    def _requires_explanation(self, query: str) -> bool:
        """Check if query requires detailed explanation"""
        explanation_indicators = [
            'explain', 'describe', 'how', 'why', 'what is', 'what are',
            'detail', 'elaborate', 'discuss'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in explanation_indicators)
    
    def _requires_comparison(self, query: str) -> bool:
        """Check if query requires comparison"""
        comparison_indicators = [
            'compare', 'contrast', 'difference', 'similar', 'versus',
            'vs', 'better', 'worse', 'advantage', 'disadvantage'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in comparison_indicators)
    
    def _extract_key_topics(self, query: str) -> list:
        """Extract key topics from the query"""
        # Simple approach: extract nouns and important terms
        words = re.findall(r'\b[A-Za-z]{3,}\b', query)
        
        # Filter out common question words and articles
        stop_words = {
            'what', 'how', 'when', 'where', 'why', 'who', 'which', 'that',
            'the', 'and', 'for', 'are', 'you', 'can', 'does', 'will'
        }
        
        topics = [word.lower() for word in words if word.lower() not in stop_words]
        return list(set(topics))  # Remove duplicates
    
    def _evaluate_aspect_coverage(self, query: str, answer: str, query_aspects: Dict[str, Any]) -> float:
        """Evaluate how well the answer covers the query aspects"""
        coverage_score = 0.5  # Base score
        
        # Check coverage based on question type
        question_type = query_aspects['question_type']
        
        if question_type == 'definition/explanation':
            if self._has_definition_elements(answer):
                coverage_score += 0.2
        elif question_type == 'process/method':
            if self._has_process_elements(answer):
                coverage_score += 0.2
        elif question_type == 'reasoning/cause':
            if self._has_reasoning_elements(answer):
                coverage_score += 0.2
        elif question_type == 'comparison':
            if self._has_comparison_elements(answer):
                coverage_score += 0.2
        
        # Check topic coverage
        key_topics = query_aspects['key_topics']
        if key_topics:
            answer_lower = answer.lower()
            covered_topics = sum(1 for topic in key_topics if topic in answer_lower)
            topic_coverage = covered_topics / len(key_topics)
            coverage_score += topic_coverage * 0.3
        
        # Check for multiple parts coverage
        if query_aspects['multiple_parts']:
            if self._addresses_multiple_aspects(answer):
                coverage_score += 0.2
            else:
                coverage_score -= 0.1
        
        return max(0.0, min(1.0, coverage_score))
    
    def _evaluate_response_depth(self, answer: str) -> float:
        """Evaluate the depth and detail of the response"""
        word_count = len(answer.split())
        sentence_count = self._count_sentences(answer)
        
        depth_score = 0.5  # Base score
        
        # Length-based depth assessment
        if word_count >= 100:
            depth_score += 0.3
        elif word_count >= 50:
            depth_score += 0.2
        elif word_count >= 20:
            depth_score += 0.1
        elif word_count < 10:
            depth_score -= 0.2
        
        # Check for depth indicators
        depth_indicators = [
            r'\b(because|since|due to|as a result|therefore)\b',  # Causal reasoning
            r'\b(for example|for instance|such as|including)\b',  # Examples
            r'\b(however|but|although|while|whereas)\b',  # Contrasts
            r'\b(furthermore|moreover|additionally|also)\b',  # Additional info
        ]
        
        answer_lower = answer.lower()
        depth_indicator_count = sum(len(re.findall(pattern, answer_lower)) for pattern in depth_indicators)
        
        if depth_indicator_count >= 3:
            depth_score += 0.2
        elif depth_indicator_count >= 1:
            depth_score += 0.1
        
        return max(0.0, min(1.0, depth_score))
    
    def _evaluate_comprehensiveness(self, answer: str) -> float:
        """Evaluate overall comprehensiveness"""
        comprehensive_score = 0.6  # Base score
        
        # Check for comprehensive elements
        comprehensive_elements = {
            'has_examples': bool(re.search(r'\b(for example|for instance|such as)\b', answer.lower())),
            'has_reasoning': bool(re.search(r'\b(because|since|due to|therefore)\b', answer.lower())),
            'has_context': bool(re.search(r'\b(context|background|historically|traditionally)\b', answer.lower())),
            'has_implications': bool(re.search(r'\b(implication|consequence|result|impact)\b', answer.lower())),
            'has_alternatives': bool(re.search(r'\b(alternative|option|choice|instead)\b', answer.lower())),
        }
        
        element_count = sum(comprehensive_elements.values())
        comprehensive_score += element_count * 0.08  # Bonus for each element
        
        return max(0.0, min(1.0, comprehensive_score))
    
    def _compare_with_expected(self, answer: str, expected_answer: str) -> float:
        """Compare coverage with expected answer"""
        # Extract key points from expected answer
        expected_sentences = self._split_into_sentences(expected_answer)
        answer_sentences = self._split_into_sentences(answer)
        
        if not expected_sentences:
            return 0.7
        
        # Simple coverage check based on sentence similarity
        coverage_count = 0
        for expected_sent in expected_sentences:
            for answer_sent in answer_sentences:
                if self._calculate_text_similarity(expected_sent, answer_sent) > 0.3:
                    coverage_count += 1
                    break
        
        coverage_ratio = coverage_count / len(expected_sentences)
        return coverage_ratio
    
    def _has_definition_elements(self, answer: str) -> bool:
        """Check if answer has definition elements"""
        definition_patterns = [
            r'\bis\b.*\ba\b', r'\bare\b.*\bthat\b', r'\bmeans\b', r'\brefers to\b',
            r'\bdefined as\b', r'\bknown as\b'
        ]
        
        answer_lower = answer.lower()
        return any(re.search(pattern, answer_lower) for pattern in definition_patterns)
    
    def _has_process_elements(self, answer: str) -> bool:
        """Check if answer has process/method elements"""
        process_patterns = [
            r'\b(first|second|third|next|then|finally)\b',
            r'\b(step|stage|phase|process)\b',
            r'\b(by|through|using|via)\b'
        ]
        
        answer_lower = answer.lower()
        return any(re.search(pattern, answer_lower) for pattern in process_patterns)
    
    def _has_reasoning_elements(self, answer: str) -> bool:
        """Check if answer has reasoning elements"""
        reasoning_patterns = [
            r'\b(because|since|due to|as a result|therefore|thus)\b',
            r'\b(reason|cause|factor|leads to|results in)\b'
        ]
        
        answer_lower = answer.lower()
        return any(re.search(pattern, answer_lower) for pattern in reasoning_patterns)
    
    def _has_comparison_elements(self, answer: str) -> bool:
        """Check if answer has comparison elements"""
        comparison_patterns = [
            r'\b(compared to|versus|vs|while|whereas|however)\b',
            r'\b(similar|different|alike|unlike|better|worse)\b',
            r'\b(advantage|disadvantage|benefit|drawback)\b'
        ]
        
        answer_lower = answer.lower()
        return any(re.search(pattern, answer_lower) for pattern in comparison_patterns)
    
    def _addresses_multiple_aspects(self, answer: str) -> bool:
        """Check if answer addresses multiple aspects"""
        # Look for structural indicators of multiple aspects
        multi_aspect_indicators = [
            r'\b(also|additionally|furthermore|moreover)\b',
            r'\b(another|other|second|third)\b',
            r'\b(in addition|as well|besides)\b'
        ]
        
        answer_lower = answer.lower()
        return any(re.search(pattern, answer_lower) for pattern in multi_aspect_indicators)
    
    def _split_into_sentences(self, text: str) -> list:
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _identify_completeness_indicators(self, answer: str) -> Dict[str, bool]:
        """Identify completeness indicators in the answer"""
        answer_lower = answer.lower()
        
        return {
            "has_examples": bool(re.search(r'\b(for example|for instance|such as)\b', answer_lower)),
            "has_reasoning": bool(re.search(r'\b(because|since|therefore)\b', answer_lower)),
            "has_multiple_points": bool(re.search(r'\b(first|second|also|additionally)\b', answer_lower)),
            "has_context": bool(re.search(r'\b(context|background|history)\b', answer_lower)),
            "has_implications": bool(re.search(r'\b(implication|consequence|impact)\b', answer_lower)),
            "addresses_alternatives": bool(re.search(r'\b(alternative|option|instead)\b', answer_lower)),
        }
    
    def _generate_completeness_analysis(self, answer: str, score: float, query_aspects: Dict[str, Any]) -> str:
        """Generate human-readable completeness analysis"""
        complexity = query_aspects.get('complexity', 'medium')
        
        if score >= 0.8:
            base_msg = "Highly complete - Thoroughly addresses the query"
        elif score >= 0.6:
            base_msg = "Good completeness - Covers most important aspects"
        elif score >= 0.4:
            base_msg = "Moderate completeness - Addresses some aspects but lacks depth"
        else:
            base_msg = "Low completeness - Missing significant aspects of the query"
        
        if complexity == 'high':
            return f"{base_msg} (complex query with multiple aspects)"
        elif complexity == 'low':
            return f"{base_msg} (straightforward query)"
        else:
            return f"{base_msg} (moderately complex query)"
