def is_allowlisted(request, policy):                                        # 조치 요청 한 건과 승인 정책을 받는 함수
    """조치 대상이 허용 목록에 있으면 True, 없으면 False 를 리턴한다.
    협력사 사무실이나 점검 서버처럼 지금 정책에서 차단하지 않기로 등록한 대상을 먼저 가려낼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. request["target"] 이 policy["allowlist_ips"] 안에 있는지(in)의 결과를 리턴한다
    return request["target"] in policy["allowlist_ips"]

def risk_score(request, policy):                                            # 조치 요청 한 건과 승인 정책을 받는 함수
    """등급 · VIP · 함께 쓰는 IP · 대상 수로 위험 점수를 더하고, 점수와 이유 리스트를 함께 리턴한다.
    자동으로 실행해도 되는 요청인지 숫자로 판단할 때 쓴다.
    """
    grade_table = policy["grade_points"]                                    # 등급마다 정한 점수 표 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. grade_table[request["grade"]] 를 score 에 저장한다 (등급 점수로 시작한다)
    score = grade_table[request["grade"]] 
    reasons = ["등급 " + request["grade"] + " +" + str(score)]              # 점수를 더한 이유 리스트 — 미리 채운 줄
    # 3. request["target"] 이 policy["vip_accounts"] 안에 있으면 (if, in)
    if request["target"] in policy["vip_accounts"]:
        # 4. score 에 score + policy["vip_points"] 를 저장한다 (VIP 점수를 더한다)
        score = score + policy["vip_points"]
        reasons.append("VIP 계정 +" + str(policy["vip_points"]))            # 이유를 추가한다 — 미리 채운 줄
    if request["users_on_ip"] >= policy["shared_ip_limit"]:                 # 여러 계정이 함께 쓰는 IP 이면 — 미리 채운 줄
        score = score + policy["shared_ip_points"]                          # 함께 쓰는 IP 점수를 더한다 — 미리 채운 줄
        reasons.append("함께 쓰는 IP +" + str(policy["shared_ip_points"]))  # 이유를 추가한다 — 미리 채운 줄
    if request["target_count"] > policy["many_targets_limit"]:              # 한 번에 조치할 대상이 많으면 — 미리 채운 줄
        score = score + policy["many_targets_points"]                       # 대상 수 점수를 더한다 — 미리 채운 줄
        reasons.append("대상 " + str(request["target_count"]) + "개 +" + str(policy["many_targets_points"]))  # 이유를 추가한다 — 미리 채운 줄
    return score, reasons                                                   # 점수와 이유 리스트를 함께 리턴한다 — 미리 채운 줄


def decide_gate(request, policy):                                           # 조치 요청 한 건과 승인 정책을 받는 함수
    """조치 요청 한 건을 「차단 금지」 · 「승인 필요」 · 「자동」 가운데 하나로 정하고, 결정과 이유 리스트를 함께 리턴한다.
    자동 대응이 조치를 실행하기 직전에, 사람의 승인이 필요한지 정할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. is_allowlisted(request, policy) 가 참이면 (if)
    if is_allowlisted(request, policy):
        return "차단 금지", ["허용 목록 대상"]                              # 결정과 이유를 함께 리턴한다 — 미리 채운 줄
    # 6. risk_score(request, policy) 의 두 결과를 score, reasons 에 저장한다
    score, reasons = risk_score(request, policy)
    reasons.append("합계 " + str(score) + "점")                             # 합계 점수를 이유에 추가한다 — 미리 채운 줄
    # 7. score 가 policy["approval_score"] 이상이면 (if, >=)
    if score >= policy["approval_score"]:
        return "승인 필요", reasons                                         # 결정과 이유를 함께 리턴한다 — 미리 채운 줄
    return "자동", reasons                                                  # 기준보다 낮으면 자동으로 실행한다 — 미리 채운 줄

