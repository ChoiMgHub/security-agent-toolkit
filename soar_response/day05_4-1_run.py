from incident import load_json, save_json                                                   # 월요일 파일의 JSON 읽기 · 쓰기 함수를 불러온다
from false_positive import handle_false_positive, RECOVERY_LIMIT                            # 방금 만든 오탐 처리 함수를 불러온다

NOW = 45                                                                                    # 오탐 신고를 처리하는 지금 시각(분)

state = load_json("fp_state.json")                                                          # 오탐 처리 전 연습용 시스템 상태를 읽는다
log = load_json("fp_log.json")                                                              # 자동 조치 기록을 리스트로 읽는다
reports = load_json("fp_reports.json")                                                      # 오탐 신고 파일을 리스트로 읽는다
print("--- 단계 1: 오탐 신고", len(reports), "건 · 조치 기록", len(log), "건 · 지금", NOW, "분")  # 단계 1 시작을 알리는 줄
print("처리 전 잠긴 계정:", state["locked_users"], "· 차단된 IP:", state["blocked_ips"])    # 처리 전 상태를 출력한다

results = []                                                                                # 신고마다 처리 결과를 저장할 빈 리스트
print("--- 단계 2: 신고마다 영향 확인 · 되돌리기 · 복구 확인 · 규칙 조정 제안")             # 단계 2 시작을 알리는 줄
for report in reports:                                                                      # 오탐 신고를 하나씩 읽는다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 8. handle_false_positive(report, log, state, NOW) 의 결과를 result 에 저장한다
    result = handle_false_positive(report, log, state, NOW)
    # 9. results 에 result 를 추가한다 (append)
    results.append(result)
    print("[" + result["incident"] + "] 신고:", report["reporter"], "—", report["reason"])  # 신고 내용을 출력한다
    print(" - 영향 확인:", result["changed"])                                               # 자동 조치가 바꾼 것을 출력한다
    print(" - 되돌리기:", result["undone"])                                                 # 되돌린 일을 출력한다
    print(" - 복구 확인: 아직 잠기거나 차단된 대상", result["remaining"], "· 걸린 시간", result["minutes"], "분 · 기준", RECOVERY_LIMIT, "분 안", result["in_time"])  # 복구 확인 결과를 출력한다
    print(" - 규칙 조정 제안:", result["tuning"])                                           # 규칙 조정 제안을 출력한다

print("--- 단계 3: 처리 뒤 상태 (오탐이 아닌 계정은 그대로인지)")                           # 단계 3 시작을 알리는 줄
print("잠긴 계정:", state["locked_users"], "· 차단된 IP:", state["blocked_ips"])            # 처리 뒤 상태를 출력한다
print("dami 는 아직 잠김:", "dami" in state["locked_users"])                                # 진짜 공격(퇴사한 계정)은 그대로 잠겨 있는지 출력한다

save_json(results, "fp_results.json")                                                       # 처리 결과를 파일에 저장한다
save_json(state, "fp_state_after.json")                                                     # 처리 뒤 상태를 다른 파일에 저장한다
print("--- 단계 4: fp_results.json 에", len(results), "건 · fp_state_after.json 저장 · 기준", RECOVERY_LIMIT, "분")  # 단계 4 시작을 알리는 줄

