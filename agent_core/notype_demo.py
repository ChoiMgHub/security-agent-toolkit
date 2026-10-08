import argparse

parser = argparse.ArgumentParser()
# 1. --port 인자를 받으세요. type=int 를 쓰지 않고, 기본값은 글자 "5000" 입니다
parser.add_argument("--port", default="5000")
args = parser.parse_args()

# 2. args.port 에 글자 "1" 을 더한 것을 출력하세요
print(args.port + "1")
