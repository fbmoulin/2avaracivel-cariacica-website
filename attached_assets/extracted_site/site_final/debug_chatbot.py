#!/usr/bin/env python3
"""
Debug script for chatbot OpenAI integration
Tests the chatbot service directly to identify issues
"""

import os
import sys
import logging
from openai import OpenAI

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def test_openai_connection():
    """Test OpenAI API connection directly"""
    print("Testing OpenAI API connection...")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found in environment")
        return False
    
    print(f"API Key found: {api_key[:10]}...")
    
    try:
        client = OpenAI(api_key=api_key)
        print("OpenAI client created successfully")
        
        # Test with a simple message
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente da 2ª Vara Cível de Cariacica. Responda brevemente."
                },
                {
                    "role": "user", 
                    "content": "Qual o horário de funcionamento?"
                }
            ],
            max_tokens=100,
            temperature=0.7,
            timeout=30
        )
        
        if response.choices and response.choices[0].message.content:
            print("SUCCESS: OpenAI API is working")
            print(f"Response: {response.choices[0].message.content}")
            return True
        else:
            print("ERROR: Empty response from OpenAI")
            return False
            
    except Exception as e:
        print(f"ERROR: OpenAI API failed - {e}")
        return False

def test_chatbot_service():
    """Test the chatbot service"""
    print("\nTesting chatbot service...")
    
    try:
        # Import the chatbot service
        sys.path.append('.')
        from services.chatbot import ChatbotService
        
        chatbot = ChatbotService()
        print(f"Chatbot service initialized. OpenAI client: {chatbot.openai_client is not None}")
        
        # Test with a message
        test_message = "Qual o horário de funcionamento?"
        response = chatbot.get_response(test_message)
        
        print(f"Test message: {test_message}")
        print(f"Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Chatbot service failed - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection for chat logging"""
    print("\nTesting database connection...")
    
    try:
        from app_factory import create_app
        from models import ChatMessage, db
        
        app = create_app()
        with app.app_context():
            # Test database connection
            db.engine.execute("SELECT 1")
            print("Database connection successful")
            
            # Test chat message creation
            test_chat = ChatMessage(
                user_message="Test message",
                bot_response="Test response",
                session_id="test-session"
            )
            db.session.add(test_chat)
            db.session.commit()
            
            # Clean up
            db.session.delete(test_chat)
            db.session.commit()
            
            print("Database operations successful")
            return True
            
    except Exception as e:
        print(f"ERROR: Database test failed - {e}")
        return False

if __name__ == "__main__":
    print("=== Chatbot Debug Test ===\n")
    
    results = {
        "OpenAI API": test_openai_connection(),
        "Chatbot Service": test_chatbot_service(),
        "Database": test_database_connection()
    }
    
    print("\n=== Test Results ===")
    for test, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test}: {status}")
    
    if all(results.values()):
        print("\nAll tests passed! Chatbot should be working.")
    else:
        print("\nSome tests failed. Check the errors above.")