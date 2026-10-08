import json
from flask import Flask, request

app = Flask(__name__)
received = []


@app.route("/webhook", methods=["POST"])
def webhook():
    received.append(request.get_json())
    # 1. "received_alerts.json" 을 쓰기로 여세요. 변수 이름은 f 입니다 (with 문)
    with open("received_alerts.json", "w", encoding="utf-8") as f:
        # 2. received 를 f 에 JSON 으로 저장하세요. 한글 그대로, 두 칸 들여쓰기입니다
        json.dump(received, f, ensure_ascii=False, indent=2)
    return {"status": "ok", "count": len(received)}, 200


app.run(port=5006)
