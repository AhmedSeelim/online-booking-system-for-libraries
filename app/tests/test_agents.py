"""
Test script for CrewAI agent (works offline with mock data)

Usage:
    python test_agents.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents import create_agent_system


def test_book_operations():
    """Test book-related operations"""
    print("\n" + "="*80)
    print("TEST 1: Book Operations")
    print("="*80)

    test_messages = [
        "Show me programming books",
        "I want to buy Clean Code",
        "Search for fiction books",
    ]

    agent_system = create_agent_system(user_id=1)

    for msg in test_messages:
        print(f"\n→ User: {msg}")
        try:
            response = agent_system.process_message(msg)
            print(f"← Agent: {response[:300]}...")
        except Exception as e:
            print(f"✗ Error: {e}")


def test_resource_operations():
    """Test resource and booking operations"""
    print("\n" + "="*80)
    print("TEST 2: Resource & Booking Operations")
    print("="*80)

    test_messages = [
        "Show me available study rooms",
        "Is Conference Room A available tomorrow at 2pm for 2 hours?",
        "Book Conference Room A for tomorrow 2pm to 4pm",
        "Cancel my booking",
    ]

    agent_system = create_agent_system(user_id=1)

    for msg in test_messages:
        print(f"\n→ User: {msg}")
        try:
            response = agent_system.process_message(msg)
            print(f"← Agent: {response[:300]}...")
        except Exception as e:
            print(f"✗ Error: {e}")


def test_mixed_requests():
    """Test mixed requests"""
    print("\n" + "="*80)
    print("TEST 3: Mixed Requests")
    print("="*80)

    test_messages = [
        "What are your library hours?",
        "I need a study room and also want to buy a book about Python",
        "Show me all available resources with at least 5 capacity",
    ]

    agent_system = create_agent_system(user_id=1)

    for msg in test_messages:
        print(f"\n→ User: {msg}")
        try:
            response = agent_system.process_message(msg)
            print(f"← Agent: {response[:300]}...")
        except Exception as e:
            print(f"✗ Error: {e}")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("CREWAI LIBRARY ASSISTANT - OFFLINE TEST SUITE")
    print("="*80)
    print("\nSingle Agent with 6 Tools:")
    print("  1. list_books")
    print("  2. purchase_book")
    print("  3. list_resources")
    print("  4. check_resource_availability")
    print("  5. create_booking")
    print("  6. cancel_booking")
    print("\nNote: Using mock data for offline testing")
    print("Set MOCK_MODE=False in tools.py to use real database\n")

    try:
        test_book_operations()
        test_resource_operations()
        test_mixed_requests()

        print("\n" + "="*80)
        print("ALL TESTS COMPLETED")
        print("="*80 + "\n")

    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\nTest suite error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()