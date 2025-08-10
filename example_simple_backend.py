#!/usr/bin/env python3
"""
Simple Backend Example using Cortex
No Flask/FastAPI needed - just pure Python
Shows how to use Cortex in any backend
"""

from cortex import Client
import json


class SimpleCoachingBackend:
    """A simple backend that could be used in any Python application"""
    
    def __init__(self):
        self.client = Client(db_path="./coaching.db")
        self.coaches = {
            "fitness": {
                "name": "Mike",
                "personality": "Energetic and motivating",
                "instructions": "You are a fitness coach. Help with exercise and nutrition."
            },
            "career": {
                "name": "Robert",
                "personality": "Professional and strategic",
                "instructions": "You are a career coach. Provide career advice and interview tips."
            },
            "mindfulness": {
                "name": "Sarah",
                "personality": "Calm and peaceful",
                "instructions": "You are a mindfulness coach. Help with meditation and stress relief."
            }
        }
    
    def handle_message(self, coach_id: str, message: str, previous_response_id: str = None):
        """
        Handle a message to a coach
        
        Args:
            coach_id: Which coach to use
            message: User's message
            previous_response_id: Optional ID to continue conversation
            
        Returns:
            Dict with response_id and reply text
        """
        coach = self.coaches.get(coach_id)
        if not coach:
            return {"error": f"Coach '{coach_id}' not found"}
        
        # Build parameters
        params = {
            "model": "cohere",
            "input": message,
            "store": True
        }
        
        if previous_response_id:
            # Continue conversation
            params["previous_response_id"] = previous_response_id
        else:
            # New conversation - add instructions
            full_instructions = f"{coach['instructions']} Your personality: {coach['personality']}"
            params["instructions"] = full_instructions
        
        # Call Cortex
        response = self.client.create(**params)
        
        if response.get("error"):
            return {"error": response["error"]["message"]}
        
        # Extract reply
        reply = response["output"][0]["content"][0]["text"]
        
        return {
            "response_id": response["id"],
            "reply": reply,
            "coach_name": coach["name"]
        }


def demo():
    """Demonstrate the backend usage"""
    print("="*60)
    print("SIMPLE BACKEND DEMO - No Flask Required!")
    print("="*60)
    
    backend = SimpleCoachingBackend()
    
    # User 1: Alice talks to fitness coach
    print("\n👤 Alice → Fitness Coach")
    print("Message: 'I want to start exercising'")
    
    response1 = backend.handle_message(
        coach_id="fitness",
        message="I want to start exercising"
    )
    
    if "error" not in response1:
        print(f"Coach Mike: {response1['reply'][:150]}...")
        print(f"Response ID: {response1['response_id']}")
        
        # Alice continues
        print("\n👤 Alice → Fitness Coach (continuing)")
        print("Message: 'What about diet?'")
        
        response2 = backend.handle_message(
            coach_id="fitness",
            message="What about diet?",
            previous_response_id=response1["response_id"]
        )
        
        print(f"Coach Mike: {response2['reply'][:150]}...")
    else:
        print(f"Error: {response1['error']}")
    
    # User 2: Bob talks to career coach
    print("\n👤 Bob → Career Coach")
    print("Message: 'I have an interview tomorrow'")
    
    response3 = backend.handle_message(
        coach_id="career",
        message="I have an interview tomorrow"
    )
    
    if "error" not in response3:
        print(f"Coach Robert: {response3['reply'][:150]}...")
    else:
        print(f"Error: {response3['error']}")
    
    # User 3: Charlie talks to mindfulness coach
    print("\n👤 Charlie → Mindfulness Coach")
    print("Message: 'I am feeling anxious'")
    
    response4 = backend.handle_message(
        coach_id="mindfulness",
        message="I am feeling anxious"
    )
    
    if "error" not in response4:
        print(f"Coach Sarah: {response4['reply'][:150]}...")
    else:
        print(f"Error: {response4['error']}")
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("""
This simple backend can be used in:
- Django views
- Flask routes  
- FastAPI endpoints
- Discord bots
- Telegram bots
- CLI applications
- Desktop apps
- Anywhere Python runs!

No web framework required - just pure Python!
    """)


if __name__ == "__main__":
    demo()