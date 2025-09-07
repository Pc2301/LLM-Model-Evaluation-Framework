# LLM Evaluation Framework

A comprehensive framework for evaluating Large Language Model (LLM) responses based on multiple criteria including relevance, accuracy, coherence, and completeness. Now includes both REST API and interactive Streamlit demo!

## Features

- **🚀 Interactive Streamlit Demo**: User-friendly web interface for testing and comparing LLM responses
- **🔧 REST API**: Easy-to-use HTTP endpoints for programmatic evaluation
- **📊 Multiple Evaluation Criteria**: 
  - **Relevance**: How well the answer addresses the query
  - **Accuracy**: Factual correctness and precision
  - **Coherence**: Logical flow and structure
  - **Completeness**: Comprehensive coverage of the topic
- **🔍 Comparison Mode**: Side-by-side evaluation of two different answers
- **📈 Visual Analytics**: Interactive radar charts and comparison visualizations
- **🎯 Flexible Input**: Accepts query-answer pairs with optional context and expected answers
- **📋 Detailed Scoring**: Provides both overall scores and detailed breakdowns
- **📚 Automatic Documentation**: FastAPI generates interactive API docs

## Quick Start

### Installation

1. Clone or download the framework
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 🎨 Running the Streamlit Demo (Recommended for Testing)

For an interactive demo experience:

```bash
# Option 1: Use the launcher script
python run_demo.py

# Option 2: Run directly
streamlit run streamlit_demo.py
```

The demo will open in your browser at `http://localhost:8501`

**Demo Features:**
- 🔄 **Single Answer Mode**: Evaluate one LLM response
- ⚖️ **Compare Mode**: Side-by-side comparison of two answers
- 📊 **Visual Charts**: Interactive radar charts showing metric scores
- 📈 **Detailed Analysis**: Expandable sections with evaluation breakdowns
- 🏆 **Winner Analysis**: See which answer performs better across metrics

### 🔧 Running the REST API Server

For programmatic access:

```bash
python main.py
```

The server will start on `http://localhost:8000`

### API Documentation

Once running, visit:
- Interactive docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## API Endpoints

### POST /evaluate

Evaluate an LLM response based on query-answer pair.

**Request Body:**
```json
{
  "query": "What is machine learning?",
  "answer": "Machine learning is a subset of artificial intelligence...",
  "context": "Optional context information",
  "expected_answer": "Optional reference answer for comparison",
  "evaluation_criteria": ["relevance", "accuracy", "coherence", "completeness"]
}
```

**Response:**
```json
{
  "query": "What is machine learning?",
  "answer": "Machine learning is a subset of artificial intelligence...",
  "overall_score": 0.85,
  "detailed_scores": {
    "relevance": 0.9,
    "accuracy": 0.8,
    "coherence": 0.85,
    "completeness": 0.85
  },
  "evaluation_summary": {
    "criteria_evaluated": ["relevance", "accuracy", "coherence", "completeness"],
    "evaluation_details": {...},
    "recommendations": [...]
  },
  "timestamp": "2024-01-01T12:00:00",
  "evaluation_id": "eval_20240101_120000_123456"
}
```

### GET /evaluators

Get information about available evaluators.

### GET /health

Health check endpoint.

## Evaluation Criteria

### 1. Relevance Evaluator
- Measures how well the answer addresses the specific query
- Analyzes term overlap, direct answer patterns, and semantic relevance
- Score range: 0.0 - 1.0

### 2. Accuracy Evaluator  
- Evaluates factual correctness and precision
- Compares with expected answers when available
- Checks for internal consistency and uncertainty handling
- Score range: 0.0 - 1.0

### 3. Coherence Evaluator
- Assesses logical flow and structure
- Evaluates readability, transitions, and consistency
- Score range: 0.0 - 1.0

### 4. Completeness Evaluator
- Measures comprehensive coverage of the topic
- Analyzes query complexity and aspect coverage
- Evaluates response depth and thoroughness
- Score range: 0.0 - 1.0

## Usage Examples

### Basic Evaluation
```python
import requests

response = requests.post("http://localhost:8000/evaluate", json={
    "query": "Explain photosynthesis",
    "answer": "Photosynthesis is the process by which plants convert sunlight into energy..."
})

result = response.json()
print(f"Overall Score: {result['overall_score']}")
```

### With Expected Answer
```python
response = requests.post("http://localhost:8000/evaluate", json={
    "query": "What is 2+2?",
    "answer": "2+2 equals 4",
    "expected_answer": "The answer is 4",
    "evaluation_criteria": ["relevance", "accuracy"]
})
```

### Custom Criteria
```python
response = requests.post("http://localhost:8000/evaluate", json={
    "query": "Describe the water cycle",
    "answer": "The water cycle involves evaporation, condensation, and precipitation...",
    "evaluation_criteria": ["completeness", "coherence"]
})
```

## Architecture

```
LLM_Evaluation_Framework/
├── main.py                 # FastAPI application and main endpoints
├── evaluators/            # Evaluation modules
│   ├── __init__.py
│   ├── base_evaluator.py  # Abstract base class
│   ├── relevance_evaluator.py
│   ├── accuracy_evaluator.py
│   ├── coherence_evaluator.py
│   └── completeness_evaluator.py
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Extending the Framework

### Adding New Evaluators

1. Create a new evaluator class inheriting from `BaseEvaluator`
2. Implement the `evaluate` method
3. Register the evaluator in `main.py`

Example:
```python
from evaluators.base_evaluator import BaseEvaluator

class CustomEvaluator(BaseEvaluator):
    def __init__(self):
        super().__init__(
            name="Custom Evaluator",
            description="Custom evaluation logic",
            score_range=(0.0, 1.0)
        )
    
    def evaluate(self, query, answer, context=None, expected_answer=None):
        # Your evaluation logic here
        score = 0.8
        details = {"custom_metric": "value"}
        return score, details
```

## Configuration

The framework uses default configurations but can be extended with:
- Custom scoring weights
- Additional evaluation parameters
- External API integrations
- Database storage for results

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.
