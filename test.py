import requests
import json
import time

BASE_URL = "http://localhost:8000/generate-sql"
# INSIGHTS_URL = "http://localhost:8000/insights"

def run_test(name, query):
    print(f"\n--- Running SQL Gen Test: {name} ---")
    print(f"Query: {query}")
    
    try:
        response = requests.post(BASE_URL, json={"user_query": query})
        
        if response.status_code == 200:
            data = response.json()
            print("Status: SUCCESS")
            print(f"SQL: {data['sql_query']}")
            print(f"Tokens Sent: {data['tokens_sent']}")
            print(f"Tokens Generated: {data['tokens_generated']}")
            print(f"Latency: {data['latency_ms']} ms")
        else:
            print(f"Status: FAILED ({response.status_code})")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

# def run_insight_test(name, query):
#     print(f"\n--- Running INSIGHT Test: {name} ---")
#     print(f"Query: {query}")
    
#     try:
#         t0 = time.time()
#         response = requests.post(INSIGHTS_URL, json={"query": query})
#         duration = time.time() - t0
        
#         if response.status_code == 200:
#             data = response.json()
#             print(f"Status: SUCCESS ({duration:.2f}s)")
#             print(f"Module: {data.get('module')}")
#             print(f"Aggregates: {data.get('aggregates')}")
#             print(f"Greeting: {data.get('greeting')}")
#             print(f"Insight: {data.get('insight')}")
#             print(f"Suggestions: {data.get('suggestions')}")
#         else:
#             print(f"Status: FAILED ({response.status_code})")
#             print(f"Error: {response.text}")
            
#     except Exception as e:
#         print(f"Error: {e}")  

def main():
    # 1. Test Aggregation (Count)
    start_time = time.time()
    run_test("Insights - Count", "How many sales orders last month give the company details?")
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time:.2f}s")

    # # 2. Test Aggregation (Sum)
    # run_insight_test("Insights - Sum", "What is the total value of invoices today?")

    # # 3. Test General
    # run_insight_test("Insights - Suppliers", "Count all suppliers")

if __name__ == "__main__":
    main()
