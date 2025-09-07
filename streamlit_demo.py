"""
Streamlit Demo App for LLM Evaluation Framework
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
import json
from datetime import datetime

# Import evaluators
from evaluators.relevance_evaluator import RelevanceEvaluator
from evaluators.accuracy_evaluator import AccuracyEvaluator
from evaluators.coherence_evaluator import CoherenceEvaluator
from evaluators.completeness_evaluator import CompletenessEvaluator

# Initialize evaluators
@st.cache_resource
def initialize_evaluators():
    """Initialize all evaluators"""
    return {
        "relevance": RelevanceEvaluator(),
        "accuracy": AccuracyEvaluator(),
        "coherence": CoherenceEvaluator(),
        "completeness": CompletenessEvaluator()
    }

def evaluate_answer(evaluators: Dict, query: str, answer: str, context: str = None, expected_answer: str = None):
    """Evaluate an answer using all available metrics"""
    results = {}
    detailed_results = {}
    
    for name, evaluator in evaluators.items():
        try:
            score, details = evaluator.evaluate(
                query=query,
                answer=answer,
                context=context if context else None,
                expected_answer=expected_answer if expected_answer else None
            )
            results[name] = score
            detailed_results[name] = details
        except Exception as e:
            st.error(f"Error evaluating {name}: {str(e)}")
            results[name] = 0.0
            detailed_results[name] = {"error": str(e)}
    
    return results, detailed_results

def create_radar_chart(scores: Dict[str, float], title: str):
    """Create a radar chart for evaluation scores"""
    categories = list(scores.keys())
    values = list(scores.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=title,
        line_color='rgb(255, 99, 132)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title=f"Evaluation Scores - {title}"
    )
    
    return fig

def create_comparison_chart(scores1: Dict[str, float], scores2: Dict[str, float]):
    """Create a comparison chart between two answers"""
    categories = list(scores1.keys())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=list(scores1.values()),
        theta=categories,
        fill='toself',
        name='Answer 1',
        line_color='rgb(255, 99, 132)'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=list(scores2.values()),
        theta=categories,
        fill='toself',
        name='Answer 2',
        line_color='rgb(54, 162, 235)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="Answer Comparison"
    )
    
    return fig

def main():
    st.set_page_config(
        page_title="LLM Evaluation Demo",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 LLM Evaluation Framework Demo")
    st.markdown("Compare and evaluate LLM responses using multiple metrics")
    
    # Initialize evaluators
    evaluators = initialize_evaluators()
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    evaluation_mode = st.sidebar.selectbox(
        "Evaluation Mode",
        ["Single Answer", "Compare Two Answers"]
    )
    
    # Main input section
    st.header("📝 Input Section")
    
    col1, col2 = st.columns(2)
    
    with col1:
        query = st.text_area(
            "Query/Question",
            placeholder="Enter the question or prompt here...",
            height=100
        )
        
        context = st.text_area(
            "Context (Optional)",
            placeholder="Enter any relevant context...",
            height=80
        )
    
    with col2:
        expected_answer = st.text_area(
            "Expected Answer (Optional)",
            placeholder="Enter the expected/reference answer...",
            height=100
        )
    
    # Answer input section
    if evaluation_mode == "Single Answer":
        st.subheader("Answer to Evaluate")
        answer = st.text_area(
            "Answer",
            placeholder="Enter the LLM response to evaluate...",
            height=150,
            key="single_answer"
        )
        
        if st.button("Evaluate Answer", type="primary"):
            if query and answer:
                with st.spinner("Evaluating answer..."):
                    scores, details = evaluate_answer(
                        evaluators, query, answer, context, expected_answer
                    )
                
                # Display results
                st.header("📊 Evaluation Results")
                
                # Overall score
                overall_score = sum(scores.values()) / len(scores)
                st.metric("Overall Score", f"{overall_score:.3f}")
                
                # Individual scores
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Individual Scores")
                    for metric, score in scores.items():
                        st.metric(metric.title(), f"{score:.3f}")
                
                with col2:
                    st.subheader("Score Visualization")
                    fig = create_radar_chart(scores, "Answer Evaluation")
                    st.plotly_chart(fig, use_container_width=True)
                
                # Detailed results
                st.subheader("Detailed Analysis")
                for metric, detail in details.items():
                    with st.expander(f"{metric.title()} Details"):
                        st.json(detail)
            else:
                st.error("Please provide both query and answer.")
    
    else:  # Compare Two Answers
        st.subheader("Answers to Compare")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Answer 1**")
            answer1 = st.text_area(
                "Answer 1",
                placeholder="Enter the first LLM response...",
                height=150,
                key="answer1"
            )
        
        with col2:
            st.markdown("**Answer 2**")
            answer2 = st.text_area(
                "Answer 2",
                placeholder="Enter the second LLM response...",
                height=150,
                key="answer2"
            )
        
        if st.button("Compare Answers", type="primary"):
            if query and answer1 and answer2:
                with st.spinner("Evaluating both answers..."):
                    scores1, details1 = evaluate_answer(
                        evaluators, query, answer1, context, expected_answer
                    )
                    scores2, details2 = evaluate_answer(
                        evaluators, query, answer2, context, expected_answer
                    )
                
                # Display comparison results
                st.header("📊 Comparison Results")
                
                # Overall scores comparison
                overall1 = sum(scores1.values()) / len(scores1)
                overall2 = sum(scores2.values()) / len(scores2)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Answer 1 Overall", f"{overall1:.3f}")
                with col2:
                    st.metric("Answer 2 Overall", f"{overall2:.3f}")
                with col3:
                    difference = overall2 - overall1
                    st.metric("Difference", f"{difference:.3f}", delta=f"{difference:.3f}")
                
                # Comparison visualization
                st.subheader("Score Comparison")
                fig_comparison = create_comparison_chart(scores1, scores2)
                st.plotly_chart(fig_comparison, use_container_width=True)
                
                # Side-by-side detailed scores
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Answer 1 Scores")
                    for metric, score in scores1.items():
                        st.metric(metric.title(), f"{score:.3f}")
                
                with col2:
                    st.subheader("Answer 2 Scores")
                    for metric, score in scores2.items():
                        st.metric(metric.title(), f"{score:.3f}")
                
                # Detailed comparison table
                st.subheader("Detailed Comparison")
                comparison_df = pd.DataFrame({
                    'Metric': list(scores1.keys()),
                    'Answer 1': list(scores1.values()),
                    'Answer 2': list(scores2.values()),
                    'Difference': [scores2[k] - scores1[k] for k in scores1.keys()]
                })
                st.dataframe(comparison_df, use_container_width=True)
                
                # Winner analysis
                st.subheader("🏆 Winner Analysis")
                winner_count = {
                    'Answer 1': sum(1 for k in scores1.keys() if scores1[k] > scores2[k]),
                    'Answer 2': sum(1 for k in scores1.keys() if scores2[k] > scores1[k]),
                    'Tie': sum(1 for k in scores1.keys() if scores1[k] == scores2[k])
                }
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Answer 1 Wins", winner_count['Answer 1'])
                with col2:
                    st.metric("Answer 2 Wins", winner_count['Answer 2'])
                with col3:
                    st.metric("Ties", winner_count['Tie'])
                
                # Detailed analysis expandable sections
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Answer 1 Detailed Analysis")
                    for metric, detail in details1.items():
                        with st.expander(f"{metric.title()} Details"):
                            st.json(detail)
                
                with col2:
                    st.subheader("Answer 2 Detailed Analysis")
                    for metric, detail in details2.items():
                        with st.expander(f"{metric.title()} Details"):
                            st.json(detail)
            else:
                st.error("Please provide query and both answers.")
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit and the LLM Evaluation Framework")

if __name__ == "__main__":
    main()
