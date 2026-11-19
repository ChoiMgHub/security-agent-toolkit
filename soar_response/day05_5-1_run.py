from incident import load_json                                                             # 월요일 파일의 JSON 읽기 함수를 불러온다
from risk_assessment import make_risk_table, assess_risks, make_assessment_lines           # 방금 만든 리스크 평가 함수를 불러온다

DOC_PATH = "risk_assessment.md"                                                            # 리스크 평가 문서를 저장할 파일 이름

risks = load_json("config/automation_risks.json")                                          # 자동 조치마다 적은 위험 파일을 리스트로 읽는다
print("--- 단계 1: 불러온 자동 조치", len(risks), "개")                                    # 단계 1 시작을 알리는 줄

table = make_risk_table(risks)                                                             # 표로 바꾸고 점수 열을 더한다
# ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
# 8. assess_risks(table) 의 결과를 rows 에 담는다
rows = assess_risks(table)
print("--- 단계 2: 점수가 큰 조치부터")                                                    # 단계 2 시작을 알리는 줄
gap_count = 0                                                                              # 빠진 통제가 있는 조치 수 : 처음에는 0
for row in rows:                                                                           # 평가 결과를 하나씩 꺼낸다
    print(row["action"], "· 점수", row["score"], "·", row["level"], "· 빠진 통제", row["missing"])  # 조치 한 줄을 출력한다
    if row["missing"] != []:                                                               # 빠진 통제가 있으면
        # 9. gap_count 에 gap_count + 1 을 담는다 (1 늘린다)
        gap_count = gap_count + 1
lines = make_assessment_lines(rows)                                                        # 문서의 줄 리스트를 만든다
text = "\n".join(lines) + "\n"                                                             # 줄 리스트를 줄바꿈으로 이어 한 문자열로 만든다
with open(DOC_PATH, "w", encoding="utf-8") as doc_file:                                    # 문서 파일을 쓰기 모드("w")로 연다
    doc_file.write(text)                                                                   # 문서 문자열을 파일에 쓴다
print("--- 단계 3: 바로 보완할 조치", gap_count, "개 ·", DOC_PATH, len(lines), "줄 저장")  # 단계 3 시작을 알리는 줄

