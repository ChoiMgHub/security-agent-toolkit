import pandas as pd                                                                        # 표를 다루기 위해 판다스를 pd 라는 이름으로 불러온다

REPORT_TITLE = "# 초동 대응 리포트 — 2026-11-12(목) 오전 근무"                             # 리포트 맨 위 제목


def make_ticket_table(tickets):                                                            # 티켓 리스트를 받는 함수
    """티켓 리스트를 표(DataFrame)로 바꾸고, 확인까지 걸린 분(ack_minutes) 열을 더해 리턴한다.
    티켓마다 담당자가 얼마나 빨리 확인했는지를 표 하나로 계산할 때 쓴다.
    """
    table = pd.DataFrame(tickets)                                                          # 티켓 리스트를 표로 바꾼다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. table["acked_at"] - table["created_at"] 를 table["ack_minutes"] 에 저장한다 (확인까지 걸린 분)
    table["ack_minutes"] = table["acked_at"] - table["created_at"]
    return table                                                                           # 열을 더한 표를 리턴한다 — 미리 채운 줄


def count_by_rule(table):                                                                  # 티켓 표를 받는 함수
    """탐지 규칙마다 티켓이 몇 장인지 세어 딕셔너리로 리턴한다.
    어떤 규칙의 사건이 많았는지 리포트 첫머리에 보여 줄 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. table["rule"].value_counts() 를 rule_counts 에 저장한다
    rule_counts = table["rule"].value_counts()
    return rule_counts.to_dict()                                                           # 센 결과를 딕셔너리로 바꿔 리턴한다 — 미리 채운 줄


def mean_ack_by_grade(table):                                                              # 티켓 표를 받는 함수
    """확인한 티켓만 남겨 등급마다 확인까지 걸린 분의 평균을 구하고, 소수 첫째 자리까지 딕셔너리로 리턴한다.
    급한 등급일수록 빨리 확인했는지 리포트로 보여 줄 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. table["acked_at"] >= 0 인 행만 남겨 acked 에 저장한다 (확인한 티켓만)
    acked = table[table["acked_at"] >= 0]
    groups = acked.groupby("grade")                                                        # 등급이 같은 행끼리 묶는다 — 미리 채운 줄
    # 4. groups["ack_minutes"].mean() 을 grade_means 에 저장한다 (등급마다 평균)
    grade_means = groups["ack_minutes"].mean()
    rounded = grade_means.round(1)                                                         # 소수 첫째 자리까지 반올림한다 — 미리 채운 줄
    return rounded.to_dict()                                                               # 등급별 평균을 딕셔너리로 바꿔 리턴한다 — 미리 채운 줄


def find_late_tickets(table):                                                              # 티켓 표를 받는 함수
    """응답 기한 시각(sla_due)보다 늦게 확인한 티켓을 딕셔너리 리스트로 리턴한다.
    응답 기한을 넘긴 티켓을 리포트에 이름으로 남길 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. table["acked_at"] > table["sla_due"] 인 행만 남겨 late 에 저장한다
    late = table[table["acked_at"] > table["sla_due"]]
    return late.to_dict("records")                                                         # 남은 행을 딕셔너리 리스트로 바꿔 리턴한다 — 미리 채운 줄


def find_missing_incidents(actions, tickets):                                              # 조치 기록 리스트와 티켓 리스트를 받는 함수
    """조치 기록 가운데 어느 티켓에도 들어 있지 않은 인시던트의 기록을 리스트로 리턴한다.
    조치는 했는데 티켓이 없어 리포트에서 빠지는 사건을 찾을 때 쓴다.
    """
    covered = []                                                                           # 티켓에 들어 있는 인시던트 번호를 모을 빈 리스트 — 미리 채운 줄
    for ticket in tickets:                                                                 # 티켓을 하나씩 읽는다 — 미리 채운 줄
        for incident_id in ticket["incidents"]:                                            # 티켓에 합쳐진 인시던트 번호를 하나씩 읽는다 — 미리 채운 줄
            covered.append(incident_id)                                                    # 번호를 추가한다 — 미리 채운 줄
    missing = []                                                                           # 티켓이 없는 조치 기록을 모을 빈 리스트 — 미리 채운 줄
    for action in actions:                                                                 # 조치 기록을 하나씩 읽는다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 6. action["incident"] 가 covered 안에 없으면 (if, not in)
        if action["incident"] not in covered:
            # 7. missing 에 action 을 추가한다 (append)
            missing.append(action)
    return missing                                                                         # 티켓이 없는 조치 기록 리스트를 리턴한다 — 미리 채운 줄


def count_actions(ticket, actions):                                                        # 티켓 한 장과 조치 기록 리스트를 받는 함수
    """티켓에 합쳐진 인시던트의 조치 기록이 몇 건인지 세어 리턴한다.
    리포트의 티켓 줄에 조치 기록 수를 함께 적을 때 쓴다.
    """
    count = 0                                                                              # 조치 기록 수 : 처음에는 0
    for action in actions:                                                                 # 조치 기록을 하나씩 읽는다
        if action["incident"] in ticket["incidents"]:                                      # 이 티켓의 인시던트 기록이면
            count = count + 1                                                              # 1 늘린다
    return count                                                                           # 센 수를 리턴한다


def make_timeline_line(ticket):                                                            # 티켓 한 장을 받는 함수
    """티켓 한 장의 생성 · 확인 · 해결 시각을 시간순으로 이은 한 줄을 리턴한다.
    높음 등급 사건이 어떤 순서로 처리됐는지 리포트에 처리 경위로 남길 때 쓴다.
    """
    steps = [str(ticket["created_at"]) + "분 티켓 생성"]                                   # 생성 시각으로 시작한다
    if ticket["acked_at"] >= 0:                                                            # 확인했으면 (확인 전이면 -1)
        steps.append(str(ticket["acked_at"]) + "분 담당자 확인")                           # 확인 시각을 추가한다
    if ticket["resolved_at"] >= 0:                                                         # 해결했으면 (해결 전이면 -1)
        steps.append(str(ticket["resolved_at"]) + "분 해결")                               # 해결 시각을 추가한다
    return "- " + ticket["id"] + " · " + ticket["entity"] + ": " + " → ".join(steps)       # 시각을 화살표로 이어 한 줄로 리턴한다


def make_report_lines(tickets, actions, rule_counts, grade_means, late_tickets, missing):  # 리포트에 넣을 재료를 받는 함수
    """리포트에 넣을 재료로 마크다운 문서의 줄 리스트를 만들어 리턴한다.
    근무가 끝난 뒤 사람이 읽을 초동 대응 리포트를 자동으로 쓸 때 쓴다.
    """
    lines = [REPORT_TITLE, ""]                                                             # 제목과 빈 줄로 시작한다 — 미리 채운 줄
    lines.append("## 1. 티켓별 초동 대응")                                                 # 1절 제목 — 미리 채운 줄
    for ticket in tickets:                                                                 # 티켓을 하나씩 읽는다 — 미리 채운 줄
        action_count = count_actions(ticket, actions)                                      # 이 티켓의 조치 기록 수 — 미리 채운 줄
        head = "- " + ticket["id"] + " [" + ticket["grade"] + "] " + ticket["entity"] + " — " + ticket["rule"]  # 티켓 번호 · 등급 · 대상 · 규칙 — 미리 채운 줄
        lines.append(head + " · 상태 " + ticket["status"] + " · 조치 기록 " + str(action_count) + "건")  # 티켓 한 줄을 추가한다 — 미리 채운 줄
    lines.append("")                                                                       # 빈 줄 — 미리 채운 줄
    lines.append("## 2. 규칙별 티켓 수")                                                   # 2절 제목 — 미리 채운 줄
    for rule in rule_counts:                                                               # 규칙 이름을 하나씩 읽는다 — 미리 채운 줄
        count = rule_counts[rule]                                                          # 그 규칙의 티켓 수 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 8. "- " + rule + ": " + str(count) + "장" 을 lines 에 추가한다 (append)
        lines.append("- " + rule + ": " + str(count) + "장")
    lines.append("")                                                                       # 빈 줄 — 미리 채운 줄
    lines.append("## 3. 등급별 평균 확인 시간(분)")                                        # 3절 제목 — 미리 채운 줄
    for grade in grade_means:                                                              # 등급을 하나씩 읽는다 — 미리 채운 줄
        lines.append("- " + grade + ": " + str(grade_means[grade]) + "분")                 # 등급 한 줄을 추가한다 — 미리 채운 줄
    lines.append("")                                                                       # 빈 줄 — 미리 채운 줄
    lines.append("## 4. 응답 기한을 넘겨 확인한 티켓")                                     # 4절 제목 — 미리 채운 줄
    for ticket in late_tickets:                                                            # 늦게 확인한 티켓을 하나씩 읽는다 — 미리 채운 줄
        lines.append("- " + ticket["id"] + " · 기한 " + str(ticket["sla_due"]) + "분 · 확인 " + str(ticket["acked_at"]) + "분")  # 티켓 한 줄을 추가한다 — 미리 채운 줄
    lines.append("")                                                                       # 빈 줄 — 미리 채운 줄
    lines.append("## 5. 티켓이 없는 조치 (사람이 티켓을 만들어야 함)")                     # 5절 제목 — 미리 채운 줄
    for action in missing:                                                                 # 티켓이 없는 조치 기록을 하나씩 읽는다 — 미리 채운 줄
        lines.append("- " + action["incident"] + " · " + action["action"] + " · " + action["target"])  # 기록 한 줄을 추가한다 — 미리 채운 줄
    lines.append("")                                                                       # 빈 줄 — 미리 채운 줄
    lines.append("## 6. 높음(high) 티켓의 처리 경위")                                      # 6절 제목 — 미리 채운 줄
    for ticket in tickets:                                                                 # 티켓을 하나씩 읽는다 — 미리 채운 줄
        if ticket["grade"] == "high":                                                      # 높음 등급 티켓이면 — 미리 채운 줄
            lines.append(make_timeline_line(ticket))                                       # 처리 경위 한 줄을 추가한다 — 미리 채운 줄
    return lines                                                                           # 완성한 줄 리스트를 리턴한다 — 미리 채운 줄

