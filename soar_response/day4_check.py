from report import find_missing_incidents                        # 오전 2교시의 티켓 없는 조치 찾기 함수를 불러온다
from approval_gate import decide_gate                            # 오전 3교시의 승인 게이트 함수를 불러온다


def check_report(report_text, tickets, actions):                 # 리포트 문자열 · 티켓 리스트 · 조치 기록 리스트를 받는 함수
    """리포트에 들어 있어야 할 티켓 번호와 티켓 없는 조치의 인시던트 번호 가운데, 리포트에 없는 번호를 리스트로 리턴한다.
    고객사에 리포트를 보내기 전에 2 · 3일 차 데이터가 빠짐없이 들어갔는지 확인할 때 쓴다.
    """
    expected = []                                                # 리포트에 있어야 할 번호를 모을 빈 리스트 — 미리 채운 줄
    for ticket in tickets:                                       # 티켓을 하나씩 꺼낸다 — 미리 채운 줄
        expected.append(ticket["id"])                            # 티켓 번호를 추가한다 — 미리 채운 줄
    for action in find_missing_incidents(actions, tickets):      # 티켓이 없는 조치를 하나씩 꺼낸다 — 미리 채운 줄
        expected.append(action["incident"])                      # 그 인시던트 번호를 추가한다 — 미리 채운 줄
    not_found = []                                               # 리포트에 없는 번호를 모을 빈 리스트 — 미리 채운 줄
    for number in expected:                                      # 있어야 할 번호를 하나씩 꺼낸다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 1. number 가 report_text 안에 없으면 (if, not in)
        if number not in report_text: 
            # 2. not_found 에 number 를 추가한다 (append)
            not_found.append(number)
    return not_found                                             # 리포트에 없는 번호 리스트를 리턴한다 — 미리 채운 줄


def check_gate(cases, policy):                                   # 시험 사례 리스트와 승인 정책을 받는 함수
    """시험 사례마다 승인 게이트를 실행해, 결정이 기대한 결정과 다른 사례의 이름을 리스트로 리턴한다.
    승인 기준을 바꾼 뒤에도 자동 · 승인 필요 · 차단 금지가 맞게 나뉘는지 확인할 때 쓴다.
    """
    wrong = []                                                   # 기대와 다른 사례를 모을 빈 리스트 — 미리 채운 줄
    for case in cases:                                           # 시험 사례를 하나씩 꺼낸다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. decide_gate(case["request"], policy) 의 두 결과를 decision, reasons 에 담는다
        decision, reasons = decide_gate(case["request"], policy)
        # 4. decision 이 case["expected"] 와 다르면 (if, !=)
        if decision != case["expected"]:    
            wrong.append(case["case"] + " (기대 " + case["expected"] + ", 결과 " + decision + ")")  # 사례 이름과 두 결정을 추가한다 — 미리 채운 줄
    return wrong                                                 # 기대와 다른 사례 리스트를 리턴한다 — 미리 채운 줄


def check_recovery(results, state, true_positive_users):         # 오탐 처리 결과 · 처리 뒤 상태 · 진짜 공격 계정 리스트를 받는 함수
    """오탐 처리 결과에서 남은 대상 · 시간 초과를 찾고, 진짜 공격 계정이 풀렸는지도 확인해 문제 문장 리스트를 리턴한다.
    오탐 복구가 신속하고 완전했는지, 진짜 공격의 조치는 그대로인지 확인할 때 쓴다.
    """
    problems = []                                                # 문제 문장을 모을 빈 리스트 — 미리 채운 줄
    for result in results:                                       # 오탐 처리 결과를 하나씩 꺼낸다 — 미리 채운 줄
        if result["remaining"] != []:                            # 아직 복구되지 않은 대상이 있으면 — 미리 채운 줄
            problems.append(result["incident"] + " 복구 안 됨")  # 문제를 추가한다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. result["in_time"] 이 False 이면 (if not)
        if not result["in_time"]:
            problems.append(result["incident"] + " 30분 넘음")   # 문제를 추가한다 — 미리 채운 줄
    for user in true_positive_users:                             # 진짜 공격 계정을 하나씩 꺼낸다 — 미리 채운 줄
        # 6. user 가 state["locked_users"] 안에 없으면 (if, not in)
        if user not in state["locked_users"]:    
            # 7. problems 에 user + " 잠금이 풀림" 을 추가한다 (append)
            problems.append(user + " 잠금이 풀림")
    return problems                                              # 문제 문장 리스트를 리턴한다 — 미리 채운 줄


def mark(problems):                                              # 문제 리스트를 받는 함수
    """문제 리스트가 비어 있으면 「통과」, 하나라도 있으면 「확인 필요」를 리턴한다.
    점검 결과를 한눈에 보이게 출력할 때 쓴다.
    """
    if problems == []:                                           # 문제가 없으면
        return "통과"                                            # 통과를 리턴한다
    return "확인 필요"                                           # 문제가 있으면 확인 필요를 리턴한다

