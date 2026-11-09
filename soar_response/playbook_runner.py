from incident import change_status, match_playbooks, run_action, make_log_entry  # 제공받은 함수를 불러온다


def run_playbook(incident, playbook, state, action_log):                         # 인시던트 · 플레이북 · 시스템 상태 · 감사 기록 리스트를 받는 함수
    """플레이북의 액션을 차례로 실행하고 감사 기록을 남긴다. 승인이 필요하면 실행하지 않고 승인 대기로 기록한다.
    실행했으면 True, 승인 대기로 멈췄으면 False 를 리턴한다.
    """
    change_status(incident, "분류됨")                                            # 대응을 시작하기 전에 분류됨 상태로 옮긴다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. playbook 의 "approval" 값이 "자동" 이 아니면 (if, !=)
    if playbook["approval"] != "자동": 
    # 2.   make_log_entry(incident, playbook, "전체", "승인 대기") 의 결과를 action_log 에 추가한다 (append)
        action_log.append(make_log_entry(incident, playbook, "전체", "승인 대기"))
    # 3.   False 를 리턴한다 (실행하지 않았다)
        return False
    for action in playbook["actions"]:                                           # 액션을 하나씩 꺼낸다
        # 4. run_action(action, incident, state) 의 결과를 result 에 담는다
        result = run_action(action, incident, state)
        # 5. make_log_entry(incident, playbook, action, result) 의 결과를 action_log 에 추가한다 (append)
        action_log.append(make_log_entry(incident, playbook, action, result))
    # 6. change_status(incident, "조치됨") 를 호출한다 (실행이 끝났으니 조치됨으로 옮긴다)
    change_status(incident, "조치됨")
    return True                                                                  # 모두 실행했으니 True 를 리턴한다


def process_incidents(incidents, registry, state, action_log):                   # 인시던트 리스트 · 플레이북 리스트 · 시스템 상태 · 감사 기록을 받는 함수
    """인시던트마다 맞는 플레이북을 찾아 실행하고 결과를 한 줄씩 출력한다.
    승인 대기로 멈춘 건의 리스트를 리턴한다.
    """
    pending = []                                                                 # 승인 대기로 멈춘 건을 담을 빈 리스트
    for incident in incidents:                                                   # 인시던트를 하나씩 꺼낸다
        playbooks = match_playbooks(incident, registry)                          # 맞는 플레이북을 찾는다
        result_text = "맞는 플레이북 없음"                                       # 처음에는 없다고 적어 둔다
        for playbook in playbooks:                                               # 맞는 플레이북을 하나씩 꺼낸다
            done = run_playbook(incident, playbook, state, action_log)           # 플레이북을 실행한다
            if done:                                                             # 실행했으면
                result_text = playbook["id"] + " 실행 완료"                      # 실행 완료라고 적는다
            else:                                                                # 승인 대기로 멈췄으면
                result_text = playbook["id"] + " 승인 대기"                      # 승인 대기라고 적는다
                waiting = {"incident": incident["id"], "entity": incident["entity"], "playbook": playbook["id"], "approval": playbook["approval"]}  # 대기 건 한 건
                pending.append(waiting)                                          # 승인 대기 리스트에 추가한다
        status_text = "(상태: " + incident["status"] + ")"                       # 지금 상태를 괄호 글자로 만든다
        print(incident["id"], incident["entity"], incident["grade"], "->", result_text, status_text)  # 번호 · 대상 · 등급 · 결과 · 상태를 출력한다
    return pending                                                               # 승인 대기 리스트를 리턴한다

