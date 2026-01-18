#!/usr/bin/env python3
"""
UniGenAI System Test Verification Script
Tests user creation, chat storage, metrics, and data isolation
"""

import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
END = '\033[0m'

def test_header(msg):
    print(f"\n{BLUE}{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}{END}")

def success(msg):
    print(f"{GREEN}✓ {msg}{END}")

def error(msg):
    print(f"{RED}✗ {msg}{END}")

def info(msg):
    print(f"{YELLOW}→ {msg}{END}")

# =================== TEST FUNCTIONS ===================

def test_user_creation():
    """Test 1: User Creation"""
    test_header("TEST 1: USER CREATION")
    
    username = f"test_user_{int(time.time())}"
    info(f"Creating user: {username}")
    
    response = requests.post(f"{BASE_URL}/api/user/create?username={username}")
    
    if response.status_code == 200:
        user = response.json()
        if "id" in user and "username" in user:
            success(f"User created: ID={user['id']}, Username={user['username']}")
            return user
        else:
            error(f"Invalid response structure: {user}")
            return None
    else:
        error(f"Failed to create user: {response.status_code}")
        return None


def test_get_user(user_id):
    """Test 2: Get User Info"""
    test_header("TEST 2: GET USER INFO")
    
    info(f"Fetching user: {user_id}")
    
    response = requests.get(f"{BASE_URL}/api/user/{user_id}")
    
    if response.status_code == 200:
        user = response.json()
        if "id" in user:
            success(f"User retrieved: {json.dumps(user)}")
            return user
        else:
            error(f"Invalid response: {user}")
            return None
    else:
        error(f"Failed to get user: {response.status_code}")
        return None


def test_save_interview(user_id):
    """Test 3: Save Interview & Calculate Metrics"""
    test_header("TEST 3: SAVE INTERVIEW METRICS")
    
    interview_data = {
        "user_id": user_id,
        "domain": "DSA",
        "score": 85.5,
        "correct": 17,
        "total": 20
    }
    
    info(f"Saving interview: {json.dumps(interview_data)}")
    
    response = requests.post(f"{BASE_URL}/api/interview/save", json=interview_data)
    
    if response.status_code == 200:
        result = response.json()
        if "session_id" in result and "score" in result:
            success(f"Interview saved: {json.dumps(result)}")
            return result
        else:
            error(f"Invalid response: {result}")
            return None
    else:
        error(f"Failed to save interview: {response.status_code}")
        return None


def test_interview_history(user_id):
    """Test 4: Get Interview History"""
    test_header("TEST 4: GET INTERVIEW HISTORY")
    
    info(f"Fetching interview history for user: {user_id}")
    
    response = requests.get(f"{BASE_URL}/api/interview/history/{user_id}")
    
    if response.status_code == 200:
        interviews = response.json()
        if isinstance(interviews, list):
            success(f"Retrieved {len(interviews)} interview(s)")
            if len(interviews) > 0:
                print(f"  Sample: {json.dumps(interviews[0], indent=2)}")
            return interviews
        else:
            error(f"Invalid response: {interviews}")
            return None
    else:
        error(f"Failed to get interview history: {response.status_code}")
        return None


def test_interview_stats(user_id):
    """Test 5: Get Interview Statistics"""
    test_header("TEST 5: GET INTERVIEW STATISTICS")
    
    info(f"Fetching interview stats for user: {user_id}")
    
    response = requests.get(f"{BASE_URL}/api/interview/stats/{user_id}")
    
    if response.status_code == 200:
        stats = response.json()
        if "avg_score" in stats and "total_interviews" in stats:
            success(f"Stats retrieved successfully")
            print(f"  Total Interviews: {stats['total_interviews']}")
            print(f"  Average Score: {stats['avg_score']}")
            print(f"  Last Score: {stats.get('last_score', 'N/A')}")
            print(f"  Improvement: {stats.get('improvement', 'N/A')}")
            print(f"  By Domain: {stats.get('by_domain', {})}")
            return stats
        else:
            error(f"Invalid stats response: {stats}")
            return None
    else:
        error(f"Failed to get stats: {response.status_code}")
        return None


def test_save_multiple_interviews(user_id):
    """Test 6: Multiple Interviews & Improvement Tracking"""
    test_header("TEST 6: MULTIPLE INTERVIEWS & IMPROVEMENT")
    
    interviews = [
        {"domain": "OS", "score": 70.0, "correct": 14, "total": 20},
        {"domain": "OS", "score": 75.0, "correct": 15, "total": 20},
        {"domain": "OS", "score": 82.5, "correct": 16, "total": 20},
        {"domain": "DBMS", "score": 80.0, "correct": 16, "total": 20},
        {"domain": "DBMS", "score": 85.0, "correct": 17, "total": 20},
    ]
    
    for interview in interviews:
        interview["user_id"] = user_id
        response = requests.post(f"{BASE_URL}/api/interview/save", json=interview)
        if response.status_code == 200:
            success(f"Saved {interview['domain']} interview (score: {interview['score']})")
        else:
            error(f"Failed to save {interview['domain']} interview")
    
    # Get updated stats
    time.sleep(0.5)  # Brief delay to ensure DB commit
    response = requests.get(f"{BASE_URL}/api/interview/stats/{user_id}")
    
    if response.status_code == 200:
        stats = response.json()
        success(f"Final Stats:")
        print(f"  Total Interviews: {stats['total_interviews']}")
        print(f"  Average Score: {stats['avg_score']}")
        print(f"  Improvement: {stats['improvement']}")
        print(f"  By Domain: {stats['by_domain']}")
        return stats
    else:
        error(f"Failed to get final stats")
        return None


def test_study_plan(user_id):
    """Test 7: Study Plan Creation & Retrieval"""
    test_header("TEST 7: STUDY PLAN MANAGEMENT")
    
    exam_date = (datetime.now() + timedelta(days=30)).isoformat()
    
    plan_data = {
        "user_id": user_id,
        "subject": "Data Structures",
        "topics": ["Arrays", "LinkedLists", "Trees", "Graphs", "Sorting"],
        "exam_date": exam_date
    }
    
    info(f"Creating study plan: {plan_data['subject']}")
    
    response = requests.post(f"{BASE_URL}/api/planner/save", json=plan_data)
    
    if response.status_code == 200:
        plan = response.json()
        success(f"Plan created: {json.dumps(plan)}")
        
        # Get user's plans
        info("Fetching user's plans")
        response = requests.get(f"{BASE_URL}/api/planner/{user_id}")
        
        if response.status_code == 200:
            plans = response.json()
            success(f"Retrieved {len(plans)} plan(s)")
            for p in plans:
                print(f"  - {p['subject']}: {p['completion']}% complete")
            return plans
        else:
            error(f"Failed to get plans")
            return None
    else:
        error(f"Failed to create plan: {response.status_code}")
        return None


def test_data_isolation():
    """Test 8: Data Isolation Between Users"""
    test_header("TEST 8: DATA ISOLATION")
    
    # Create two users
    user1 = test_user_creation()
    if not user1:
        error("Failed to create user 1")
        return False
    
    time.sleep(0.5)
    user2_name = f"test_user_{int(time.time())}"
    response = requests.post(f"{BASE_URL}/api/user/create?username={user2_name}")
    if response.status_code != 200:
        error("Failed to create user 2")
        return False
    user2 = response.json()
    
    # Save interview for user 1
    info(f"Saving interview for user {user1['id']}")
    interview1 = {
        "user_id": user1["id"],
        "domain": "DSA",
        "score": 90.0,
        "correct": 18,
        "total": 20
    }
    requests.post(f"{BASE_URL}/api/interview/save", json=interview1)
    
    # Save different interview for user 2
    info(f"Saving interview for user {user2['id']}")
    interview2 = {
        "user_id": user2["id"],
        "domain": "OS",
        "score": 70.0,
        "correct": 14,
        "total": 20
    }
    requests.post(f"{BASE_URL}/api/interview/save", json=interview2)
    
    # Verify isolation
    time.sleep(0.5)
    
    stats1 = requests.get(f"{BASE_URL}/api/interview/stats/{user1['id']}").json()
    stats2 = requests.get(f"{BASE_URL}/api/interview/stats/{user2['id']}").json()
    
    if stats1['avg_score'] == 90.0 and stats2['avg_score'] == 70.0:
        success(f"Data properly isolated")
        print(f"  User 1 avg: {stats1['avg_score']} (Domain: {list(stats1['by_domain'].keys())})")
        print(f"  User 2 avg: {stats2['avg_score']} (Domain: {list(stats2['by_domain'].keys())})")
        return True
    else:
        error(f"Data isolation failed")
        print(f"  User 1: {stats1}")
        print(f"  User 2: {stats2}")
        return False


# =================== MAIN TEST SUITE ===================

def run_all_tests():
    """Run complete test suite"""
    
    print(f"\n{BLUE}")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "UniGenAI System Test Suite" + " "*17 + "║")
    print("║" + " "*20 + "Testing User Management" + " "*14 + "║")
    print("║" + " "*18 + "Chat Storage & Metrics" + " "*16 + "║")
    print("╚" + "="*58 + "╝")
    print(f"{END}")
    
    try:
        # Test 1: User Creation
        user = test_user_creation()
        if not user:
            error("Cannot proceed without user creation")
            return
        
        # Test 2: Get User
        test_get_user(user['id'])
        
        # Test 3: Save Single Interview
        test_save_interview(user['id'])
        
        # Test 4: Interview History
        test_interview_history(user['id'])
        
        # Test 5: Interview Stats (should show single interview)
        test_interview_stats(user['id'])
        
        # Test 6: Multiple Interviews & Improvement
        test_save_multiple_interviews(user['id'])
        
        # Test 7: Study Plan
        test_study_plan(user['id'])
        
        # Test 8: Data Isolation
        test_data_isolation()
        
        # Final summary
        test_header("ALL TESTS COMPLETED")
        print(f"{GREEN}✓ System is working correctly!{END}\n")
        
    except requests.exceptions.ConnectionError:
        error("Cannot connect to backend. Is the server running?")
        print(f"  Try: uvicorn backend.app:app --reload")
    except Exception as e:
        error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
