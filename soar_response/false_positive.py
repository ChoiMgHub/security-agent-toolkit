from rollback import find_incident_records, rollback_incident                        # 수요일에 만든 되돌리기 함수를 불러온다

RECOVERY_LIMIT = 30                                                                  # 오탐 신고를 받은 뒤 복구를 끝내야 하는 시간(분)


def list_changes(log, incident_id):                                                  # 조치 기록 리스트와 인시던트 번호를 받는 함수
    """그 인시던트의 기록 가운데 조치 전과 조치 후가 다른 기록(자동 조치가 실제로 바꾼 것)만 리스트로 리턴한다.
    오탐 신고를 받았을 때, 무엇이 바뀌어서 누가 영향을 받았는지 먼저 확인할 때 쓴다.
    """
    changes = []                                                                     # 실제로 바뀐 기록을 모을 빈 리스트 — 미리 채운 줄
    for record in find_incident_records(log, incident_id):                           # 그 인시던트의 기록을 하나씩 읽는다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 1. record["before"] 와 record["after"] 가 다르면 (if, !=)
        if record["before"] != record["after"]: 
            # 2. changes 에 record 를 추가한다 (append)
            changes.append(record)
    return changes                                                                   # 실제로 바뀐 기록 리스트를 리턴한다 — 미리 채운 줄


def find_not_recovered(changes, state):                                              # 바뀐 기록 리스트와 연습용 시스템 상태를 받는 함수
    """되돌린 뒤에도 아직 잠겨 있는 계정이나 차단된 IP 를 리스트로 리턴한다. 빈 리스트이면 복구가 끝난 것이다.
    되돌리기 함수를 실행한 뒤, 실제 상태가 원래대로 돌아왔는지 확인할 때 쓴다.
    """
    remaining = []                                                                   # 아직 복구되지 않은 대상을 모을 빈 리스트 — 미리 채운 줄
    for record in changes:                                                           # 바뀐 기록을 하나씩 읽는다 — 미리 채운 줄
        target = record["target"]                                                    # 조치 대상(계정 또는 IP) — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. record["action"] 이 "계정 잠금" 이고(and) target 이 state["locked_users"] 안에 있으면 (if, ==, in)
        if record["action"] == "계정 잠금" and target in state["locked_users"]:
            remaining.append(target)                                                 # 아직 잠겨 있는 계정을 추가한다 — 미리 채운 줄
        # 4. record["action"] 이 "IP 차단" 이고(and) target 이 state["blocked_ips"] 안에 있으면 (if, ==, in)
        if record["action"] == "IP 차단" and target in state["blocked_ips"]:      
            remaining.append(target)                                                 # 아직 차단된 IP 를 추가한다 — 미리 채운 줄
    return remaining                                                                 # 복구되지 않은 대상 리스트를 리턴한다 — 미리 채운 줄


def make_tuning_note(changes):                                                       # 바뀐 기록 리스트를 받는 함수
    """같은 오탐이 다시 나지 않도록 규칙을 어떻게 고칠지 제안 문장을 만들어 리턴한다.
    복구한 뒤, 탐지 규칙이나 허용 목록을 고치자고 담당자에게 남길 때 쓴다.
    """
    for record in changes:                                                           # 바뀐 기록을 하나씩 읽는다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. record["action"] 이 "IP 차단" 이면 (if, ==)
        if record["action"] == "IP 차단":
            # 6. "허용 목록에 추가 검토: " + record["target"] 을 리턴한다
            return "허용 목록에 추가 검토: " + record["target"] 
    first = changes[0]                                                               # 첫 번째 바뀐 기록 — 미리 채운 줄
    return "탐지 규칙 예외 검토: " + first["target"] + " (" + first["reason"] + ")"  # 계정이면 규칙 예외를 제안한다 — 미리 채운 줄


def handle_false_positive(report, log, state, now):                                  # 오탐 신고 한 건 · 조치 기록 · 상태 · 지금 시각(분)을 받는 함수
    """오탐 신고 한 건을 영향 확인 → 되돌리기 → 복구 확인 순서로 처리하고, 규칙 조정 제안을 함께 담은 결과 딕셔너리를 리턴한다.
    오탐으로 잘못 잠그거나 차단한 것을 빠르고 빠짐없이 원래대로 돌릴 때 쓴다.
    """
    incident_id = report["incident"]                                                 # 오탐으로 신고된 인시던트 번호 — 미리 채운 줄
    changes = list_changes(log, incident_id)                                         # 영향 확인: 자동 조치가 실제로 바꾼 기록 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. rollback_incident(incident_id, log, state) 의 결과를 undo_records 에 저장한다 (되돌리기)
    undo_records = rollback_incident(incident_id, log, state)
    remaining = find_not_recovered(changes, state)                                   # 복구 확인: 아직 남은 대상 — 미리 채운 줄
    changed = []                                                                     # 영향 받은 대상과 조치를 모을 빈 리스트 — 미리 채운 줄
    for record in changes:                                                           # 바뀐 기록을 하나씩 읽는다 — 미리 채운 줄
        changed.append(record["action"] + " " + record["target"])                    # 「조치 대상」 꼴로 추가한다 — 미리 채운 줄
    undone = []                                                                      # 되돌린 일을 모을 빈 리스트 — 미리 채운 줄
    for record in undo_records:                                                      # 되돌리기 기록을 하나씩 읽는다 — 미리 채운 줄
        undone.append(record["action"] + " " + record["target"])                     # 「조치 대상」 꼴로 추가한다 — 미리 채운 줄
    minutes = now - report["reported_at"]                                            # 신고를 받은 뒤 걸린 시간(분) — 미리 채운 줄
    result = {                                                                       # 처리 결과 한 건 — 미리 채운 줄
        "incident": incident_id,                                                     # 인시던트 번호
        "changed": changed,                                                          # 영향 받은 대상과 조치
        "undone": undone,                                                            # 되돌린 일
        "remaining": remaining,                                                      # 아직 복구되지 않은 대상
        "minutes": minutes,                                                          # 걸린 시간(분)
        "in_time": minutes <= RECOVERY_LIMIT,                                        # 정한 시간 안에 끝났는지
        "tuning": make_tuning_note(changes),                                         # 규칙 조정 제안
    }
    return result                                                                    # 처리 결과를 리턴한다 — 미리 채운 줄

