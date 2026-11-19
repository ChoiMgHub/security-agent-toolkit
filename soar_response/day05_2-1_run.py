from incident import load_json                                                                # 월요일 파일의 JSON 읽기 함수를 불러온다
from report import make_ticket_table, count_by_rule, mean_ack_by_grade, find_late_tickets, find_missing_incidents, make_report_lines  # 방금 만든 리포트 함수를 불러온다

REPORT_PATH = "incident_report_20261112.md"                                                   # 리포트를 저장할 파일 이름

tickets = load_json("day05_tickets.json")                                                     # 목요일 근무의 티켓 파일을 리스트로 읽는다
actions = load_json("day05_actions.json")                                                     # 목요일 근무의 조치 기록 파일을 리스트로 읽는다
print("--- 단계 1: 불러온 티켓", len(tickets), "장 · 조치 기록", len(actions), "건")          # 단계 1 시작을 알리는 줄

# ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
# 9. make_ticket_table(tickets) 의 결과를 table 에 저장한다
table = make_ticket_table(tickets)
rule_counts = count_by_rule(table)                                                            # 규칙별 티켓 수
grade_means = mean_ack_by_grade(table)                                                        # 등급별 평균 확인 시간
late_tickets = find_late_tickets(table)                                                       # 응답 기한을 넘겨 확인한 티켓
missing = find_missing_incidents(actions, tickets)                                            # 티켓이 없는 조치 기록

print("--- 단계 2: 규칙별 티켓 수")                                                           # 단계 2 시작을 알리는 줄
for rule in rule_counts:                                                                      # 규칙 이름을 하나씩 읽는다
    print(rule, ":", rule_counts[rule], "장")                                                 # 규칙과 티켓 수를 출력한다

print("--- 단계 3: 등급별 평균 확인 시간(분)")                                                # 단계 3 시작을 알리는 줄
for grade in grade_means:                                                                     # 등급을 하나씩 읽는다
    print(grade, ":", grade_means[grade], "분")                                               # 등급과 평균을 출력한다

print("--- 단계 4: 응답 기한을 넘겨 확인한 티켓", len(late_tickets), "장 · 티켓이 없는 조치", len(missing), "건")  # 단계 4 시작을 알리는 줄
for ticket in late_tickets:                                                                   # 늦게 확인한 티켓을 하나씩 읽는다
    print(ticket["id"], "기한", ticket["sla_due"], "분 · 확인", ticket["acked_at"], "분")     # 티켓과 두 시각을 출력한다
for action in missing:                                                                        # 티켓이 없는 조치 기록을 하나씩 읽는다
    print(action["incident"], action["action"], action["target"], "→ 티켓 없음")              # 기록을 출력한다

lines = make_report_lines(tickets, actions, rule_counts, grade_means, late_tickets, missing)  # 리포트 줄 리스트를 만든다
text = "\n".join(lines) + "\n"                                                                # 줄 리스트를 줄바꿈으로 이어 한 문자열로 만든다
with open(REPORT_PATH, "w", encoding="utf-8") as report_file:                                 # 리포트 파일을 쓰기 모드("w")로 연다
    report_file.write(text)                                                                   # 리포트 문자열을 파일에 쓴다
print("--- 단계 5: 리포트 파일", REPORT_PATH, "·", len(lines), "줄 저장")                     # 단계 5 시작을 알리는 줄과 저장한 줄 수

