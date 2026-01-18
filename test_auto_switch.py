#!/usr/bin/env python3
"""
Test Auto-Switch Functionality
Tests if all 4 chatbots (Academic, Code, Content, General) 
can auto-switch based on intent detection
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

# ANSI Colors
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
END = '\033[0m'

def header(msg):
    print(f"\n{BLUE}{'='*70}")
    print(f"  {msg}")
    print(f"{'='*70}{END}\n")

def success(msg):
    print(f"{GREEN}✓ {msg}{END}")

def error(msg):
    print(f"{RED}✗ {msg}{END}")

def info(msg):
    print(f"{YELLOW}→ {msg}{END}")

def test_case(test_num, message, expected_agent, selected_agent=None):
    """Test a single auto-switch case"""
    
    agent_label = f"[{selected_agent or 'NO_SELECT'}] → [{expected_agent}]"
    print(f"\n{CYAN}Test {test_num}: {agent_label}{END}")
    print(f"Message: '{message}'")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat?user_id=1",
            json={
                "message": message,
                "forced_role": selected_agent
            },
            headers={"Accept": "text/event-stream"}
        )
        
        if response.status_code != 200:
            error(f"HTTP {response.status_code}: {response.text}")
            return False
        
        # Parse streaming response to get agent
        reader = response.raw
        detected_agent = None
        
        for line in reader.stream(decode_content=True):
            if b"data: " in line:
                try:
                    data = json.loads(line.decode().replace("data: ", ""))
                    if "agent" in data and data["agent"]:
                        detected_agent = data["agent"]
                        break
                except:
                    pass
        
        if detected_agent == expected_agent:
            success(f"Correct! Routed to: {detected_agent}")
            return True
        else:
            error(f"Wrong route! Expected: {expected_agent}, Got: {detected_agent}")
            return False
            
    except Exception as e:
        error(f"Exception: {str(e)}")
        return False

def main():
    header("AUTO-SWITCH TEST SUITE")
    
    print(f"{YELLOW}Testing all 4 agents' auto-switch capabilities...{END}\n")
    
    tests = [
        # ACADEMIC AGENT TESTS
        (1, "start mock interview", "academic", None),
        (2, "What is data structure?", "academic", None),
        (3, "Create study plan", "academic", None),
        (4, "Define binary search", "academic", None),
        
        # CODE AGENT TESTS
        (5, "write python code to swap two numbers", "code", None),
        (6, "How to debug this error?", "code", None),
        (7, "Write a java program", "code", None),
        (8, "Fix this C++ bug", "code", None),
        
        # CONTENT AGENT TESTS
        (9, "write a youtube script", "content", None),
        (10, "Create a blog post", "content", None),
        (11, "write an essay", "content", None),
        (12, "write a speech", "content", None),
        
        # GENERAL AGENT TESTS
        (13, "hello", "general", None),
        (14, "how are you?", "general", None),
        (15, "what is your name?", "general", None),
        
        # STAYING IN AGENT TESTS (forced_role set, compatible intent)
        (16, "what is polymorphism?", "academic", "academic"),
        (17, "write a hello world program", "code", "code"),
        (18, "create instagram content", "content", "content"),
        (19, "tell me a joke", "general", "general"),
        
        # AUTO-SWITCH TESTS (forced_role set, incompatible intent)
        (20, "write python code", "code", "academic"),  # Should switch from academic to code
        (21, "write a script", "content", "code"),       # Should switch from code to content
        (22, "what is DSA", "academic", "content"),      # Should switch from content to academic
    ]
    
    passed = 0
    failed = 0
    
    for test_num, message, expected_agent, selected_agent in tests:
        if test_case(test_num, message, expected_agent, selected_agent):
            passed += 1
        else:
            failed += 1
        time.sleep(0.5)  # Rate limiting
    
    # Summary
    header("TEST SUMMARY")
    print(f"Total Tests: {len(tests)}")
    success(f"Passed: {passed}")
    error(f"Failed: {failed}")
    print(f"\nSuccess Rate: {(passed/len(tests))*100:.1f}%")
    
    if failed == 0:
        print(f"\n{GREEN}✓ ALL TESTS PASSED! Auto-switch works perfectly!{END}")
    else:
        print(f"\n{RED}✗ Some tests failed. Check agent capabilities and intent classification.{END}")

if __name__ == "__main__":
    main()
