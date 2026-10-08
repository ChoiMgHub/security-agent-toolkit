import argparse

parser = argparse.ArgumentParser(description="포트와 룰을 받습니다")
parser.add_argument("--port", type=int, default=5000, help="열어 둘 포트 번호")
# 1. --rule 인자를 더 받으세요. --rule 의 기본값은 "brute_force", 설명은 "보낼 룰 이름" 입니다
parser.add_argument("--rule", default="brute_force", help="보낼 룰 이름")
args = parser.parse_args()

# 2. f-string 으로 "포트 5000 · 룰 brute_force" 꼴을 출력하세요. 두 값은 args 에서 꺼냅니다
print(f"포트 {args.port} · 룰 {args.rule}")
