from incident import load_json, match_playbooks                                         # 월요일 파일의 JSON 읽기 · 플레이북 찾기 함수를 불러온다
from containment_store import new_state                                                 # 수요일 파일의 연습용 시스템 상태 함수를 불러온다
from account_actions import lock_account                                                # 수요일 파일의 계정 잠금 함수를 불러온다
from ip_actions import block_ip, count_users_on_ip, DEFAULT_TTL                         # 수요일 파일의 IP 차단 · 사용 계정 수 세기 함수와 차단 유지 시간을 불러온다
from approval_gate import decide_gate                                                   # 금요일 파일의 승인 게이트 함수를 불러온다
from ticketing import make_ticket, NEXT_STEPS                                           # 목요일 파일의 티켓 함수와 다음 할 일 딕셔너리를 불러온다

ENGINE_REASON = "자동 대응 엔진"                                                        # 조치 기록의 이유에 적는 실행 주체
CONTAINMENT_ACTIONS = ["계정 잠금", "IP 차단"]                                          # 승인 게이트를 거쳐 실행하는 조치 이름
TICKET_STATUS = {"자동 실행": "조치됨", "승인 대기": "승인 대기", "차단 금지": "조치 없음", "조치 없음": "조치 없음"}  # 처리 결과를 목요일 티켓의 알림 상태 이름으로 바꾸는 딕셔너리


def load_context():                                                                     # 인자가 없는 함수
    """설정 파일 네 개를 읽고 새 연습용 시스템 상태를 만들어 딕셔너리 하나로 리턴한다. 엔진이 알림을 처리하는 데 쓰는 재료를 한 번에 준비할 때 쓴다."""
    context = {                                                                         # 엔진이 쓰는 재료를 담을 딕셔너리
        "registry": load_json("config/playbook_registry.json"),                         # 플레이북 리스트
        "policy": load_json("config/approval_policy.json"),                             # 승인 게이트 정책
        "ip_users": load_json("ip_users.json"),                                         # IP 별 사용 계정 딕셔너리
        "ticket_rules": load_json("config/escalation_rules.json"),                      # 등급별 응답 기한(분) 설정
        "state": new_state(),                                                           # 연습용 시스템 상태 : 실행할 때마다 처음 상태에서 시작한다
        "tickets": [],                                                                  # 만든 티켓을 모을 빈 리스트
    }
    return context                                                                      # 재료 딕셔너리를 리턴한다


def make_request(alert, action, context):                                               # 알림 · 조치 이름 · 엔진 재료를 받는 함수
    """알림 한 건과 조치 이름으로 승인 게이트가 읽는 조치 요청 딕셔너리를 만든다. 위험 점수에 쓰는 「그 IP 를 함께 쓰는 계정 수」를 채울 때 쓴다."""
    users_on_ip = 0                                                                     # 그 IP 를 쓰는 계정 수 : 계정 조치이면 0 — 미리 채운 줄
    if action == "IP 차단":                                                             # 조치가 IP 차단이면 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 1. count_users_on_ip(alert["entity"], context["ip_users"]) 의 결과를 users_on_ip 에 저장한다
        users_on_ip = count_users_on_ip(alert["entity"], context["ip_users"])
    request = {                                                                         # 승인 게이트가 읽는 조치 요청 한 건 — 미리 채운 줄
        "id": alert["id"],                                                              # 요청 번호는 알림 번호를 쓴다
        "incident": alert["id"],                                                        # 인시던트 번호
        "action": action,                                                               # 조치 이름
        "target": alert["entity"],                                                      # 조치 대상(계정 또는 IP)
        "grade": alert["grade"],                                                        # 알림 등급
        "users_on_ip": users_on_ip,                                                     # 그 IP 를 쓰는 계정 수
        "target_count": 1,                                                              # 알림 한 건은 대상 하나를 조치한다
    }
    return request                                                                      # 조치 요청을 리턴한다 — 미리 채운 줄


def execute_action(request, context):                                                   # 조치 요청과 엔진 재료를 받는 함수
    """계정 잠금이면 lock_account, IP 차단이면 block_ip 로 조치를 실행하고 조치 기록 한 건을 리턴한다. 승인 게이트가 자동으로 정한 조치를 실제로 실행할 때 쓴다."""
    state = context["state"]                                                            # 연습용 시스템 상태 — 미리 채운 줄
    vip_accounts = context["policy"]["vip_accounts"]                                    # VIP 계정 리스트 — 미리 채운 줄
    if request["action"] == "계정 잠금":                                                # 조치가 계정 잠금이면 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 2. lock_account(request["target"], state, vip_accounts, request["incident"], ENGINE_REASON) 의 결과를 record 에 저장한다
        record = lock_account(request["target"], state, vip_accounts, request["incident"], ENGINE_REASON)
    else:                                                                               # 아니면 IP 차단이다 — 미리 채운 줄
        # 3. block_ip(request["target"], state, request["incident"], ENGINE_REASON, DEFAULT_TTL) 의 결과를 record 에 저장한다
        record = block_ip(request["target"], state, request["incident"], ENGINE_REASON, DEFAULT_TTL)
    return record                                                                       # 조치 기록을 리턴한다 — 미리 채운 줄


def run_step(alert, action, context):                                                   # 알림 · 조치 이름 · 엔진 재료를 받는 함수
    """조치 하나를 승인 게이트에 묻고, 자동으로 정해졌을 때만 실행해서 결정 · 이유 · 실행 여부를 담은 딕셔너리를 리턴한다. 조치마다 한 번씩 쓴다."""
    request = make_request(alert, action, context)                                      # 승인 게이트에 보낼 조치 요청을 만든다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. decide_gate(request, context["policy"]) 의 두 결과를 decision, reasons 에 저장한다
    decision, reasons = decide_gate(request, context["policy"])
    step = {                                                                            # 조치 하나의 결과 : 처음에는 실행하지 않은 것으로 적는다 — 미리 채운 줄
        "action": action,                                                               # 조치 이름
        "target": alert["entity"],                                                      # 조치 대상
        "decision": decision,                                                           # 승인 게이트의 결정
        "reasons": reasons,                                                             # 결정 이유 리스트
        "executed": False,                                                              # 실행했는지
        "before": "",                                                                   # 조치 전 상태
        "after": "",                                                                    # 조치 후 상태
        "request": request,                                                             # 승인 게이트가 본 조치 요청(나중에 점검할 때 다시 쓴다)
    }
    # 5. decision 이 "자동" 이면 (if, ==)
    if decision == "자동":    
        record = execute_action(request, context)                                       # 조치를 실행하고 조치 기록을 받는다 — 미리 채운 줄
        step["executed"] = True                                                         # 실행했다고 적는다 — 미리 채운 줄
        step["before"] = record["before"]                                               # 조치 전 상태를 적는다 — 미리 채운 줄
        step["after"] = record["after"]                                                 # 조치 후 상태를 적는다 — 미리 채운 줄
    return step                                                                         # 조치 하나의 결과를 리턴한다 — 미리 채운 줄


def decide_outcome(steps):                                                              # 조치 결과 리스트를 받는 함수
    """조치 결과들로 알림 전체의 처리 결과(승인 대기 · 차단 금지 · 자동 실행 · 조치 없음)를 정한다. 사람이 먼저 봐야 하는 결과부터 판단한다."""
    decisions = []                                                                      # 조치마다 승인 게이트의 결정을 모을 빈 리스트
    for step in steps:                                                                  # 조치 결과를 하나씩 꺼낸다
        decisions.append(step["decision"])                                              # 결정을 추가한다
    if "승인 필요" in decisions:                                                        # 승인이 필요한 조치가 있으면
        return "승인 대기"                                                              # 사람의 승인을 기다리는 알림이다
    if "차단 금지" in decisions:                                                        # 차단 금지인 조치가 있으면
        return "차단 금지"                                                              # 실행하지 않은 알림이다
    if "자동" in decisions:                                                             # 자동으로 정해진 조치가 있으면
        return "자동 실행"                                                              # 자동으로 실행한 알림이다
    return "조치 없음"                                                                  # 승인 게이트를 거칠 조치가 없으면 조치 없음이다


def open_ticket(alert, steps, playbook_id, outcome, context):                           # 알림 · 조치 결과 리스트 · 플레이북 번호 · 처리 결과 · 엔진 재료를 받는 함수
    """처리 결과를 목요일 티켓 형식의 알림으로 바꿔 make_ticket 으로 티켓을 만들고 티켓 리스트에 추가한다. 조치를 했든 안 했든 담당자가 볼 티켓을 남길 때 쓴다."""
    done_list = []                                                                      # 실행한 조치를 「조치: 전 → 후」 문장으로 모을 빈 리스트
    for step in steps:                                                                  # 조치 결과를 하나씩 꺼낸다
        if step["executed"]:                                                            # 실행한 조치이면
            done_text = step["action"] + ": " + step["before"] + " → " + step["after"]  # 조치와 전 · 후 상태를 한 문장으로 만든다
            done_list.append(done_text)                                                 # 문장을 추가한다
    rule_text = ", ".join(alert["reasons"])                                             # 탐지된 규칙 이름을 쉼표로 이어 한 문자열로 만든다
    ticket_alert = {                                                                    # 목요일 티켓 함수가 읽는 알림 모양
        "id": alert["id"],                                                              # 알림 번호
        "minute": 0,                                                                    # 엔진을 실행한 시각 : 0분
        "entity": alert["entity"],                                                      # 대상
        "rule": rule_text,                                                              # 탐지된 규칙
        "grade": alert["grade"],                                                        # 등급
        "status": TICKET_STATUS[outcome],                                               # 처리 결과에 맞는 알림 상태
        "playbook": playbook_id,                                                        # 플레이북 번호
        "done": done_list,                                                              # 실행한 조치 문장 리스트
    }
    ticket_no = len(context["tickets"]) + 1                                             # 지금까지 만든 티켓 수에 1 을 더해 번호를 만든다
    ticket = make_ticket(ticket_alert, ticket_no, context["ticket_rules"], NEXT_STEPS)  # 목요일 함수로 티켓을 만든다
    context["tickets"].append(ticket)                                                   # 티켓 리스트에 추가한다
    return ticket                                                                       # 만든 티켓을 리턴한다


def run_soar_pipeline(alert, context):                                                  # 알림 한 건과 엔진 재료를 받는 함수
    """알림 한 건을 플레이북 찾기 → 조치마다 승인 게이트 → 티켓 만들기 순서로 처리하고 결과 기록 한 건을 리턴한다. 알림마다 한 번씩 쓴다."""
    playbooks = match_playbooks(alert, context["registry"])                             # 월요일 함수로 맞는 플레이북을 찾는다 — 미리 채운 줄
    playbook_id = "없음"                                                                # 맞는 플레이북이 없으면 「없음」으로 남긴다 — 미리 채운 줄
    steps = []                                                                          # 조치마다 결과를 모을 빈 리스트 — 미리 채운 줄
    for playbook in playbooks:                                                          # 맞는 플레이북을 하나씩 꺼낸다 — 미리 채운 줄
        playbook_id = playbook["id"]                                                    # 플레이북 번호를 적는다 — 미리 채운 줄
        for action in playbook["actions"]:                                              # 플레이북의 액션을 하나씩 꺼낸다 — 미리 채운 줄
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            # 6. action 이 CONTAINMENT_ACTIONS 안에 있으면 (if, in)
            if action in CONTAINMENT_ACTIONS:        
                step = run_step(alert, action, context)                                 # 승인 게이트를 거쳐 실행한다 — 미리 채운 줄
                steps.append(step)                                                      # 조치 결과를 추가한다 — 미리 채운 줄
    outcome = decide_outcome(steps)                                                     # 알림 전체의 처리 결과를 정한다 — 미리 채운 줄
    ticket = open_ticket(alert, steps, playbook_id, outcome, context)                   # 티켓을 만든다 — 미리 채운 줄
    result = {                                                                          # 알림 한 건의 결과 기록 — 미리 채운 줄
        "incident": alert["id"],                                                        # 알림 번호
        "entity": alert["entity"],                                                      # 대상
        "grade": alert["grade"],                                                        # 등급
        "playbook": playbook_id,                                                        # 플레이북 번호
        "outcome": outcome,                                                             # 처리 결과
        "steps": steps,                                                                 # 조치마다 결과 리스트
        "ticket": ticket["id"],                                                         # 티켓 번호
        "error": "",                                                                    # 오류 문장 : 정상이면 비어 있다
    }
    return result                                                                       # 결과 기록을 리턴한다 — 미리 채운 줄


def make_failure_result(alert, error):                                                  # 알림 한 건과 오류를 받는 함수
    """처리하지 못한 알림의 결과 기록 한 건을 만든다. 오류 이름과 내용을 남겨 담당자가 어떤 알림이 왜 멈췄는지 알 수 있게 할 때 쓴다."""
    error_name = type(error).__name__                                                   # 오류의 종류 이름(예: KeyError)
    error_text = error_name + ": " + str(error)                                         # 오류 이름과 내용을 한 문장으로 만든다
    result = {                                                                          # 실패한 알림의 결과 기록
        "incident": alert.get("id", "번호 없음"),                                       # 알림 번호 : 키가 없으면 「번호 없음」
        "entity": alert.get("entity", ""),                                              # 대상 : 키가 없으면 빈 문자열
        "grade": alert.get("grade", ""),                                                # 등급 : 키가 없으면 빈 문자열
        "playbook": "없음",                                                             # 플레이북을 찾기 전에 멈췄을 수 있다
        "outcome": "실패",                                                              # 처리 결과는 실패
        "steps": [],                                                                    # 실행한 조치 없음
        "ticket": "",                                                                   # 티켓 없음
        "error": error_text,                                                            # 오류 문장
    }
    return result                                                                       # 실패 기록을 리턴한다


def run_all(alerts, context):                                                           # 알림 리스트와 엔진 재료를 받는 함수
    """알림을 하나씩 처리하되, 오류가 난 알림은 실패 기록만 남기고 다음 알림으로 넘어간다. 알림 하나의 오류가 나머지 알림의 처리를 막지 않게 할 때 쓴다."""
    results = []                                                                        # 알림마다 결과 기록을 모을 빈 리스트 — 미리 채운 줄
    for alert in alerts:                                                                # 알림을 하나씩 꺼낸다 — 미리 채운 줄
        try:                                                                            # 오류가 날 수 있는 처리를 시작한다 — 미리 채운 줄
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            # 7. run_soar_pipeline(alert, context) 의 결과를 result 에 저장한다
            result = run_soar_pipeline(alert, context)
        # 8. 어떤 종류의 오류든 error 에 저장해 받는다 (except, Exception, as)
        except Exception as error:    
            result = make_failure_result(alert, error)                                  # 실패 기록을 만든다 — 미리 채운 줄
        results.append(result)                                                          # 정상 결과든 실패 기록이든 결과 리스트에 추가한다 — 미리 채운 줄
    return results                                                                      # 결과 기록 리스트를 리턴한다 — 미리 채운 줄

