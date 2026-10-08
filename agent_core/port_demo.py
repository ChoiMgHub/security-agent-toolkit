import argparse

parser = argparse.ArgumentParser(description="포트를 받아 출력해 봅니다")
parser.add_argument("--port", type=int, default=5000, help="열어 둘 포트 번호")
args = parser.parse_args()

print("받은 포트:", args.port)
