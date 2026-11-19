import pandas as pd                                                         # 표를 다루기 위해 판다스를 pd 라는 이름으로 불러온다

REQUIRED_CONTROLS = {                                                       # 위험 등급마다 반드시 있어야 하는 통제
    "높음": ["승인 게이트", "감사 기록"],                                   # 잘못되면 피해가 큰 조치
    "보통": ["감사 기록"],                                                  # 나중에 확인할 수 있어야 하는 조치
    "낮음": [],                                                             # 따로 요구하지 않는다
}


def make_risk_table(risks):                                                 # 자동 조치마다 적은 위험 리스트를 받는 함수
    """위험 리스트를 표(DataFrame)로 바꾸고, 영향도 × 발생 가능성으로 위험 점수(score) 열을 더해 리턴한다.
    자동 조치마다 위험이 얼마나 큰지 숫자 하나로 비교할 때 쓴다.
    """
    table = pd.DataFrame(risks)                                             # 위험 리스트를 표로 바꾼다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. table["impact"] * table["likelihood"] 를 table["score"] 에 담는다 (위험 점수)
    table["score"] = table["impact"] * table["likelihood"]
    return table                                                            # 점수 열을 더한 표를 리턴한다 — 미리 채운 줄


def risk_level(score):                                                      # 위험 점수를 받는 함수
    """위험 점수가 6 이상이면 「높음」, 3 이상이면 「보통」, 그보다 낮으면 「낮음」을 리턴한다.
    점수를 사람이 읽기 쉬운 등급으로 바꿀 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. score 가 6 이상이면 (if, >=)
    if score >= 6:
        # 3. "높음" 을 리턴한다
        return "높음"
    if score >= 3:                                                          # 3 이상이면 — 미리 채운 줄
        return "보통"                                                       # 보통을 리턴한다 — 미리 채운 줄
    return "낮음"                                                           # 그보다 낮으면 낮음을 리턴한다 — 미리 채운 줄


def find_missing_controls(level, controls):                                 # 위험 등급과 지금 있는 통제 리스트를 받는 함수
    """그 등급에 반드시 있어야 하는 통제 가운데 지금 없는 것을 리스트로 리턴한다.
    위험이 큰 자동 조치에 승인이나 되돌리기 같은 통제가 빠졌는지 찾을 때 쓴다.
    """
    missing = []                                                            # 빠진 통제를 모을 빈 리스트 — 미리 채운 줄
    required = REQUIRED_CONTROLS[level]                                     # 이 등급에 반드시 있어야 하는 통제 — 미리 채운 줄
    for control in required:                                                # 있어야 하는 통제를 하나씩 꺼낸다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 4. control 이 controls 안에 없으면 (if, not in)
        if control not in controls:
            # 5. missing 에 control 을 추가한다 (append)
            missing.append(control)
    return missing                                                          # 빠진 통제 리스트를 리턴한다 — 미리 채운 줄


def assess_risks(table):                                                    # 점수 열이 있는 위험 표를 받는 함수
    """점수가 큰 조치부터 정렬하고, 조치마다 등급과 빠진 통제를 붙인 딕셔너리 리스트를 리턴한다.
    리스크 평가 문서에 위험이 큰 조치부터 적을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 6. table.sort_values("score", ascending=False) 를 sorted_table 에 담는다 (점수가 큰 것부터)
    sorted_table = table.sort_values("score", ascending=False)
    rows = []                                                               # 평가 결과를 모을 빈 리스트 — 미리 채운 줄
    for row in sorted_table.to_dict("records"):                             # 표를 딕셔너리 리스트로 바꿔 하나씩 꺼낸다 — 미리 채운 줄
        level = risk_level(row["score"])                                    # 점수로 등급을 정한다 — 미리 채운 줄
        # 7. find_missing_controls(level, row["controls"]) 의 결과를 missing 에 담는다
        missing = find_missing_controls(level, row["controls"])
        row["level"] = level                                                # 등급을 딕셔너리에 넣는다 — 미리 채운 줄
        row["missing"] = missing                                            # 빠진 통제를 딕셔너리에 넣는다 — 미리 채운 줄
        rows.append(row)                                                    # 평가 결과를 추가한다 — 미리 채운 줄
    return rows                                                             # 평가 결과 리스트를 리턴한다 — 미리 채운 줄


def make_assessment_lines(rows):                                            # 평가 결과 리스트를 받는 함수
    """평가 결과로 리스크 평가 문서(마크다운)의 줄 리스트를 만들어 리턴한다.
    자동 조치를 운영에 넣기 전에 팀이 함께 읽을 문서를 쓸 때 쓴다.
    """
    lines = ["# 자동 대응 리스크 평가 — 2026-11-13(금)", ""]                # 제목과 빈 줄로 시작한다
    lines.append("- 점수 = 영향도(1~3) × 발생 가능성(1~3). 6 이상 높음, 3 이상 보통, 그 밖은 낮음")  # 기준을 적는다
    lines.append("")                                                        # 빈 줄
    lines.append("| 자동 조치 | 영향도 | 발생 가능성 | 점수 | 등급 | 지금 있는 통제 | 빠진 통제 |")  # 표의 제목 줄
    lines.append("|---|---|---|---|---|---|---|")                           # 표의 구분 줄
    for row in rows:                                                        # 평가 결과를 하나씩 꺼낸다
        controls_text = ", ".join(row["controls"])                          # 지금 있는 통제를 쉼표로 잇는다
        missing_text = ", ".join(row["missing"])                            # 빠진 통제를 쉼표로 잇는다
        if missing_text == "":                                              # 빠진 통제가 없으면
            missing_text = "없음"                                           # 없음이라고 적는다
        numbers = str(row["impact"]) + " | " + str(row["likelihood"]) + " | " + str(row["score"])  # 영향도 · 발생 가능성 · 점수를 표 모양으로 잇는다
        lines.append("| " + row["action"] + " | " + numbers + " | " + row["level"] + " | " + controls_text + " | " + missing_text + " |")  # 표의 한 줄
    lines.append("")                                                        # 빈 줄
    lines.append("## 바로 보완할 조치")                                     # 보완할 조치 절의 제목
    for row in rows:                                                        # 평가 결과를 하나씩 꺼낸다
        if row["missing"] != []:                                            # 빠진 통제가 있으면
            gap_text = ", ".join(row["missing"])                            # 빠진 통제를 쉼표로 잇는다
            lines.append("- " + row["action"] + ": " + gap_text + " 추가")  # 보완할 내용을 적는다
    return lines                                                            # 완성한 줄 리스트를 리턴한다

