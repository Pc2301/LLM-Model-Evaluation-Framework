"""
LLM Evaluation Framework - Main API Server
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn
from datetime import datetime
import json
import logging

from evaluators.base_evaluator import BaseEvaluator
from evaluators.relevance_evaluator import RelevanceEvaluator
from evaluators.accuracy_evaluator import AccuracyEvaluator
from evaluators.coherence_evaluator import CoherenceEvaluator
from evaluators.completeness_evaluator import CompletenessEvaluator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLM Evaluation Framework",
    description="A comprehensive framework for evaluating LLM responses",
    version="1.0.0"
)

class EvaluationRequest(BaseModel):
    query: str
    answer: str
    context: Optional[str] = None
    expected_answer: Optional[str] = None
    evaluation_criteria: Optional[List[str]] = ["relevance", "accuracy", "coherence", "completeness"]

class EvaluationResponse(BaseModel):
    query: str
    answer: str
    overall_score: float
    detailed_scores: Dict[str, float]
    evaluation_summary: Dict[str, Any]
    timestamp: str
    evaluation_id: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

# Initialize evaluators
evaluators = {
    "relevance": RelevanceEvaluator(),
    "accuracy": AccuracyEvaluator(),
    "coherence": CoherenceEvaluator(),
    "completeness": CompletenessEvaluator()
}

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with basic information"""
    return {
        "message": "LLM Evaluation Framework API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_llm_response(request: EvaluationRequest):
    """
    Evaluate an LLM response based on query-answer pair
    
    Args:
        request: EvaluationRequest containing query, answer, and optional parameters
        
    Returns:
        EvaluationResponse with detailed evaluation results
    """
    try:
        logger.info(f"Evaluating query: {request.query[:100]}...")
        
        # Generate unique evaluation ID
        evaluation_id = f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        detailed_scores = {}
        evaluation_details = {}
        
        # Run evaluations based on specified criteria
        for criterion in request.evaluation_criteria:
            if criterion in evaluators:
                evaluator = evaluators[criterion]
                score, details = evaluator.evaluate(
                    query=request.query,
                    answer=request.answer,
                    context=request.context,
                    expected_answer=request.expected_answer
                )
                detailed_scores[criterion] = score
                evaluation_details[criterion] = details
            else:
                logger.warning(f"Unknown evaluation criterion: {criterion}")
        
        # Calculate overall score (weighted average)
        if detailed_scores:
            overall_score = sum(detailed_scores.values()) / len(detailed_scores)
        else:
            overall_score = 0.0
        
        # Create evaluation summary
        evaluation_summary = {
            "criteria_evaluated": list(detailed_scores.keys()),
            "evaluation_details": evaluation_details,
            "recommendations": _generate_recommendations(detailed_scores, evaluation_details)
        }
        
        response = EvaluationResponse(
            query=request.query,
            answer=request.answer,
            overall_score=round(overall_score, 3),
            detailed_scores={k: round(v, 3) for k, v in detailed_scores.items()},
            evaluation_summary=evaluation_summary,
            timestamp=datetime.now().isoformat(),
            evaluation_id=evaluation_id
        )
        
        logger.info(f"Evaluation completed. ID: {evaluation_id}, Overall Score: {overall_score:.3f}")
        return response
        
    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@app.get("/evaluators", response_model=Dict[str, Any])
async def get_available_evaluators():
    """Get information about available evaluators"""
    evaluator_info = {}
    for name, evaluator in evaluators.items():
        evaluator_info[name] = {
            "name": evaluator.name,
            "description": evaluator.description,
            "score_range": evaluator.score_range
        }
    return evaluator_info

def _generate_recommendations(scores: Dict[str, float], details: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on evaluation scores"""
    recommendations = []
    
    for criterion, score in scores.items():
        if score < 0.6:
            if criterion == "relevance":
                recommendations.append("Consider making the answer more relevant to the specific query")
            elif criterion == "accuracy":
                recommendations.append("Verify factual accuracy and provide more precise information")
            elif criterion == "coherence":
                recommendations.append("Improve logical flow and structure of the response")
            elif criterion == "completeness":
                recommendations.append("Provide more comprehensive coverage of the topic")
    
    if not recommendations:
        recommendations.append("Great job! The response meets quality standards across all criteria")
    
    return recommendations

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
