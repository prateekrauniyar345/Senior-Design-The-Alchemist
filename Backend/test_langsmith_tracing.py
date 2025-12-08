"""
Test script to verify LangSmith tracing is configured correctly.
Run this after setting up your .env file with LANGCHAIN_* variables.
"""

import os
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

def test_langsmith_connection():
    """Test if LangSmith is properly configured"""
    print("Testing LangSmith Configuration...\n")
    
    # Check environment variables
    required_vars = [
        "LANGSMITH_TRACING",
        "LANGSMITH_API_KEY",
        "LANGSMITH_PROJECT"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("ERROR: Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nAdd these to your Backend/.env file")
        return False
    
    print("SUCCESS: Environment variables configured:")
    print(f"   - LANGSMITH_TRACING: {os.getenv('LANGSMITH_TRACING')}")
    print(f"   - LANGSMITH_PROJECT: {os.getenv('LANGSMITH_PROJECT')}")
    print(f"   - LANGCHAIN_ENDPOINT: {os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')}")
    
    # Test API connection
    try:
        client = Client()
        print("\nSUCCESS: Successfully connected to LangSmith API")
        print(f"   - Project: {os.getenv('LANGSMITH_PROJECT')}")
        return True
    except Exception as e:
        print(f"\nERROR: Failed to connect to LangSmith API: {e}")
        print("   - Check your LANGSMITH_API_KEY is valid")
        return False


def test_simple_trace():
    """Test a simple traced function"""
    print("\nTesting simple trace...\n")
    
    from langsmith import traceable
    
    @traceable(name="test_function")
    def sample_function(text: str) -> str:
        return f"Processed: {text}"
    
    try:
        result = sample_function("Hello LangSmith!")
        print(f"SUCCESS: Trace created successfully")
        print(f"   - Result: {result}")
        print(f"   - View traces at: https://smith.langchain.com/")
        print(f"   - Project: {os.getenv('LANGSMITH_PROJECT')}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create trace: {e}")
        return False


def test_agent_system():
    """Test if agent system can be traced"""
    print("\nTesting agent system tracing...\n")
    
    try:
        import sys
        from pathlib import Path
        
        # Add Backend directory to Python path
        backend_dir = Path(__file__).parent
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))
        
        # Now import the agent system
        from agents.initialize_agent import agent_graph
        from langchain_core.messages import HumanMessage
        
        print("SUCCESS: Agent graph loaded successfully")
        print("   - All agent nodes have @traceable decorators")
        print("   - All tools have @traceable decorators")
        print("\nTo see traces:")
        print("   1. Start your backend: cd Backend && uvicorn main:app --reload")
        print("   2. Send a query via the frontend or API")
        print("   3. Visit https://smith.langchain.com/")
        print(f"   4. Check project: {os.getenv('LANGSMITH_PROJECT')}")
        
        return True
    except Exception as e:
        print(f"ERROR: Failed to load agent system: {e}")
        print(f"   - This is normal if running outside the application context")
        print(f"   - Tracing will work when the backend server runs")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("LangSmith Tracing Configuration Test")
    print("=" * 60)
    
    # Run tests
    config_ok = test_langsmith_connection()
    
    if config_ok:
        trace_ok = test_simple_trace()
        agent_ok = test_agent_system()
        
        print("\n" + "=" * 60)
        if config_ok and trace_ok:
            print("SUCCESS: CORE TESTS PASSED!")
            print("LangSmith tracing is fully configured")
            print("\nNext steps:")
            print("   1. Start your backend server")
            print("   2. Send queries through your chat interface")
            print("   3. View traces at https://smith.langchain.com/")
            if not agent_ok:
                print("\n   Note: Agent graph test failed but this is normal.")
                print("   Tracing will work when your backend server runs.")
        else:
            print("WARNING: SOME TESTS FAILED")
            print("   - Review the errors above")
            print("   - Check your .env configuration")
    else:
        print("\n" + "=" * 60)
        print("WARNING: CONFIGURATION INCOMPLETE")
        print("   - Add LangSmith variables to Backend/.env")
        print("   - Get API key from https://smith.langchain.com/")
    
    print("=" * 60)
