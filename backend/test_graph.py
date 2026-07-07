import sys
import os

# Add root to python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.orchestrator import orchestrator_graph

def test_graph_execution():
    initial_state = {
        "transactions": [{"amount": 100, "vendor": "Test Corp"}],
        "extracted_data": {},
        "advisory_report": "",
        "revision_count": 0
    }
    
    print("Starting Graph Execution...")
    final_state = orchestrator_graph.invoke(initial_state)
    print("\n--- Final State ---")
    print(f"Revision Count: {final_state.get('revision_count')}")
    print(f"Report: {final_state.get('advisory_report')}")

if __name__ == "__main__":
    test_graph_execution()
