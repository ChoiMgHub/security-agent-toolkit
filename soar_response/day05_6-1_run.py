from incident import load_json                                                              # 월요일 파일의 JSON 읽기 함수를 불러온다
from false_positive import handle_false_positive                                            # 오전 4교시의 오탐 처리 함수를 불러온다
from day4_check import check_report, check_gate, check_recovery, mark                       # 방금 만든 점검 함수를 불러온다

REPORT_PATH = "incident_report_20261112.md"                                                 # 오전 2교시가 만든 리포트 파일 이름
TRUE_POSITIVE_USERS = ["dami"]                                                              # 진짜 공격으로 확인된 계정 (오탐 처리로 풀면 안 된다)
NOW = 45                                                                                    # 오탐 신고를 처리하는 지금 시각(분)

tickets = load_json("day05_tickets.json")                                                   # 목요일 근무의 티켓 파일을 읽는다
actions = load_json("day05_actions.json")                                                   # 목요일 근무의 조치 기록 파일을 읽는다
policy = load_json("config/approval_policy.json")                                           # 승인 정책 파일을 읽는다
cases = load_json("gate_cases.json")                                                        # 승인 게이트 시험 사례 파일을 읽는다
print("--- 단계 1: 점검 재료 · 티켓", len(tickets), "장 · 조치 기록", len(actions), "건 · 시험 사례", len(cases), "개")  # 단계 1 시작을 알리는 줄

with open(REPORT_PATH, encoding="utf-8") as report_file:                                    # 리포트 파일을 읽기 모드로 연다
    report_text = report_file.read()                                                        # 파일 내용을 한 문자열로 읽는다
# ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
# 8. check_report(report_text, tickets, actions) 의 결과를 report_problems 에 담는다
report_problems = check_report(report_text, tickets, actions)
gate_problems = check_gate(cases, policy)                                                   # 승인 게이트 점검

state = load_json("fp_state.json")                                                          # 오탐 처리 전 연습용 시스템 상태를 읽는다
log = load_json("fp_log.json")                                                              # 자동 조치 기록을 읽는다
results = []                                                                                # 오탐 처리 결과를 담을 빈 리스트
for report in load_json("fp_reports.json"):                                                 # 오탐 신고를 하나씩 꺼낸다
    result = handle_false_positive(report, log, state, NOW)                                 # 신고 한 건을 처리한다
    results.append(result)                                                                  # 처리 결과를 추가한다
# 9. check_recovery(results, state, TRUE_POSITIVE_USERS) 의 결과를 recovery_problems 에 담는다
recovery_problems = check_recovery(results, state, TRUE_POSITIVE_USERS)
checks = [                                                                                  # 강의계획서 Day 4 평가 기준마다 점검 결과
    {"title": "① 2 · 3일 차 데이터가 리포트에 빠짐없이 들어갔다", "problems": report_problems},  # 리포트 점검
    {"title": "② 위험 점수에 따라 자동 · 승인 필요 · 차단 금지가 맞게 나뉜다", "problems": gate_problems},  # 승인 게이트 점검
    {"title": "③ 오탐 복구가 30분 안에 빠짐없이 끝났고 진짜 공격의 잠금은 그대로다", "problems": recovery_problems},  # 오탐 복구 점검
]
print("--- 단계 2: Day 4 점검 목록")                                                        # 단계 2 시작을 알리는 줄
lines = ["# Day 4 마무리 점검 — 2026-11-13(금)", ""]                                        # 점검 문서의 제목과 빈 줄
for check in checks:                                                                        # 점검 결과를 하나씩 꺼낸다
    result_mark = mark(check["problems"])                                                   # 통과인지 확인 필요인지 정한다
    print("[" + result_mark + "]", check["title"], "· 문제", len(check["problems"]), "개")  # 점검 한 줄을 출력한다
    lines.append("- [" + result_mark + "] " + check["title"])                               # 점검 문서에 한 줄을 추가한다
    for problem in check["problems"]:                                                       # 문제 문장을 하나씩 꺼낸다
        print("   -", problem)                                                              # 문제를 출력한다
        lines.append("  - " + problem)                                                      # 점검 문서에 문제를 추가한다

text = "\n".join(lines) + "\n"                                                              # 줄 리스트를 줄바꿈으로 이어 한 문자열로 만든다
with open("day4_checklist.md", "w", encoding="utf-8") as check_file:                        # 점검 문서 파일을 쓰기 모드("w")로 연다
    check_file.write(text)                                                                  # 점검 문서를 파일에 쓴다
print("--- 단계 3: day4_checklist.md", len(lines), "줄 저장")                               # 단계 3 시작을 알리는 줄과 저장한 줄 수

