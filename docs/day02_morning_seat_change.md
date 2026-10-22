# 아침 과제 16 · 새 자리에서 내 깃허브 연결하기 — 앞 사람 흔적 확인 · 내 폴더 받기

10월 22일 (목) · 아침 과제

**오늘 하는 일:** 어제 자리를 바꿨습니다. 지금 앉은 PC 에는 **앞 사람의 폴더와 깃허브 로그인**이 남아 있을 수 있습니다. 그대로 쓰면 내 코드가 **앞 사람 이름 · 앞 사람 계정**으로 올라갑니다. 오늘 아침에는 앞 사람 흔적을 확인해 끊고, 어제 올려 둔 **내 폴더를 깃허브에서 받아** 내 것이 맞는지 확인합니다.

**끝나면 이렇게 됩니다**
- `문서(Documents)` 안에 앞 사람 폴더는 `security-agent-toolkit_old`, 내 폴더는 `security-agent-toolkit`
- 이 PC 에서 push 하면 **내 이름 · 내 계정**으로 올라감
- 깃허브 내 저장소에 오늘 만든 확인 파일이 보임
- 앞 사람이 켜 둔 도커 컨테이너가 없어 포트가 비어 있음

---

## 1. 터미널을 엽니다

1. **[VS Code]** 위 메뉴 **Terminal › New Terminal** 을 누릅니다.
2. **[터미널]** 오른쪽 위 목록에 **bash** 가 보이는지 확인합니다. 아니면 `+` 옆 화살표에서 **Git Bash** 를 고릅니다.
3. **[터미널]** 문서 폴더로 갑니다.
   ```bash
   cd ~/Documents
   pwd
   ```
   - 명령 풀이: `cd ~/Documents` 내 문서 폴더로 이동 · `pwd` 지금 위치를 보여 줌
   - `…/Documents` 로 끝나면 됩니다.

---

## 2. 앞 사람의 흔적을 확인합니다

**왜 하나요** — 무엇이 남아 있는지 알아야 무엇을 끊을지 정할 수 있습니다.

1. **[터미널]** 문서 폴더에 무엇이 있는지 봅니다.
   ```bash
   ls
   ```
   - `security-agent-toolkit` 이 **보이면** → 2번으로
   - 그 이름은 없지만 앞 사람이 **다른 이름으로 만든 폴더**처럼 보이는 것(예: `toolkit`, `my-security`)이 있으면 → 그 폴더 이름으로 2번을 합니다
   - **둘 다 없으면** → 4장으로 건너뜁니다(이름 바꿀 폴더가 없음)

2. **[터미널]** 그 폴더가 **누구 저장소**인지 봅니다.
   ```bash
   cd security-agent-toolkit
   git remote -v
   cd ..
   ```
   - 명령 풀이: `git remote -v` 이 폴더가 연결된 깃허브 저장소 주소를 보여 줌 · `cd ..` 한 단계 위(문서 폴더)로 돌아감
   - 이렇게 나옵니다(예시).
     ```
     origin  https://github.com/앞사람아이디/security-agent-toolkit.git (fetch)
     origin  https://github.com/앞사람아이디/security-agent-toolkit.git (push)
     ```
   - `github.com/` 바로 뒤가 **그 저장소 주인의 깃허브 아이디**입니다. 내 아이디가 아니면 앞 사람 폴더입니다.
   - 폴더 이름이 다르면 `cd` 뒤에 그 이름을 씁니다(예: `cd toolkit`).

3. **[터미널]** 이 PC 에 적힌 **git 이름 · 이메일**을 봅니다.
   ```bash
   git config --global user.name
   git config --global user.email
   ```
   - 앞 사람 이름이 나오면, 이대로 커밋할 때 **앞 사람 이름이 찍힙니다.**
   - 아무것도 안 나오면 비어 있는 것입니다.

4. **[Windows]** 이 PC 에 저장된 **깃허브 로그인**을 봅니다.
   1. 시작 메뉴에서 **자격 증명 관리자** 를 검색해 엽니다.
   2. **Windows 자격 증명** 을 누릅니다.
   3. 목록에 **`git:https://github.com`** 이 있는지 봅니다. 펼치면 **사용자 이름**에 로그인한 깃허브 아이디가 보입니다.
   - 이 항목이 있으면, 이 PC 에서 `git push` 할 때 **그 아이디로** 올리려고 합니다.

---

## 3. 앞 사람 연결을 끊고 내 것으로 바꿉니다

**왜 하나요** — 커밋에 찍히는 이름과 push 할 때 쓰는 로그인이 모두 이 PC 에 남아 있습니다. 둘 다 내 것으로 바꿔야 내 저장소에 내 이름으로 올라갑니다.

1. **[Windows]** 2장 4번의 **`git:https://github.com`** 항목을 펼쳐 **제거** → **예** 를 누릅니다.
   - 항목이 없었으면 건너뜁니다.
   - 다음에 push 할 때 로그인 창이 다시 뜨고, 그때 **내 계정**으로 로그인합니다(6장).

2. **[터미널]** git 이름 · 이메일을 **내 것**으로 적습니다. 따옴표 안만 바꿉니다.
   ```bash
   git config --global user.name "내 이름"
   git config --global user.email "깃허브에 가입한 이메일"
   ```
   - 확인합니다. 방금 적은 값이 나오면 됩니다.
     ```bash
     git config --global user.name
     git config --global user.email
     ```

---

## 4. 앞 사람 폴더 이름 끝에 `_old` 를 붙입니다

**왜 하나요** — 내 폴더도 이름이 `security-agent-toolkit` 이라 같은 자리에 받을 수 없습니다. 앞 사람 폴더는 **지우지 않고** 이름만 바꿔 둡니다.

2장 1번에서 폴더가 **없었으면** 이 장은 건너뜁니다.

1. **[VS Code]** 그 폴더가 VS Code 에 열려 있으면 먼저 **File › Close Folder** 로 닫습니다. 열려 있으면 이름이 안 바뀔 수 있습니다. 닫은 뒤 1장처럼 터미널을 다시 열고 `cd ~/Documents` 합니다.
2. **[터미널]** 이름을 바꿉니다.
   ```bash
   mv security-agent-toolkit security-agent-toolkit_old
   ls
   ```
   - 명령 풀이: `mv 지금이름 새이름` 폴더 이름을 바꿈
   - `ls` 에 `security-agent-toolkit_old` 가 보이고 `security-agent-toolkit` 은 없어야 합니다.
   - 앞 사람 폴더 이름이 **다르면** 그 이름 끝에 `_old` 를 붙입니다(예: `mv toolkit toolkit_old`). 내 것과 헷갈리지 않게 표시해 두는 것입니다.

---

## 5. 내 폴더를 깃허브에서 받습니다

**왜 하나요** — 어제 마지막에 내 파일을 모두 깃허브에 올렸습니다. 이 PC 에는 내 폴더가 없으니 **처음 받는 것**이라 `git pull` 이 아니라 **`git clone`** 을 씁니다. `pull` 은 이미 받은 폴더를 최신으로 맞출 때 씁니다.

1. **[브라우저]** github.com 에 **내 계정**으로 들어가 **내 저장소**를 엽니다.
   - 저장소 이름이 `security-agent-toolkit` 이 **아닐 수도** 있습니다. 내가 처음 만들 때 다른 이름을 붙였다면 그 이름입니다.
   - 이름이 기억나지 않으면: 오른쪽 위 **내 프로필 사진** → **Your repositories** → 목록에서 하나씩 열어, 안에 `agent_core` · `network_zt` · `access_control` 폴더가 있는 저장소를 찾습니다. 그것이 내 저장소입니다.
   - 찾은 저장소 이름을 적어 둡니다(예: `my-toolkit`).
2. **[브라우저]** 초록색 **Code** 단추 → **HTTPS** → 주소 오른쪽 **복사** 아이콘을 누릅니다.
3. **[터미널]** 문서 폴더에서 받습니다. `git clone ` 뒤에 복사한 주소를 붙여 넣습니다(Git Bash 붙여 넣기 = **Shift + Insert** 또는 마우스 오른쪽 클릭).
   ```bash
   git clone https://github.com/내아이디/security-agent-toolkit.git
   ```
   - 명령 풀이: `git clone 주소` 깃허브 저장소를 내 PC 에 폴더째 받음
   - `Cloning into 'security-agent-toolkit'...` 다음에 `done.` 이 나오면 됩니다.
   - 저장소가 비공개면 여기서 로그인 창이 뜹니다. **내 계정**으로 로그인합니다.
   - **저장소 이름이 다르면** 주소 끝이 그 이름입니다(예: `…/내아이디/my-toolkit.git`). 이때는 주소 뒤에 한 칸 띄우고 `security-agent-toolkit` 을 붙여 받습니다. 그러면 내 PC 의 폴더 이름이 수업 문서와 같은 `security-agent-toolkit` 이 됩니다.
     ```bash
     git clone https://github.com/내아이디/my-toolkit.git security-agent-toolkit
     ```
     - 명령 풀이: `git clone 주소 폴더이름` 받은 저장소를 내가 정한 폴더 이름으로 만듦. 깃허브의 저장소 이름은 바뀌지 않습니다.
     - `Cloning into 'security-agent-toolkit'...` 가 나오면 됩니다. 폴더 이름을 붙이지 않으면 `Cloning into 'my-toolkit'...` 처럼 저장소 이름 그대로 폴더가 생깁니다.

4. **[VS Code]** **File › Open Folder** → `문서(Documents)` → **`security-agent-toolkit`**(뒤에 `_old` 가 **없는** 것)을 엽니다.

---

## 6. 받은 폴더가 내 것인지 확인합니다

**왜 하나요** — 이름이 같은 폴더가 두 개 있으니, 지금 연 것이 **내 저장소의 어제 마지막 상태**인지 눈으로 확인합니다.

1. **[터미널]** VS Code 에서 터미널을 새로 엽니다(1장 1~2번). 위치가 `…/security-agent-toolkit` 인지 봅니다.
   ```bash
   pwd
   ```
2. **[터미널]** 세 가지를 확인합니다.
   ```bash
   git remote -v
   git log --oneline -3
   ls
   ```
   | 명령 | 이렇게 나오면 됩니다 |
   |---|---|
   | `git remote -v` | 주소의 `github.com/` 뒤가 **내 아이디** |
   | `git log --oneline -3` | 맨 위 줄이 어제 마지막 커밋 **`Save all files before seat change`** |
   | `ls` | `agent_core` · `network_zt` · `access_control` 폴더가 보임 |
   - 명령 풀이: `git log --oneline -3` 최근 커밋 3개를 한 줄씩 보여 줌
3. **[브라우저]** 깃허브 내 저장소 화면의 폴더 목록과 VS Code 왼쪽 목록이 같은지 봅니다.

---

## 7. 내 계정으로 올라가는지 확인합니다

**왜 하나요** — 3장에서 로그인을 지웠으니, 처음 push 할 때 **내 계정**으로 로그인해야 합니다. 작은 파일 하나를 올려 확인합니다.

1. **[터미널]** 확인용 파일을 만듭니다.
   ```bash
   mkdir -p docs
   vim docs/2026-10-22_seat.md
   ```
   - `i` 를 누르고 `새 자리 준비 완료` 한 줄을 씁니다 → `Esc` → `:wq` → Enter
   - 명령 풀이: `mkdir -p docs` docs 폴더가 없으면 만들고, 있으면 그냥 넘어감
2. **[터미널]** 올립니다.
   ```bash
   git status
   git add .
   git commit -m "Check new seat setup"
   git push
   ```
   - `git status` 의 빨간 목록에 `.env` 가 보이면 멈추고 `.gitignore` 에 `.env` 한 줄이 있는지 확인합니다.
   - `git push` 때 **로그인 창**이 뜨면 **Sign in with your browser** → 브라우저에서 **내 계정**으로 로그인 → **Authorize** 를 누릅니다.
3. **[브라우저]** 내 저장소에서 `docs/2026-10-22_seat.md` 가 보이는지, 그 파일의 커밋 옆 이름이 **내 아이디**인지 확인합니다.

---

## 8. 앞 사람이 켜 둔 도커 컨테이너를 확인하고 지웁니다

**왜 하나요** — 앞 사람이 켜 둔 컨테이너가 있으면 그 컨테이너가 **포트(8081 · 8082 같은 번호)를 차지**하고 있어서, 나중에 내가 같은 포트로 서버를 켤 때 막힙니다. 이 PC 의 컨테이너는 앞 사람 것이니 지워도 됩니다. 내가 어제까지 쓴 컨테이너도 명령으로 언제든 다시 만들 수 있습니다.

1. **[Windows]** 시작 메뉴에서 **Docker Desktop** 을 켭니다. 왼쪽 아래가 초록색(**Engine running**)이 될 때까지 1분쯤 기다립니다.
   - Docker Desktop 이 이 PC 에 **없으면** 이 장은 건너뜁니다. 지울 컨테이너도 없습니다.

2. **[터미널]** 켜져 있는(**Up**) 컨테이너를 봅니다.
   ```bash
   docker ps
   ```
   - 명령 풀이: `docker ps` 지금 켜져 있는 컨테이너 목록을 보여 줌
   - 이렇게 나오면 켜진 것이 있습니다(예시, 실제 줄은 더 깁니다).
     ```
     CONTAINER ID   IMAGE          ...   STATUS         PORTS                    NAMES
     43d353c583cc   nginx:alpine   ...   Up 42 hours    0.0.0.0:8081->80/tcp     closed-web-8081
     ```
   - `STATUS` 칸이 **Up** 으로 시작하면 켜져 있는 것입니다. 맨 오른쪽 **NAMES** 칸이 컨테이너 이름입니다.
   - 첫 줄(제목 줄)만 나오고 아래가 비어 있으면 켜진 것이 없습니다.

3. **[터미널]** 꺼진 것까지 **모두** 봅니다.
   ```bash
   docker ps -a
   ```
   - 명령 풀이: `-a` 는 all(올), 꺼진(**Exited**) 컨테이너까지 보여 줌
   - `STATUS` 가 `Exited (…)` 인 줄은 꺼져 있지만 아직 남아 있는 것입니다. 이것도 이름을 차지하고 있어서 같이 지웁니다.

4. **[터미널]** **NAMES** 칸의 이름을 띄어 써서 한 번에 지웁니다. 이름은 내 화면에 나온 것을 그대로 씁니다.
   ```bash
   docker rm -f closed-web-8081 open-web-8082
   ```
   - 명령 풀이: `docker rm` 컨테이너를 지움 · `-f` 는 force(포스), 켜져 있어도 먼저 끄고 지움
   - 지운 이름이 한 줄씩 다시 나오면 됩니다.
     ```
     closed-web-8081
     open-web-8082
     ```
   - 이름 대신 **CONTAINER ID** 앞 몇 글자(예: `43d3`)를 써도 됩니다.

5. **[터미널]** 다 지워졌는지 확인합니다.
   ```bash
   docker ps -a
   ```
   - 제목 줄 한 줄만 나오면 끝입니다.

- 이미지(nginx 같은 원본)는 지우지 않아도 됩니다. 컨테이너만 지우면 포트와 이름이 비워집니다.
- 화면에 `error during connect` 나 `Cannot connect to the Docker daemon` 이 나오면 Docker Desktop 이 아직 안 켜진 것입니다. 1번처럼 켜고 초록색이 될 때까지 기다린 뒤 다시 칩니다.

---

## 막히면

| 화면에 나온 것 | 뜻 | 할 일 |
|---|---|---|
| `fatal: destination path 'security-agent-toolkit' already exists and is not an empty directory.` | 같은 이름 폴더가 아직 있음 | 4장(`_old` 로 이름 바꾸기)을 먼저 합니다 |
| `mv` 뒤에 `Permission denied` 또는 `Device or resource busy` | 그 폴더가 어딘가에 열려 있음 | VS Code 에서 **File › Close Folder**, 파일 탐색기 창도 닫고 다시 `mv` |
| `git push` 에 `Permission … denied to 앞사람아이디` | 앞 사람 로그인이 아직 남아 있음 | 3장 1번(자격 증명 제거)을 하고 다시 `git push` |
| 깃허브 커밋 옆 이름이 앞 사람 | git 이름 · 이메일이 앞 사람 것 | 3장 2번을 하고, 다음 커밋부터 내 이름으로 찍힘 |
| `git log` 맨 위에 어제 커밋이 없음 | 어제 push 가 안 됐거나 다른 저장소를 받음 | 6장 `git remote -v` 주소가 내 아이디인지, 브라우저 저장소에 어제 파일이 있는지 봅니다 |

---

## 다 했으면 확인

- [ ] `문서` 에 `security-agent-toolkit_old`(앞 사람)와 `security-agent-toolkit`(내 것)이 따로 있다 (앞 사람 폴더가 없었으면 내 것만)
- [ ] `git config --global user.name` 이 내 이름이다
- [ ] `git remote -v` 주소에 내 아이디가 있다
- [ ] `git log --oneline -3` 맨 위가 어제 커밋이다
- [ ] 깃허브 내 저장소에 `docs/2026-10-22_seat.md` 가 내 아이디로 올라가 있다
- [ ] `docker ps -a` 에 제목 줄만 나온다 (Docker Desktop 이 없으면 건너뜀)
