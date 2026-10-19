# Day 6 Docker ① · nginx 서버 · 오후 (최민기 · 2026-10-19)

> **쓰는 법**
> - 문제를 하나 풀 때마다 그 문제 제목 아래를 채웁니다.
> - 질문마다 `쓸 내용:` 에 **무엇을 쓰면 되는지** 적혀 있습니다. 그 내용대로 `답:` 뒤에 씁니다.
> - 「왜 그럴까요?」 같은 질문은 한 단어로 끝내지 말고, 내 화면에서 본 값이나 배운 내용을 근거로 이유까지 씁니다.
> - 🔍 는 그 교시에 꼭 알아야 할 핵심 질문입니다. 답을 못 찾았으면 「모름 — 막힌 곳: …」 이라고 씁니다.

---


> **기록 범위와 확인 상태**
> - SKT ALEPH 국비교육 수강생으로서, 오후 수업의 설명을 듣고 질문하며 실습한 과정과 결과를 정리했다. A사 상황과 실습 명칭은 학습용 예시이며 실제 운영 시스템을 구축한 기록은 아니다.
> - 직접 확인한 터미널 출력과 첨부 화면은 실제 결과로 기록했다. 설치·Resource Saver 해제, hello-world 실행, 공식 태그 탐색, nginx 실행·로그 확인, 오류 해결, 두 컨테이너 실행·정리를 포함한다.
> - 채팅에 없는 ls 전체 목록, 일부 브라우저 화면 비교와 HTML 수정 반영은 확인 기준과 실제 기록을 구분했다. 7-3에서는 저장소 맨 위의 git status 출력에서 미추적 파일·폴더 항목 17줄과 .env·.venv/ 미표시를 직접 확인했다. 현재 출력은 add·commit·push 전 상태이므로 GitHub 업로드 완료와는 구분했다.

## 5교시 · 왜 도커인가 · 이미지와 컨테이너 · 같이 설치하기

### 문제 5-1 · 설치를 확인하고 첫 컨테이너 실행하기

- (가) `docker --version` 으로 나온 값을 적어 주세요.
  - 쓸 내용: 「Docker version … build …」 한 줄
  - 답:

    점심시간에 Docker Desktop을 설치했고, Git Bash에서 다음 버전을 직접 확인했다.

    ```text
    Docker version 29.8.2, build 7fc2dff
    ```

    버전 확인은 클라이언트 명령이 설치되어 인식된다는 확인이고, 엔진이 실행 중인지와는 별개라는 설명을 들었다. Docker Desktop 화면을 첨부해 질문했을 때 왼쪽 아래가 Resource Saver mode였다. 사용하지 않을 때 자원을 아끼는 상태라는 설명을 듣고, 오른쪽 삼각형 버튼을 눌러 엔진을 실행했다.

- (나) 🔍 `docker run hello-world` 출력이 말하는 일의 순서를 5.5 그림의 번호(① ~ ④)에 맞춰 설명해 주세요.
  - 쓸 내용: ① ~ ④ 번호마다 한 일 (클라이언트 · 엔진 · Docker Hub · 컨테이너)
  - 답:

    실행한 명령은 docker run hello-world이고, 실제로 Hello from Docker!가 출력됐다.

    ① 터미널에서 입력한 docker 명령인 클라이언트가 엔진·데몬에 컨테이너 실행을 요청한다.

    ② 엔진은 필요한 이미지가 로컬에 없으면 Docker Hub에서 받는다. 이미 저장돼 있다면 기본 동작에서는 재사용할 수 있다.

    ③ 엔진이 이미지를 바탕으로 새 컨테이너를 만들고, 그 안의 프로그램을 실행한다.

    ④ 프로그램의 출력이 엔진과 클라이언트를 거쳐 내 터미널에 표시된다.

    내가 확인한 출력의 핵심 부분:

    ```text
    Hello from Docker!
    This message shows that your installation appears to be working correctly.

    To generate this message, Docker took the following steps:
     1. The Docker client contacted the Docker daemon.
     2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
        (amd64)
     3. The Docker daemon created a new container from that image which runs the
        executable that produces the output you are currently reading.
     4. The Docker daemon streamed that output to the Docker client, which sent it
        to your terminal.
    ```

    이미지를 직접 받은 적이 없는데 어떻게 생겼는지 질문했다. run이 필요할 때 이미지를 자동으로 받을 수 있다는 설명을 들었다. 위 안내 문장은 동작 원리를 설명하는 출력이며, 내가 공유한 이 실행에는 다운로드 진행 줄이 없으므로 최초 다운로드 시점까지 확정할 수는 없다.

- (다) 🔍 `docker images` 에 보인 것과 `docker ps -a` 에 보인 것은 각각 이미지와 컨테이너 중 무엇이고, 어떻게 다른가요?
  - 쓸 내용: ① images 에 보인 것과 그 종류 ② ps -a 에 보인 것과 그 종류 ③ 둘의 차이
  - 답:

    docker images에서는 **hello-world:latest 이미지 한 개**를 확인했고, docker ps -a에서는 그 이미지로 만든 **컨테이너 두 개**를 확인했다.

    이미지는 프로그램과 필요한 파일을 담은 읽기 전용 바탕이고, 컨테이너는 그 이미지를 바탕으로 만든 개별 실행 환경이다. 같은 이미지로 컨테이너를 여러 개 만들 수 있다. run은 새 컨테이너를 생성하므로, 이미지가 하나여도 컨테이너는 두 개일 수 있다는 설명을 들었다.

    내 컨테이너 이름은 sad_euclid와 gifted_chaplygin이었다. 둘 다 안내 문장을 출력하고 정상 종료해 Exited (0)으로 남아 있었다. 종료는 삭제와 다르며, -a를 붙여 종료된 것까지 조회한 것이다. 이미지는 현재 network_zt 폴더에 일반 파일로 받아지는 것이 아니라 도커가 관리하는 저장 공간에 보관되므로 images 명령으로 확인한다.

- (라) 🔍 `docker images` 출력을 붙여 넣고, `hello-world` 줄의 `IMAGE` · `ID` · `EXTRA` 값과 각각의 뜻을 적어 주세요.
  - 쓸 내용: ① 출력 ② `IMAGE` · `ID` · `EXTRA` 의 값과 뜻
  - 답:

    내가 직접 확인한 이미지 목록은 다음과 같다.

    ```text
                                                                                                                     i Info →   U  In Use
    IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
    hello-world:latest   11a3eb1597e8       25.9kB         9.49kB    U
    ```

    | 항목 | 내 실제 값 | 설명 |
    |---|---|---|
    | IMAGE | hello-world:latest | 이미지 이름은 hello-world, 태그는 latest이다. 태그를 생략하면 기본 태그 latest가 사용된다. |
    | ID | 11a3eb1597e8 | 이미지를 식별하는 값이다. 컨테이너 ID와는 다른 대상이다. |
    | EXTRA | U | 이 이미지를 사용하는 컨테이너가 있다는 표시이다. 종료된 컨테이너도 포함한다. |

    latest는 기본 태그의 이름이며, 이름만으로 언제나 가장 최신 버전임을 보장하는 것은 아니라는 설명을 들었다. U도 현재 실행 중이라는 표시로 단정하지 않는다.

- (마) 🔍 `docker ps -a` 출력을 붙여 넣고, `hello-world` 줄의 `STATUS` · `PORTS` · `NAMES` · `IMAGE` 값과 각각의 뜻을 적어 주세요.
  - 쓸 내용: ① 출력 ② `STATUS` · `PORTS` · `NAMES` · `IMAGE` 의 값과 뜻
  - 답:

    내가 직접 확인한 전체 컨테이너 목록은 다음과 같다. 경과 시간은 출력 당시의 값이다.

    ```text
    CONTAINER ID   IMAGE         COMMAND    CREATED              STATUS                          PORTS     NAMES
    2313e0cef55e   hello-world   "/hello"   12 seconds ago       Exited (0) 10 seconds ago                 sad_euclid
    dd5b8acd2bf6   hello-world   "/hello"   About a minute ago   Exited (0) About a minute ago             gifted_chaplygin
    ```

    | 항목 | 내 실제 값 | 설명 |
    |---|---|---|
    | STATUS | 두 줄 모두 Exited (0) | 프로그램이 작업을 마치고 정상 종료한 상태이다. |
    | PORTS | 두 줄 모두 비어 있음 | 표시된 포트 공개·연결 설정이 없다. hello-world는 브라우저 요청을 받는 웹 서버가 아니므로 웹 접속용 포트 공개가 필요하지 않다. |
    | NAMES | sad_euclid / gifted_chaplygin | 이름을 지정하지 않아 도커가 자동으로 붙인 컨테이너 이름이다. |
    | IMAGE | 두 줄 모두 hello-world | 컨테이너를 만드는 데 사용한 이미지이다. |

    같은 이미지로 컨테이너가 두 번 생성된 것이며 중복 설치 오류는 아니다. ps는 실행 중인 것, ps -a는 종료된 것까지 보여준다는 차이를 정리했다.

### 문제 5-2 · Docker Hub 에서 이미지 이름 읽고 없는 이미지 받아 보기

- (가) `nginx:1.28` 에서 `nginx` 와 `1.28` 이 각각 무엇을 정하는지 적어 주세요.
  - 쓸 내용: ① nginx 가 정하는 것 ② 1.28 이 정하는 것
  - 답:

    nginx는 사용할 이미지 이름이고, 1.28은 버전 계열을 구분하는 태그이다. 콜론 뒤의 문자열 전체가 태그이다.

    Docker Hub의 nginx 페이지에 직접 접속해 1.28을 검색했는데, 1.28.3-trixie-perl·1.28.3-perl·1.28-trixie-perl처럼 여러 항목이 나와 무엇을 봐야 하는지 질문했다. 버전뿐 아니라 기반 환경과 추가 기능에 따라 구성이 나뉘며, 이번 수업에서는 뒤에 다른 단어가 붙지 않은 정확한 태그 1.28을 사용한다는 설명을 들었다.

    이후 TAG 1.28과 docker pull nginx:1.28이 표시된 화면을 찾아 첨부해 확인받았다. 아래의 linux/amd64 등은 실행 환경별 구분이며, nginx:1.28을 받을 때 도커가 맞는 환경의 이미지를 선택한다는 설명을 들었다. trixie는 컨테이너 내부 Debian 기반의 구분이고, perl은 Perl 관련 기능을 포함한 구성이지 내 윈도를 바꾸라는 뜻이 아니다.

- (나) 🔍 `docker pull nginxx` 를 쳤을 때 나온 오류 문구와 그 뜻을 적어 주세요.
  - 쓸 내용: ① 오류 문구 ② 뜻 ③ 고치는 방법
  - 답:

    문제에서 의도적으로 이름을 틀리게 입력하는 실습으로 다음 명령을 실행했다.

    ```bash
    docker pull nginxx
    ```

    내 실제 출력:

    ```text
    Using default tag: latest
    Error response from daemon: pull access denied for nginxx, repository does not exist or may require 'docker login'
    ```

    첫 줄은 태그를 생략해 latest를 사용한다는 안내이고 오류가 아니다. 다음 줄은 nginxx 이미지를 받을 수 없으며, 저장소가 없거나 접근 권한을 가진 계정의 로그인이 필요할 수 있다는 오류이다.

    이번에는 올바른 이름 nginx를 nginxx로 일부러 틀린 상황이므로, 먼저 이름을 고쳐 nginx:1.28처럼 정확한 이미지와 태그를 지정해야 한다. login이라는 단어가 있다고 무조건 로그인부터 하는 것이 아니라 이름·태그를 먼저 확인한다. 이 단계에서 정상 nginx 이미지를 따로 pull한 기록은 없고, 이후 6-1의 run에서 실제 다운로드를 확인했다.

- (한 줄) 보안 담당에게 보낼 답을 한 문장으로 적어 주세요.
  - 쓸 내용: 보안 담당이 바로 읽을 수 있는 한 문장(도커를 쓰면 무엇이 같아지는지)
  - 답:

    도커는 같은 이미지와 실행 설정으로 PC마다 발생하는 프로그램 환경 차이를 줄일 수 있으며, 이미지를 사용할 때 공식 저장소에서 이름과 태그를 확인해 정확히 지정해야 한다.

- 이 교시에서 새로 알게 된 것 하나를 적어 주세요.
  - 쓸 내용: 자유롭게
  - 답:

    설명만으로는 도커가 왜 필요한지 바로 이해되지 않아 설치 화면과 함께 도커가 무엇을 하는 프로그램인지 다시 질문했다. 도커 자체가 웹 서버인 것이 아니라, 준비된 이미지로 프로그램 실행 환경을 만들고 관리하는 도구라는 설명을 들었다. nginx는 그 안에서 실행할 웹 서버 프로그램이고, Docker Hub는 이미지를 받아오는 저장소이다.

    이미지를 직접 다운로드하지 않았는데 hello-world:latest가 생겨 질문했고, run이 로컬에 없는 이미지를 자동으로 받을 수 있다는 것을 배웠다. 이미지 한 개와 종료된 컨테이너 두 개가 함께 보인 실제 결과로 원본 바탕과 개별 실행 환경의 차이를 정리했다.

    이미지 이름 뒤에 붙는 여러 태그가 헷갈려 공식 페이지에서 정확한 1.28을 다시 찾았다. 이름은 어떤 이미지인지, 태그는 버전·구성 구분이라는 점을 설명받았다. 설치 버전 확인, 엔진 실행 상태 확인, 실제 컨테이너 실행 확인도 각각 다른 단계라는 점을 복습했다.

## 6교시 · nginx 서버 켜고 접속 기록 읽기

### 문제 6-1 · 포트 없이 켜 보고, 포트를 연결해 접속하고, 기록 읽기

- (가) 포트 없이 켠 `web` 에 접속했을 때 어떻게 되었는지 적어 주세요.
  - 쓸 내용: 접속했을 때 나온 화면이나 오류와 `docker ps` 의 PORTS 열
  - 답:

    처음 다음 명령으로 포트 공개 설정 없이 컨테이너를 실행했다.

    ```bash
    docker run -d --name web nginx:1.28
    ```

    이번에는 로컬에 이미지가 없다는 메시지와 Pull complete, Downloaded newer image가 실제로 출력되어 nginx:1.28 다운로드를 확인했다. 생성된 컨테이너의 상태는 다음과 같았다.

    ```text
    CONTAINER ID   IMAGE        COMMAND                   CREATED          STATUS          PORTS     NAMES
    adc16a9b8e2b   nginx:1.28   "/docker-entrypoint.…"   29 seconds ago   Up 28 seconds   80/tcp    web
    ```

    컨테이너는 Up이었지만 PORTS에는 80/tcp만 있고 내 PC 8080번의 전달 설정은 없었다. 따라서 이 구성에서는 127.0.0.1:8080을 통한 해당 nginx 접속 경로가 연결되지 않는다.

    공유한 화면은 이후 포트 연결에 성공한 Welcome to nginx! 화면이며, 포트 연결 전의 브라우저 오류 문구는 채팅에 남아 있지 않다. 직접 확인한 실행 상태·포트 설정과, 이 설정으로부터 설명받은 접속 불가 원리를 구분해 기록한다.

- (나) 🔍 `-p 8080:80` 이 하는 일을 내 PC의 포트와 컨테이너의 포트로 나눠 설명해 주세요.
  - 쓸 내용: ① 내 PC 쪽 포트 ② 컨테이너 쪽 포트 ③ 연결이 하는 일
  - 답:

    앞의 8080은 **내 PC에서 요청을 받는 포트**, 뒤의 80은 **컨테이너 안의 nginx가 요청을 받는 포트**이다. -p 8080:80은 내 PC의 8080번 요청을 컨테이너의 TCP 80번으로 전달하도록 연결한다.

    기존 web을 삭제하고 다음 명령으로 새로 만들었다.

    ```bash
    docker run -d --name web -p 8080:80 nginx:1.28
    ```

    직접 확인한 실행 목록:

    ```text
    CONTAINER ID   IMAGE        COMMAND                   CREATED          STATUS          PORTS                                     NAMES
    a8f6e1358fb4   nginx:1.28   "/docker-entrypoint.…"   49 seconds ago   Up 49 seconds   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   web
    ```

    브라우저에서 http://127.0.0.1:8080의 Welcome to nginx! 화면을 확인하고 첨부했다. 127.0.0.1은 내 PC 자신이고 주소의 8080은 접속할 내 PC 쪽 포트이다. PORTS의 0.0.0.0은 모든 IPv4 인터페이스, [::]는 모든 IPv6 인터페이스에 대한 대기 설정이며, 서버 두 개를 만든 뜻이 아니다.

- (다) 🔍 `docker logs web` 출력에서 `GET /` 줄 하나를 붙여 넣고, 접속자 주소 · 시각 · 요청 · 응답 번호를 찾아 적어 주세요.
  - 쓸 내용: ① `GET /` 줄 ② 접속자 주소 · 시각 · 요청 · 응답 번호 네 가지
  - 답:

    docker logs web에서 직접 확인한 성공 요청 한 줄은 다음과 같다.

    ```text
    172.17.0.1 - - [19/Oct/2026:06:21:24 +0000] "GET / HTTP/1.1" 200 615 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36" "-"
    ```

    | 항목 | 내 실제 값 | 설명 |
    |---|---|---|
    | 접속자 주소 | 172.17.0.1 | nginx가 관찰한 연결 상대 주소이다. 이번 실습에서는 도커 네트워크 전달 과정의 주소로 보일 수 있으며 외부 공격자의 주소라고 단정하지 않는다. |
    | 시각 | 19/Oct/2026:06:21:24 +0000 | UTC 시각이다. 한국 시간으로는 같은 날 15:21:24이며 첨부 화면의 시간대와 맞는다. |
    | 요청 | GET / HTTP/1.1 | HTTP/1.1로 기본 경로 /를 요청했다. |
    | 응답 번호 | 200 | 요청을 성공적으로 처리했다. |

    응답 번호 뒤의 615는 기본 로그 형식에서 응답 본문 크기인 바이트 수이다. 글자 수와 반드시 같지는 않다.

    같은 출력에 GET /favicon.ico의 404와 파일 없음 오류도 있었다. 브라우저가 탭 아이콘을 추가 요청했지만 그 파일이 없었던 것으로, 첫 화면 GET /의 200 성공과 구분해야 한다는 설명을 들었다. 시작 로그의 nginx/1.28.3은 사용한 1.28 태그 이미지에 들어 있는 실제 프로그램 버전이며, OS 줄에는 WSL2 실행 기반도 표시됐다.

### 문제 6-2 · 컨테이너 안을 들여다보고, 끄고, 지우기

- (가) 컨테이너 안에서 `ls /usr/share/nginx/html` 로 본 파일 이름을 모두 적고, 그중 브라우저의 첫 화면이 어느 파일인지 적어 주세요.
  - 쓸 내용: ① 파일 이름 모두 ② 첫 화면 파일
  - 답:

    컨테이너 안의 전체 파일 목록을 보여주는 ls 출력은 채팅에 기록되지 않았다. 첫 공유에서는 docker exec -it web sh로 들어간 다음 바로 exit했다. 따라서 파일 목록을 직접 확인했다고 꾸미지 않는다.

    안내문 기준으로 확인할 파일은 **50x.html과 index.html**이며, 기본 설정에서 Welcome to nginx! 첫 화면을 제공하는 파일은 **index.html**이다. 50x.html은 서버 오류 안내용 파일이다.

    컨테이너가 실행 중일 때 다음 순서로 목록을 확인하도록 안내받았다.

    ```bash
    docker exec -it web sh
    ```

    컨테이너 안에서:

    ```sh
    ls /usr/share/nginx/html
    exit
    ```

    이후 7-1에서는 index.html을 수정하고 cat으로 <h1>inside</h1>를 직접 확인한 출력이 있지만, 이것은 전체 ls 목록을 확인한 것과는 별개이다.

- (나) 🔍 `docker stop web` 뒤에 `docker ps` 와 `docker ps -a` 에 각각 `web` 이 보이나요? 차이를 설명해 주세요.
  - 쓸 내용: ① stop 뒤 ps 에 보이는지 ② ps -a 에 보이는지 ③ 차이의 이유
  - 답:

    stop 뒤 docker ps에서는 web이 보이지 않았고, docker ps -a에서는 Exited (0) 상태로 남아 있었다.

    내 실제 전체 목록 중 web 줄:

    ```text
    CONTAINER ID   IMAGE         COMMAND                   CREATED          STATUS                      PORTS     NAMES
    a8f6e1358fb4   nginx:1.28    "/docker-entrypoint.…"   4 minutes ago    Exited (0) 10 seconds ago             web
    ```

    docker ps는 실행 중인 것만 표시하고, docker ps -a는 종료된 컨테이너도 표시하기 때문이다. stop은 실행을 멈출 뿐 컨테이너를 삭제하지 않는다. 한편 exec로 연 셸에서 exit한 것은 셸을 종료한 것이며, nginx를 중지한 작업은 별도로 실행한 docker stop web이었다.

- (다) 🔍 같은 이름으로 다시 `run` 했을 때 나온 오류 문구와, `docker rm` 이 필요한 이유를 적어 주세요.
  - 쓸 내용: ① 오류 문구 ② rm 이 필요한 이유
  - 답:

    중지된 기존 web이 남아 있는 상태에서 같은 이름으로 run하자 다음 오류가 실제로 나왔다.

    ```text
    docker: Error response from daemon: Conflict. The container name "/web" is already in use by container "a8f6e1358fb4792e260f0f91e450b1bb1605ec1e3e482c882a879c33a56f1533". You have to remove (or rename) that container to be able to reuse that name.
    ```

    run은 새 컨테이너를 만드는 작업이므로, 중지됐더라도 기존 web이 그 이름을 사용하면 새 컨테이너에 같은 이름을 줄 수 없다. 이번처럼 같은 이름으로 새로 만들려면 기존 것을 삭제하거나 이름을 바꿔야 한다.

    나는 docker rm web으로 삭제하고 전체 목록에서 사라진 것을 확인했다. 그 뒤 stop과 rm을 다시 실행했더니 다음 오류가 나와 질문했다.

    ```text
    Error response from daemon: No such container: web
    ```

    이미 삭제해 대상이 없다는 뜻이었다. 이후 run으로 새 web을 만들었고, ID fcd8bf792ecf가 Up이며 8080->80/tcp로 연결된 것을 직접 확인했다. Conflict는 이미 존재해서, No such container는 존재하지 않아서 발생한 서로 다른 상황이다.

- (한 줄) 보안 담당에게 보낼 답을 한 문장으로 적어 주세요.
  - 쓸 내용: 보안 담당이 바로 읽을 수 있는 한 문장(켜는 명령 · 기록 보는 명령 · 정리 방법)
  - 답:

    nginx는 docker run -d --name web -p 8080:80 nginx:1.28로 실행하고 docker logs web으로 기록을 확인하며, 중지한 기존 컨테이너를 삭제한 뒤 같은 이름으로 새로 생성할 수 있다.

- 이 교시에서 새로 알게 된 것 하나를 적어 주세요.
  - 쓸 내용: 자유롭게
  - 답:

    서버 실행과 브라우저 연결은 별개여서 Up뿐 아니라 PORTS도 확인해야 한다는 설명을 들었다. 실제로 포트 설정이 없는 80/tcp 상태와 8080->80/tcp로 연결한 상태를 비교했고, 연결 후 Welcome to nginx! 화면과 GET /의 200 로그를 확인했다.

    exec로 연 셸에서 나오는 exit, 컨테이너를 멈추는 stop, 삭제하는 rm의 차이도 배웠다. 이름 충돌 뒤 삭제하고 나서는 No such container가 나와 이유를 질문했고, 이미 없어진 대상을 다시 찾았기 때문임을 설명받았다.

    run 뒤 출력된 긴 문자열이 무엇인지 별도로 질문했다. fcd8bf792ecf0e1a96d0ff9ce34d45b35a2a9541015e1b96622a0409bc560245는 컨테이너 ID이며, 목록에서는 앞 12자리로 짧게 보인다는 것을 배웠다. 이름 web과 ID는 같은 컨테이너를 가리키는 서로 다른 식별 방식이고, -d로 백그라운드 실행할 때 ID를 출력한 뒤 터미널이 돌아온다는 설명을 들었다.

## 7교시 · 내 페이지 연결 · 두 서버 · 올리기

### 문제 7-1 · 컨테이너 안의 변경이 사라지는 것을 보고, 내 폴더를 연결하기

- (가) 컨테이너 안에서 바꾼 뒤 `docker rm -f web` 으로 지우고 다시 켰을 때 화면이 어떻게 되었는지 적어 주세요.
  - 쓸 내용: ① 바꾼 뒤 화면 ② 지우고 다시 켠 뒤 화면
  - 답:

    **직접 확인한 파일 변경과 재생성:** 실행 중인 web의 셸에서 아래 명령을 입력했고, cat 출력으로 변경 내용을 확인했다.

    ```sh
    echo '<h1>inside</h1>' > /usr/share/nginx/html/index.html
    cat /usr/share/nginx/html/index.html
    ```

    내 실제 출력:

    ```html
    <h1>inside</h1>
    ```

    이후 해당 web을 삭제하고 같은 nginx:1.28로 새 컨테이너를 만들었다. 새 ID는 0f17a8b14f69beff774cb0c1c47b85aecab172949d607225434f64dab49e225b였다.

    **화면 비교의 원리:** 기본 Welcome to nginx!에서 내부 파일 수정 후 inside로 바뀌고, 삭제·재생성하면 기본 Welcome to nginx!로 돌아오는 과정을 확인하는 문제라는 설명을 들었다. 6-1의 기본 화면은 실제 첨부로 확인됐지만, 7-1의 수정 직후·재생성 직후 브라우저 화면 내용은 채팅에 별도로 기록되지 않았다. 파일 수정·삭제·재생성은 실제 실행 기록으로 남기고, 두 화면을 직접 제시한 것처럼 쓰지는 않는다.

    실습 초반에는 기존 web이 있어 run에서 이름 충돌이 났다. 이어 start 명령 끝에 역슬래시를 붙여 다음 줄 exit가 이어지면서 webexit라는 이름을 찾는 오류도 났다. docker start web을 다시 정확히 입력하자 기존 컨테이너가 시작됐다. 명령 뒤에 불필요한 줄 연결 문자를 붙이지 않아야 한다는 설명을 들었다.

- (나) 🔍 컨테이너 안에서 바꾼 내용이 사라진 이유와, `-v` 로 폴더를 연결하면 무엇이 달라지는지 적어 주세요.
  - 쓸 내용: ① 사라진 이유 ② -v 로 연결하면 달라지는 점
  - 답:

    컨테이너 안에서 직접 수정한 파일은 해당 컨테이너의 변경으로 저장되고 원본 이미지에는 반영되지 않는다. 삭제 후 새 컨테이너를 만들면 원본 이미지의 파일에서 시작하므로 이전 컨테이너의 변경은 이어지지 않는다. 같은 컨테이너의 stop/start와 삭제 후 run은 다르다.

    이번에는 내 PC의 day06_docker/site-one/index.html을 vim으로 작성하고, 다음 연결을 사용했다.

    ```text
    -v "$(pwd)/site-one:/usr/share/nginx/html:ro"
    ```

    $(pwd)/site-one은 현재 작업 위치 아래의 내 PC 폴더이고, /usr/share/nginx/html은 컨테이너에서 파일을 읽을 위치이다. 이 방식은 파일을 한 번 복사하는 것이 아니라 내 PC의 폴더를 컨테이너 경로에 연결하는 바인드 마운트이다. 원본은 내 PC에서 관리하므로 컨테이너 삭제로 함께 삭제되지 않고 새 컨테이너에 다시 연결할 수 있다.

    ro는 읽기 전용이다. 컨테이너는 그 연결을 통해 파일을 읽기만 하고, 나는 PC의 편집기에서 원본을 수정할 수 있다. 서버가 켜져 있는지와 내 파일이 실제로 보이는지는 따로 확인해야 한다는 안내를 받았다.

- (다) 🔍 `MSYS_NO_PATHCONV=1` 없이 `-v` 를 실행했을 때 화면에 무엇이 나왔고 왜 그랬는지 적어 주세요.
  - 쓸 내용: ① 화면에 나온 것 ② 그렇게 된 이유
  - 답:

    **이번 실제 오류와 경로 변환 원리를 구분해 기록한다.** 처음 -v 명령에서는 기존 web이 8080번을 사용하고 있어 다음 오류가 실제로 발생했다.

    ```text
    Bind for 0.0.0.0:8080 failed: port is already allocated
    ```

    이 오류는 경로 변환이 아니라 포트 충돌이었다. 기존 web과 실행에 실패한 web-one을 삭제한 뒤 다시 실행했다. 이후 확인한 결과는 다음과 같다.

    | 구분 | 컨테이너 ID | 실제 확인 내용 |
    |---|---|---|
    | MSYS_NO_PATHCONV=1 없이 재실행 | e35d1c4cd5cb | Up 14 seconds, 8080->80/tcp |
    | 위 컨테이너 삭제 후 설정을 붙여 새로 실행 | 0709ac43ef69 | Up 6 seconds, 8080->80/tcp |

    설명받은 원리는 Git Bash가 컨테이너 쪽 경로를 윈도 경로로 변환할 수 있어, 자료의 사례처럼 서버는 켜져도 내 페이지 대신 기본 화면이 보일 수 있다는 것이다. MSYS_NO_PATHCONV=1은 그 명령 한 번의 자동 경로 변환을 막는다.

    내가 끝까지 진행한 터미널 출력은 공유했지만 설정 전후 브라우저 문구는 별도 공유되지 않았다. 따라서 ‘설정 전에는 기본 화면, 설정 후에는 내 페이지가 보였다’를 실제 화면 기록으로 확정하지는 않는다. 최종적으로 내가 작성한 페이지가 보이는지 확인하는 것이 폴더 연결 검증이다.

    또 실패한 run에서도 ID가 먼저 출력된 뒤 오류가 나왔으므로, 긴 ID 출력만으로 성공을 확정하지 않고 뒤의 메시지와 ps 상태를 확인해야 한다는 설명을 들었다.

### 문제 7-2 · 서버 두 대를 띄워 포트로 구분하고, 파일을 고쳐 바로 반영되는지 보기

- (가) 두 주소(`8080` · `8081`)에서 보이는 화면을 각각 적어 주세요.
  - 쓸 내용: 두 주소의 화면 문구
  - 답:

    구성상 8080은 web-one에 연결된 site-one/index.html을, 8081은 web-two에 연결된 site-two/index.html을 보여주도록 했다. site-two/index.html도 vim으로 작성한 명령 기록이 있다.

    안내문 기본 문구 기준의 화면 구분은 다음과 같다. 아래 문구는 구성과 작성 안내에 따른 확인 기준이며, 내가 공유한 브라우저 화면의 전사 기록은 아니다.

    | 주소 | 연결 대상 | 안내문 기준 문구 |
    |---|---|---|
    | http://127.0.0.1:8080 | web-one / site-one/index.html | site-one · 첫 번째 서버입니다 |
    | http://127.0.0.1:8081 | web-two / site-two/index.html | site-two · 두 번째 서버입니다 |

    두 서버의 동시 실행과 포트는 실제 ps 출력으로 확인했다. 다만 두 주소의 실제 표시 문구, site-one의 문구 수정, 수정 뒤 8080만 바뀌고 8081은 유지된 결과는 채팅에 제시되지 않았다. 이 부분을 수행·확인한 결과처럼 임의로 채우지 않고 별도 확인 대상으로 남긴다.

- (나) 🔍 `docker ps` 의 PORTS 열에서 두 서버를 구분해 주는 것은 무엇인가요?
  - 쓸 내용: PORTS 열에서 서버를 구분하는 값
  - 답:

    **내 PC 쪽 포트 번호 8080과 8081**이 두 서버를 구분한다. 실제 실행 목록은 다음과 같다.

    ```text
    CONTAINER ID   IMAGE        COMMAND                   CREATED          STATUS          PORTS                                     NAMES
    d8bc7f24c8d9   nginx:1.28   "/docker-entrypoint.…"   23 seconds ago   Up 22 seconds   0.0.0.0:8081->80/tcp, [::]:8081->80/tcp   web-two
    0709ac43ef69   nginx:1.28   "/docker-entrypoint.…"   5 minutes ago    Up 4 minutes    0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   web-one
    ```

    이미지는 둘 다 nginx:1.28이고 컨테이너 쪽 포트는 둘 다 80이지만, web-one은 내 PC의 8080, web-two는 8081로 연결했다. 각 컨테이너의 네트워크 환경이 나뉘어 있으므로 내부 80번은 같아도 된다. 이번 구성에서는 같은 PC 주소의 포트를 달리하여 접속 대상을 구분한다.

- (다) 🔍 `:ro` 는 무슨 뜻이고, 왜 읽기 전용으로 연결하나요?
  - 쓸 내용: ① :ro 의 뜻 ② 읽기 전용으로 연결하는 이유
  - 답:

    ro는 **read-only, 읽기 전용**이다. 연결된 폴더를 컨테이너가 읽을 수는 있지만 그 연결을 통해 수정하거나 삭제하지 못하도록 제한한다.

    nginx가 페이지를 보여주기 위해서는 파일 읽기가 필요하며 원본을 수정하는 권한까지 필요하지 않다. 따라서 오전의 최소권한과 연결되는 설정이다. 내가 PC에서 vim이나 VS Code로 원본을 고치는 것은 가능하다. 이 옵션은 연결한 폴더에 대한 쓰기를 제한하는 것이며, 컨테이너 전체의 모든 보안 문제를 해결하는 설정이라고 확대해서 이해하지 않는다.

- (한 줄) 보안 담당에게 보낼 답을 한 문장으로 적어 주세요.
  - 쓸 내용: 보안 담당이 바로 읽을 수 있는 한 문장(두 서버를 어떻게 띄웠는지)
  - 답:

    같은 nginx:1.28 이미지로 컨테이너 두 개를 만들고 각각 내 PC의 페이지 폴더를 읽기 전용으로 연결했으며, 8080·8081 포트로 구분해 실행한 뒤 두 컨테이너를 정리했다.

- 이 교시에서 새로 알게 된 것 하나를 적어 주세요.
  - 쓸 내용: 자유롭게
  - 답:

    이미지 한 개로 여러 컨테이너를 만들고, 각각 다른 폴더와 내 PC 쪽 포트를 연결할 수 있다는 설명을 들었다. 실제로 web-one과 web-two가 같은 nginx:1.28을 사용하면서 8080과 8081로 나뉘어 동시에 Up인 것을 확인했다.

    마지막에는 docker rm -f web-one web-two를 실행했고 두 이름이 출력됐다. 이어 ps -a에서 web-one·web-two가 사라지고 기존 hello-world 두 개만 남은 것을 확인했다. 원본 파일은 내 PC에서 별도로 관리하고, 컨테이너는 다시 만들 수 있도록 나누는 이유를 정리했다.

    7-1에서 포트 충돌로 막혔을 때 기존 web이 8080을 쓰고 있다는 설명을 듣고 정리한 뒤 재실행했다. 복사한 명령을 실행하는 것에 더해 현재 컨테이너 이름, 상태, 포트, 연결 폴더를 함께 읽는 방법을 복습 항목으로 정리했다. 단순 HTML 파일은 연결된 원본을 수정하고 새 요청을 보내면 변경 내용을 제공할 수 있다는 원리를 배웠으며, 이번 채팅에 없는 실제 화면 변화와 파일 목록은 별도로 확인해 보완할 부분이다.

### 문제 7-3 · 오늘 만든 것을 깃허브에 올리기

- (가) `git status` 를 쳤을 때 빨간 목록에 줄이 몇 개였는지, 그 가운데 `.env` · `.venv` 가 있었는지 적어 주세요.
  - 쓸 내용: ① 줄 수 ② .env · .venv 가 있었는지
  - 답:

    **① Untracked files 아래 파일·폴더 항목은 17줄이었다. ② 그 목록에 .env와 .venv/는 보이지 않았다.**

    day06_docker 위치에서 cd ../..로 이동한 다음 pwd로 저장소 맨 위인 /c/Users/User/Documents/Aleph_Choi/security-agent-toolkit을 확인했다. 그 위치에서 실행한 git status의 실제 목록은 다음과 같다.

    ```text
    docs/day04_morning_vscode_setup.md
    docs/day05_morning_vim.md
    network_zt/day04_5-2_http_80_81.pcapng
    network_zt/day04_6-1_portquiz_443_445_3389.pcapng
    network_zt/day04_am_vpn.md
    network_zt/day04_pm_firewall.md
    network_zt/day05_am_cloud_diagram.md
    network_zt/day05_pm_quality.md
    network_zt/day06_3-1_decide_admin.py
    network_zt/day06_3-2_batch_decide.py
    network_zt/day06_4-1_zt_score.py
    network_zt/day06_am_report.md
    network_zt/day06_am_zero_trust.md
    network_zt/day06_docker/
    network_zt/day06_pm_docker_basics.md
    network_zt/day06_pm_report.md
    network_zt/day06_zt_scenario.md
    ```

    On branch나 Untracked files 같은 제목·안내 문장은 제외하고, 그 아래 표시된 파일·폴더 항목만 세었다.

    17줄 중 이전 Day 4·5 자료가 8줄이고 오늘 Day 6 자료가 9줄이다. day06_docker/는 폴더 안의 개별 파일 수와 관계없이 이 출력에서 한 줄로 센다. 따라서 17은 오늘 만든 개별 파일의 총수가 아니라, 이번 git status에 표시된 미추적 파일·폴더 항목 수이다.

    이로써 7-3 (가)의 목록 줄 수와 .env·.venv/ 표시 여부는 실제 출력으로 확인했다. 다만 nothing added to commit but untracked files present라고 나왔으므로 현재는 add·commit·push 전이다. 수정 보고서를 저장한 뒤 업로드할 변경을 선택하고 기록·전송한 다음 GitHub에서 확인할 예정이다.

