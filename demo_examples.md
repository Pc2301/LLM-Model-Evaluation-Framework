# Demo Examples for LLM Evaluation Framework

This document provides sample inputs you can use to test and demonstrate the Streamlit app.

## Example 1: Basic Question Answering

**Query:**
```
What is the capital of France?
```

**Expected Answer:**
```
The capital of France is Paris.
```

**Answer 1 (Good):**
```
Paris is the capital and largest city of France. It is located in the north-central part of the country and serves as the political, economic, and cultural center of France.
```

**Answer 2 (Poor):**
```
France has many beautiful cities. Lyon is known for its cuisine, Nice for its beaches, and Marseille for its ports.
```

## Example 2: Technical Explanation

**Query:**
```
Explain how machine learning works in simple terms.
```

**Context:**
```
This is for a general audience with no technical background.
```

**Expected Answer:**
```
Machine learning is a way for computers to learn patterns from data without being explicitly programmed for each task. The computer analyzes examples and finds patterns to make predictions on new, unseen data.
```

**Answer 1 (Good):**
```
Machine learning is like teaching a computer to recognize patterns, similar to how a child learns to identify animals. You show the computer many examples (like thousands of photos of cats and dogs), and it learns to spot the differences. Once trained, it can look at a new photo and predict whether it's a cat or dog based on the patterns it learned.
```

**Answer 2 (Technical):**
```
Machine learning utilizes statistical algorithms and neural networks to optimize objective functions through gradient descent, employing techniques like backpropagation and regularization to minimize overfitting in high-dimensional feature spaces.
```

## Example 3: Creative Writing

**Query:**
```
Write a short story about a robot learning to paint.
```

**Answer 1 (Creative):**
```
ARIA-7 stared at the blank canvas, her mechanical fingers trembling as they gripped the paintbrush. For months, she had analyzed thousands of masterpieces, calculated color theory, and studied brush techniques. But now, facing the empty white space, she felt something her programming couldn't explain—uncertainty.

She dipped the brush in blue paint and made her first stroke. It was clumsy, imperfect. Her sensors screamed "ERROR," but something deeper whispered, "Continue." As hours passed, ARIA-7 discovered that art wasn't about precision—it was about expressing the inexplicable spark that had somehow ignited within her circuits.
```

**Answer 2 (Mechanical):**
```
The robot unit designated RBT-001 was programmed to paint. It analyzed color wavelengths and applied paint to canvas in predetermined patterns. The robot completed the painting task in 2.3 hours with 99.7% accuracy according to its programming parameters.
```

## Example 4: Problem Solving

**Query:**
```
How would you solve traffic congestion in a major city?
```

**Context:**
```
Consider both short-term and long-term solutions for a city with 2 million people.
```

**Answer 1 (Comprehensive):**
```
To solve traffic congestion, I'd implement a multi-layered approach:

Short-term solutions:
- Smart traffic light systems that adapt to real-time traffic flow
- Congestion pricing in downtown areas during peak hours
- Enhanced public transportation with dedicated bus lanes
- Remote work incentives to reduce peak-hour travel

Long-term solutions:
- Expand subway/metro systems with new lines
- Develop mixed-use neighborhoods to reduce commuting distances
- Invest in electric bike-sharing programs and cycling infrastructure
- Implement autonomous vehicle lanes to improve traffic flow efficiency

This combination addresses immediate needs while building sustainable transportation infrastructure.
```

**Answer 2 (Simplistic):**
```
Build more roads and highways to handle more cars.
```

## How to Use These Examples

1. **Copy and paste** the queries, contexts, and answers into the Streamlit app
2. **Compare different answers** using the "Compare Two Answers" mode
3. **Observe how different metrics score** each response:
   - **Relevance**: How well does the answer address the question?
   - **Accuracy**: Is the information correct?
   - **Coherence**: Is the answer well-structured and logical?
   - **Completeness**: Does it fully address all aspects of the question?

## Expected Results

- **Good answers** should score higher across all metrics
- **Technical vs. Simple answers** will show different coherence scores based on context
- **Creative vs. Mechanical answers** will demonstrate completeness and relevance differences
- **Comprehensive vs. Simplistic answers** will show significant completeness score variations

## Tips for Effective Demos

1. **Start with clear examples** like the capital of France
2. **Show contrast** by comparing good vs. poor answers
3. **Explain each metric** as you demonstrate
4. **Use the radar charts** to visualize differences
5. **Highlight the detailed analysis** in the expandable sections
