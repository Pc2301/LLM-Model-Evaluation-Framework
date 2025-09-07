"""
Coherence Evaluator - Evaluates the logical flow and structure of the answer
"""

from typing import Tuple, Dict, Any, Optional
from .base_evaluator import BaseEvaluator
import re

class CoherenceEvaluator(BaseEvaluator):
    """Evaluates the coherence and logical flow of an answer"""
    
    def __init__(self):
        super().__init__(
            name="Coherence Evaluator",
            description="Measures the logical flow, structure, and readability of the answer",
            score_range=(0.0, 1.0)
        )
    
    def evaluate(self, query: str, answer: str, context: Optional[str] = None, 
                expected_answer: Optional[str] = None) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate coherence of answer
        
        Returns:
            Tuple of (coherence_score, evaluation_details)
        """
        # Evaluate different aspects of coherence
        structure_score = self._evaluate_structure(answer)
        flow_score = self._evaluate_logical_flow(answer)
        readability_score = self._evaluate_readability(answer)
        consistency_score = self._evaluate_consistency(answer)
        
        # Calculate weighted coherence score
        coherence_score = (
            structure_score * 0.3 +
            flow_score * 0.3 +
            readability_score * 0.2 +
            consistency_score * 0.2
        )
        
        evaluation_details = {
            "structure_score": round(structure_score, 3),
            "flow_score": round(flow_score, 3),
            "readability_score": round(readability_score, 3),
            "consistency_score": round(consistency_score, 3),
            "sentence_count": self._count_sentences(answer),
            "word_count": self._count_words(answer),
            "structure_analysis": self._analyze_structure(answer),
            "analysis": self._generate_coherence_analysis(answer, coherence_score)
        }
        
        return coherence_score, evaluation_details
    
    def _evaluate_structure(self, answer: str) -> float:
        """Evaluate the structural organization of the answer"""
        structure_score = 0.5  # Base score
        
        # Check for clear introduction/conclusion patterns
        sentences = self._split_into_sentences(answer)
        
        if len(sentences) == 0:
            return 0.0
        
        # Single sentence handling
        if len(sentences) == 1:
            return 0.7 if len(answer.split()) > 5 else 0.4
        
        # Check for organizational elements
        answer_lower = answer.lower()
        
        # Positive structure indicators
        structure_indicators = [
            r'\b(first|second|third|finally|lastly|in conclusion)\b',
            r'\b(however|moreover|furthermore|additionally|therefore)\b',
            r'\b(for example|for instance|such as|including)\b',
            r'\b(because|since|due to|as a result)\b',
        ]
        
        for pattern in structure_indicators:
            if re.search(pattern, answer_lower):
                structure_score += 0.1
        
        # Check for lists or enumeration
        if re.search(r'^\s*[-•*]\s+', answer, re.MULTILINE):
            structure_score += 0.2
        
        if re.search(r'\b\d+\.\s+', answer):
            structure_score += 0.2
        
        # Penalty for very short or very long answers without structure
        word_count = len(answer.split())
        if word_count < 10:
            structure_score -= 0.1
        elif word_count > 200 and not re.search(r'[.!?].*[.!?]', answer):
            structure_score -= 0.2
        
        return max(0.0, min(1.0, structure_score))
    
    def _evaluate_logical_flow(self, answer: str) -> float:
        """Evaluate the logical flow between sentences"""
        sentences = self._split_into_sentences(answer)
        
        if len(sentences) <= 1:
            return 0.8  # Single sentence, assume good flow
        
        flow_score = 0.7  # Base score
        
        # Check for transition words and phrases
        transition_patterns = [
            r'\b(however|but|although|while|whereas)\b',  # Contrast
            r'\b(therefore|thus|consequently|as a result)\b',  # Consequence
            r'\b(furthermore|moreover|additionally|also)\b',  # Addition
            r'\b(for example|for instance|specifically)\b',  # Example
            r'\b(first|second|next|then|finally)\b',  # Sequence
        ]
        
        answer_lower = answer.lower()
        transition_count = 0
        
        for pattern in transition_patterns:
            transition_count += len(re.findall(pattern, answer_lower))
        
        # Bonus for appropriate use of transitions
        transition_ratio = transition_count / max(len(sentences) - 1, 1)
        if 0.2 <= transition_ratio <= 0.8:
            flow_score += 0.2
        elif transition_ratio > 0.8:
            flow_score -= 0.1  # Too many transitions can be awkward
        
        # Check for abrupt topic changes (simplified)
        flow_score += self._check_topic_continuity(sentences)
        
        return max(0.0, min(1.0, flow_score))
    
    def _evaluate_readability(self, answer: str) -> float:
        """Evaluate readability of the answer"""
        readability_score = 0.6  # Base score
        
        # Sentence length analysis
        sentences = self._split_into_sentences(answer)
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            
            # Optimal sentence length is around 15-20 words
            if 10 <= avg_sentence_length <= 25:
                readability_score += 0.2
            elif avg_sentence_length > 30:
                readability_score -= 0.2
            elif avg_sentence_length < 5:
                readability_score -= 0.1
        
        # Check for complex punctuation usage
        complex_punct_count = len(re.findall(r'[;:()"]', answer))
        word_count = len(answer.split())
        
        if word_count > 0:
            punct_ratio = complex_punct_count / word_count
            if 0.02 <= punct_ratio <= 0.1:  # Moderate use of complex punctuation
                readability_score += 0.1
            elif punct_ratio > 0.15:
                readability_score -= 0.1
        
        # Check for overly complex vocabulary (simplified)
        long_words = len([word for word in answer.split() if len(word) > 8])
        if word_count > 0:
            long_word_ratio = long_words / word_count
            if long_word_ratio > 0.3:
                readability_score -= 0.1
        
        return max(0.0, min(1.0, readability_score))
    
    def _evaluate_consistency(self, answer: str) -> float:
        """Evaluate internal consistency of tone and style"""
        consistency_score = 0.8  # Base score (assume consistent unless proven otherwise)
        
        # Check for tense consistency
        past_tense_count = len(re.findall(r'\b\w+ed\b|\bwas\b|\bwere\b|\bhad\b', answer.lower()))
        present_tense_count = len(re.findall(r'\bis\b|\bare\b|\bhas\b|\bhave\b', answer.lower()))
        
        total_tense_indicators = past_tense_count + present_tense_count
        if total_tense_indicators > 0:
            tense_consistency = 1 - abs(past_tense_count - present_tense_count) / total_tense_indicators
            consistency_score = (consistency_score + tense_consistency) / 2
        
        # Check for person consistency (1st, 2nd, 3rd person)
        first_person = len(re.findall(r'\b(i|me|my|mine|we|us|our|ours)\b', answer.lower()))
        second_person = len(re.findall(r'\b(you|your|yours)\b', answer.lower()))
        third_person = len(re.findall(r'\b(he|she|it|they|them|their|his|her|its)\b', answer.lower()))
        
        # Penalty for mixing persons inappropriately
        person_indicators = [first_person, second_person, third_person]
        active_persons = sum(1 for count in person_indicators if count > 0)
        
        if active_persons > 2:
            consistency_score -= 0.1
        
        return max(0.0, min(1.0, consistency_score))
    
    def _check_topic_continuity(self, sentences: list) -> float:
        """Check for topic continuity between sentences"""
        if len(sentences) <= 1:
            return 0.0
        
        continuity_bonus = 0.0
        
        # Simple approach: check for word overlap between consecutive sentences
        for i in range(len(sentences) - 1):
            current_words = set(sentences[i].lower().split())
            next_words = set(sentences[i + 1].lower().split())
            
            overlap = len(current_words.intersection(next_words))
            if overlap >= 2:  # At least 2 words in common
                continuity_bonus += 0.02
        
        return min(0.2, continuity_bonus)  # Cap the bonus
    
    def _split_into_sentences(self, text: str) -> list:
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _analyze_structure(self, answer: str) -> Dict[str, Any]:
        """Analyze the structural elements of the answer"""
        sentences = self._split_into_sentences(answer)
        
        return {
            "has_introduction": self._has_introduction(answer),
            "has_conclusion": self._has_conclusion(answer),
            "has_transitions": bool(re.search(r'\b(however|therefore|furthermore|moreover)\b', answer.lower())),
            "has_examples": bool(re.search(r'\b(for example|for instance|such as)\b', answer.lower())),
            "has_enumeration": bool(re.search(r'\b(first|second|third|finally)\b', answer.lower())),
            "paragraph_count": len(answer.split('\n\n')) if '\n\n' in answer else 1,
        }
    
    def _has_introduction(self, answer: str) -> bool:
        """Check if answer has an introductory pattern"""
        intro_patterns = [
            r'^(to answer|in response|regarding|concerning)',
            r'^(the answer is|this is|it is)',
            r'^(let me explain|to understand)',
        ]
        
        answer_lower = answer.lower().strip()
        return any(re.match(pattern, answer_lower) for pattern in intro_patterns)
    
    def _has_conclusion(self, answer: str) -> bool:
        """Check if answer has a concluding pattern"""
        conclusion_patterns = [
            r'\b(in conclusion|to conclude|finally|in summary)\b',
            r'\b(therefore|thus|as a result)\b.*[.!?]\s*$',
        ]
        
        answer_lower = answer.lower()
        return any(re.search(pattern, answer_lower) for pattern in conclusion_patterns)
    
    def _generate_coherence_analysis(self, answer: str, score: float) -> str:
        """Generate human-readable coherence analysis"""
        if score >= 0.8:
            return "Excellent coherence - Well-structured with clear logical flow"
        elif score >= 0.6:
            return "Good coherence - Generally well-organized with minor flow issues"
        elif score >= 0.4:
            return "Moderate coherence - Some structural issues affecting readability"
        else:
            return "Poor coherence - Significant issues with structure and logical flow"
