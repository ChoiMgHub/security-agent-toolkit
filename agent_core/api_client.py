import requests
import json

API_KEY = None
with open(".env", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split("=", 1)
        if parts[0] == "API_KEY":
            API_KEY = parts[1]


def call_with_retry(url, tries=3):
    for i in range(tries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            print(f"{i + 1}번째 실패")
    return None


def fetch_data(ip):
    data = call_with_retry(f"https://ipwho.is/{ip}")
    if data and data["success"]:
        return {"ip": ip, "country": data["country"], "isp": data["connection"]["isp"]}
    else:
        return None


results = []
for ip in ["185.220.101.34", "211.45.12.9"]:
    row = fetch_data(ip)
    if row:
        results.append(row)

with open("api_result.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

for row in results:
    print(f"[추적] {row['ip']} -> {row['country']} ({row['isp']})")
