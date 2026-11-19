from incident import load_json, save_json                                                # 월요일 파일의 JSON 읽기 · 쓰기 함수를 불러온다
from soar_engine import load_context, run_all                                            # 방금 만든 엔진 함수를 불러온다

LOG_PATH = "engine_log.json"                                                             # 처리 결과를 저장할 파일 이름
TICKET_PATH = "engine_tickets.json"                                                      # 만든 티켓을 저장할 파일 이름

context = load_context()                                                                 # 플레이북 · 승인 정책 · 설정 · 연습용 시스템 상태를 한꺼번에 읽는다
alerts = load_json("engine_alerts.json")                                                 # 오늘 들어온 알림 파일을 리스트로 읽는다
print("--- 단계 1: 불러온 알림", len(alerts), "건 · 플레이북", len(context["registry"]), "개 · 승인 기준", context["policy"]["approval_score"], "점")  # 단계 1 시작을 알리는 줄

results = run_all(alerts, context)                                                       # 알림을 하나씩 엔진으로 처리한다
counts = {"자동 실행": 0, "승인 대기": 0, "차단 금지": 0, "조치 없음": 0, "실패": 0}     # 처리 결과마다 알림 수 : 처음에는 모두 0
print("--- 단계 2: 알림마다 처리 결과")                                                  # 단계 2 시작을 알리는 줄
for result in results:                                                                   # 결과 기록을 하나씩 꺼낸다
    outcome = result["outcome"]                                                          # 이 알림의 처리 결과 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 9. counts[outcome] 에 counts[outcome] + 1 을 저장한다 (1 늘린다)
    counts[outcome] = counts[outcome] + 1
    if outcome == "실패":                                                                # 처리하지 못한 알림이면
        print(result["incident"], result["entity"], "→", outcome, "·", result["error"])  # 알림과 오류를 출력한다
    else:                                                                                # 처리한 알림이면
        print(result["incident"], result["entity"], result["grade"], "→", outcome, "·", result["playbook"], "· 티켓", result["ticket"])  # 알림과 처리 결과를 출력한다
    for step in result["steps"]:                                                         # 조치 결과를 하나씩 꺼낸다
        reason_text = ", ".join(step["reasons"])                                         # 결정 이유 리스트를 쉼표로 이어 한 문자열로 만든다
        print("   ", step["action"], step["target"], "→", step["decision"], "·", reason_text)  # 조치와 승인 게이트의 결정을 출력한다
        if step["executed"]:                                                             # 실행한 조치이면
            print("   ", "실행:", step["before"], "→", step["after"])                    # 조치 전 · 후 상태를 출력한다

print("--- 단계 3: 처리 결과별 알림 수")                                                 # 단계 3 시작을 알리는 줄
for outcome in counts:                                                                   # 처리 결과 이름을 하나씩 꺼낸다
    print(outcome, ":", counts[outcome], "건")                                           # 결과 이름과 알림 수를 출력한다

save_json(results, LOG_PATH)                                                             # 결과 기록 리스트를 파일에 저장한다
save_json(context["tickets"], TICKET_PATH)                                               # 만든 티켓 리스트를 파일에 저장한다
print("--- 단계 4:", LOG_PATH, "에", len(results), "건 ·", TICKET_PATH, "에 티켓", len(context["tickets"]), "장 저장")  # 단계 4 시작을 알리는 줄과 저장한 수

