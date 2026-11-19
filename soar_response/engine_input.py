REQUIRED_KEYS = ["entity", "score", "grade", "reasons"]              # 4과목 결과 기록에 반드시 있어야 하는 키
GRADES = ["high", "mid", "low"]                                      # 엔진이 읽을 수 있는 등급 이름
FIRST_NUMBER = 501                                                   # 엔진이 붙이는 알림 번호의 시작 (INC-501 부터)


def find_schema_problem(record):                                     # 4과목 결과 기록 한 건을 받는 함수
    """엔진이 읽을 수 없는 기록이면 그 이유 문장을, 문제가 없으면 빈 문자열("")를 리턴한다. 4과목 파일의 모양이 바뀌었을 때 엔진이 오류를 내기 전에 걸러 낼 때 쓴다."""
    for key in REQUIRED_KEYS:                                        # 필수 키를 하나씩 꺼낸다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 1. key 가 record 안에 없으면 (if, not in)
        if key not in record:    
            return "필수 키 없음: " + key                            # 어떤 키가 없는지 이유로 리턴한다 — 미리 채운 줄
    # 2. record["grade"] 가 GRADES 안에 없으면 (if, not in)
    if record["grade"] not in GRADES:    
        return "알 수 없는 등급: " + record["grade"]                 # 등급 이름을 이유로 리턴한다 — 미리 채운 줄
    if record["reasons"] == []:                                      # 탐지된 규칙 리스트가 비어 있으면 — 미리 채운 줄
        return "탐지된 규칙이 없음"                                  # 이유를 리턴한다 — 미리 채운 줄
    return ""                                                        # 문제가 없으면 빈 문자열를 리턴한다 — 미리 채운 줄


def make_alert(record, number):                                      # 4과목 결과 기록 한 건과 알림 번호 숫자를 받는 함수
    """4과목 결과 기록(대상 · 점수 · 등급 · 이유)에 알림 번호와 상태를 붙여 월요일 인시던트 모양의 딕셔너리로 리턴한다. 4과목 파일의 기록을 엔진의 입력으로 바꿀 때 쓴다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. "INC-" 뒤에 str(number) 를 이어 붙여 alert_id 에 저장한다
    alert_id = "INC-" + str(number)
    # 4. 키 "id"(alert_id) · "entity" · "grade" · "score" · "reasons"(record 의 같은 이름 키의 값), "status"("탐지됨") 를 가진 딕셔너리를 alert 에 저장한다
    alert = {                                                  # 엔진이 읽는 알림 딕셔너리
        "id": alert_id,                                        # 알림 번호
        "entity": record["entity"],                            # 대상
        "grade": record["grade"],                              # 등급
        "score": record["score"],                              # 점수
        "reasons": record["reasons"],                          # 탐지된 규칙 이름 리스트
        "status": "탐지됨",                                    # 처음 상태
    }
    return alert                                                     # 엔진이 읽을 알림을 리턴한다 — 미리 채운 줄


def split_records(records):                                          # 4과목 결과 기록 리스트를 받는 함수
    """기록마다 모양을 점검해 엔진에 넣을 알림 리스트와 거절한 기록 리스트를 만들고 두 리스트를 함께 리턴한다. 거절한 기록을 이유와 함께 남겨 기록 없이 빠지지 않게 할 때 쓴다."""
    alerts = []                                                      # 엔진에 넣을 알림을 모을 빈 리스트 — 미리 채운 줄
    rejected = []                                                    # 거절한 기록과 이유를 모을 빈 리스트 — 미리 채운 줄
    number = FIRST_NUMBER                                            # 다음에 붙일 알림 번호 — 미리 채운 줄
    for record in records:                                           # 기록을 하나씩 꺼낸다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. find_schema_problem(record) 의 결과를 problem 에 저장한다
        problem = find_schema_problem(record)
        # 6. problem 이 "" 이면 (if, ==)
        if problem == "":    
            alert = make_alert(record, number)                       # 알림 모양으로 바꾼다 — 미리 채운 줄
            alerts.append(alert)                                     # 알림 리스트에 추가한다 — 미리 채운 줄
            number = number + 1                                      # 다음 번호로 넘어간다 — 미리 채운 줄
        else:                                                        # 문제가 있으면 — 미리 채운 줄
            rejected.append({"record": record, "problem": problem})  # 기록과 이유를 거절 리스트에 추가한다 — 미리 채운 줄
    return alerts, rejected                                          # 두 리스트를 함께 리턴한다 — 미리 채운 줄


def summarize(results):                                              # 엔진 결과 기록 리스트를 받는 함수
    """결과 기록을 모아 처리 결과별 알림 수 · 만든 티켓 수 · 실제로 실행한 조치 문장 리스트를 담은 요약 딕셔너리를 리턴한다. 운영 담당자가 한 번에 볼 요약이 필요할 때 쓴다."""
    outcome_counts = {"자동 실행": 0, "승인 대기": 0, "차단 금지": 0, "조치 없음": 0, "실패": 0}  # 처리 결과마다 알림 수 : 처음에는 모두 0 — 미리 채운 줄
    ticket_count = 0                                                 # 만든 티켓 수 : 처음에는 0 — 미리 채운 줄
    executed_actions = []                                            # 실제로 실행한 조치 문장을 모을 빈 리스트 — 미리 채운 줄
    for result in results:                                           # 결과 기록을 하나씩 꺼낸다 — 미리 채운 줄
        outcome = result["outcome"]                                  # 이 알림의 처리 결과 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 7. outcome_counts[outcome] 에 outcome_counts[outcome] + 1 을 저장한다 (1 늘린다)
        outcome_counts[outcome] = outcome_counts[outcome] + 1
        if result["ticket"] != "":                                   # 티켓이 있으면 — 미리 채운 줄
            ticket_count = ticket_count + 1                          # 티켓 수를 1 늘린다 — 미리 채운 줄
        for step in result["steps"]:                                 # 조치 결과를 하나씩 꺼낸다 — 미리 채운 줄
            # 8. step["executed"] 가 참이면 (if)
            if step["executed"]:
                action_text = result["incident"] + " " + step["action"] + " " + step["target"] + ": " + step["before"] + " → " + step["after"]  # 알림 · 조치 · 대상 · 전 · 후 상태를 한 문장으로 만든다 — 미리 채운 줄
                executed_actions.append(action_text)                 # 문장을 추가한다 — 미리 채운 줄
    summary = {"outcome_counts": outcome_counts, "ticket_count": ticket_count, "executed_actions": executed_actions}  # 요약 딕셔너리 — 미리 채운 줄
    return summary                                                   # 요약을 리턴한다 — 미리 채운 줄

