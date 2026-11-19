from incident import load_json, save_json                                                   # 월요일 파일의 JSON 읽기 · 쓰기 함수를 불러온다
from policy_check import run_checks, judge                                                  # 방금 만든 점검 함수를 불러온다

LOG_FILES = ["engine_log.json", "risk_engine_log.json", "gate_off_log.json"]                # 점검할 엔진 로그 파일 세 개
CHECK_PATH = "policy_check.json"                                                            # 점검 결과를 저장할 파일 이름

policy = load_json("config/approval_policy.json")                                           # 승인 정책 파일을 딕셔너리로 읽는다
print("--- 단계 1: 점검할 로그", len(LOG_FILES), "개 · 점검 4가지")                         # 단계 1 시작을 알리는 줄

rows = []                                                                                   # 점검 결과 한 줄씩 모을 빈 리스트
fail_count = 0                                                                              # FAIL 이 나온 점검 수 : 처음에는 0
print("--- 단계 2: 로그마다 점검 결과")                                                     # 단계 2 시작을 알리는 줄
for log_path in LOG_FILES:                                                                  # 로그 파일을 하나씩 꺼낸다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. load_json(log_path) 의 결과를 results 에 저장한다
    results = load_json(log_path)
    checks = run_checks(results, policy)                                                    # 점검 네 가지를 실행한다 — 미리 채운 줄
    print("[" + log_path + "] 알림", len(results), "건")                                    # 로그 이름과 알림 수를 출력한다
    for check_name in checks:                                                               # 점검 이름을 하나씩 꺼낸다
        violations = checks[check_name]                                                     # 그 점검에서 위반한 알림 번호 리스트 — 미리 채운 줄
        verdict = judge(violations)                                                         # 통과 여부를 구한다 — 미리 채운 줄
        # 8. verdict 가 "FAIL" 이면 (if, ==)
        if verdict == "FAIL":     
            fail_count = fail_count + 1                                                     # FAIL 이 나온 점검 수를 1 늘린다 — 미리 채운 줄
        print("  ", check_name, ":", verdict, "· 위반", len(violations), "건", violations)  # 점검 이름 · 결과 · 위반한 알림 번호 리스트를 출력한다
        rows.append({"log": log_path, "check": check_name, "result": verdict, "violations": violations})  # 점검 결과 한 줄을 추가한다 — 미리 채운 줄

print("--- 단계 3: FAIL 이 나온 점검", fail_count, "개 · 전체 점검", len(rows), "개")       # 단계 3 시작을 알리는 줄과 개수
# ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
# 9. rows 를 CHECK_PATH 파일에 저장한다 (save_json)
save_json(rows, CHECK_PATH)
print("--- 단계 4:", CHECK_PATH, "에", len(rows), "개 저장")                                # 단계 4 시작을 알리는 줄과 저장한 수

