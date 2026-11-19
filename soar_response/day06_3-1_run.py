from incident import load_json, save_json                                                    # 월요일 파일의 JSON 읽기 · 쓰기 함수를 불러온다
from soar_engine import load_context, run_all                                                # 2교시에 만든 엔진 함수를 불러온다
from engine_input import find_schema_problem, split_records, summarize                       # 방금 만든 연결 함수를 불러온다

TEST_RECORDS = [                                                                             # 모양을 일부러 틀리게 만든 시험 기록 두 건
    {"entity": "hana", "score": 40, "reasons": ["업무 시간 밖 로그인"]},                     # grade 키가 없다
    {"entity": "minsu", "score": 90, "grade": "critical", "reasons": ["퇴사한 계정"]},       # 엔진이 모르는 등급 이름이다
]

records = load_json("day03_risk_scores.json")                                                # 4과목이 저장한 탐지 결과 파일을 리스트로 읽는다
print("--- 단계 1: 4과목 탐지 결과", len(records), "건")                                     # 단계 1 시작을 알리는 줄과 건수

print("--- 단계 2: 모양 점검 시험 (일부러 틀린 기록)")                                       # 단계 2 시작을 알리는 줄
for test_record in TEST_RECORDS:                                                             # 시험 기록을 하나씩 꺼낸다
    test_problem = find_schema_problem(test_record)                                          # 모양 점검 결과를 받는다
    print(test_record["entity"], "→", test_problem)                                          # 대상과 점검 결과를 출력한다

alerts, rejected = split_records(records)                                                    # 기록을 엔진에 넣을 알림과 거절한 기록으로 나눈다
print("--- 단계 3: 엔진에 넣을 알림", len(alerts), "건 · 거절한 기록", len(rejected), "건")  # 단계 3 시작을 알리는 줄과 건수
for alert in alerts:                                                                         # 알림을 하나씩 꺼낸다
    print(alert["id"], alert["entity"], alert["grade"], alert["score"], alert["reasons"])    # 알림 번호 · 대상 · 등급 · 점수 · 이유를 출력한다

context = load_context()                                                                     # 엔진이 쓰는 재료를 읽는다
# ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
# 9. run_all(alerts, context) 의 결과를 results 에 저장한다
results = run_all(alerts, context)
print("--- 단계 4: 엔진 처리 결과")                                                          # 단계 4 시작을 알리는 줄
for result in results:                                                                       # 결과 기록을 하나씩 꺼낸다
    print(result["incident"], result["entity"], "→", result["outcome"], "·", result["playbook"], "· 티켓", result["ticket"])  # 알림 · 대상 · 처리 결과 · 플레이북 · 티켓을 출력한다

summary = summarize(results)                                                                 # 결과를 모아 운영 요약을 만든다
counts = summary["outcome_counts"]                                                           # 처리 결과별 알림 수 딕셔너리
print("--- 단계 5: 운영 요약")                                                               # 단계 5 시작을 알리는 줄
print("자동 실행", counts["자동 실행"], "건 · 승인 대기", counts["승인 대기"], "건 · 차단 금지", counts["차단 금지"], "건 · 조치 없음", counts["조치 없음"], "건 · 실패", counts["실패"], "건")  # 처리 결과별 알림 수를 한 줄로 출력한다
print("티켓", summary["ticket_count"], "건 · 실제로 실행한 조치", len(summary["executed_actions"]), "건")  # 티켓 수와 실행한 조치 수를 출력한다
for action_text in summary["executed_actions"]:                                              # 실행한 조치 문장을 하나씩 꺼낸다
    print(action_text)                                                                       # 문장을 출력한다

save_json(results, "risk_engine_log.json")                                                   # 결과 기록 리스트를 파일에 저장한다
save_json(summary, "engine_summary.json")                                                    # 운영 요약을 파일에 저장한다
save_json(context["tickets"], "risk_tickets.json")                                           # 만든 티켓 리스트를 파일에 저장한다
print("--- 단계 6: risk_engine_log.json · engine_summary.json · risk_tickets.json 저장")     # 단계 6 시작을 알리는 줄

