from incident import load_json, save_json                           # 월요일 파일의 JSON 읽기 · 쓰기 함수를 불러온다
from approval_gate import decide_gate                               # 방금 만든 승인 게이트 함수를 불러온다

policy = load_json("config/approval_policy.json")                   # 승인 정책 파일을 딕셔너리로 읽는다
requests = load_json("gate_requests.json")                          # 오늘 들어온 조치 요청 파일을 리스트로 읽는다
print("--- 단계 1: 불러온 조치 요청", len(requests), "건 · 승인 기준", policy["approval_score"], "점")  # 단계 1 시작을 알리는 줄

counts = {"자동": 0, "승인 필요": 0, "차단 금지": 0}                # 결정마다 요청 수 : 처음에는 모두 0
results = []                                                        # 요청마다 결정을 저장할 빈 리스트
print("--- 단계 2: 요청마다 결정과 이유")                           # 단계 2 시작을 알리는 줄
for request in requests:                                            # 조치 요청을 하나씩 읽는다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 8. decide_gate(request, policy) 의 두 결과를 decision, reasons 에 저장한다
    decision, reasons = decide_gate(request, policy) 
    # 9. counts[decision] 에 counts[decision] + 1 을 저장한다 (1 늘린다)
    counts[decision] = counts[decision] + 1
    reason_text = ", ".join(reasons)                                # 이유 리스트를 쉼표로 이어 한 문자열로 만든다
    print(request["id"], request["action"], request["target"], "→", decision, "·", reason_text)  # 요청과 결정을 출력한다
    results.append({"id": request["id"], "incident": request["incident"], "action": request["action"], "target": request["target"], "decision": decision})  # 결정을 추가한다

print("--- 단계 3: 결정별 요청 수")                                 # 단계 3 시작을 알리는 줄
for decision in counts:                                             # 결정 이름을 하나씩 읽는다
    print(decision, ":", counts[decision], "건")                    # 결정과 요청 수를 출력한다

print("--- 단계 4: 담당자에게 보낼 승인 요청")                      # 단계 4 시작을 알리는 줄
for result in results:                                              # 결정을 하나씩 읽는다
    if result["decision"] == "승인 필요":                           # 사람의 승인이 필요하면
        print(result["id"], result["incident"], result["action"], result["target"], "→ 담당자 승인을 기다림")  # 승인 요청을 출력한다

save_json(results, "gate_results.json")                             # 결정 리스트를 파일에 저장한다
print("--- 단계 5: gate_results.json 에", len(results), "건 저장")  # 단계 5 시작을 알리는 줄과 저장한 수

