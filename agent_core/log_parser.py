import logging
from collections import Counter

logging.basicConfig(
    filename="agent.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8",
)


def parse_line(line):
    parts = line.strip().split(",")
    return {"time": parts[0], "user": parts[1], "event": parts[2], "ip": parts[3]}


logging.info("파서 시작: sample_logs_broken.csv")

logs = []
with open("sample_logs_broken.csv", encoding="utf-8") as f:
    for line in f:
        try:
            logs.append(parse_line(line))
        except IndexError:
            logging.warning(f"깨진 줄 건너뜀: {line.strip()}")

logging.info(f"정상 로그 {len(logs)}건 처리 완료")

failed_users = []
for log in logs:
    if log["event"] == "LOGIN_FAIL":
        failed_users.append(log["user"])

counted = Counter(failed_users)
for user in counted:
    if counted[user] >= 3:
        print(f"확인 필요: {user} — 실패 {counted[user]}회")
