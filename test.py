import requests
import json
import time

root_url = "http://localhost:8000"
# INSIGHTS_URL = "http://localhost:8000/insights"

def run_test(name, query):
    print(f"\n--- Running SQL Gen Test: {name} ---")
    print(f"Query: {query}")
    
    try:
        response = requests.post(root_url + "/generate-sql", json={"user_query": query})
        
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
 

def run_sql_gen_test(name, query):
    print(f"\n=== Running Full Flow Test: {name} ===")
    print(f"Query: {query}")
    
    # 1. Generate SQL
    print(">>> Generating SQL...")
    t0 = time.time()
    try:
        res_sql = requests.post(root_url + "/generate-sql", json={"user_query": query})
        if res_sql.status_code != 200:
            print("SQL Gen Failed:", res_sql.text)
            return
        sql_data = res_sql.json()
        sql_query = sql_data["sql_query"]
        print(f"SQL: {sql_query}")
        return sql_query
    except Exception as e:
        print("SQL Gen Error:", e)
        return

def test_execute_sql(sql_query):
    print(">>> Executing SQL...")
    try:
        res_exec = requests.post(root_url + "/execute-sql", json={"sql_query": sql_query})
        if res_exec.status_code != 200:
            print("Execution Failed:", res_exec.text)
            return
        exec_data = res_exec.json()
        raw_data = exec_data["data"]
        is_truncated = exec_data["is_truncated"]
        print(f"Rows Fetched: {exec_data['row_count']} (Truncated: {is_truncated})")
        return raw_data
        # print("Sample Data:", json.dumps(raw_data[:1], indent=2))
    except Exception as e:
        print("Execution Error:", e)
        return

def test_generate_text(query,raw_data,is_truncated = False):
    print(">>> Generating Insights...")
    try:
        payload = {
            "user_query": query,
            "retrieved_data": raw_data, # Wrap list in dict as per prompt expectation? Or prompt handles list? 
                                                     # prompts.py expects Dict[str, Any] usually, but let's check prompts.py
            "is_truncated": is_truncated
        }
        res_text = requests.post(f"{root_url}/generate-text", json=payload)
        if res_text.status_code != 200:
            print("Insight Gen Failed:", res_text.text)
            print(res_text.text) 
            return
        
        text_data = res_text.json()
        print(f"Insight: {text_data['insight']}")
        print(f"Greeting: {text_data['greeting']}")
        print(f"Confidence: {text_data['confidence']}")

        
    except Exception as e:
        print("Insight Gen Error:", e)

    # print(f"Total Flow Time: {time.time() - t0:.2f}s")

def test_insight_generator(query):
    print(f"\n=== Testing Unified Agent: {query} ===")
    t0 = time.time()
    try:
        res = requests.post(f"{root_url}/insight-generator", json={"user_query": query})
        if res.status_code != 200:
            print("Failed:", res.text)
            return
        
        data = res.json()
        print(f"Status: SUCCESS (Latency: {data['latency_ms']:.2f}ms)")
        print(f"SQL: {data['sql_query']}")
        print(f"Greeting: {data['greeting']}")
        print(f"Insight: {data['insight']}")
        print(f"Data Rows: {len(data.get('data') or [])}")
        
    except Exception as e:
        print("Error:", e)
    print(f"Total Client Time: {time.time() - t0:.2f}s")

def main():
    # 1. Test Aggregation (Count)
    # start_time = time.time()
    # run_test("Insights - Count", "How many sales orders last month give the company details?")
    # end_time = time.time()
    # print(f"Total time taken: {end_time - start_time:.2f}s")
    
    # query = "How many old yarn stock are there?"
    # result = run_sql_gen_test("Full Pipeline Test", query)
    # data = test_execute_sql(result)
    # test_generate_text(query,data,is_truncated = False)

    test_insight_generator("How many old yarn stock are there?")
#     test_execute_sql("""SELECT Company, COUNT(*) AS SalesOrderCount
# FROM dbo.T_Ord_Main
# WHERE Po_Date >= DATEADD(MONTH, -1, DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE
# ()), 0))
#   AND Po_Date <  DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0)
# GROUP BY Company;""")
    # test_generate_text("How many sales orders last month give the company details?",{'Company': 'SHRI PRANAV TEXTILE CREATIONS PRIVATE LIMITED', 'SalesOrderCount': 72},False)
    
if __name__ == "__main__":
    main()
