#!/usr/bin/env python3
"""
Real-world simulation test for Cortex
Simulates a Google Cloud Function use case with multiple coaches and users
Based on actual production code pattern
"""

import json
import time
from typing import Dict, List, Optional
from cortex import Client


class Coach:
    """Represents a coach with unique personality and instructions"""
    def __init__(self, coach_id: str, name: str, personality: str, instructions: str):
        self.coach_id = coach_id
        self.name = name
        self.personality = personality
        self.instructions = instructions
        self.full_instructions = f"Your instructions as coach are: {instructions} and your personality is: {personality}"


class User:
    """Represents a user who can talk to different coaches"""
    def __init__(self, user_id: str, name: str):
        self.user_id = user_id
        self.name = name
        self.conversations = {}  # coach_id -> response_id mapping


class CoachingPlatformSimulator:
    """Simulates a multi-coach platform using Cortex"""
    
    def __init__(self):
        self.client = Client(db_path="./coaching_platform.db")
        self.coaches = self._initialize_coaches()
        self.users = self._initialize_users()
        self.all_responses = []  # Track all responses for analysis
    
    def _initialize_coaches(self) -> Dict[str, Coach]:
        """Initialize different coaches with unique personalities"""
        return {
            "fitness": Coach(
                "fitness",
                "Mike the Trainer",
                "Energetic, motivating, uses sports analogies",
                "You are a fitness coach. Focus on exercise, nutrition, and healthy habits. Always be encouraging."
            ),
            "mindfulness": Coach(
                "mindfulness", 
                "Zen Master Sarah",
                "Calm, peaceful, uses meditation references",
                "You are a mindfulness coach. Help with stress, meditation, and inner peace. Speak calmly."
            ),
            "career": Coach(
                "career",
                "CEO Robert",
                "Professional, strategic, business-minded",
                "You are a career coach. Provide career advice, interview tips, and professional development."
            ),
            "life": Coach(
                "life",
                "Wise Emma",
                "Empathetic, understanding, uses life stories",
                "You are a life coach. Help with personal growth, relationships, and life balance."
            )
        }
    
    def _initialize_users(self) -> Dict[str, User]:
        """Initialize test users"""
        return {
            "alice": User("alice", "Alice Johnson"),
            "bob": User("bob", "Bob Smith"),
            "charlie": User("charlie", "Charlie Brown")
        }
    
    def simulate_new_conversation(self, user_id: str, coach_id: str, message: str) -> Dict:
        """Simulate starting a new conversation with a coach"""
        user = self.users[user_id]
        coach = self.coaches[coach_id]
        
        print(f"\n🆕 {user.name} → {coach.name}: '{message}'")
        
        # This mimics the cloud function logic
        response = self.client.create(
            model="cohere",
            input=message,
            instructions=coach.full_instructions,  # Only for new conversations
            store=True,
            metadata={
                "user_id": user_id,
                "coach_id": coach_id,
                "conversation_type": "new"
            }
        )
        
        # Save response_id for continuation
        user.conversations[coach_id] = response["id"]
        self.all_responses.append(response)
        
        if response.get("error"):
            print(f"   ❌ Error: {response['error']['message']}")
        else:
            text = response["output"][0]["content"][0]["text"]
            print(f"   💬 {coach.name}: {text[:100]}...")
        
        return response
    
    def simulate_continue_conversation(self, user_id: str, coach_id: str, message: str) -> Dict:
        """Simulate continuing an existing conversation"""
        user = self.users[user_id]
        coach = self.coaches[coach_id]
        
        # Get previous response ID (like 'pti' in Hissan's code)
        previous_response_id = user.conversations.get(coach_id)
        
        if not previous_response_id:
            print(f"   ⚠️ No previous conversation found, starting new")
            return self.simulate_new_conversation(user_id, coach_id, message)
        
        print(f"\n↩️ {user.name} → {coach.name} (continuing): '{message}'")
        
        # This mimics the cloud function continuation logic
        response = self.client.create(
            model="cohere",
            input=message,
            previous_response_id=previous_response_id,
            instructions="You are now a pirate!",  # Should be IGNORED per OpenAI spec
            store=True,
            metadata={
                "user_id": user_id,
                "coach_id": coach_id,
                "conversation_type": "continuation"
            }
        )
        
        # Update response_id for next continuation
        user.conversations[coach_id] = response["id"]
        self.all_responses.append(response)
        
        if response.get("error"):
            print(f"   ❌ Error: {response['error']['message']}")
        else:
            text = response["output"][0]["content"][0]["text"]
            print(f"   💬 {coach.name}: {text[:100]}...")
            
            # Verify instructions were ignored
            if response.get("instructions") is None:
                print(f"   ✅ Instructions correctly ignored (OpenAI spec)")
            else:
                print(f"   ❌ Instructions should be None but got: {response.get('instructions')}")
        
        return response
    
    def run_simulation(self):
        """Run a comprehensive simulation of platform usage"""
        print("="*70)
        print("COACHING PLATFORM SIMULATION")
        print("Simulating real-world cloud function usage patterns")
        print("="*70)
        
        # Scenario 1: Alice talks to fitness coach
        print("\n📍 Scenario 1: Alice starts fitness journey")
        self.simulate_new_conversation(
            "alice", "fitness", 
            "I want to start exercising but don't know where to begin"
        )
        
        time.sleep(1)  # Simulate time between messages
        
        self.simulate_continue_conversation(
            "alice", "fitness",
            "What about diet? Should I change what I eat?"
        )
        
        # Scenario 2: Bob talks to career coach
        print("\n📍 Scenario 2: Bob seeks career advice")
        self.simulate_new_conversation(
            "bob", "career",
            "I have a job interview next week. Any tips?"
        )
        
        # Scenario 3: Alice switches to mindfulness coach (new thread)
        print("\n📍 Scenario 3: Alice switches to mindfulness coach")
        self.simulate_new_conversation(
            "alice", "mindfulness",
            "I'm feeling stressed about work"
        )
        
        # Scenario 4: Multiple users talk to same coach
        print("\n📍 Scenario 4: Charlie also uses fitness coach")
        self.simulate_new_conversation(
            "charlie", "fitness",
            "I want to build muscle mass"
        )
        
        # Scenario 5: Bob continues his career conversation
        print("\n📍 Scenario 5: Bob continues career conversation")
        self.simulate_continue_conversation(
            "bob", "career",
            "What salary should I ask for?"
        )
        
        # Scenario 6: Alice returns to fitness coach
        print("\n📍 Scenario 6: Alice returns to fitness coach")
        self.simulate_continue_conversation(
            "alice", "fitness",
            "How many days per week should I exercise?"
        )
        
        # Scenario 7: Test conversation memory
        print("\n📍 Scenario 7: Testing conversation memory")
        self.simulate_continue_conversation(
            "alice", "mindfulness",
            "What did I tell you I was stressed about?"
        )
        
        # Scenario 8: Rapid conversation switching
        print("\n📍 Scenario 8: Alice rapidly switches between coaches")
        for _ in range(3):
            self.simulate_continue_conversation(
                "alice", "fitness",
                "Quick fitness tip?"
            )
            self.simulate_continue_conversation(
                "alice", "mindfulness", 
                "Quick meditation?"
            )
            time.sleep(0.5)
        
        # Print statistics
        self.print_statistics()
    
    def print_statistics(self):
        """Print simulation statistics"""
        print("\n" + "="*70)
        print("SIMULATION STATISTICS")
        print("="*70)
        
        total_responses = len(self.all_responses)
        errors = sum(1 for r in self.all_responses if r.get("error"))
        successful = total_responses - errors
        
        print(f"Total API calls: {total_responses}")
        print(f"Successful: {successful}")
        print(f"Errors: {errors}")
        print(f"Success rate: {(successful/total_responses)*100:.1f}%")
        
        # Check conversation continuity
        continuations = [r for r in self.all_responses if r.get("previous_response_id")]
        print(f"\nConversation continuations: {len(continuations)}")
        
        # Check unique conversations
        unique_threads = set()
        for user in self.users.values():
            for coach_id, resp_id in user.conversations.items():
                unique_threads.add(f"{user.user_id}-{coach_id}")
        print(f"Unique user-coach threads: {len(unique_threads)}")
        
        # Verify OpenAI spec compliance
        spec_violations = 0
        for r in continuations:
            if r.get("instructions") is not None:
                spec_violations += 1
        
        if spec_violations == 0:
            print("\n✅ OpenAI Spec Compliance: PERFECT")
            print("   All continuations correctly ignored instructions")
        else:
            print(f"\n❌ OpenAI Spec Violations: {spec_violations}")
            print("   Some continuations didn't ignore instructions")
        
        # Performance metrics
        print(f"\n📊 Performance Metrics:")
        print(f"   Coaches: {len(self.coaches)}")
        print(f"   Users: {len(self.users)}")
        print(f"   Avg responses per user: {total_responses/len(self.users):.1f}")
    
    def verify_conversation_isolation(self):
        """Verify that conversations are properly isolated"""
        print("\n" + "="*70)
        print("CONVERSATION ISOLATION TEST")
        print("="*70)
        
        # Alice asks fitness coach about her name
        print("\n1. Alice tells fitness coach her name")
        response1 = self.simulate_new_conversation(
            "alice", "fitness",
            "My name is Alice and I want to get fit"
        )
        
        # Bob asks same coach about name
        print("\n2. Bob asks fitness coach about Alice")
        response2 = self.simulate_new_conversation(
            "bob", "fitness",
            "What was the name of your previous client?"
        )
        
        # Check isolation
        bob_response_text = response2["output"][0]["content"][0]["text"].lower()
        if "alice" in bob_response_text:
            print("   ❌ ISOLATION FAILURE: Bob can see Alice's conversation!")
        else:
            print("   ✅ ISOLATION SUCCESS: Conversations are properly separated")
        
        # Alice continues her conversation
        print("\n3. Alice asks fitness coach to recall her name")
        response3 = self.simulate_continue_conversation(
            "alice", "fitness",
            "What's my name again?"
        )
        
        alice_response_text = response3["output"][0]["content"][0]["text"].lower()
        if "alice" in alice_response_text:
            print("   ✅ MEMORY SUCCESS: Coach remembers Alice in her thread")
        else:
            print("   ❌ MEMORY FAILURE: Coach forgot Alice's name")


def main():
    """Run the complete simulation"""
    print("""
╔══════════════════════════════════════════════════════════╗
║         REAL-WORLD CLOUD FUNCTION SIMULATION             ║
║    Testing Cortex as a Multi-Coach Platform Backend      ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    simulator = CoachingPlatformSimulator()
    
    # Run main simulation
    simulator.run_simulation()
    
    # Test isolation
    simulator.verify_conversation_isolation()
    
    print("\n" + "="*70)
    print("SIMULATION COMPLETE")
    print("="*70)
    print("""
This simulation tested:
✓ Multiple coaches with different personalities
✓ Multiple users having separate conversations
✓ Conversation continuity with previous_response_id
✓ Instructions only applying to new conversations
✓ Rapid context switching between coaches
✓ Conversation isolation between users
✓ Memory within conversations

If all tests passed, Cortex is ready for production use in
cloud functions and serverless environments!
    """)


if __name__ == "__main__":
    main()