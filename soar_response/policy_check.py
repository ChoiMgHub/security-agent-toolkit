from approval_gate import decide_gate                                                      # 금요일 파일의 승인 게이트 함수를 불러온다


def count_executed(result):                                                                # 결과 기록 한 건을 받는 함수
    """결과 기록에서 실제로 실행한 조치가 몇 개인지 센다. 실행한 조치가 있는데 티켓이 없는 알림을 찾을 때 쓴다."""
    executed_count = 0                                                                     # 실행한 조치 수 : 처음에는 0
    for step in result["steps"]:                                                           # 조치 결과를 하나씩 꺼낸다
        if step["executed"]:                                                               # 실행한 조치이면
            executed_count = executed_count + 1                                            # 실행한 조치 수를 1 늘린다
    return executed_count                                                                  # 실행한 조치 수를 리턴한다


def find_gate_bypass(results, policy):                                                     # 결과 기록 리스트와 승인 정책을 받는 함수
    """저장된 조치 요청으로 승인 게이트의 결정을 다시 구해, 자동이 아닌데 실행된 조치가 있는 알림 번호를 리스트로 리턴한다. 게이트를 거치지 않았거나 결정을 바꿔 쓴 실행을 찾을 때 쓴다."""
    violations = []                                                                        # 위반한 알림 번호를 모을 빈 리스트 — 미리 채운 줄
    for result in results:                                                                 # 결과 기록을 하나씩 꺼낸다 — 미리 채운 줄
        for step in result["steps"]:                                                       # 조치 결과를 하나씩 꺼낸다 — 미리 채운 줄
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            # 1. decide_gate(step["request"], policy) 의 두 결과를 new_decision, new_reasons 에 저장한다
            new_decision, new_reasons = decide_gate(step["request"], policy)
            # 2. new_decision 이 "자동" 이 아니고(and) step["executed"] 가 참이면 (if, !=, and)
            if new_decision != "자동" and step["executed"]:    
                violations.append(result["incident"])                                      # 알림 번호를 위반 리스트에 추가한다 — 미리 채운 줄
    return violations                                                                      # 위반한 알림 번호 리스트를 리턴한다 — 미리 채운 줄


def find_allowlist_blocks(results, allowlist_ips):                                         # 결과 기록 리스트와 허용 목록을 받는 함수
    """허용 목록 IP 를 실제로 차단한 알림 번호를 리스트로 리턴한다. 승인 게이트와 별개로, 업무에 필요한 IP 가 차단되지 않았는지 확인할 때 쓴다."""
    violations = []                                                                        # 위반한 알림 번호를 모을 빈 리스트 — 미리 채운 줄
    for result in results:                                                                 # 결과 기록을 하나씩 꺼낸다 — 미리 채운 줄
        for step in result["steps"]:                                                       # 조치 결과를 하나씩 꺼낸다 — 미리 채운 줄
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            # 3. step["target"] 이 allowlist_ips 안에 있고(and) step["after"] 가 "차단됨" 이면 (if, in, ==, and)
            if step["target"] in allowlist_ips and step["after"] == "차단됨":    
                violations.append(result["incident"])                                      # 알림 번호를 위반 리스트에 추가한다 — 미리 채운 줄
    return violations                                                                      # 위반한 알림 번호 리스트를 리턴한다 — 미리 채운 줄


def find_vip_locks(results, vip_accounts):                                                 # 결과 기록 리스트와 VIP 계정 리스트를 받는 함수
    """VIP 계정을 실제로 잠근 알림 번호를 리스트로 리턴한다. 승인 게이트와 별개로, VIP 계정이 자동으로 잠기지 않았는지 확인할 때 쓴다."""
    violations = []                                                                        # 위반한 알림 번호를 모을 빈 리스트 — 미리 채운 줄
    for result in results:                                                                 # 결과 기록을 하나씩 꺼낸다 — 미리 채운 줄
        for step in result["steps"]:                                                       # 조치 결과를 하나씩 꺼낸다 — 미리 채운 줄
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            # 4. step["target"] 이 vip_accounts 안에 있고(and) step["after"] 가 "잠김" 이면 (if, in, ==, and)
            if step["target"] in vip_accounts and step["after"] == "잠김":    
                violations.append(result["incident"])                                      # 알림 번호를 위반 리스트에 추가한다 — 미리 채운 줄
    return violations                                                                      # 위반한 알림 번호 리스트를 리턴한다 — 미리 채운 줄


def find_missing_tickets(results):                                                         # 결과 기록 리스트를 받는 함수
    """조치를 실행했는데 티켓이 없는 알림 번호를 리스트로 리턴한다. 실행한 조치가 담당자에게 인계되지 않고 사라지지 않았는지 확인할 때 쓴다."""
    violations = []                                                                        # 위반한 알림 번호를 모을 빈 리스트 — 미리 채운 줄
    for result in results:                                                                 # 결과 기록을 하나씩 꺼낸다 — 미리 채운 줄
        executed_count = count_executed(result)                                            # 실행한 조치 수를 센다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. executed_count 가 0 보다 크고(and) result["ticket"] 이 "" 이면 (if, >, ==, and)
        if executed_count > 0 and result["ticket"] == "":    
            violations.append(result["incident"])                                          # 알림 번호를 위반 리스트에 추가한다 — 미리 채운 줄
    return violations                                                                      # 위반한 알림 번호 리스트를 리턴한다 — 미리 채운 줄


def run_checks(results, policy):                                                           # 결과 기록 리스트와 승인 정책을 받는 함수
    """점검 네 가지를 모두 실행해 점검 이름마다 위반한 알림 번호 리스트를 담은 딕셔너리를 리턴한다. 로그 하나를 정책에 비추어 한 번에 점검할 때 쓴다."""
    checks = {}                                                                            # 점검 이름 → 위반한 알림 번호 리스트 — 미리 채운 줄
    checks["게이트 우회 실행"] = find_gate_bypass(results, policy)                         # 점검 ① — 미리 채운 줄
    checks["허용 목록 IP 차단"] = find_allowlist_blocks(results, policy["allowlist_ips"])  # 점검 ② — 미리 채운 줄
    checks["VIP 계정 잠금"] = find_vip_locks(results, policy["vip_accounts"])              # 점검 ③ — 미리 채운 줄
    checks["티켓 없는 조치"] = find_missing_tickets(results)                               # 점검 ④ — 미리 채운 줄
    return checks                                                                          # 점검 결과 딕셔너리를 리턴한다 — 미리 채운 줄


def judge(violations):                                                                     # 위반한 알림 번호 리스트를 받는 함수
    """위반이 하나도 없으면 「PASS」, 하나라도 있으면 「FAIL」을 리턴한다. 점검 결과를 한눈에 보이게 출력할 때 쓴다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 6. violations 가 빈 리스트 [] 이면 (if, ==)
    if violations == []:     
        return "PASS"                                                                      # 위반이 없으면 PASS 를 리턴한다 — 미리 채운 줄
    return "FAIL"                                                                          # 위반이 있으면 FAIL 을 리턴한다 — 미리 채운 줄

