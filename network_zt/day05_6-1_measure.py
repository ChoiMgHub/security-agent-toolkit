# 3 개 회선의 ping 결과 10 번씩 (단위: ms). None 은 응답이 없었던 것(손실)이다
LINES = {
    "회선 A": [22, 21, 23, 22, 21, 22, 23, 22, 21, 22],
    "회선 B": [18, 19, 95, 17, 18, 110, 19, 18, 92, 17],
    "회선 C": [40, 41, None, 42, 40, None, 41, 43, None, 40],
}

def jitter(got):
    """받은 응답 시간으로 지터를 계산한다.

    입력: 응답 시간 리스트 got(ms, 2개 이상)
    리턴: 이웃한 차이의 절댓값을 평균 낸 지터(ms)
    """
    total = 0
    for i in range(1, len(got)):
        total = total + abs(got[i] - got[i - 1])
    return total / (len(got) - 1)                 

def measure(name, data):                  # 회선 하나의 지연 · 지터 · 손실을 구해 출력하는 함수이다
    got = []                              # 응답을 받은 값만 모을 빈 리스트이다
    for v in data:                        # 응답 10 개를 하나씩 꺼낸다
        if v != None:                     # 응답이 있으면 (None 이 아니면)
            got.append(v)                 # got 에 담는다

    delay = sum(got) / len(got)           # 평균 지연 = 받은 값의 합 ÷ 받은 개수
    jitter_value = jitter(got)            # 위에서 만든 jitter 함수에 got 을 넘겨 지터를 받는다
    loss = (len(data) - len(got)) / len(data) * 100   # 손실률 = 못 받은 개수 ÷ 보낸 개수 × 100

    print(name, "| 지연", round(delay, 1), "ms | 지터", round(jitter_value, 1), "ms | 손실", round(loss), "%")   # 한 줄로 출력한다

for name in LINES:                        # 회선 이름을 하나씩 꺼낸다
    measure(name, LINES[name])            # 그 회선의 값을 measure 에 넘긴다

