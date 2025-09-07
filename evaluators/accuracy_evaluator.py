"""
Accuracy Evaluator - Evaluates the factual accuracy of the answer
"""

from typing import Tuple, Dict, Any, Optional
from .base_evaluator import BaseEvaluator
import re

class AccuracyEvaluator(BaseEvaluator):
    """Evaluates the factual accuracy of an answer"""
    
    def __init__(self):
        super().__init__(
            name="Accuracy Evaluator",
            description="Measures the factual correctness and precision of the answer",
            score_range=(0.0, 1.0)
        )
    
    def evaluate(self, query: str, answer: str, context: Optional[str] = None, 
                expected_answer: Optional[str] = None) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate accuracy of answer
        
        Returns:
            Tuple of (accuracy_score, evaluation_details)
        """
        # If expected answer is provided, use it for comparison
        if expected_answer:
            similarity_score = self._calculate_text_similarity(answer, expected_answer)
            factual_consistency_score = self._check_factual_consistency(answer, expected_answer)
            precision_score = self._evaluate_precision(answer, expected_answer)
        else:
            # Without expected answer, use heuristic approaches
            similarity_score = 0.5  # Neutral score
            factual_consistency_score = self._check_internal_consistency(answer)
            precision_score = self._evaluate_answer_precision(answer)
        
        # Check for uncertainty indicators
        uncertainty_score = self._check_uncertainty_handling(answer)
        
        # Calculate weighted accuracy score
        accuracy_score = (
            similarity_score * 0.3 +
            factual_consistency_score * 0.3 +
            precision_score * 0.2 +
            uncertainty_score * 0.2
        )
        
        evaluation_details = {
            "has_expected_answer": expected_answer is not None,
            "similarity_score": round(similarity_score, 3),
            "factual_consistency_score": round(factual_consistency_score, 3),
            "precision_score": round(precision_score, 3),
            "uncertainty_score": round(uncertainty_score, 3),
            "accuracy_indicators": self._identify_accuracy_indicators(answer),
            "analysis": self._generate_accuracy_analysis(answer, accuracy_score, expected_answer is not None)
        }
        
        return accuracy_score, evaluation_details
    
    def _check_factual_consistency(self, answer: str, expected_answer: str) -> float:
        """Check consistency between answer and expected answer"""
        # Extract key facts from both answers
        answer_facts = self._extract_key_facts(answer)
        expected_facts = self._extract_key_facts(expected_answer)
        
        if not expected_facts:
            return 0.5  # Neutral if no expected facts
        
        # Check for contradictions
        contradictions = 0
        matches = 0
        
        for fact in answer_facts:
            for expected_fact in expected_facts:
                similarity = self._calculate_text_similarity(fact, expected_fact)
                if similarity > 0.7:
                    matches += 1
                elif similarity > 0.3 and self._are_contradictory(fact, expected_fact):
                    contradictions += 1
        
        if len(expected_facts) == 0:
            return 0.5
        
        consistency_score = (matches - contradictions) / len(expected_facts)
        return max(0.0, min(1.0, consistency_score))
    
    def _check_internal_consistency(self, answer: str) -> float:
        """Check internal consistency of the answer"""
        sentences = self._split_into_sentences(answer)
        
        if len(sentences) < 2:
            return 0.8  # Single sentence, assume consistent
        
        consistency_score = 0.8  # Start with high consistency
        
        # Check for obvious contradictions
        contradiction_patterns = [
            (r'\b(yes|true|correct)\b.*\b(no|false|incorrect)\b', -0.3),
            (r'\b(always)\b.*\b(never)\b', -0.2),
            (r'\b(all)\b.*\b(none)\b', -0.2),
            (r'\b(increase)\b.*\b(decrease)\b', -0.1),
        ]
        
        answer_lower = answer.lower()
        for pattern, penalty in contradiction_patterns:
            if re.search(pattern, answer_lower):
                consistency_score += penalty
        
        return max(0.0, min(1.0, consistency_score))
    
    def _evaluate_precision(self, answer: str, expected_answer: str) -> float:
        """Evaluate precision when expected answer is available"""
        # Check for specific vs vague language
        answer_specificity = self._measure_specificity(answer)
        expected_specificity = self._measure_specificity(expected_answer)
        
        # Compare numerical accuracy if present
        numerical_accuracy = self._compare_numerical_values(answer, expected_answer)
        
        precision_score = (answer_specificity + numerical_accuracy) / 2
        return precision_score
    
    def _evaluate_answer_precision(self, answer: str) -> float:
        """Evaluate precision without expected answer"""
        specificity_score = self._measure_specificity(answer)
        
        # Check for hedging language that might indicate uncertainty
        hedging_penalty = self._check_hedging_language(answer)
        
        precision_score = specificity_score - hedging_penalty
        return max(0.0, min(1.0, precision_score))
    
    def _measure_specificity(self, text: str) -> float:
        """Measure how specific the text is"""
        specificity_score = 0.5  # Base score
        
        # Check for specific indicators
        specific_indicators = [
            r'\b\d+(\.\d+)?\s*(percent|%|degrees?|miles?|kilometers?|years?|months?|days?)\b',
            r'\b(exactly|precisely|specifically|particularly)\b',
            r'\b\d{4}\b',  # Years
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # Proper nouns (names, places)
        ]
        
        text_lower = text.lower()
        for pattern in specific_indicators:
            if re.search(pattern, text_lower):
                specificity_score += 0.1
        
        # Check for vague language
        vague_indicators = [
            r'\b(some|many|few|several|various|different|often|sometimes|usually)\b',
            r'\b(approximately|roughly|about|around|nearly)\b',
            r'\b(might|could|may|possibly|probably|likely)\b',
        ]
        
        for pattern in vague_indicators:
            if re.search(pattern, text_lower):
                specificity_score -= 0.05
        
        return max(0.0, min(1.0, specificity_score))
    
    def _compare_numerical_values(self, answer: str, expected_answer: str) -> float:
        """Compare numerical values between answers"""
        answer_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', answer)
        expected_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', expected_answer)
        
        if not answer_numbers and not expected_numbers:
            return 0.8  # No numbers to compare
        
        if not answer_numbers or not expected_numbers:
            return 0.3  # One has numbers, other doesn't
        
        # Simple comparison of first number found
        try:
            answer_num = float(answer_numbers[0])
            expected_num = float(expected_numbers[0])
            
            if answer_num == expected_num:
                return 1.0
            
            # Calculate relative error
            relative_error = abs(answer_num - expected_num) / max(abs(expected_num), 1)
            accuracy = max(0.0, 1.0 - relative_error)
            return accuracy
        except (ValueError, ZeroDivisionError):
            return 0.5
    
    def _check_uncertainty_handling(self, answer: str) -> float:
        """Check how well the answer handles uncertainty"""
        answer_lower = answer.lower()
        
        # Positive uncertainty handling
        good_uncertainty = [
            r'\b(according to|based on|research suggests|studies show)\b',
            r'\b(it depends|varies|may vary)\b',
            r'\b(generally|typically|commonly|usually)\b',
        ]
        
        # Poor uncertainty handling
        poor_uncertainty = [
            r'\b(definitely|absolutely|certainly|without doubt)\b',
            r'\b(never|always|all|none|every)\b',
        ]
        
        uncertainty_score = 0.7  # Base score
        
        for pattern in good_uncertainty:
            if re.search(pattern, answer_lower):
                uncertainty_score += 0.1
        
        for pattern in poor_uncertainty:
            if re.search(pattern, answer_lower):
                uncertainty_score -= 0.1
        
        return max(0.0, min(1.0, uncertainty_score))
    
    def _check_hedging_language(self, answer: str) -> float:
        """Check for excessive hedging that reduces precision"""
        hedging_patterns = [
            r'\b(i think|i believe|i guess|perhaps|maybe|possibly)\b',
            r'\b(sort of|kind of|somewhat|rather)\b',
        ]
        
        answer_lower = answer.lower()
        hedging_count = 0
        
        for pattern in hedging_patterns:
            hedging_count += len(re.findall(pattern, answer_lower))
        
        # Penalty based on hedging frequency
        word_count = len(answer.split())
        hedging_ratio = hedging_count / max(word_count, 1)
        
        return min(0.3, hedging_ratio * 2)  # Cap penalty at 0.3
    
    def _extract_key_facts(self, text: str) -> list:
        """Extract key factual statements from text"""
        sentences = self._split_into_sentences(text)
        
        # Simple fact extraction - sentences with specific patterns
        facts = []
        for sentence in sentences:
            if any(pattern in sentence.lower() for pattern in [
                'is', 'are', 'was', 'were', 'has', 'have', 'contains', 'includes'
            ]):
                facts.append(sentence.strip())
        
        return facts
    
    def _split_into_sentences(self, text: str) -> list:
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _are_contradictory(self, fact1: str, fact2: str) -> bool:
        """Simple check for contradictory facts"""
        # This is a simplified implementation
        contradictory_pairs = [
            ('true', 'false'), ('yes', 'no'), ('increase', 'decrease'),
            ('positive', 'negative'), ('good', 'bad'), ('high', 'low')
        ]
        
        fact1_lower = fact1.lower()
        fact2_lower = fact2.lower()
        
        for word1, word2 in contradictory_pairs:
            if word1 in fact1_lower and word2 in fact2_lower:
                return True
            if word2 in fact1_lower and word1 in fact2_lower:
                return True
        
        return False
    
    def _identify_accuracy_indicators(self, answer: str) -> Dict[str, bool]:
        """Identify various accuracy indicators in the answer"""
        answer_lower = answer.lower()
        
        return {
            "has_citations": bool(re.search(r'\b(according to|source|study|research)\b', answer_lower)),
            "has_specific_numbers": bool(re.search(r'\b\d+(\.\d+)?\b', answer)),
            "has_dates": bool(re.search(r'\b\d{4}\b|\b(january|february|march|april|may|june|july|august|september|october|november|december)\b', answer_lower)),
            "uses_hedging": bool(re.search(r'\b(might|could|may|possibly|probably)\b', answer_lower)),
            "shows_uncertainty": bool(re.search(r'\b(uncertain|unclear|unknown|varies)\b', answer_lower)),
        }
    
    def _generate_accuracy_analysis(self, answer: str, score: float, has_expected: bool) -> str:
        """Generate human-readable accuracy analysis"""
        if score >= 0.8:
            base_msg = "High accuracy - Answer appears factually sound"
        elif score >= 0.6:
            base_msg = "Good accuracy - Answer is mostly accurate with minor issues"
        elif score >= 0.4:
            base_msg = "Moderate accuracy - Answer has some accuracy concerns"
        else:
            base_msg = "Low accuracy - Answer may contain factual errors or inconsistencies"
        
        if has_expected:
            return f"{base_msg} (compared against expected answer)"
        else:
            return f"{base_msg} (evaluated using heuristic methods)"
