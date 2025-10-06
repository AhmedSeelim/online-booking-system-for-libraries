"""
CrewAI Agent Implementation
Creates and manages the three crews: Receptionist, Books Officer, Resources Officer
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from crewai import Agent, Task, Crew, Process, LLM
from langchain.output_parsers import PydanticOutputParser
from app.agents.config import GOOGLE_API_KEY
from app.agents.models import ReceptionistOutput
from app.agents.tools import create_book_tools, create_resource_tools
from app.crud.ai_audit_log import create_audit_log


# Load configuration files
CONFIG_DIR = Path(__file__).parent / "config"

def load_yaml_config(filename: str) -> Dict[str, Any]:
    """Load YAML configuration file"""
    config_path = CONFIG_DIR / filename
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


# Load agent and task configurations
agents_config = load_yaml_config("agents.yaml")
tasks_config = load_yaml_config("tasks.yaml")

# Initialize LLM
gemini_llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=GOOGLE_API_KEY
)


class LibraryAgentSystem:
    """Main system managing all three crews"""

    def __init__(self, user_id: int):
        """
        Initialize the agent system

        Args:
            user_id: Current user ID for context
        """
        self.user_id = user_id
        self.receptionist_crew = self._create_receptionist_crew()
        self.books_crew = self._create_books_crew()
        self.resources_crew = self._create_resources_crew()

    def _create_receptionist_crew(self) -> Crew:
        """Create the receptionist crew for intent classification"""

        # Create output parser for structured Pydantic output
        output_parser = PydanticOutputParser(pydantic_object=ReceptionistOutput)

        # Create receptionist agent
        receptionist_agent = Agent(
            role=agents_config['receptionist_agent']['role'],
            goal=agents_config['receptionist_agent']['goal'],
            backstory=agents_config['receptionist_agent']['backstory'],
            verbose=True,
            memory=False,
            llm=gemini_llm,
            allow_delegation=False
        )

        # Create receptionist task
        receptionist_task = Task(
            description=tasks_config['receptionist_task']['description'],
            expected_output=tasks_config['receptionist_task']['expected_output'],
            agent=receptionist_agent,
            output_pydantic=ReceptionistOutput
        )

        # Create crew
        receptionist_crew = Crew(
            agents=[receptionist_agent],
            tasks=[receptionist_task],
            process=Process.sequential,
            verbose=True
        )

        return receptionist_crew

    def _create_books_crew(self) -> Crew:
        """Create the books officer crew"""

        # Create book tools
        book_tools = create_book_tools()

        # Create books officer agent
        book_officer_agent = Agent(
            role=agents_config['Book_Officerr_agent']['role'],
            goal=agents_config['Book_Officerr_agent']['goal'],
            backstory=agents_config['Book_Officerr_agent']['backstory'],
            verbose=True,
            memory=False,
            tools=book_tools,
            llm=gemini_llm,
            allow_delegation=False
        )

        # Create books task
        book_officer_task = Task(
            description=tasks_config['Book_Officer_task']['description'],
            expected_output=tasks_config['Book_Officer_task']['expected_output'],
            agent=book_officer_agent
        )

        # Create crew
        books_crew = Crew(
            agents=[book_officer_agent],
            tasks=[book_officer_task],
            process=Process.sequential,
            verbose=True
        )

        return books_crew

    def _create_resources_crew(self) -> Crew:
        """Create the resources officer crew"""

        # Create resource tools
        resource_tools = create_resource_tools()

        # Create resources officer agent
        resources_officer_agent = Agent(
            role=agents_config['Resources_Office_agent']['role'],
            goal=agents_config['Resources_Office_agent']['goal'],
            backstory=agents_config['Resources_Office_agent']['backstory'],
            verbose=True,
            memory=False,
            tools=resource_tools,
            llm=gemini_llm,
            allow_delegation=False
        )

        # Create resources task
        resources_officer_task = Task(
            description=tasks_config['Resources_Officer_task']['description'],
            expected_output=tasks_config['Resources_Officer_task']['expected_output'],
            agent=resources_officer_agent
        )

        # Create crew
        resources_crew = Crew(
            agents=[resources_officer_agent],
            tasks=[resources_officer_task],
            process=Process.sequential,
            verbose=True
        )

        return resources_crew

    def process_message(self, user_message: str) -> str:
        """
        Process a user message through the agent system

        Args:
            user_message: User's input message

        Returns:
            Response string from the appropriate crew
        """
        try:
            # Step 1: Receptionist classifies intent
            print(f"\n{'='*60}")
            print("RECEPTIONIST: Classifying intent...")
            print(f"{'='*60}\n")

            receptionist_result = self.receptionist_crew.kickoff(
                inputs={"user_message": user_message}
            )

            intent_result = receptionist_result.to_dict()

            # Log to audit
            self._log_audit(
                agent_type="receptionist",
                input_text=user_message,
                detected_intent=intent_result["intent"],
                actions_taken={"classification": intent_result}
            )

            # Step 2: Route based on intent
            print(f"\n{'='*60}")
            print("INTENT:" ,intent_result["intent"])
            print ("confidence:" ,intent_result["confidence"])
            print(f"{'='*60}\n")

            if intent_result["intent"] == "other_question":
                # Handle directly
                response = intent_result["parsed_details"].get("response",
                    "I'd be happy to help! The library is open Monday-Friday 9am-9pm, "
                    "and Saturday-Sunday 10am-6pm. How else can I assist you?")
                return response

            elif intent_result["intent"] == "book_question":
                # Route to books crew
                print(f"\n{'='*60}")
                print("BOOK OFFICER: Processing book request...")
                print(f"{'='*60}\n")

                context = self._build_context(user_message, intent_result["parsed_details"])
                result = self.books_crew.kickoff(
                    inputs={
                        "user_message": user_message,
                        "user_id": self.user_id,
                        "context": context
                    }
                )

                self._log_audit(
                    agent_type="book_officer",
                    input_text=user_message,
                    detected_intent="book_operation",
                    actions_taken={"result": str(result)}
                )

                return str(result)

            elif intent_result["intent"] == "resources_question":
                # Route to resources crew
                print(f"\n{'='*60}")
                print("RESOURCES OFFICER: Processing booking request...")
                print(f"{'='*60}\n")

                context = self._build_context(user_message, intent_result["parsed_details"])
                result = self.resources_crew.kickoff(
                    inputs={
                        "user_message": user_message,
                        "user_id": self.user_id,
                        "context": context
                    }
                )

                self._log_audit(
                    agent_type="resources_officer",
                    input_text=user_message,
                    detected_intent="resource_operation",
                    actions_taken={"result": str(result)}
                )

                return str(result)

            else:  # This should rarely happen now
                return "I'd be happy to help! Could you please provide more details about what you need?"

        except Exception as e:
            print(f"Error processing message: {e}")
            return f"I encountered an error processing your request. Please try again or rephrase your question."

    def _build_context(self, user_message: str, parsed_details: Optional[Dict[str, Any]]) -> str:
        """Build context string for specialist crews"""
        context = f"User ID: {self.user_id}\n"
        context += f"##USER MESSAGE: {user_message}\n"

        if parsed_details:
            context += "\nExtracted details:\n"
            for key, value in parsed_details.items():
                context += f"  - {key}: {value}\n"

        return context

    def _log_audit(self, agent_type: str, input_text: str, detected_intent: str,
                   actions_taken: Dict[str, Any], metadata: Optional[Dict] = None):
        """Log agent action to audit log"""
        try:
            import json
            from app.database import engine
            from sqlmodel import Session

            with Session(engine) as db:
                create_audit_log(
                    db=db,
                    agent_type=agent_type,
                    input_text=input_text[:500],  # Truncate if too long
                    detected_intent=detected_intent,
                    actions_taken=json.dumps(actions_taken),
                    metadata=json.dumps(metadata) if metadata else None
                )
        except Exception as e:
            print(f"Warning: Could not log to audit: {e}")


def create_agent_system(user_id: int) -> LibraryAgentSystem:
    """
    Factory function to create a new agent system instance

    Args:
        user_id: Current user ID

    Returns:
        Configured LibraryAgentSystem instance
    """
    return LibraryAgentSystem(user_id=user_id)