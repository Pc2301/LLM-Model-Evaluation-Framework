#!/usr/bin/env python3
"""
Launcher script for the Streamlit demo app
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit demo app"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the streamlit demo
    demo_path = os.path.join(script_dir, "streamlit_demo.py")
    
    print("🚀 Starting LLM Evaluation Framework Demo...")
    print("📱 The demo will open in your default web browser")
    print("🔗 URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the demo")
    print("-" * 50)
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", demo_path,
            "--server.port", "8501",
            "--server.address", "localhost"
        ], cwd=script_dir)
    except KeyboardInterrupt:
        print("\n👋 Demo stopped. Thanks for using the LLM Evaluation Framework!")
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        print("Make sure you have installed the requirements: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
