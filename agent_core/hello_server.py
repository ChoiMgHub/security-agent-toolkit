from flask import Flask, request

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    event = request.get_json()
    if "rule" in event:
        print("[수신]", event["rule"])
    else:
        print("[수신] rule 칸이 없는 요청")
    return {"status": "ok"}, 200


app.run(port=5001)
