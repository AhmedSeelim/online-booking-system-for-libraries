from app.agents import create_agent_system

test_messages = [
    "What are your library hours?",
    "I want to buy the book Clean Code",
    "Can I book a conference room for tomorrow at 2pm?",
    "Show me all technology books",
    "I need to cancel my booking"
]

agent_system = create_agent_system(user_id=1)

msg="Show me all technology books"
print(f"\n→ User: {msg}")
try:
    response = agent_system.process_message(msg)
    print(f"← Agent: {response[:200]}...")
except Exception as e:
    print(f"✗ Error: {e}")