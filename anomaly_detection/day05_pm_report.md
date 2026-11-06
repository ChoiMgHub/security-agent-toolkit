# 4과목 Day 5 도커 컴포즈로 서버 두 대 켜기 · 웹 서버 로그 만들기 · 오후 (최민기 · 2026-11-06(금))

> **쓰는 법**
> - 문제를 풀 때마다 그 문제 제목 아래 질문에 답합니다.
> - 질문마다 `쓸 내용:` 에 무엇을 쓰면 되는지 적혀 있습니다. 그대로 `답:` 뒤에 씁니다.
> - 출력이나 코드를 붙여 넣는 질문은 `답:` 아래 빈 코드 상자에 붙여 넣고, 설명은 `답:` 뒤에 씁니다.
> - 「왜」를 묻는 질문은 한 단어로 끝내지 말고, 내 화면에서 본 값이나 배운 내용을 근거로 이유까지 씁니다.
> - 🔍 는 이 교시에서 꼭 알아야 할 핵심 질문입니다. 답을 못 찾았으면 「모름 — 막힌 곳: …」 이라고 씁니다. 🔍 가 없는 질문도 못 적으면 같은 말을 씁니다.

---

## 5교시 · 도커 복습 · 컴포즈로 서버 두 대 한 번에 켜기

### 문제 5-1 · 서버 한 대를 복습하고 컴포즈로 두 대 켜기

- (가) 5교시 순서의 서버 켜기 · 확인 명령(`docker images` 부터 `curl` 까지)과 그 결과를 친 순서대로 붙여 넣고, 서비스 이름 두 개와 각 서비스의 포트를 적어 주세요.
  - 쓸 내용: ① 명령과 결과를 친 순서대로(코드 상자에 붙여 넣기): `docker images` · `docker run` · `docker ps` · `docker stop` · `docker compose up -d` · `docker compose ps` · `curl` 두 개 (`docker pull` 은 받았을 때만, `pwd` · `touch` · `ls` 는 붙이지 않아도 됩니다) ② 서비스 이름 두 개 ③ 각 서비스의 포트
  - 답: 이미지 목록에서 `nginx:1.28`이 이미 있는 것을 확인했다. 이번에 제공한 실행 기록에는 `docker pull`이 없어 이미지를 새로 받은 결과를 추가하지 않는다. 먼저 `docker run`으로 컨테이너 한 개를 실행하고 상태를 확인한 뒤 중지했다. 이어 컴포즈로 두 서비스를 함께 실행하고 각각의 응답을 확인했다.

다음은 내가 실행한 순서와 주요 출력이다. 터미널의 사용자·경로 프롬프트, 안내 문구와 진행 시간 표시는 생략했다.

```text
$ docker images nginx:1.28
IMAGE        ID             DISK USAGE   CONTENT SIZE   EXTRA
nginx:1.28   146adea4768b        240MB         65.8MB

$ docker run -d --rm -p 8080:80 --name web-run nginx:1.28
106cbcda39d9c10ba633d4f414936a763e4ff9d116141fa598ac521f953278e6

$ docker ps
CONTAINER ID   IMAGE        COMMAND                   CREATED         STATUS         PORTS                                     NAMES
106cbcda39d9   nginx:1.28   "/docker-entrypoint.…"   5 seconds ago   Up 5 seconds   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   web-run

$ docker stop web-run
web-run

$ docker compose up -d
[+] up 3/3
 ✔ Network anomaly_detection_default  Created
 ✔ Container anomaly_detection-web2-1 Started
 ✔ Container anomaly_detection-web1-1 Started

$ docker compose ps
NAME                       IMAGE        COMMAND                   SERVICE   CREATED          STATUS          PORTS
anomaly_detection-web1-1   nginx:1.28   "/docker-entrypoint.…"   web1      16 seconds ago   Up 15 seconds   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
anomaly_detection-web2-1   nginx:1.28   "/docker-entrypoint.…"   web2      16 seconds ago   Up 15 seconds   0.0.0.0:8081->80/tcp, [::]:8081->80/tcp

$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080
200

$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8081
200
```

| 서비스 이름 | 내 PC의 포트 | 컨테이너 안의 포트 | 확인 결과 |
|---|---|---|---|
| `web1` | 8080 | 80 | 실행 상태 `Up`, 요청 결과 200 |
| `web2` | 8081 | 80 | 실행 상태 `Up`, 요청 결과 200 |

`web1`, `web2`는 컴포즈 파일의 서비스 이름이고, `anomaly_detection-web1-1`처럼 표시된 것은 실제 컨테이너 이름이다. `Up`은 컨테이너 실행 상태를, `200`은 보낸 웹 요청의 성공을 보여 준다. 실행 결과의 `3/3`은 네트워크 한 개와 컨테이너 두 개를 처리한 결과이며 서버 세 대라는 뜻은 아니다.

- (나) 🔍 서버 두 대를 `docker run` 으로 켜는 것과 `compose.yaml` 과 `docker compose up -d` 로 켜는 것을 비교해, 컴포즈가 더 나은 점을 두 가지 적어 주세요.
  - 쓸 내용: ① 컴포즈가 더 나은 점 두 가지
  - 답: 첫째, 이미지 버전과 포트 등 실행 설정을 `compose.yaml` 한 파일에 모아 두므로 긴 명령의 옵션을 매번 다시 입력하지 않아도 된다. 어떤 설정으로 실행하는지 읽고 검토하기 쉽고, 설정 파일을 Git으로 관리하면 변경 기록도 남길 수 있다.

둘째, `docker compose up -d` 한 줄로 파일에 정의한 여러 서비스를 함께 실행할 수 있다. 이번에는 `web1`과 `web2`를 한 번에 실행했다. 서비스가 늘어나도 설정을 파일에 추가하고 같은 실행 명령을 사용할 수 있다.

- (다) 🔍 보안 사고가 난 뒤 감사팀이 「사고 당시와 같은 구성으로 서버를 다시 켜 보라」고 요청했습니다. 팀원 한 명은 3주 전에 긴 `docker run` 명령을 직접 쳐서 서버를 켰는데 그 명령을 기억하지 못합니다. 다른 팀은 `compose.yaml` 을 깃허브에 올려 두었습니다. 두 팀이 같은 구성을 다시 켤 수 있는지 비교하고, 파일에 `nginx:1.28` 처럼 버전을 적어 두는 것이 이런 재현에 왜 중요한지 적어 주세요.
  - 쓸 내용: ① 두 팀의 차이 ② 버전을 적어 두는 것이 재현에 중요한 이유
  - 답: `docker run` 명령을 기억하지 못하는 팀은 당시 이미지 버전과 포트 등을 바로 확인하기 어렵다. 같은 구성을 다시 실행하려면 명령 기록이나 남아 있는 컨테이너의 설정을 찾아 확인해야 한다. `docker run`을 썼다는 이유만으로 재현이 불가능한 것은 아니지만, 설정 기록이 없으면 당시 구성을 확인하기가 어려워진다.

반면 `compose.yaml`을 GitHub에 보관한 팀은 사고 당시 커밋의 파일에서 서비스별 이미지와 포트 설정을 확인하고, 그 설정으로 다시 실행할 수 있다. 현재 파일만 보는 것이 아니라 당시 저장된 버전을 확인하는 것이 중요하다.

`nginx:1.28`처럼 버전을 적으면 사용한 버전 범위를 명확히 할 수 있다. `nginx`만 쓰면 기본적으로 `latest` 태그를 사용하므로, 나중에 다른 이미지 내용으로 실행돼 결과가 달라질 수 있다. 버전 태그가 이미지 내용을 영구히 고정하는 것은 아니지만, 이번 실습에서는 사용한 버전을 설정에 명시해 재현의 기준을 남기는 점이 중요하다.

이 질문은 사고 상황을 가정한 설명이다. 내가 실제 보안 사고 당시의 서버를 재현한 결과는 아니다.

- (라) 🔍 팀원 세 명이 같은 `compose.yaml` 로 서버를 켰는데 한 명의 PC 에서만 `8081` 번 포트를 다른 프로그램이 쓰고 있어서 `web2` 가 켜지지 않았습니다. 이 사람이 파일의 어느 줄을 어떻게 바꾸면 되는지 적고, 바꿔도 서버 안에서는 여전히 `80` 번 포트로 동작하는 이유를 적어 주세요. 이 사람이 `curl` 로 확인할 때 달라지는 점도 적어 주세요.
  - 쓸 내용: ① 바꿀 줄과 바꾼 모양 ② 서버 안은 그대로 80 인 이유 ③ curl 주소의 달라지는 점
  - 답: 질문의 가정에서는 `web2`의 `ports` 아래 줄에서 왼쪽 포트만 다른 프로그램이 사용하지 않는 번호로 바꾼다. 예를 들어 8082번이 비어 있다면 다음과 같이 바꿀 수 있다.

```yaml
# 변경 전
- "8081:80"

# 변경 예시
- "8082:80"
```

콜론 왼쪽은 내 PC에서 요청을 받는 포트이고, 오른쪽은 컨테이너 안의 nginx가 사용하는 포트다. PC 쪽 포트만 바꾸므로 컨테이너 안에서는 계속 80번으로 동작한다. 변경한 파일을 적용한 뒤 요청 주소도 PC 쪽 포트에 맞춰 바꿔야 한다.

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8082
```

다른 팀원은 기존 8081번 주소를 사용한다. 이 내용은 질문에 대한 변경 예시이며, 내 실제 실습의 포트를 바꾼 기록이 아니다. 나는 수업에서 정한 대로 `web1`은 8080, `web2`는 8081, 6교시의 `web3`은 8082를 사용했다.

## 6교시 · 서버마다 접속 범위 정하기 · 설정 바꿔 적용하기

### 문제 6-1 · 서버마다 접속 범위를 정해 컴포즈 파일로 적용하기

- (가) 1번과 5번의 `docker compose ps` 출력을 붙여 넣고, 접속 범위가 바뀐 기존 서비스와 새로 추가된 서비스를 따로 적어 주세요.
  - 쓸 내용: ① 1번 출력(코드 상자에 붙여 넣기) ② 5번 출력(코드 상자에 붙여 넣기) ③ 접속 범위가 바뀐 기존 서비스 ④ 새로 추가된 서비스
  - 답: 접속 범위를 바꾼 기존 서비스는 `web2`이고, 새로 추가한 서비스는 `web3`이다. 아래는 첫 포트 오류를 확인한 뒤 재실행하면서 남긴 변경 전후 출력이다. `web1`은 유지하고 `web2`만 먼저 중지한 다음 새 설정을 적용했다. 터미널 프롬프트와 진행 표시의 소요 시간은 생략했다.

```text
$ docker compose up -d
[+] up 3/3
 ✔ Network anomaly_detection_default  Created
 ✔ Container anomaly_detection-web2-1 Started
 ✔ Container anomaly_detection-web1-1 Started

$ docker compose ps
NAME                       IMAGE        COMMAND                   SERVICE   CREATED         STATUS         PORTS
anomaly_detection-web1-1   nginx:1.28   "/docker-entrypoint.…"   web1      5 seconds ago   Up 4 seconds   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
anomaly_detection-web2-1   nginx:1.28   "/docker-entrypoint.…"   web2      5 seconds ago   Up 4 seconds   0.0.0.0:8081->80/tcp, [::]:8081->80/tcp

$ docker compose stop web2
[+] stop 1/1
 ✔ Container anomaly_detection-web2-1 Stopped

$ docker compose -f compose.secure.yaml up -d
[+] up 3/3
 ✔ Container anomaly_detection-web1-1 Running
 ✔ Container anomaly_detection-web3-1 Started
 ✔ Container anomaly_detection-web2-1 Started

$ docker compose -f compose.secure.yaml ps
NAME                       IMAGE        COMMAND                   SERVICE   CREATED          STATUS          PORTS
anomaly_detection-web1-1   nginx:1.28   "/docker-entrypoint.…"   web1      22 seconds ago   Up 22 seconds   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
anomaly_detection-web2-1   nginx:1.28   "/docker-entrypoint.…"   web2      4 seconds ago    Up 3 seconds    127.0.0.1:8081->80/tcp
anomaly_detection-web3-1   nginx:1.28   "/docker-entrypoint.…"   web3      4 seconds ago    Up 4 seconds    127.0.0.1:8082->80/tcp
```

| 서비스 | 변경 전 | 변경 후 | 확인한 변화 |
|---|---|---|---|
| `web1` | `0.0.0.0:8080` | `0.0.0.0:8080` | 기존 공개 방식과 컨테이너 유지 |
| `web2` | `0.0.0.0:8081` | `127.0.0.1:8081` | PC의 공개 포트를 로컬 접속으로 제한 |
| `web3` | 없음 | `127.0.0.1:8082` | 서비스 새로 추가 |

재적용 후 세 서비스에 실제 요청을 보내 각각 200을 확인했다. 요청은 아래 순서로 실행했다.

```text
$ curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8081
200

$ curl -sS -o /dev/null -w "%{http_code}\n" http://localhost:8080
200

$ curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8082
200
```

첫 적용에서는 `web2` 시작 중 다음 오류가 발생했고, 당시 `ps`에는 `web1`과 `web3`만 있었다. 8080과 8082 요청은 200이었지만 8081 요청은 000이었다.

```text
Error response from daemon: ports are not available: exposing port TCP 127.0.0.1:8081 -> 127.0.0.1:0: listen tcp4 127.0.0.1:8081: bind: Only one usage of each socket address (protocol/network address/port) is normally permitted.
```

000은 서버가 보낸 HTTP 상태 코드가 아니라 HTTP 응답을 받지 못한 결과다. 첫 실행에서는 로그 저장을 확인한 뒤 `down`으로 정리했다. 이후 위 재실행에서 `web2`만 먼저 중지하고 설정을 적용하자 정상 실행과 200 응답을 확인했다. 설정에 맞는 출력이 나온 최종 결과와, 처음 실패한 결과를 구분해 기록한다.

- (나) 🔍 `"8081:80"` 과 `"127.0.0.1:8081:80"` 은 누가 접속할 수 있는지가 어떻게 다른가요? 관리 화면이나 데이터베이스 서버를 이렇게 설정하는 이유도 적어 주세요.
  - 쓸 내용: ① 두 포트 줄에서 누가 접속할 수 있는지의 차이 ② 관리 화면 · 데이터베이스를 이렇게 설정하는 이유
  - 답: `"8081:80"`은 기본적으로 PC의 모든 네트워크 인터페이스에 포트를 열기 때문에 네트워크와 방화벽이 허용하면 다른 PC에서도 접근할 수 있다. `"127.0.0.1:8081:80"`은 PC 자신을 가리키는 주소에만 포트를 열어 해당 PC에서 그 포트로 접속하도록 제한한다. 오른쪽의 80번은 두 설정 모두 컨테이너 안에서 nginx가 사용하는 포트다.

관리 화면이나 데이터베이스처럼 외부에서 직접 접속할 필요가 없는 서비스는 공개 범위를 줄여 불필요한 접근을 제한한다. 이 설정은 네트워크 접속 범위를 제한하는 것으로, 사용자별 로그인이나 권한 검사를 대신하지는 않는다.

내 실습에서는 변경 후 `ps`에서 `web2`와 `web3`의 앞부분이 `127.0.0.1:`로 표시됐고 내 PC에서 보낸 요청은 모두 200이었다. 다른 PC에서 접속해 차단을 확인한 결과는 제공한 실행 기록에 없으므로, 그 결과까지 실측했다고 적지 않는다.

- (다) 🔍 `up -d` 의 출력에서 `web1` 은 `Running`, `web2` 는 `Recreated`, `web3` 은 `Created` 였습니다. 서버마다 출력이 다른 이유와, 운영 중인 서비스의 설정을 바꿀 때 이것이 왜 도움이 되는지 적어 주세요.
  - 쓸 내용: ① 서버마다 출력이 다른 이유 ② 서버를 끊지 않고 바꿀 수 있는 것의 쓸모
  - 답: 문제에 제시된 정상 예시에서 `web1`은 설정이 같아 기존 컨테이너를 유지하므로 `Running`, `web2`는 포트 설정이 바뀌어 컨테이너를 다시 만들므로 `Recreated`, `web3`은 새 서비스이므로 `Created`로 표시된다. 설정이 그대로인 서비스를 함께 중지하지 않고 변경이 필요한 서비스만 다시 적용할 수 있다는 점이 도움이 된다.

내가 실제 재실행에서 본 출력은 `web1 Running`, `web2 Started`, `web3 Started`였다. 화면에 없는 `Recreated`와 `Created`를 직접 봤다고 쓰지 않는다. 대신 변경 후 `ps`에서 `web1`은 생성 후 22초 동안 계속 실행 중이었고, `web2`와 `web3`은 생성 후 4초로 표시된 것을 확인했다. 이 생성 시각과 변경된 포트 설정을 근거로 기존 `web1` 유지, `web2` 재생성, `web3` 신규 생성을 확인했다.

이번에는 오류 해결 과정에서 `web2`만 먼저 중지한 뒤 적용했다. 따라서 모든 서버를 무중단으로 바꾼 실습이라고 쓰지 않는다. 확인한 것은 설정 적용 동안 `web1` 컨테이너가 계속 실행됐다는 점이며, 연속 요청으로 무중단 가용성을 측정한 것은 아니다.

#### 로그 저장과 종료 후 보존 확인

`web3`의 `volumes` 설정 `./logs:/var/log/nginx`는 내 `logs` 폴더를 컨테이너의 로그 폴더에 연결하는 바인드 마운트다. 첫 실행에서 정상 경로와 스캐너 요청을 흉내 낸 두 경로를 요청해 다음 결과를 확인했다. web2의 포트 오류가 있어도 web3의 요청과 로그 저장은 정상적으로 수행됐다.

```text
$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8082
200

$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8082/.env
404

$ curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8082/phpmyadmin
404

$ cat logs/access.log
172.18.0.1 - - [06/Nov/2026:05:59:02 +0000] "GET / HTTP/1.1" 200 615 "-" "curl/8.22.0" "-"
172.18.0.1 - - [06/Nov/2026:05:59:07 +0000] "GET /.env HTTP/1.1" 404 153 "-" "curl/8.22.0" "-"
172.18.0.1 - - [06/Nov/2026:05:59:12 +0000] "GET /phpmyadmin HTTP/1.1" 404 153 "-" "curl/8.22.0" "-"

$ grep " 404 " logs/access.log | wc -l
2

$ grep " 404 " logs/access.log > logs/web_404.log
```

`grep`으로 파일에 저장하는 명령은 화면 출력 없이 끝났다. 404는 존재하지 않는 연습용 경로에 대한 응답이며, 실제 공격을 발견한 결과는 아니다.

재실행 후에도 web3에 정상 요청을 보냈으므로 `access.log`의 줄 수는 처음 세 줄보다 늘어날 수 있다. 재실행 후 404 재집계 결과와 저장된 `web_404.log`의 본문은 추가로 확인하지 않았다.

최종적으로 세 서비스의 200 응답을 확인한 뒤 다음을 실행했다.

```text
$ docker compose -f compose.secure.yaml down
[+] down 4/4
 ✔ Container anomaly_detection-web3-1 Removed
 ✔ Container anomaly_detection-web1-1 Removed
 ✔ Container anomaly_detection-web2-1 Removed
 ✔ Network anomaly_detection_default  Removed

$ ls logs
access.log  error.log  web_404.log
```

컨테이너와 네트워크를 삭제한 뒤에도 로그 파일 세 개가 남은 것을 확인했다. 설정 변경 중에는 `web1`을 유지했고, 실습을 마친 다음에는 `down`으로 전체를 정리했다.

#### 포트 오류 원인 확인 과정과 조사 범위

AI의 안내로 Windows PowerShell에서 8081번 포트의 수신 대기 프로세스를 조회했고, 출력이 없었다. 그 조회는 컨테이너를 `down`으로 정리한 뒤였으므로 오류 당시 포트를 누가 점유했는지를 보여 주는 결과는 아니다.

Docker Desktop의 호스트 로그와 이전 엔진 로그를 조회하고, 그 결과를 AI와 함께 살펴봤다. 호스트 로그에서는 한국 시간 14:58:37 무렵 기존 `0.0.0.0:8081` 연결 제거 처리 뒤 약 0.08초 만에 새 `127.0.0.1:8081` 연결을 시도한 순서가 확인됐다. 재실행에서는 기존 연결 제거 뒤 약 5.5초 후 새 연결이 정상 설정됐다. 이 시간 차이는 확인한 기록이며, 그 자체로 포트 해제 지연을 증명하지는 않는다.

현재 엔진 로그의 검색 결과는 0건이었다. 이전 엔진 로그에서는 실패한 컨테이너 등과 관련된 38개 항목이 검색됐지만, 전달한 본문은 모두 컨테이너 관리·상태 조회의 `apiproxy` 정보 기록이었다. 정확한 포트 점유 주체나 내부 실패 원인을 확정할 추가 근거는 얻지 못했다.

기존 연결 해제가 완료되기 전에 새 연결을 시도했을 가능성은 있으나, 특정 Docker 버그나 다른 프로그램의 점유라고 단정하지 않는다. 남아 있는 로그 조사까지 진행하고 시간상 재현·동시 추적 실험은 하지 않았다. 확인된 해결 조치는 `web2`를 먼저 중지한 뒤 새 설정을 적용한 것이며, 최종적으로 세 서비스의 200 응답을 확인했다.

처음 UCRT64에서 PowerShell을 호출하는 명령을 실행할 때 오류가 있었다고 전달했으나 오류 원문을 대화에 전달하지 않아 그 원인은 미확인이다. 이후 Windows PowerShell에서 직접 수행한 조회는 실행됐고, 조건에 맞는 기록이 없을 때는 출력 없음 또는 0건으로 나타났다. 이를 PowerShell 자체가 동작하지 않은 결과와 구분했다.

### 마무리 · 오늘 만든 것을 깃허브에 올리기

- (가) `git status` 를 쳤을 때 `.env` 나 `.venv` 가 보였는지, 보였다면 어떻게 했는지 적어 주세요.
  - 쓸 내용: ① `.env` · `.venv` 가 보였는지 ② 보였다면 한 조치
  - 답: 업로드 직전 내 PC의 `git status` 출력은 대화에 제공하지 않아, 당시 `.env`나 `.venv`가 표시됐는지와 별도 조치 여부는 미확인으로 남긴다.

업로드 후 AI가 GitHub `main`의 [8e0e757 커밋](https://github.com/ChoiMgHub/security-agent-toolkit/commit/8e0e757883bdf2d0bff97f1cd1f44c073b9bc1ca)을 직접 검수했다. 오늘 오전의 알림 데이터·평가 및 튜닝 코드·실행 스크립트·수업 자료·보고서와 오후의 컴포즈 파일 두 개·로그 파일 세 개·수업 자료·보고서가 포함된 변경 파일 18개를 확인했다.

해당 커밋의 전체 파일 목록에는 `.env`, `.venv`, `__pycache__`가 추적 파일로 포함되지 않았고, 루트 `.gitignore`에 세 항목이 설정된 것도 확인했다. 이는 GitHub에 올라간 상태를 확인한 결과이며, 업로드 직전 PC의 `git status` 출력과는 구분한다.

AI는 업로드된 오전 실행 스크립트 세 개를 별도 환경에서 재실행해 알림·오탐·미탐 수가 내 출력과 일치함을 확인했다. 오후 설정은 파일을 대조했고, 저장된 `web_404.log` 두 줄이 `access.log`에서 404를 고른 결과와 같음을 확인했다. 내 PC의 도커 재실행 결과는 앞의 실제 출력 기록을 근거로 한다.
