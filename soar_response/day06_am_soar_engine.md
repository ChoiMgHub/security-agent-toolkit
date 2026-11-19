# 11/16(월) 오전 · 5과목 자동 대응(SOAR) ⑩ — 통합 엔진(orchestration engine) `soar_engine.py`: 승인 게이트를 거친 조치 실행과 오류 격리(failure isolation) · 4과목 탐지 결과의 종단간(end-to-end) 연결 · 정책 준수 점검과 최종 회고

<mark style="background:#e0d4ff">지난주에는 플레이북 찾기(월) · 계정 잠금과 IP 차단(수) · 티켓(목) · 승인 게이트(금)</mark>를 단계마다 따로 구현했습니다. 오늘 오전에는 <mark>**이 모듈들을 하나의 엔진으로 연결해 알림 한 건을 처음부터 끝까지 처리하고, 4과목의 탐지 결과를 입력으로 받아 실행하고, 엔진이 정책을 지켰는지 로그로 점검하는 부분**</mark>을 구현합니다. 통합 엔진(orchestration engine, 오케스트레이션 엔진: 여러 모듈을 정해진 순서로 호출해 하나의 흐름으로 실행하는 프로그램)은 SOAR(Security Orchestration, Automation and Response, 쏘아: 보안 오케스트레이션 · 자동화 · 대응) 제품의 핵심 부분입니다.

- **2교시**: 알림 한 건을 <mark>플레이북 찾기 → 승인 게이트 → 조치 실행 → 티켓</mark> 순서로 처리하는 엔진을 만듭니다. 알림 하나에서 오류가 나도 그 알림만 실패(failure)로 기록하고 나머지 알림을 계속 처리합니다(`soar_engine.py`).
- **3교시**: 4과목이 저장한 탐지 결과 `day03_risk_scores.json` 을 엔진이 읽는 알림으로 바꾸고, 파일 모양을 엔진 앞에서 점검합니다. 엔진 실행 결과는 운영 요약(operations summary: 처리 결과별 알림 수 · 티켓 수 · 실제로 실행한 조치를 한 번에 보여 주는 요약)으로 정리합니다(`engine_input.py`). 종단간(end-to-end: 처음 입력부터 마지막 결과까지 중간에 끊기지 않고 한 흐름으로 이어지는 것) 연결입니다.
- **4교시**: 엔진이 남긴 로그로 <mark>정책 준수 점검</mark>(policy compliance check: 승인 게이트와 허용 목록 같은 통제가 실제로 지켜졌는지 확인하는 일)을 하고, 5일간의 회고 문서 `day05_final_retrospective.md` 를 쓴 뒤 깃허브에 올립니다(`policy_check.py`).

새 문법은 2교시의 `except Exception as error` 하나입니다. 이 수업에서는 판다스를 쓰지 않습니다. 보고서의 🔍 질문은 <mark>내 출력 값을 근거로 이유까지</mark> 씁니다. 들여쓰기(줄 앞의 빈칸)는 각 번호 주석과 같은 위치에서 시작합니다. 각 번호 주석 바로 아래에 직접 쓰고(3교시 4번만 딕셔너리라서 여러 줄), 주석은 지우지 않습니다.

📎 **이전 파일**: 오늘 가져와 사용(import)하는 이전 파일은 아래 표와 같습니다. 없는 파일은 시작하기 뒤의 「🛟 이전 파일이 없을 때」 코드 상자로 만듭니다.

| 파일 | 만든 날 | 가져다 쓰는 것 | 쓰는 교시 |
|---|---|---|---|
| `incident.py` | 월요일 | `load_json` · `save_json` · `match_playbooks` | 2 · 3 · 4교시 |
| `config/playbook_registry.json` | 월요일 | 플레이북 3개(`actions` · 트리거 규칙 · 최소 등급) | 2 · 3교시 |
| `containment_store.py` · `account_actions.py` · `ip_actions.py` | 수요일 | `new_state` · `lock_account` · `block_ip` · `count_users_on_ip` | 2교시 |
| `ip_users.json` | 수요일 | IP 별로 그 IP 를 쓰는 계정 리스트 | 2교시 |
| `ticketing.py` · `config/escalation_rules.json` | 목요일 | `make_ticket` · 등급별 응답 기한(`sla_minutes`) | 2교시 |
| `approval_gate.py` · `config/approval_policy.json` | 금요일 | `decide_gate` · 승인 정책 | 2 · 4교시 |
| `day03_risk_scores.json` | 4과목 11/5(목) 오후 | 대상별 점수 · 등급 · 이유 5건 | 3교시 |

## 시작하기

1. **[VS Code]** `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 엽니다.
2. **[터미널]** 5과목 폴더로 들어가 파일을 확인합니다. <mark>`ls` 결과에 `incident.py` · `approval_gate.py` · `ticketing.py` · `ip_users.json` 과 `config` 가 보이고, `ls config` 결과에 `playbook_registry.json` · `approval_policy.json` · `escalation_rules.json` 이 보이면</mark> 됩니다. 수요일 파일 세 개(`containment_store.py` · `account_actions.py` · `ip_actions.py`)도 필요합니다. 없는 파일은 아래 「🛟」에서 만듭니다.
   ```bash
   pwd
   cd soar_response
   ls
   ls config
   ```
   - 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `cd 폴더이름` 그 폴더로 이동 · `ls` 폴더 안의 파일 이름 보기
   - `pwd` 가 이미 `…/soar_response` 로 끝나면 `cd soar_response` 는 건너뜁니다.
3. 오늘 받은 파일 두 개(`day06_am_soar_engine.md`, `day06_am_report.md`)를 `soar_response` 폴더로 옮기고, 보고서 제목의 `이름` 을 내 이름으로 바꿉니다.
4. **[터미널]** 월요일의 플레이북 등록 값을 점검합니다(맥북은 `python3`). 엔진은 이 파일의 `actions` · 트리거 규칙 · 최소 등급을 읽으므로, <mark>아래 출력과 같아야</mark> 오늘 출력이 문서와 일치합니다. 다르면 아래 「🛟」의 `config/playbook_registry.json` 으로 덮어씁니다.
   ```bash
   python -c "import json; print([(p['id'], p['trigger_rule'], p['min_grade'], p['actions']) for p in json.load(open('config/playbook_registry.json', encoding='utf-8'))])"
   ```
   ```
   [('PB-001', '퇴사한 계정', 'high', ['계정 잠금', '티켓 생성']), ('PB-002', '대량 다운로드', 'mid', ['담당자 알림', '티켓 생성']), ('PB-003', '경로 스캔', 'low', ['IP 차단', '티켓 생성'])]
   ```
5. **[터미널]** 2교시 데이터 파일을 만들고 **[VS Code]** 에서 열어 아래 내용을 붙여 넣습니다.
   ```bash
   touch engine_alerts.json
   ls
   ```

**`engine_alerts.json`** — 오늘 아침 들어온 알림 8건입니다.

- **무엇인가**:
  - 월요일 `incident_samples.json` 과 같은 알림 모양입니다. 키는 `id`(알림 번호) · `entity`(대상 계정 또는 IP) · `grade`(등급) · `score`(점수) · `reasons`(탐지된 규칙 이름 리스트) · `status`(상태)입니다.
  - 알림마다 다른 처리 경로를 지나도록 만든 시험용 데이터입니다. `INC-402` 는 `grade` 키가 없는 알림입니다.
  - `203.0.113.80` 은 허용 목록(allowlist, 얼라우리스트: 차단 대상에서 제외하기로 미리 정한 IP 의 목록)에 있는 협력사 사무실 IP 이고, `192.0.2.41` 은 `junho` 와 `hana` 가 함께 쓰는 IP 이며, `gaeun` 은 VIP 계정입니다.
- **어디에 쓰나**: 2교시 엔진이 알림을 하나씩 처리합니다.

```
[
  {"id": "INC-401", "entity": "dami", "grade": "high", "score": 60, "reasons": ["퇴사한 계정"], "status": "탐지됨"},
  {"id": "INC-402", "entity": "hana", "score": 40, "reasons": ["업무 시간 밖 로그인"], "status": "탐지됨"},
  {"id": "INC-403", "entity": "198.51.100.45", "grade": "low", "score": 30, "reasons": ["경로 스캔"], "status": "탐지됨"},
  {"id": "INC-404", "entity": "203.0.113.80", "grade": "high", "score": 65, "reasons": ["경로 스캔"], "status": "탐지됨"},
  {"id": "INC-405", "entity": "192.0.2.41", "grade": "mid", "score": 35, "reasons": ["경로 스캔"], "status": "탐지됨"},
  {"id": "INC-406", "entity": "gaeun", "grade": "high", "score": 60, "reasons": ["퇴사한 계정"], "status": "탐지됨"},
  {"id": "INC-407", "entity": "seoyeon", "grade": "mid", "score": 45, "reasons": ["대량 다운로드"], "status": "탐지됨"},
  {"id": "INC-408", "entity": "jiwoo", "grade": "mid", "score": 35, "reasons": ["업무 시간 밖 로그인"], "status": "탐지됨"}
]
```

6. **[터미널]** 파일이 정상인지 확인합니다(맥북은 `python3`). <mark>`8` 이 나와야</mark> 합니다.
   ```bash
   python -c "import json; print(len(json.load(open('engine_alerts.json', encoding='utf-8'))))"
   ```

### 🛟 이전 파일이 없을 때 (월 · 수 · 목 · 금요일 파일)

해당 요일에 결석했거나 파일을 지운 경우에만 만듭니다. **이미 있는 파일은 건너뜁니다.** 먼저 **[터미널]** 에서 빈 파일을 만듭니다. 이미 있는 파일은 `touch` 가 그대로 두고, `config` 폴더가 이미 있으면 `mkdir -p` 도 그대로 둡니다.

```bash
mkdir -p config
touch incident.py containment_store.py account_actions.py ip_actions.py ticketing.py approval_gate.py
touch ip_users.json config/playbook_registry.json config/approval_policy.json config/escalation_rules.json
ls
```

- 명령 풀이: `mkdir -p 폴더이름` 폴더가 없을 때만 만들기 · `touch 파일이름들` 빈 파일 만들기 · `ls` 폴더 안의 파일 이름 보기
- 아래 코드 상자를 **[VS Code]** 에서 같은 이름의 파일에 붙여 넣고 저장합니다. 이미 있는 파일은 붙여 넣지 않습니다(플레이북 등록 파일만 4번 점검 결과가 다를 때 덮어씁니다).

**`incident.py`** — 월요일 파일에서 오늘 쓰는 부분(`load_json` · `save_json` · `match_playbooks` 와 그 함수가 쓰는 `is_grade_enough`)만 담았습니다. 월요일 파일 전체가 있으면 그것을 그대로 씁니다.

```python
import json                                                                   # JSON 파일을 읽고 쓰기 위해 json 을 불러온다

GRADE_ORDER = {"low": 1, "mid": 2, "high": 3}                                 # 등급을 크기를 비교할 수 있는 숫자로 바꾸는 딕셔너리


def load_json(path):                                                          # 파일 경로를 받는 함수
    """JSON 파일을 읽어 리스트나 딕셔너리로 리턴한다.
    인시던트와 플레이북 등록 파일을 읽을 때 쓴다.
    """
    with open(path, encoding="utf-8") as file:                                # 파일을 읽기 모드로 연다
        data = json.load(file)                                                # JSON 글자를 파이썬 값으로 바꾼다
    return data                                                               # 읽은 값을 리턴한다


def save_json(data, path):                                                    # 저장할 값과 파일 경로를 받는 함수
    """값을 JSON 파일로 저장한다.
    실행 결과 상태와 감사 기록을 남길 때 쓴다.
    """
    with open(path, "w", encoding="utf-8") as file:                           # 파일을 쓰기 모드로 연다
        json.dump(data, file, ensure_ascii=False, indent=2)                   # 한글은 그대로, 줄을 나눠 저장한다


def is_grade_enough(incident_grade, min_grade):                               # 인시던트 등급과 플레이북의 최소 등급을 받는 함수
    """인시던트 등급이 최소 등급 이상이면 True, 아니면 False 를 리턴한다.
    등급이 낮은 인시던트에 무거운 대응이 실행되지 않게 할 때 쓴다.
    """
    return GRADE_ORDER[incident_grade] >= GRADE_ORDER[min_grade]              # 등급을 숫자로 바꿔 비교한 결과를 리턴한다


def match_playbooks(incident, registry):                                      # 인시던트와 플레이북 리스트를 받는 함수
    """트리거 규칙과 조건 등급이 모두 맞는 플레이북을 리스트로 리턴한다.
    알림이 올 때 어떤 대응 절차를 쓸지 찾을 때 쓴다.
    """
    matched = []                                                              # 맞는 플레이북을 담을 빈 리스트
    for playbook in registry:                                                 # 플레이북을 하나씩 꺼낸다
        has_rule = playbook["trigger_rule"] in incident["reasons"]            # 트리거 규칙이 탐지된 규칙 리스트 안에 있는지 구한다
        grade_ok = is_grade_enough(incident["grade"], playbook["min_grade"])  # 인시던트 등급이 최소 등급 이상인지 구한다
        if has_rule and grade_ok:                                             # 트리거와 조건이 모두 맞으면
            matched.append(playbook)                                          # 맞는 플레이북을 리스트에 추가한다
    return matched                                                            # 맞는 플레이북 리스트를 리턴한다
```

**`config/playbook_registry.json`** — 월요일의 플레이북 3개입니다. 오늘 엔진은 `trigger_rule` · `min_grade` · `actions` 만 읽습니다.

```
[
  {
    "id": "PB-001",
    "name": "퇴사한 계정의 서버 요청",
    "trigger_rule": "퇴사한 계정",
    "min_grade": "high",
    "actions": [
      "계정 잠금",
      "티켓 생성"
    ],
    "approval": "자동",
    "reason": "퇴사한 사람의 계정으로 서버에 요청이 오면 그 계정이 아직 사용할 수 있는 상태라는 뜻입니다. 퇴사한 사람이 쓰는 계정이 없으므로 잠가도 막히는 업무가 없습니다."
  },
  {
    "id": "PB-002",
    "name": "대량 다운로드",
    "trigger_rule": "대량 다운로드",
    "min_grade": "mid",
    "actions": [
      "담당자 알림",
      "티켓 생성"
    ],
    "approval": "담당자 승인 필요",
    "reason": "파일을 많이 내려받은 것은 업무 때문일 수도 있습니다. 사람이 확인하기 전에는 정상인지 알 수 없으므로 담당자가 허락한 뒤에 실행합니다."
  },
  {
    "id": "PB-003",
    "name": "경로 스캔",
    "trigger_rule": "경로 스캔",
    "min_grade": "low",
    "actions": [
      "IP 차단",
      "티켓 생성"
    ],
    "approval": "담당자 승인 필요",
    "reason": "경로 스캔의 대상은 사용자가 아니라 IP 입니다. 같은 IP 를 여러 사람이 쓰고 있으면 차단했을 때 정상 사용자의 업무도 막히므로, 담당자가 확인한 뒤에 차단합니다."
  }
]
```

**`containment_store.py`** — 수요일 오전 파일에서 오늘 쓰는 부분(`new_state` · `make_record`)만 담았습니다. 조치 기록 한 건을 만들고 연습용 시스템의 처음 상태를 만듭니다. 수요일 파일 전체가 있으면 그것을 그대로 씁니다.

```python
import copy                                                           # 처음 상태를 복사해 쓰기 위해 copy 를 불러온다

INITIAL_STATE = {                                                     # 수업을 시작할 때의 연습용 시스템 상태
    "locked_users": ["junho"],                                        # 이미 잠겨 있는 계정 : junho 는 수업 전부터 잠겨 있다
    "blocked_ips": [],                                                # 차단한 IP 리스트 : 처음에는 비어 있다
    "block_expiry": {},                                               # IP 별 차단이 끝나는 시각(분) : 처음에는 비어 있다
    "clock": 0,                                                       # 연습용 시스템의 시계(분) : 0 에서 시작한다
    "sessions": {"dami": ["S-101", "S-102"], "seoyeon": ["S-201"], "gaeun": ["S-301"], "jiwoo": ["S-401"], "junho": ["S-501"], "hana": ["S-601"]},  # 계정별로 열려 있는 로그인 세션
}


def new_state():                                                      # 인자가 없는 함수
    """처음 상태를 복사해 새 연습용 시스템 상태를 리턴한다.
    실행할 때마다 같은 상태에서 시작해 결과를 비교할 때 쓴다.
    """
    return copy.deepcopy(INITIAL_STATE)                               # 처음 상태의 복사본을 리턴한다


def make_record(action, target, incident_id, before, after, reason):  # 조치 이름 · 대상 · 인시던트 번호 · 조치 전 · 조치 후 · 이유를 받는 함수
    """조치 한 건(무엇을 · 누구에게 · 조치 전 · 조치 후 · 이유)의 기록을 딕셔너리로 만들어 리턴한다.
    조치 전과 후 상태를 함께 남겨 두고 싶을 때 쓴다.
    """
    record = {"action": action, "target": target, "incident": incident_id, "before": before, "after": after, "reason": reason}  # 조치 한 건의 기록을 딕셔너리로 만든다
    return record                                                     # 기록 한 건을 리턴한다
```

**`account_actions.py`** — 수요일 오전 파일에서 오늘 쓰는 부분(`lock_account` 와 그 함수가 쓰는 `check_policy` · `verify_locked`)만 담았습니다. VIP 이면 잠그지 않고, 아니면 계정을 잠급니다.

```python
from containment_store import make_record                                             # 기록 한 건을 만드는 함수를 불러온다


def check_policy(user, vip_accounts):                                                 # 계정 이름과 VIP 계정 리스트를 받는 함수
    """자동으로 조치하면 안 되는 계정(VIP)이면 그 이유 문장을, 아니면 빈 글자("")를 리턴한다.
    경로에서 이미 `승인 필요` 로 보냈어도 조치 함수가 마지막으로 한 번 더 막고 싶을 때 쓴다.
    """
    if user in vip_accounts:                                                          # VIP 계정이면
        return "VIP 계정이라 자동 조치 대상이 아님"                                   # 막는 이유를 리턴한다
    return ""                                                                         # 막을 이유가 없으면 빈 글자를 리턴한다 — 미리 채운 줄


def verify_locked(user, state):                                                       # 계정 이름과 연습용 시스템 상태를 받는 함수
    """계정이 잠긴 계정 리스트에 들어 있으면 True, 없으면 False 를 리턴한다.
    잠그라고 호출한 것과 실제로 잠긴 것이 같은지 조치 뒤에 확인할 때 쓴다.
    """
    return user in state["locked_users"]                                              # 잠긴 계정 리스트 안에 있는지 확인한 결과를 리턴한다


def lock_account(user, state, vip_accounts, incident_id, reason):                     # 계정 · 상태 · VIP 리스트 · 인시던트 번호 · 이유를 받는 함수
    """VIP 인지 먼저 확인하고 계정을 잠근 뒤, 실제로 잠겼는지 다시 확인해 조치 기록 한 건을 리턴한다.
    VIP 이거나 이미 잠겨 있으면 잠그지 않고 그 이유를 기록에 남긴다.
    """
    blocked = check_policy(user, vip_accounts)                                        # 자동 조치를 막을 이유를 구한다 — 미리 채운 줄
    if blocked != "":                                                                 # 막을 이유가 있으면 — 미리 채운 줄
        return make_record("계정 잠금", user, incident_id, "변경 없음", "변경 없음", blocked)  # 바꾸지 않고 이유를 기록한다 — 미리 채운 줄
    if user in state["locked_users"]:                                                 # 이미 잠겨 있으면 — 미리 채운 줄
        return make_record("계정 잠금", user, incident_id, "잠김", "잠김", "이미 잠겨 있어 변경 없음")  # 바꾸지 않고 기록한다 — 미리 채운 줄
    state["locked_users"].append(user)                                                # 잠긴 계정 리스트에 추가한다
    after = "잠김"                                                                    # 조치 뒤 상태 : 일단 잠겼다고 적고 — 미리 채운 줄
    if not verify_locked(user, state):                                                # 실제로 확인해 잠기지 않았으면 — 미리 채운 줄
        after = "잠기지 않음 (확인 실패)"                                             # 확인 실패라고 고쳐 적는다 — 미리 채운 줄
    return make_record("계정 잠금", user, incident_id, "잠기지 않음", after, reason)  # 조치 전 · 후 상태와 함께 기록한다 — 미리 채운 줄
```

**`ip_actions.py`** — 수요일 오전 파일에서 오늘 쓰는 부분(`block_ip` · `count_users_on_ip` · `DEFAULT_TTL`)만 담았습니다. IP 를 차단하고, 그 IP 를 쓰는 계정 수를 셉니다.

```python
from containment_store import make_record             # 기록 한 건을 만드는 함수를 불러온다

DEFAULT_TTL = 120                                     # 차단을 유지하는 시간(분)


def count_users_on_ip(ip, ip_users):                  # IP 와 IP 별 사용 계정 딕셔너리를 받는 함수
    """그 IP 를 쓰는 계정이 몇 개인지 리턴한다. ip_users.json 에 없는 IP 는 0 을 리턴한다.
    차단하면 정상 사용자가 몇 명 영향을 받는지 확인할 때 쓴다.
    """
    return len(ip_users.get(ip, []))                  # 그 IP 를 쓰는 계정 수를 리턴한다 (목록에 없으면 0)


def block_ip(ip, state, incident_id, reason, ttl):    # IP · 상태 · 인시던트 번호 · 이유 · 유지 시간을 받는 함수
    """IP 를 차단하고 끝나는 시각을 적은 뒤, 실제로 차단됐는지 확인해 기록 한 건을 리턴한다.
    영구 차단 대신, 시간이 지나면 자동으로 풀리는 임시 차단을 만들 때 쓴다.
    """
    state["blocked_ips"].append(ip)                   # 차단한 IP 리스트에 추가한다
    state["block_expiry"][ip] = state["clock"] + ttl  # 차단이 끝나는 시각을 적는다
    after = "차단됨"                                  # 조치 뒤 상태 : 일단 차단됐다고 적고 — 미리 채운 줄
    if ip not in state["blocked_ips"]:                # 실제로 확인해 차단되지 않았으면 — 미리 채운 줄
        after = "차단되지 않음 (확인 실패)"           # 확인 실패라고 고쳐 적는다 — 미리 채운 줄
    return make_record("IP 차단", ip, incident_id, "차단되지 않음", after, reason + " (" + str(ttl) + "분 뒤 자동 해제)")  # 조치 전 · 후 상태와 함께 기록한다 — 미리 채운 줄
```

**`ip_users.json`** — 수요일 오전 파일입니다. IP 별로 그 IP 를 쓰는 계정 리스트입니다.

```
{"203.0.113.80": ["seoyeon", "jiwoo"], "192.0.2.41": ["junho", "hana"]}
```

**`ticketing.py`** — 목요일 오전 파일입니다. 알림 한 건으로 티켓 한 장을 만듭니다.

```python
DEFAULT_NEXT_STEP = "담당자가 알림 내용을 읽고 필요한 일을 정한다"                      # 알림 상태를 모를 때 쓰는 다음 할 일
MANUAL_STEP = "조치가 확인되지 않았다. 담당자가 직접 계정이나 IP 상태를 보고 조치한다"  # 조치 확인에 실패한 티켓의 다음 할 일
NEXT_STEPS = {                                                                          # 알림 상태마다 담당자가 할 다음 일
    "조치됨": "조치 결과가 맞는지 확인하고 계정이나 IP 상태를 점검한다",                # 자동 조치가 끝난 알림
    "승인 대기": "승인할지 거절할지 정하고 정한 사람의 이름을 남긴다",                  # 승인을 기다리는 알림
    "조치 없음": "자동 조치가 없는 알림이니 직접 보고 조치가 필요한지 정한다",          # 자동 조치 대상이 아닌 알림
}


def make_title(alert):                                                                  # 알림 한 건을 받는 함수
    """티켓 제목(등급 · 대상 · 규칙)을 문자열로 만들어 리턴한다.
    티켓 목록에서 제목만 봐도 무슨 일인지 알 수 있게 할 때 쓴다.
    """
    grade = alert["grade"]                                                              # 알림 등급 — 미리 채운 줄
    entity = alert["entity"]                                                            # 알림 대상(사용자 이름 또는 IP) — 미리 채운 줄
    rule = alert["rule"]                                                                # 탐지된 규칙 이름 — 미리 채운 줄
    return "[" + grade + "] " + entity + " — " + rule                                   # 등급 · 대상 · 규칙을 이어 붙인 제목을 리턴한다


def find_next_step(alert, next_steps):                                                  # 알림 한 건과 다음 할 일 딕셔너리를 받는 함수
    """알림 상태에 맞는 다음 할 일 문장을 리턴한다. 정해 둔 문장이 없으면 기본 문장을 리턴한다.
    담당자가 티켓을 열자마자 무엇부터 할지 알게 할 때 쓴다.
    """
    status = alert["status"]                                                            # 알림 상태(조치됨 · 승인 대기 · 조치 없음) — 미리 채운 줄
    return next_steps.get(status, DEFAULT_NEXT_STEP)                                    # 상태에 맞는 다음 할 일을 리턴한다 (없으면 기본 문장)


def has_failed_action(done_list):                                                       # 조치 내역 문장 리스트를 받는 함수
    """조치 내역에 「확인 실패」가 들어 있는 문장이 하나라도 있으면 True, 없으면 False 를 리턴한다.
    조치했다고 했지만 실제로 바뀌지 않은 알림을 사람이 직접 보게 할 때 쓴다.
    """
    for text in done_list:                                                              # 조치 내역 문장을 하나씩 읽는다 — 미리 채운 줄
        if "확인 실패" in text:                                                         # 문장 안에 확인 실패가 있으면
            return True                                                                 # 확인 실패가 있다고 True 를 리턴한다
    return False                                                                        # 하나도 없으면 False 를 리턴한다 — 미리 채운 줄


def make_ticket(alert, ticket_no, rules, next_steps):                                   # 알림 · 티켓 번호 · 규칙 · 다음 할 일 딕셔너리를 받는 함수
    """알림 한 건으로 티켓 한 장(딕셔너리)을 만들어 리턴한다. 만든 시각과 응답 기한(SLA)을 함께 적는다.
    알림이 오면 바로 담당자가 읽을 수 있는 티켓을 만들 때 쓴다.
    """
    sla_table = rules["sla_minutes"]                                                    # 등급마다 정한 응답 기한(분) 표 — 미리 채운 줄
    sla_minutes = sla_table[alert["grade"]]                                             # 이 알림 등급의 응답 기한(분)을 꺼낸다
    sla_due = alert["minute"] + sla_minutes                                             # 알림이 온 시각 + 응답 기한 = 응답해야 하는 시각
    needs_manual = has_failed_action(alert["done"])                                     # 조치 확인에 실패한 내역이 있는지 — 미리 채운 줄
    next_step = find_next_step(alert, next_steps)                                       # 다음 할 일 문장 — 미리 채운 줄
    if needs_manual:                                                                    # 확인 실패가 있으면 — 미리 채운 줄
        next_step = MANUAL_STEP                                                         # 직접 확인하라는 문장으로 바꾼다 — 미리 채운 줄
    ticket = {                                                                          # 티켓 한 장 — 미리 채운 줄
        "id": "TCK-" + str(ticket_no),                                                  # 티켓 번호
        "title": make_title(alert),                                                     # 제목
        "entity": alert["entity"],                                                      # 대상
        "rule": alert["rule"],                                                          # 규칙
        "grade": alert["grade"],                                                        # 등급
        "playbook": alert["playbook"],                                                  # 실행한 플레이북
        "done": alert["done"],                                                          # 조치 내역
        "status": "열림",                                                               # 티켓 상태 : 처음에는 열림
        "next_step": next_step,                                                         # 다음 할 일
        "needs_manual": needs_manual,                                                   # 직접 확인이 필요한지
        "created_at": alert["minute"],                                                  # 만든 시각(분)
        "updated_at": alert["minute"],                                                  # 마지막으로 갱신한 시각(분)
        "sla_due": sla_due,                                                             # 응답 기한 시각(분)
        "count": 1,                                                                     # 합쳐진 알림 수 : 처음에는 1
        "incidents": [alert["id"]],                                                     # 합쳐진 알림 번호
        "notified_count": 0,                                                            # 알림을 보낸 횟수
        "last_notified": -1,                                                            # 마지막으로 알림을 보낸 시각(분) : 아직 없음
        "acked_at": -1,                                                                 # 담당자가 처음 확인한 시각(분) : 아직 없음
        "resolved_at": -1,                                                              # 해결한 시각(분) : 아직 없음
        "escalation_level": 0,                                                          # 상급자에게 올린 단계 : 아직 없음
        "comments": [],                                                                 # 상태를 바꾼 기록
    }
    return ticket                                                                       # 만든 티켓을 리턴한다
```

**`config/escalation_rules.json`** — 목요일 오전 파일입니다. 오늘은 등급별 응답 기한(`sla_minutes`)만 읽습니다.

```
{
  "sla_minutes": {"high": 15, "mid": 60, "low": 240},
  "recipients": {
    "high": ["kim.sec", "lee.soc", "team.lead"],
    "mid": ["kim.sec", "lee.soc"],
    "low": ["kim.sec"]
  },
  "merge_window_minutes": 60,
  "send_gap_minutes": 30,
  "alert_url": "http://127.0.0.1:5001/alert",
  "escalation_steps": [
    {"overdue_minutes": 0, "notify": "team.lead"},
    {"overdue_minutes": 30, "notify": "soc.head"}
  ]
}
```

**`approval_gate.py`** — 금요일 오전 파일입니다. 조치 요청 한 건을 자동 · 승인 필요 · 차단 금지로 정합니다.

```python
def is_allowlisted(request, policy):                                        # 조치 요청 한 건과 승인 정책을 받는 함수
    """조치 대상이 허용 목록에 있으면 True, 없으면 False 를 리턴한다.
    협력사 사무실이나 점검 서버처럼 지금 정책에서 차단하지 않기로 등록한 대상을 먼저 가려낼 때 쓴다.
    """
    return request["target"] in policy["allowlist_ips"]                     # 대상이 허용 목록에 있는지의 결과를 리턴한다


def risk_score(request, policy):                                            # 조치 요청 한 건과 승인 정책을 받는 함수
    """등급 · VIP · 함께 쓰는 IP · 대상 수로 위험 점수를 더하고, 점수와 이유 리스트를 함께 리턴한다.
    자동으로 실행해도 되는 요청인지 숫자로 판단할 때 쓴다.
    """
    grade_table = policy["grade_points"]                                    # 등급마다 정한 점수 표 — 미리 채운 줄
    score = grade_table[request["grade"]]                                   # 이 요청 등급의 점수로 시작한다
    reasons = ["등급 " + request["grade"] + " +" + str(score)]              # 점수를 더한 이유 리스트 — 미리 채운 줄
    if request["target"] in policy["vip_accounts"]:                         # 대상이 VIP 계정이면
        score = score + policy["vip_points"]                                # VIP 점수를 더한다
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
    if is_allowlisted(request, policy):                                     # 허용 목록 대상이면
        return "차단 금지", ["허용 목록 대상"]                              # 결정과 이유를 함께 리턴한다 — 미리 채운 줄
    score, reasons = risk_score(request, policy)                            # 위험 점수와 이유 리스트를 함께 받는다
    reasons.append("합계 " + str(score) + "점")                             # 합계 점수를 이유에 추가한다 — 미리 채운 줄
    if score >= policy["approval_score"]:                                   # 승인 기준 점수 이상이면
        return "승인 필요", reasons                                         # 결정과 이유를 함께 리턴한다 — 미리 채운 줄
    return "자동", reasons                                                  # 기준보다 낮으면 자동으로 실행한다 — 미리 채운 줄
```

**`config/approval_policy.json`** — 금요일 오전 파일입니다. 승인 게이트의 점수 기준입니다.

```
{
  "allowlist_ips": ["203.0.113.80", "192.0.2.10"],
  "vip_accounts": ["gaeun"],
  "grade_points": {"high": 2, "mid": 1, "low": 0},
  "vip_points": 3,
  "shared_ip_points": 2,
  "shared_ip_limit": 2,
  "many_targets_points": 2,
  "many_targets_limit": 3,
  "approval_score": 3
}
```

### 🆘 오류가 나면

- `pwd` 가 `soar_response` 로 끝나는지, `ls` 로 <mark>파일 이름이 문서와 같은지</mark> 봅니다.
- `ModuleNotFoundError: No module named 'approval_gate'` 처럼 `No module named` 이 나오면 <mark style="background:#ffc4d6">그 이름의 파일이 이 폴더에 없다는 뜻</mark>입니다. 위 「🛟 이전 파일이 없을 때」의 코드 상자로 만듭니다.
- `FileNotFoundError` 가 나오면 오류 문장에 적힌 파일(`ip_users.json` · `config/playbook_registry.json` · `config/approval_policy.json` · `config/escalation_rules.json`)이 그 위치에 없는 것입니다. `ls` 와 `ls config` 로 확인한 뒤 위 「🛟 이전 파일이 없을 때」의 코드 상자로 만듭니다.
- `json.decoder.JSONDecodeError` 가 나오면 붙여 넣은 JSON 파일에서 쉼표나 괄호가 빠졌거나 남은 것입니다. 오류 문장의 `line` 숫자 근처를 확인하고, 모르겠으면 파일 내용을 모두 지운 뒤 문서의 코드 상자를 다시 붙여 넣습니다.
- 먼저 오류 전체와 내가 친 명령을 AI 에게 붙여 넣어 묻습니다(`.env` · API 키는 지웁니다). 그래도 막히면 맨 아래 「정답」을 봅니다. 그래도 풀리지 않으면 보고서에 「모름 — 막힌 곳: …」 이라고 씁니다.

> 실행은 VS Code 의 ▶ 단추가 아니라 <mark style="background:#ffc4d6">**터미널**에서</mark> 합니다. 실행할 때마다 같은 입력 파일에서 시작해 같은 결과가 나옵니다.
---
# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">2교시 (10:00–10:50) · 알림 8건을 승인 게이트를 거쳐 조치하고 티켓을 남기며, 오류가 난 알림은 실패로 격리해 처리하는 통합 엔진(soar_engine.py) 만들기</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: 월요일의 `match_playbooks` 는 알림에 맞는 플레이북을 찾고, 수요일의 `lock_account` · `block_ip` 는 조치를 실행하고, 목요일의 `make_ticket` 은 티켓을 만들고, 금요일의 `decide_gate` 는 자동 · 승인 필요 · 차단 금지를 정합니다. <mark style="background:#e0d4ff">화요일의 `flow.py` 는 알림 처리 흐름을 한 번에 실행하지만, 조치는 월요일의 간단한 `run_action` 으로 실행합니다.</mark> 그래서 수요일 이후에 만든 함수는 그 흐름에 연결되어 있지 않습니다. 오늘 아침 알림 8건(`INC-401` ~ `INC-408`)이 들어옵니다.
> - **문제**: 함수를 사람이 순서대로 호출하면 승인 게이트를 건너뛰고 `lock_account` 를 바로 호출하는 실수를 막을 수 없습니다. 또 알림 한 건에서 오류가 나면 프로그램 전체가 멈춥니다. `INC-402` 는 등급(`grade`) 키가 없어서 플레이북을 찾는 단계에서 오류가 납니다. <mark style="background:#ffc4d6">오류를 처리하지 않으면 앞의 `INC-401` 은 `dami` 계정을 이미 잠갔는데 로그와 티켓 파일이 저장되지 않고, 뒤의 알림 6건은 처리되지 않습니다.</mark>
> - **부탁**: 알림 한 건을 「플레이북 찾기 → 승인 게이트 → 조치 실행 → 티켓」 순서로 처리하는 통합 엔진 `soar_engine.py` 를 만들어 주세요. 오류가 난 알림은 오류 이름과 함께 실패로 기록하고, 다음 알림을 계속 처리해야 합니다.
> - **바뀌는 점**: 알림 8건이 <mark style="background:#bde3ff">자동 실행 2 · 승인 대기 2 · 차단 금지 1 · 조치 없음 2 · 실패 1</mark>로 처리되고, 티켓 <mark style="background:#bde3ff">7장</mark>이 `engine_tickets.json` 에 저장됩니다. 상황과 이름은 설명을 위한 예시입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다. (문법 상자의 코드는 눈으로 읽어도 되고, 따라 쳐 보아도 됩니다.)

### 📖 2.1 통합 엔진은 알림 한 건을 「플레이북 찾기 → 조치 요청 → 승인 게이트 → 조치 실행 → 티켓」 순서로 처리하고, 오류는 알림마다 격리한다

| 순서 | 하는 일 | 가져다 쓰는 함수 | 엔진의 함수 |
|---|---|---|---|
| 1. 플레이북 찾기 | 알림의 탐지 규칙과 등급이 맞는 플레이북을 찾는다 | 월요일 `match_playbooks` | `run_soar_pipeline` (6번) |
| 2. 조치 요청 만들기 | 조치 이름 · 대상 · 등급 · 그 IP 를 쓰는 계정 수를 담은 딕셔너리를 만든다 | 수요일 `count_users_on_ip` | `make_request` (1번) |
| 3. 승인 게이트 | 자동 · 승인 필요 · 차단 금지를 정한다 | 금요일 `decide_gate` | `run_step` (4 · 5번) |
| 4. 조치 실행 | 자동으로 정해진 조치만 실행한다 | 수요일 `lock_account` · `block_ip` | `execute_action` (2 · 3번) |
| 5. 티켓 | 처리 결과를 티켓 한 장으로 남긴다 | 목요일 `make_ticket` | `open_ticket` (미리 채움) |
| 6. 오류 격리 | 알림 하나의 오류를 그 알림의 실패 기록으로 한정하고 다음 알림으로 넘어간다 | `try` / `except` | `run_all` (7 · 8번) |

- 알림 한 건의 처리 결과(`outcome`)는 <mark>자동 실행 · 승인 대기 · 차단 금지 · 조치 없음 · 실패</mark> 다섯 가지입니다. 조치 없음은 승인 게이트를 거칠 조치가 없는 알림입니다. `decide_outcome` 은 사람이 먼저 봐야 하는 결과가 앞서도록 승인 대기부터 판단합니다.
- <mark style="background:#e0d4ff">월요일 플레이북의 승인 값(`approval`)은 이 엔진이 읽지 않습니다.</mark> 금요일에 승인 여부를 플레이북 하나에 값 하나로 정하는 대신 요청마다 위험 점수로 정하도록 바꿨기 때문입니다. 플레이북에서는 `actions` 만 읽습니다.
- 플레이북의 액션 가운데 `계정 잠금` · `IP 차단` 만 승인 게이트를 거쳐 실행합니다(`CONTAINMENT_ACTIONS`). 티켓은 처리한 알림마다 항상 만듭니다. 실패한 알림은 티켓이 없어서 알림 8건에 티켓 7장이 됩니다. `담당자 알림` 은 <mark style="background:#e0d4ff">목요일의 알림 서버(5001번 포트)</mark>가 켜져 있어야 보낼 수 있어서 오늘은 연결하지 않고, 담당자에게 넘기는 일은 티켓이 맡습니다.
- 오류 격리(failure isolation, 페일러 아이솔레이션: 한 작업의 오류가 다른 작업으로 번지지 않게 막는 방식)로 오류의 영향 범위를 알림 한 건으로 제한합니다. 대신 <mark style="background:#ffc4d6">코드의 실수도 알림마다 「실패」로 나타납니다.</mark> 실패 건수가 알림 수에 가까우면 데이터가 아니라 코드를 의심합니다.
- `executed` 는 조치 함수를 호출했다는 뜻입니다. 이미 잠긴 계정처럼 호출해도 조치 전 · 후 상태가 같을 수 있어서, 무엇이 바뀌었는지는 `before` · `after` 로 확인합니다.
- 티켓의 시각은 엔진을 실행한 때를 0분으로 놓습니다(목요일 티켓처럼 분 단위 숫자입니다). 연습용 시스템(실제 서버를 대신하는 시스템)은 실행할 때마다 처음 상태(`junho` 만 잠김)에서 시작합니다.
- 오늘 엔진에 연결하지 않은 것: 화요일의 재시도(`run_with_retry`) · 수요일의 세션 종료 · 목요일의 에스컬레이션입니다.

**🐍 문법 상자 — `except Exception as error` 는 어떤 종류의 오류든 받아서 프로그램이 멈추지 않게 한다**

```python
students = [{"name": "민지", "score": 80}, {"name": "서준"}, {"name": "하은", "score": 95}]  # 서준에게는 score 키가 없다

for student in students:                                                                     # 학생을 하나씩 꺼낸다
    try:                                                                                     # 오류가 날 수 있는 부분을 시작한다
        print(student["name"], student["score"])                                             # 이름과 점수를 출력한다
    except Exception as error:                                                               # 어떤 종류의 오류든 error 에 저장해 받는다
        print(student["name"], "→ 오류:", type(error).__name__, error)                       # 오류의 종류 이름과 내용을 출력한다
```

실행 결과:

```
민지 80
서준 → 오류: KeyError 'score'
하은 95
```

| 코드 | 뜻 |
|---|---|
| `except Exception as error:` | <mark style="background:#e0d4ff">화요일의 `except ConnectionError as error` 는 연결 오류 한 종류만 받았습니다.</mark> `Exception` 은 `KeyError` 같은 거의 모든 오류의 부모 이름이라 어떤 종류든 받습니다 |
| `type(error).__name__` | 오류의 종류 이름(`KeyError`)입니다. 오류를 받은 뒤에는 이 이름과 내용을 반드시 기록해서 사람이 볼 수 있게 합니다 |
| 위 코드의 출력 | <mark style="background:#bde3ff">`서준` 줄에서 오류가 나도 `하은` 줄까지 출력됩니다</mark>. `try` 없이 쓰면 `서준` 에서 멈추고 `하은` 은 출력되지 않습니다 |

함수 아홉 개와 실행 파일 가운데 직접 쓰는 곳은 **아홉 군데**입니다.

```
soar_engine.py  load_context          : 설정 파일을 읽어 엔진 재료를 만든다 (미리 채움)
                make_request          : IP 차단이면 그 IP 를 쓰는 계정 수를 센다 (1번)
                execute_action        : 계정 잠금 (2번) · IP 차단 (3번) 을 실행한다
                run_step              : 승인 게이트에 묻고 (4번) 자동이면 (5번) 실행한다
                decide_outcome        : 조치 결과들로 알림의 처리 결과를 정한다 (미리 채움)
                open_ticket           : 처리 결과로 티켓 한 장을 만든다 (미리 채움)
                run_soar_pipeline     : 게이트를 거칠 조치만 (6번) 처리하고 티켓까지 만든다
                make_failure_result   : 실패한 알림의 결과 기록을 만든다 (미리 채움)
                run_all               : 알림마다 처리하고 (7번) 오류는 실패로 기록한다 (8번)
실행 파일       day06_2-1_run.py      : 처리 결과별 알림 수를 센다 (9번)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 2-1 · 알림 8건을 승인 게이트를 거쳐 조치하고 티켓을 남기며, 오류가 난 알림은 실패로 격리하는 통합 엔진 만들기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>플레이북 찾기 · 승인 게이트 · 조치 · 티켓이 파일마다 따로 있고, 한 알림의 오류가 전체 처리를 멈춥니다</mark>.
- **만드는 것**: 조치 요청 · 조치 실행 · 승인 게이트 거치기 · 알림 한 건 처리 · 오류 격리(`soar_engine.py`), 처리 결과별 알림 수 세기(`day06_2-1_run.py`).
- **실행하면**: <mark>단계 1: 불러온 알림 수와 승인 기준, 단계 2: 알림마다 처리 결과와 승인 게이트의 결정, 단계 3: 처리 결과별 알림 수, 단계 4: 저장한 로그와 티켓 파일이 나옵니다.</mark>

**🎯 할 일**: 두 파일을 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행한 뒤 단계 2 를 알림마다 읽습니다.

**`soar_engine.py`** — 엔진 함수 모음입니다. 3교시가 가져와 사용(import)합니다. 4교시는 이 파일을 가져오지 않고 엔진이 남긴 로그 파일을 읽습니다. 직접 쓰는 곳은 1 ~ 8번입니다.

- 1번 · 2번 · 3번은 `if` · `else` 줄이 미리 채워져 있어서 그 아래에 들여쓴 한 줄만 씁니다.
- 5번과 6번은 `if` 한 줄만 씁니다. 그 아래 미리 채운 줄이 `if` 안쪽입니다.
- 7번은 `try:` 아래에 한 줄, 8번은 `except` 줄 한 줄을 씁니다. 8번 아래 미리 채운 줄이 `except` 안쪽입니다.

```python
from incident import load_json, match_playbooks                                         # 월요일 파일의 JSON 읽기 · 플레이북 찾기 함수를 불러온다
from containment_store import new_state                                                 # 수요일 파일의 연습용 시스템 상태 함수를 불러온다
from account_actions import lock_account                                                # 수요일 파일의 계정 잠금 함수를 불러온다
from ip_actions import block_ip, count_users_on_ip, DEFAULT_TTL                         # 수요일 파일의 IP 차단 · 사용 계정 수 세기 함수와 차단 유지 시간을 불러온다
from approval_gate import decide_gate                                                   # 금요일 파일의 승인 게이트 함수를 불러온다
from ticketing import make_ticket, NEXT_STEPS                                           # 목요일 파일의 티켓 함수와 다음 할 일 딕셔너리를 불러온다

ENGINE_REASON = "자동 대응 엔진"                                                        # 조치 기록의 이유에 적는 실행 주체
CONTAINMENT_ACTIONS = ["계정 잠금", "IP 차단"]                                          # 승인 게이트를 거쳐 실행하는 조치 이름
TICKET_STATUS = {"자동 실행": "조치됨", "승인 대기": "승인 대기", "차단 금지": "조치 없음", "조치 없음": "조치 없음"}  # 처리 결과를 목요일 티켓의 알림 상태 이름으로 바꾸는 딕셔너리


def load_context():                                                                     # 인자가 없는 함수
    """설정 파일 네 개를 읽고 새 연습용 시스템 상태를 만들어 딕셔너리 하나로 리턴한다. 엔진이 알림을 처리하는 데 쓰는 재료를 한 번에 준비할 때 쓴다."""
    context = {                                                                         # 엔진이 쓰는 재료를 담을 딕셔너리
        "registry": load_json("config/playbook_registry.json"),                         # 플레이북 리스트
        "policy": load_json("config/approval_policy.json"),                             # 승인 게이트 정책
        "ip_users": load_json("ip_users.json"),                                         # IP 별 사용 계정 딕셔너리
        "ticket_rules": load_json("config/escalation_rules.json"),                      # 등급별 응답 기한(분) 설정
        "state": new_state(),                                                           # 연습용 시스템 상태 : 실행할 때마다 처음 상태에서 시작한다
        "tickets": [],                                                                  # 만든 티켓을 모을 빈 리스트
    }
    return context                                                                      # 재료 딕셔너리를 리턴한다


def make_request(alert, action, context):                                               # 알림 · 조치 이름 · 엔진 재료를 받는 함수
    """알림 한 건과 조치 이름으로 승인 게이트가 읽는 조치 요청 딕셔너리를 만든다. 위험 점수에 쓰는 「그 IP 를 함께 쓰는 계정 수」를 채울 때 쓴다."""
    users_on_ip = 0                                                                     # 그 IP 를 쓰는 계정 수 : 계정 조치이면 0 — 미리 채운 줄
    if action == "IP 차단":                                                             # 조치가 IP 차단이면 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 1. count_users_on_ip(alert["entity"], context["ip_users"]) 의 결과를 users_on_ip 에 저장한다
    request = {                                                                         # 승인 게이트가 읽는 조치 요청 한 건 — 미리 채운 줄
        "id": alert["id"],                                                              # 요청 번호는 알림 번호를 쓴다
        "incident": alert["id"],                                                        # 인시던트 번호
        "action": action,                                                               # 조치 이름
        "target": alert["entity"],                                                      # 조치 대상(계정 또는 IP)
        "grade": alert["grade"],                                                        # 알림 등급
        "users_on_ip": users_on_ip,                                                     # 그 IP 를 쓰는 계정 수
        "target_count": 1,                                                              # 알림 한 건은 대상 하나를 조치한다
    }
    return request                                                                      # 조치 요청을 리턴한다 — 미리 채운 줄


def execute_action(request, context):                                                   # 조치 요청과 엔진 재료를 받는 함수
    """계정 잠금이면 lock_account, IP 차단이면 block_ip 로 조치를 실행하고 조치 기록 한 건을 리턴한다. 승인 게이트가 자동으로 정한 조치를 실제로 실행할 때 쓴다."""
    state = context["state"]                                                            # 연습용 시스템 상태 — 미리 채운 줄
    vip_accounts = context["policy"]["vip_accounts"]                                    # VIP 계정 리스트 — 미리 채운 줄
    if request["action"] == "계정 잠금":                                                # 조치가 계정 잠금이면 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 2. lock_account(request["target"], state, vip_accounts, request["incident"], ENGINE_REASON) 의 결과를 record 에 저장한다
    else:                                                                               # 아니면 IP 차단이다 — 미리 채운 줄
        # 3. block_ip(request["target"], state, request["incident"], ENGINE_REASON, DEFAULT_TTL) 의 결과를 record 에 저장한다
    return record                                                                       # 조치 기록을 리턴한다 — 미리 채운 줄


def run_step(alert, action, context):                                                   # 알림 · 조치 이름 · 엔진 재료를 받는 함수
    """조치 하나를 승인 게이트에 묻고, 자동으로 정해졌을 때만 실행해서 결정 · 이유 · 실행 여부를 담은 딕셔너리를 리턴한다. 조치마다 한 번씩 쓴다."""
    request = make_request(alert, action, context)                                      # 승인 게이트에 보낼 조치 요청을 만든다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. decide_gate(request, context["policy"]) 의 두 결과를 decision, reasons 에 저장한다
    step = {                                                                            # 조치 하나의 결과 : 처음에는 실행하지 않은 것으로 적는다 — 미리 채운 줄
        "action": action,                                                               # 조치 이름
        "target": alert["entity"],                                                      # 조치 대상
        "decision": decision,                                                           # 승인 게이트의 결정
        "reasons": reasons,                                                             # 결정 이유 리스트
        "executed": False,                                                              # 실행했는지
        "before": "",                                                                   # 조치 전 상태
        "after": "",                                                                    # 조치 후 상태
        "request": request,                                                             # 승인 게이트가 본 조치 요청(나중에 점검할 때 다시 쓴다)
    }
    # 5. decision 이 "자동" 이면 (if, ==)
        record = execute_action(request, context)                                       # 조치를 실행하고 조치 기록을 받는다 — 미리 채운 줄
        step["executed"] = True                                                         # 실행했다고 적는다 — 미리 채운 줄
        step["before"] = record["before"]                                               # 조치 전 상태를 적는다 — 미리 채운 줄
        step["after"] = record["after"]                                                 # 조치 후 상태를 적는다 — 미리 채운 줄
    return step                                                                         # 조치 하나의 결과를 리턴한다 — 미리 채운 줄


def decide_outcome(steps):                                                              # 조치 결과 리스트를 받는 함수
    """조치 결과들로 알림 전체의 처리 결과(승인 대기 · 차단 금지 · 자동 실행 · 조치 없음)를 정한다. 사람이 먼저 봐야 하는 결과부터 판단한다."""
    decisions = []                                                                      # 조치마다 승인 게이트의 결정을 모을 빈 리스트
    for step in steps:                                                                  # 조치 결과를 하나씩 꺼낸다
        decisions.append(step["decision"])                                              # 결정을 추가한다
    if "승인 필요" in decisions:                                                        # 승인이 필요한 조치가 있으면
        return "승인 대기"                                                              # 사람의 승인을 기다리는 알림이다
    if "차단 금지" in decisions:                                                        # 차단 금지인 조치가 있으면
        return "차단 금지"                                                              # 실행하지 않은 알림이다
    if "자동" in decisions:                                                             # 자동으로 정해진 조치가 있으면
        return "자동 실행"                                                              # 자동으로 실행한 알림이다
    return "조치 없음"                                                                  # 승인 게이트를 거칠 조치가 없으면 조치 없음이다


def open_ticket(alert, steps, playbook_id, outcome, context):                           # 알림 · 조치 결과 리스트 · 플레이북 번호 · 처리 결과 · 엔진 재료를 받는 함수
    """처리 결과를 목요일 티켓 형식의 알림으로 바꿔 make_ticket 으로 티켓을 만들고 티켓 리스트에 추가한다. 조치를 했든 안 했든 담당자가 볼 티켓을 남길 때 쓴다."""
    done_list = []                                                                      # 실행한 조치를 「조치: 전 → 후」 문장으로 모을 빈 리스트
    for step in steps:                                                                  # 조치 결과를 하나씩 꺼낸다
        if step["executed"]:                                                            # 실행한 조치이면
            done_text = step["action"] + ": " + step["before"] + " → " + step["after"]  # 조치와 전 · 후 상태를 한 문장으로 만든다
            done_list.append(done_text)                                                 # 문장을 추가한다
    rule_text = ", ".join(alert["reasons"])                                             # 탐지된 규칙 이름을 쉼표로 이어 한 문자열로 만든다
    ticket_alert = {                                                                    # 목요일 티켓 함수가 읽는 알림 모양
        "id": alert["id"],                                                              # 알림 번호
        "minute": 0,                                                                    # 엔진을 실행한 시각 : 0분
        "entity": alert["entity"],                                                      # 대상
        "rule": rule_text,                                                              # 탐지된 규칙
        "grade": alert["grade"],                                                        # 등급
        "status": TICKET_STATUS[outcome],                                               # 처리 결과에 맞는 알림 상태
        "playbook": playbook_id,                                                        # 플레이북 번호
        "done": done_list,                                                              # 실행한 조치 문장 리스트
    }
    ticket_no = len(context["tickets"]) + 1                                             # 지금까지 만든 티켓 수에 1 을 더해 번호를 만든다
    ticket = make_ticket(ticket_alert, ticket_no, context["ticket_rules"], NEXT_STEPS)  # 목요일 함수로 티켓을 만든다
    context["tickets"].append(ticket)                                                   # 티켓 리스트에 추가한다
    return ticket                                                                       # 만든 티켓을 리턴한다


def run_soar_pipeline(alert, context):                                                  # 알림 한 건과 엔진 재료를 받는 함수
    """알림 한 건을 플레이북 찾기 → 조치마다 승인 게이트 → 티켓 만들기 순서로 처리하고 결과 기록 한 건을 리턴한다. 알림마다 한 번씩 쓴다."""
    playbooks = match_playbooks(alert, context["registry"])                             # 월요일 함수로 맞는 플레이북을 찾는다 — 미리 채운 줄
    playbook_id = "없음"                                                                # 맞는 플레이북이 없으면 「없음」으로 남긴다 — 미리 채운 줄
    steps = []                                                                          # 조치마다 결과를 모을 빈 리스트 — 미리 채운 줄
    for playbook in playbooks:                                                          # 맞는 플레이북을 하나씩 꺼낸다 — 미리 채운 줄
        playbook_id = playbook["id"]                                                    # 플레이북 번호를 적는다 — 미리 채운 줄
        for action in playbook["actions"]:                                              # 플레이북의 액션을 하나씩 꺼낸다 — 미리 채운 줄
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            # 6. action 이 CONTAINMENT_ACTIONS 안에 있으면 (if, in)
                step = run_step(alert, action, context)                                 # 승인 게이트를 거쳐 실행한다 — 미리 채운 줄
                steps.append(step)                                                      # 조치 결과를 추가한다 — 미리 채운 줄
    outcome = decide_outcome(steps)                                                     # 알림 전체의 처리 결과를 정한다 — 미리 채운 줄
    ticket = open_ticket(alert, steps, playbook_id, outcome, context)                   # 티켓을 만든다 — 미리 채운 줄
    result = {                                                                          # 알림 한 건의 결과 기록 — 미리 채운 줄
        "incident": alert["id"],                                                        # 알림 번호
        "entity": alert["entity"],                                                      # 대상
        "grade": alert["grade"],                                                        # 등급
        "playbook": playbook_id,                                                        # 플레이북 번호
        "outcome": outcome,                                                             # 처리 결과
        "steps": steps,                                                                 # 조치마다 결과 리스트
        "ticket": ticket["id"],                                                         # 티켓 번호
        "error": "",                                                                    # 오류 문장 : 정상이면 비어 있다
    }
    return result                                                                       # 결과 기록을 리턴한다 — 미리 채운 줄


def make_failure_result(alert, error):                                                  # 알림 한 건과 오류를 받는 함수
    """처리하지 못한 알림의 결과 기록 한 건을 만든다. 오류 이름과 내용을 남겨 담당자가 어떤 알림이 왜 멈췄는지 알 수 있게 할 때 쓴다."""
    error_name = type(error).__name__                                                   # 오류의 종류 이름(예: KeyError)
    error_text = error_name + ": " + str(error)                                         # 오류 이름과 내용을 한 문장으로 만든다
    result = {                                                                          # 실패한 알림의 결과 기록
        "incident": alert.get("id", "번호 없음"),                                       # 알림 번호 : 키가 없으면 「번호 없음」
        "entity": alert.get("entity", ""),                                              # 대상 : 키가 없으면 빈 문자열
        "grade": alert.get("grade", ""),                                                # 등급 : 키가 없으면 빈 문자열
        "playbook": "없음",                                                             # 플레이북을 찾기 전에 멈췄을 수 있다
        "outcome": "실패",                                                              # 처리 결과는 실패
        "steps": [],                                                                    # 실행한 조치 없음
        "ticket": "",                                                                   # 티켓 없음
        "error": error_text,                                                            # 오류 문장
    }
    return result                                                                       # 실패 기록을 리턴한다


def run_all(alerts, context):                                                           # 알림 리스트와 엔진 재료를 받는 함수
    """알림을 하나씩 처리하되, 오류가 난 알림은 실패 기록만 남기고 다음 알림으로 넘어간다. 알림 하나의 오류가 나머지 알림의 처리를 막지 않게 할 때 쓴다."""
    results = []                                                                        # 알림마다 결과 기록을 모을 빈 리스트 — 미리 채운 줄
    for alert in alerts:                                                                # 알림을 하나씩 꺼낸다 — 미리 채운 줄
        try:                                                                            # 오류가 날 수 있는 처리를 시작한다 — 미리 채운 줄
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            # 7. run_soar_pipeline(alert, context) 의 결과를 result 에 저장한다
        # 8. 어떤 종류의 오류든 error 에 저장해 받는다 (except, Exception, as)
            result = make_failure_result(alert, error)                                  # 실패 기록을 만든다 — 미리 채운 줄
        results.append(result)                                                          # 정상 결과든 실패 기록이든 결과 리스트에 추가한다 — 미리 채운 줄
    return results                                                                      # 결과 기록 리스트를 리턴한다 — 미리 채운 줄
```

**`day06_2-1_run.py`** — 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다.

```python
from incident import load_json, save_json                                                # 월요일 파일의 JSON 읽기 · 쓰기 함수를 불러온다
from soar_engine import load_context, run_all                                            # 방금 만든 엔진 함수를 불러온다

LOG_PATH = "engine_log.json"                                                             # 처리 결과를 저장할 파일 이름
TICKET_PATH = "engine_tickets.json"                                                      # 만든 티켓을 저장할 파일 이름

context = load_context()                                                                 # 플레이북 · 승인 정책 · 설정 · 연습용 시스템 상태를 한꺼번에 읽는다
alerts = load_json("engine_alerts.json")                                                 # 오늘 들어온 알림 파일을 리스트로 읽는다
print("--- 단계 1: 불러온 알림", len(alerts), "건 · 플레이북", len(context["registry"]), "개 · 승인 기준", context["policy"]["approval_score"], "점")  # 단계 1 시작을 알리는 줄

results = run_all(alerts, context)                                                       # 알림을 하나씩 엔진으로 처리한다
counts = {"자동 실행": 0, "승인 대기": 0, "차단 금지": 0, "조치 없음": 0, "실패": 0}     # 처리 결과마다 알림 수 : 처음에는 모두 0
print("--- 단계 2: 알림마다 처리 결과")                                                  # 단계 2 시작을 알리는 줄
for result in results:                                                                   # 결과 기록을 하나씩 꺼낸다
    outcome = result["outcome"]                                                          # 이 알림의 처리 결과 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 9. counts[outcome] 에 counts[outcome] + 1 을 저장한다 (1 늘린다)
    if outcome == "실패":                                                                # 처리하지 못한 알림이면
        print(result["incident"], result["entity"], "→", outcome, "·", result["error"])  # 알림과 오류를 출력한다
    else:                                                                                # 처리한 알림이면
        print(result["incident"], result["entity"], result["grade"], "→", outcome, "·", result["playbook"], "· 티켓", result["ticket"])  # 알림과 처리 결과를 출력한다
    for step in result["steps"]:                                                         # 조치 결과를 하나씩 꺼낸다
        reason_text = ", ".join(step["reasons"])                                         # 결정 이유 리스트를 쉼표로 이어 한 문자열로 만든다
        print("   ", step["action"], step["target"], "→", step["decision"], "·", reason_text)  # 조치와 승인 게이트의 결정을 출력한다
        if step["executed"]:                                                             # 실행한 조치이면
            print("   ", "실행:", step["before"], "→", step["after"])                    # 조치 전 · 후 상태를 출력한다

print("--- 단계 3: 처리 결과별 알림 수")                                                 # 단계 3 시작을 알리는 줄
for outcome in counts:                                                                   # 처리 결과 이름을 하나씩 꺼낸다
    print(outcome, ":", counts[outcome], "건")                                           # 결과 이름과 알림 수를 출력한다

save_json(results, LOG_PATH)                                                             # 결과 기록 리스트를 파일에 저장한다
save_json(context["tickets"], TICKET_PATH)                                               # 만든 티켓 리스트를 파일에 저장한다
print("--- 단계 4:", LOG_PATH, "에", len(results), "건 ·", TICKET_PATH, "에 티켓", len(context["tickets"]), "장 저장")  # 단계 4 시작을 알리는 줄과 저장한 수
```

**순서**

1. **[터미널]** 파일 두 개를 만들고 **[VS Code]** 에서 열어 붙여 넣습니다.
   ```bash
   pwd
   touch soar_engine.py day06_2-1_run.py
   ls
   ```
2. **[VS Code]** `soar_engine.py` 1 ~ 8번, `day06_2-1_run.py` 9번을 씁니다. 막히면 위 문법 상자와 아래 「2교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 가 `soar_response` 로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   python day06_2-1_run.py
   ```
4. 출력은 네 단계입니다. 제목 줄은 줄 수에 넣지 않습니다.
   - 단계 1 과 단계 4 는 숫자가 제목 줄에 함께 나와 그 아래 줄이 없습니다.
   - 단계 2 는 알림마다 1줄이고, 조치가 있는 알림은 조치마다 1 ~ 2줄이 더 붙습니다. 단계 3 은 5줄입니다.
5. **[VS Code]** 새로 생긴 `engine_log.json` 과 `engine_tickets.json` 을 열어 <mark>`INC-402` 의 `error` 와 `TCK-1` 의 `done`</mark> 을 읽습니다.
6. **[보고서]** `day06_am_report.md` 의 `## 2교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 처리 결과별 알림 수와 승인 대기인 알림 번호를 적어 주세요.
   - (나) 🔍 `INC-402` 는 실패인데 `INC-403` ~ `INC-408` 은 처리됐습니다. 단계 2 의 `INC-402` 오류 문장과 `run_all` 의 `except` 줄을 근거로 그 이유를 적고, `try` / `except` 가 없으면 `INC-402` 이후의 알림이 어떻게 되는지 적어 주세요.
   - (다) 🔍 `INC-404` 와 `INC-406` 은 둘 다 high 등급인데 결과가 「차단 금지」와 「승인 대기」로 다릅니다. 단계 2 의 결정 이유를 근거로 그 차이를 적고, 승인 게이트가 `execute_action` 보다 먼저 와야 하는 이유도 적어 주세요.

### 2교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 함수 결과를 변수에 저장하기 | `users_on_ip = count_users_on_ip(alert["entity"], context["ip_users"])` |
| 두 결과를 함께 받기 | `decision, reasons = decide_gate(request, context["policy"])` |
| 같으면 | `if decision == "자동":` |
| 리스트 안에 있으면 | `if action in CONTAINMENT_ACTIONS:` |
| 어떤 종류의 오류든 받기 | `except Exception as error:` |
| 1 늘려 다시 저장하기 | `counts[outcome] = counts[outcome] + 1` |
---
# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">3교시 (11:00–11:50) · 4과목 탐지 결과 5건을 엔진의 입력으로 바꾸고, 모양을 점검한 뒤 실행해 운영 요약 만들기 (종단간 연결)</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: <mark style="background:#e0d4ff">4과목에서 `risk_scores.py` 가 대상별 점수 · 등급 · 이유를 `day03_risk_scores.json` 에 저장했습니다.</mark> `dami`(60점 high) · `seoyeon`(45점 mid) · `gaeun`(40점 mid) · `jiwoo`(35점 mid) · `198.51.100.90`(30점 low) 5건입니다. 2교시 엔진은 월요일 `incident_samples.json` 과 같은 모양의 알림을 읽습니다. 오늘 아침 팀장이 「4과목에서 탐지된 5건을 엔진으로 처리하고, 무엇을 실행했는지 한 장으로 보고해 달라」고 요청합니다.
> - **문제**: 4과목 파일에는 알림 번호(`id`)와 상태(`status`)가 없어서 엔진에 바로 넣을 수 없습니다. 4과목과 5과목은 따로 만든 프로그램이라, 4과목 파일의 모양이 바뀌면(필수 키가 빠지거나 등급 이름이 늘면) 엔진 안에서 오류가 납니다. 엔진 안에서 잡힌 오류는 그 알림의 조치와 티켓이 없는 「실패」로만 남습니다(2교시 `INC-402`). <mark style="background:#ffc4d6">어느 기록이 왜 못 들어갔는지 엔진 앞에서 이유와 함께 남기지 않으면 탐지된 대상이 사라집니다.</mark>
> - **부탁**: 4과목 탐지 결과를 엔진이 읽는 알림으로 바꾸되, 바꾸기 전에 모양을 점검해 문제가 있는 기록은 이유와 함께 따로 모아 주세요. 엔진을 실행한 뒤에는 처리 결과별 알림 수 · 티켓 수 · 실제로 실행한 조치를 운영 요약으로 정리해 주세요.
> - **바뀌는 점**: 5건이 알림 `INC-501` ~ `INC-505` 로 바뀌어 모두 엔진에 들어가고(거절 <mark style="background:#bde3ff">0건</mark>), <mark style="background:#bde3ff">자동 실행 2건</mark>(`dami` 잠금 · `198.51.100.90` 차단)과 <mark style="background:#bde3ff">조치 없음 3건</mark>으로 처리됩니다. 티켓 <mark style="background:#bde3ff">5장</mark>이 만들어지고, 운영 요약은 `engine_summary.json` 에 저장됩니다. 상황과 숫자는 설명을 위한 예시입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다.

### 📖 3.1 엔진 앞에서는 입력의 모양을 점검하고(입력 검증), 엔진 뒤에서는 결과를 운영 요약으로 정리한다

| 4과목 `day03_risk_scores.json` 의 키 | 엔진이 읽는 알림의 키 | 하는 일 |
|---|---|---|
| `entity` · `score` · `grade` · `reasons` | 같은 이름 | 값을 그대로 옮긴다 |
| (없음) | `id` | `INC-501` 부터 번호를 붙인다 (3번) |
| (없음) | `status` | 처음 상태인 `탐지됨` 을 적는다 (4번) |

- 4과목의 출력과 5과목의 입력이 같은 키 이름과 모양을 쓰기로 정한 약속을 공통 스키마(common schema, 커먼 스키마: 프로그램끼리 주고받는 데이터의 키 이름과 모양을 미리 정한 약속)라고 합니다. 오늘 엔진의 공통 스키마는 <mark style="background:#e0d4ff">월요일 `incident_samples.json` 의 알림 모양</mark>입니다.
- 입력 검증(input validation, 인풋 밸리데이션: 데이터를 처리하기 전에 필수 키와 값의 범위가 맞는지 확인하는 일)에서는 <mark>필수 키가 있는지(1번), 등급 이름을 엔진이 아는지(2번)</mark> 점검합니다. 탐지된 규칙 이름이 비어 있는 기록도 거절합니다.
- 문제가 있는 기록은 버리지 않고 이유와 함께 거절 리스트(`rejected`)에 모읍니다. 거절 리스트가 있으면 4과목 파일을 고쳐야 하는지 알 수 있습니다.
- 방어는 두 겹입니다. 엔진 앞의 입력 검증은 <mark>알려진 문제를 이유와 함께 걸러 내고</mark>, 2교시의 오류 격리는 <mark>걸러 내지 못한 문제가 다른 알림으로 번지지 않게</mark> 합니다.
- 운영 요약은 근무를 인계하거나 보고할 때 한 번에 보여 주는 정리입니다. 오늘은 처리 결과별 알림 수(7번), 티켓 수, 실제로 실행한 조치(8번)를 담습니다. <mark>실제로 실행한 조치는 `executed` 가 참인 조치만 모읍니다.</mark>
- 4과목의 등급은 점수로 정해지고(60점 이상 high, 35점 이상 mid, 그 아래 low), 엔진은 이 등급을 그대로 승인 게이트의 `grade` 로 씁니다.

함수 네 개와 실행 파일 가운데 직접 쓰는 곳은 **아홉 군데**입니다.

```
engine_input.py   find_schema_problem  : 필수 키가 없으면 (1번) · 모르는 등급이면 (2번) 이유를 리턴한다
                  make_alert           : 알림 번호를 만들고 (3번) 4과목 기록을 알림 딕셔너리로 바꾼다 (4번)
                  split_records        : 기록마다 점검하고 (5번) 문제가 없으면 (6번) 알림 리스트에 넣는다
                  summarize            : 처리 결과별 알림 수를 세고 (7번) 실행한 조치만 (8번) 모은다
실행 파일         day06_3-1_run.py     : 엔진을 실행한다 (9번)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 3-1 · 4과목 탐지 결과 5건을 점검해 엔진의 입력으로 바꾸고, 엔진을 실행해 운영 요약 만들기</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>4과목 탐지 결과 파일은 있지만 엔진이 읽는 알림 모양이 아니고, 엔진을 실행한 결과를 한눈에 보고할 요약이 없습니다</mark>.
- **만드는 것**: 모양 점검 · 알림으로 바꾸기 · 기록 나누기 · 운영 요약(`engine_input.py`), 엔진 실행과 출력(`day06_3-1_run.py`).
- **실행하면**: <mark>단계 1: 4과목 탐지 결과 수, 단계 2: 일부러 틀리게 만든 기록 두 건의 점검 결과, 단계 3: 엔진에 넣을 알림, 단계 4: 알림마다 엔진 처리 결과, 단계 5: 운영 요약, 단계 6: 저장한 파일이 나옵니다.</mark>

**🎯 할 일**: 데이터 파일 한 개와 코드 파일 두 개를 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행해서 단계 3 ~ 5 를 읽습니다.

**`day03_risk_scores.json`** — 4과목 11/5(목) 오후 6교시 파일입니다. 4과목 폴더(`anomaly_detection`)에 이 파일이 있으면 `cp ../anomaly_detection/day03_risk_scores.json .` 으로 복사하고, 없으면 만들어 붙여 넣습니다.

- 대상(`entity`)은 계정 이름 또는 IP, 점수(`score`)는 탐지된 규칙의 점수를 더한 값, 등급(`grade`)은 점수로 정한 high · mid · low 이고, 이유(`reasons`)는 탐지된 규칙 이름 리스트입니다.

```
[
  {
    "entity": "dami",
    "score": 60,
    "grade": "high",
    "reasons": [
      "퇴사한 계정"
    ]
  },
  {
    "entity": "seoyeon",
    "score": 45,
    "grade": "mid",
    "reasons": [
      "평소와 다른 IP",
      "대량 다운로드"
    ]
  },
  {
    "entity": "gaeun",
    "score": 40,
    "grade": "mid",
    "reasons": [
      "규칙은 허용인데 서버가 거절",
      "여러 로그 연결"
    ]
  },
  {
    "entity": "jiwoo",
    "score": 35,
    "grade": "mid",
    "reasons": [
      "업무 시간 밖 로그인",
      "평소와 다른 IP"
    ]
  },
  {
    "entity": "198.51.100.90",
    "score": 30,
    "grade": "low",
    "reasons": [
      "경로 스캔"
    ]
  }
]
```

**`engine_input.py`** — 4과목 연결 함수 모음입니다. 4교시는 가져오지 않습니다. 직접 쓰는 곳은 1 ~ 8번입니다.

- 1번 · 2번 · 6번 · 8번은 `if` 한 줄만 쓰고, 그 아래 미리 채운 줄이 `if` 안쪽입니다. 7번은 한 줄을 쓰고, 4번은 딕셔너리라서 줄을 나눠 씁니다.

```python
REQUIRED_KEYS = ["entity", "score", "grade", "reasons"]              # 4과목 결과 기록에 반드시 있어야 하는 키
GRADES = ["high", "mid", "low"]                                      # 엔진이 읽을 수 있는 등급 이름
FIRST_NUMBER = 501                                                   # 엔진이 붙이는 알림 번호의 시작 (INC-501 부터)


def find_schema_problem(record):                                     # 4과목 결과 기록 한 건을 받는 함수
    """엔진이 읽을 수 없는 기록이면 그 이유 문장을, 문제가 없으면 빈 문자열("")를 리턴한다. 4과목 파일의 모양이 바뀌었을 때 엔진이 오류를 내기 전에 걸러 낼 때 쓴다."""
    for key in REQUIRED_KEYS:                                        # 필수 키를 하나씩 꺼낸다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 1. key 가 record 안에 없으면 (if, not in)
            return "필수 키 없음: " + key                            # 어떤 키가 없는지 이유로 리턴한다 — 미리 채운 줄
    # 2. record["grade"] 가 GRADES 안에 없으면 (if, not in)
        return "알 수 없는 등급: " + record["grade"]                 # 등급 이름을 이유로 리턴한다 — 미리 채운 줄
    if record["reasons"] == []:                                      # 탐지된 규칙 리스트가 비어 있으면 — 미리 채운 줄
        return "탐지된 규칙이 없음"                                  # 이유를 리턴한다 — 미리 채운 줄
    return ""                                                        # 문제가 없으면 빈 문자열를 리턴한다 — 미리 채운 줄


def make_alert(record, number):                                      # 4과목 결과 기록 한 건과 알림 번호 숫자를 받는 함수
    """4과목 결과 기록(대상 · 점수 · 등급 · 이유)에 알림 번호와 상태를 붙여 월요일 인시던트 모양의 딕셔너리로 리턴한다. 4과목 파일의 기록을 엔진의 입력으로 바꿀 때 쓴다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. "INC-" 뒤에 str(number) 를 이어 붙여 alert_id 에 저장한다
    # 4. 키 "id"(alert_id) · "entity" · "grade" · "score" · "reasons"(record 의 같은 이름 키의 값), "status"("탐지됨") 를 가진 딕셔너리를 alert 에 저장한다
    return alert                                                     # 엔진이 읽을 알림을 리턴한다 — 미리 채운 줄


def split_records(records):                                          # 4과목 결과 기록 리스트를 받는 함수
    """기록마다 모양을 점검해 엔진에 넣을 알림 리스트와 거절한 기록 리스트를 만들고 두 리스트를 함께 리턴한다. 거절한 기록을 이유와 함께 남겨 기록 없이 빠지지 않게 할 때 쓴다."""
    alerts = []                                                      # 엔진에 넣을 알림을 모을 빈 리스트 — 미리 채운 줄
    rejected = []                                                    # 거절한 기록과 이유를 모을 빈 리스트 — 미리 채운 줄
    number = FIRST_NUMBER                                            # 다음에 붙일 알림 번호 — 미리 채운 줄
    for record in records:                                           # 기록을 하나씩 꺼낸다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. find_schema_problem(record) 의 결과를 problem 에 저장한다
        # 6. problem 이 "" 이면 (if, ==)
            alert = make_alert(record, number)                       # 알림 모양으로 바꾼다 — 미리 채운 줄
            alerts.append(alert)                                     # 알림 리스트에 추가한다 — 미리 채운 줄
            number = number + 1                                      # 다음 번호로 넘어간다 — 미리 채운 줄
        else:                                                        # 문제가 있으면 — 미리 채운 줄
            rejected.append({"record": record, "problem": problem})  # 기록과 이유를 거절 리스트에 추가한다 — 미리 채운 줄
    return alerts, rejected                                          # 두 리스트를 함께 리턴한다 — 미리 채운 줄


def summarize(results):                                              # 엔진 결과 기록 리스트를 받는 함수
    """결과 기록을 모아 처리 결과별 알림 수 · 만든 티켓 수 · 실제로 실행한 조치 문장 리스트를 담은 요약 딕셔너리를 리턴한다. 운영 담당자가 한 번에 볼 요약이 필요할 때 쓴다."""
    outcome_counts = {"자동 실행": 0, "승인 대기": 0, "차단 금지": 0, "조치 없음": 0, "실패": 0}  # 처리 결과마다 알림 수 : 처음에는 모두 0 — 미리 채운 줄
    ticket_count = 0                                                 # 만든 티켓 수 : 처음에는 0 — 미리 채운 줄
    executed_actions = []                                            # 실제로 실행한 조치 문장을 모을 빈 리스트 — 미리 채운 줄
    for result in results:                                           # 결과 기록을 하나씩 꺼낸다 — 미리 채운 줄
        outcome = result["outcome"]                                  # 이 알림의 처리 결과 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 7. outcome_counts[outcome] 에 outcome_counts[outcome] + 1 을 저장한다 (1 늘린다)
        if result["ticket"] != "":                                   # 티켓이 있으면 — 미리 채운 줄
            ticket_count = ticket_count + 1                          # 티켓 수를 1 늘린다 — 미리 채운 줄
        for step in result["steps"]:                                 # 조치 결과를 하나씩 꺼낸다 — 미리 채운 줄
            # 8. step["executed"] 가 참이면 (if)
                action_text = result["incident"] + " " + step["action"] + " " + step["target"] + ": " + step["before"] + " → " + step["after"]  # 알림 · 조치 · 대상 · 전 · 후 상태를 한 문장으로 만든다 — 미리 채운 줄
                executed_actions.append(action_text)                 # 문장을 추가한다 — 미리 채운 줄
    summary = {"outcome_counts": outcome_counts, "ticket_count": ticket_count, "executed_actions": executed_actions}  # 요약 딕셔너리 — 미리 채운 줄
    return summary                                                   # 요약을 리턴한다 — 미리 채운 줄
```

**`day06_3-1_run.py`** — 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다.

```python
from incident import load_json, save_json                                                    # 월요일 파일의 JSON 읽기 · 쓰기 함수를 불러온다
from soar_engine import load_context, run_all                                                # 2교시에 만든 엔진 함수를 불러온다
from engine_input import find_schema_problem, split_records, summarize                       # 방금 만든 연결 함수를 불러온다

TEST_RECORDS = [                                                                             # 모양을 일부러 틀리게 만든 시험 기록 두 건
    {"entity": "hana", "score": 40, "reasons": ["업무 시간 밖 로그인"]},                     # grade 키가 없다
    {"entity": "minsu", "score": 90, "grade": "critical", "reasons": ["퇴사한 계정"]},       # 엔진이 모르는 등급 이름이다
]

records = load_json("day03_risk_scores.json")                                                # 4과목이 저장한 탐지 결과 파일을 리스트로 읽는다
print("--- 단계 1: 4과목 탐지 결과", len(records), "건")                                     # 단계 1 시작을 알리는 줄과 건수

print("--- 단계 2: 모양 점검 시험 (일부러 틀린 기록)")                                       # 단계 2 시작을 알리는 줄
for test_record in TEST_RECORDS:                                                             # 시험 기록을 하나씩 꺼낸다
    test_problem = find_schema_problem(test_record)                                          # 모양 점검 결과를 받는다
    print(test_record["entity"], "→", test_problem)                                          # 대상과 점검 결과를 출력한다

alerts, rejected = split_records(records)                                                    # 기록을 엔진에 넣을 알림과 거절한 기록으로 나눈다
print("--- 단계 3: 엔진에 넣을 알림", len(alerts), "건 · 거절한 기록", len(rejected), "건")  # 단계 3 시작을 알리는 줄과 건수
for alert in alerts:                                                                         # 알림을 하나씩 꺼낸다
    print(alert["id"], alert["entity"], alert["grade"], alert["score"], alert["reasons"])    # 알림 번호 · 대상 · 등급 · 점수 · 이유를 출력한다

context = load_context()                                                                     # 엔진이 쓰는 재료를 읽는다
# ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
# 9. run_all(alerts, context) 의 결과를 results 에 저장한다
print("--- 단계 4: 엔진 처리 결과")                                                          # 단계 4 시작을 알리는 줄
for result in results:                                                                       # 결과 기록을 하나씩 꺼낸다
    print(result["incident"], result["entity"], "→", result["outcome"], "·", result["playbook"], "· 티켓", result["ticket"])  # 알림 · 대상 · 처리 결과 · 플레이북 · 티켓을 출력한다

summary = summarize(results)                                                                 # 결과를 모아 운영 요약을 만든다
counts = summary["outcome_counts"]                                                           # 처리 결과별 알림 수 딕셔너리
print("--- 단계 5: 운영 요약")                                                               # 단계 5 시작을 알리는 줄
print("자동 실행", counts["자동 실행"], "건 · 승인 대기", counts["승인 대기"], "건 · 차단 금지", counts["차단 금지"], "건 · 조치 없음", counts["조치 없음"], "건 · 실패", counts["실패"], "건")  # 처리 결과별 알림 수를 한 줄로 출력한다
print("티켓", summary["ticket_count"], "건 · 실제로 실행한 조치", len(summary["executed_actions"]), "건")  # 티켓 수와 실행한 조치 수를 출력한다
for action_text in summary["executed_actions"]:                                              # 실행한 조치 문장을 하나씩 꺼낸다
    print(action_text)                                                                       # 문장을 출력한다

save_json(results, "risk_engine_log.json")                                                   # 결과 기록 리스트를 파일에 저장한다
save_json(summary, "engine_summary.json")                                                    # 운영 요약을 파일에 저장한다
save_json(context["tickets"], "risk_tickets.json")                                           # 만든 티켓 리스트를 파일에 저장한다
print("--- 단계 6: risk_engine_log.json · engine_summary.json · risk_tickets.json 저장")     # 단계 6 시작을 알리는 줄
```

**순서**

1. **[터미널]** 파일 세 개를 만들고 **[VS Code]** 에서 열어 붙여 넣습니다. 4과목 파일을 복사했으면 아래 `touch` 에서 `day03_risk_scores.json` 을 뺍니다.
   ```bash
   pwd
   touch day03_risk_scores.json engine_input.py day06_3-1_run.py
   ls
   ```
2. **[VS Code]** `engine_input.py` 1 ~ 8번, `day06_3-1_run.py` 9번을 씁니다. 막히면 아래 「3교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 가 `soar_response` 로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   python day06_3-1_run.py
   ```
4. 출력은 여섯 단계입니다. 제목 줄은 줄 수에 넣지 않습니다.
   - 단계 1 과 단계 6 은 숫자나 파일 이름이 제목 줄에 함께 나와 그 아래 줄이 없습니다.
   - 단계 2 는 2줄, 단계 3 은 제목 줄에 건수가 나오고 그 아래 5줄입니다. 단계 4 는 5줄입니다.
   - 단계 5 는 제목 줄 아래 2줄에 실행한 조치 줄이 더 붙습니다.
5. **[보고서]** `day06_am_report.md` 의 `## 3교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, 단계 5 의 처리 결과별 알림 수와 실제로 실행한 조치 두 개를 적어 주세요.
   - (나) 🔍 `seoyeon` · `gaeun` · `jiwoo` 는 모두 「조치 없음」인데 티켓은 만들어졌습니다. 단계 4 에서 알림 뒤에 나오는 플레이북 번호를 근거로 세 알림에 조치가 없는 이유를 적고, 티켓이 없다면 이 세 알림이 어떻게 되는지 적어 주세요.
   - (다) 🔍 단계 2 의 `minsu` 기록은 등급이 `critical` 입니다. `find_schema_problem` 이 이 기록을 엔진 앞에서 거절하는 이유를 적고, 거절 없이 엔진에 넣으면 어떤 오류가 나고 그 알림이 어떻게 기록되는지 2교시 `INC-402` 와 연결해 적어 주세요.

### 3교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 리스트 안에 없으면 | `if key not in record:` · `if record["grade"] not in GRADES:` |
| 문자열을 이어 붙여 저장하기 | `alert_id = "INC-" + str(number)` |
| 키와 값을 짝지어 딕셔너리 만들기 | `alert = {"id": alert_id, "entity": record["entity"], …}` |
| 함수 결과를 변수에 저장하기 | `problem = find_schema_problem(record)` |
| 같으면 | `if problem == "":` |
| 1 늘려 다시 저장하기 | `outcome_counts[outcome] = outcome_counts[outcome] + 1` |
| 참이면 | `if step["executed"]:` |
---
# <mark style="display:block; background:#c8e6c9; color:#1a1a1a; padding:6px 12px; border-radius:4px">4교시 (12:00–12:50) · 엔진 로그 3개를 정책 네 가지로 점검해 승인 게이트 우회와 허용 목록 · VIP 위반을 찾고, 5일간의 회고 문서 쓰기</mark>

> 📨 **오늘 들어온 일**
>
> - **상황**: 2교시와 3교시에 엔진을 실행하면 처리 결과 로그가 남습니다(`engine_log.json` 8건 · `risk_engine_log.json` 5건). 오늘 아침 고객사 보안 담당자가 「승인 게이트와 허용 목록 · VIP 예외가 정책대로 지켜졌는지 로그로 확인해 달라」고 요청합니다. 시험 운영 때 승인 게이트를 끄고 알림 5건(`INC-401` · `INC-403` ~ `INC-406`)을 처리한 로그 `gate_off_log.json` 도 점검 대상입니다.
> - **문제**: 로그를 사람이 한 줄씩 읽으면 알림이 늘수록 놓치기 쉽습니다. 게다가 로그의 `decision`(결정) 값은 엔진이 적은 값이라서, 게이트를 끈 로그에는 모든 조치가 「자동」으로 적혀 있습니다. <mark style="background:#ffc4d6">결정 값만 읽으면 게이트를 끈 로그에서 위반을 찾지 못합니다.</mark>
> - **부탁**: 로그마다 네 가지(게이트 우회 실행 · 허용 목록 IP 차단 · VIP 계정 잠금 · 티켓 없는 조치)를 자동으로 점검해 PASS · FAIL 표를 만들어 주세요. 게이트 우회 실행은 로그에 저장된 조치 요청으로 <mark style="background:#e0d4ff">금요일의 `decide_gate`</mark> 를 다시 호출해 결정을 새로 구한 뒤, 실행 여부와 비교합니다. 점검이 끝나면 5일간의 회고 문서를 쓰고 저장소에 올려 주세요.
> - **바뀌는 점**: 점검 12개 가운데 <mark style="background:#bde3ff">FAIL 2개</mark>가 나오고, 모두 `gate_off_log.json` 에서 나옵니다. 오늘 2 · 3교시에서 만든 로그 두 개는 점검 8개가 모두 PASS 입니다. 상황과 이름은 설명을 위한 예시입니다.

> 📖 **읽을거리 — 문제가 아닙니다.** 읽고 이해만 합니다.

### 📖 4.1 정책 준수 점검은 로그를 증거로 통제가 실제로 지켜졌는지 확인하고, 엔진이 적은 결정 대신 저장된 입력으로 다시 구한다

| 점검 | 위반으로 보는 것 | 찾는 방법 | 번호 |
|---|---|---|---|
| ① 게이트 우회 실행 | 다시 구한 결정이 「자동」이 아닌데 실행한 조치 | 로그의 `request` 로 `decide_gate` 를 다시 호출 | 1 · 2번 |
| ② 허용 목록 IP 차단 | 조치 후 상태가 「차단됨」인 허용 목록 IP | `target` 과 `after` 를 허용 목록과 비교 | 3번 |
| ③ VIP 계정 잠금 | 조치 후 상태가 「잠김」인 VIP 계정 | `target` 과 `after` 를 VIP 리스트와 비교 | 4번 |
| ④ 티켓 없는 조치 | 실행한 조치가 있는데 `ticket` 이 빈 알림 | `count_executed` 로 센 뒤 `ticket` 확인 | 5번 |

- 정책 준수 점검(policy compliance check)은 통제가 설계한 대로 작동했는지 실제 기록으로 확인하는 일이고, 이때 로그가 증거(audit evidence, 오딧 에비던스: 사실을 뒷받침하는 기록)가 됩니다.
- ①은 재수행(re-performance, 리퍼포먼스: 기록된 입력으로 판단을 다시 계산해 기록된 결과와 비교하는 방법)입니다. 로그의 `request` 는 <mark style="background:#e0d4ff">금요일 승인 게이트가 본 입력</mark>이라서, 같은 정책으로 다시 계산하면 그 조치가 원래 자동이었는지 알 수 있습니다.
- ②와 ③은 불변 조건(invariant, 인베리언트: 어떤 경우에도 항상 지켜져야 하는 조건)을 점검합니다. 게이트의 계산을 거치지 않고 결과만 보므로 <mark>게이트 코드에 오류가 있어도 위반을 찾습니다.</mark>
- <mark style="background:#e0d4ff">수요일의 `lock_account` 는 VIP 계정이면 잠그지 않고 이유를 기록합니다.</mark> 그래서 VIP 계정은 승인 게이트를 꺼도 잠기지 않을 수 있습니다. 다만 방어를 여러 겹 두는 것(다층 방어, defense in depth)과 각 겹을 따로 점검하는 것은 별개입니다.
- 점검 결과는 `judge`(6번)가 PASS 또는 FAIL 로 정하고, 실행 파일이 로그마다 네 줄씩 출력합니다. FAIL 이 나오면 위반한 알림 번호로 로그를 열어 그 알림의 `request` 와 `decision` 을 확인합니다.

함수 일곱 개와 실행 파일 가운데 직접 쓰는 곳은 **아홉 군데**입니다.

```
policy_check.py   count_executed         : 실행한 조치 수를 센다 (미리 채움)
                  find_gate_bypass       : 저장된 조치 요청으로 결정을 다시 구하고 (1번) 자동이 아닌데 실행했으면 (2번) 모은다
                  find_allowlist_blocks  : 허용 목록 IP 가 차단되었으면 (3번) 모은다
                  find_vip_locks         : VIP 계정이 잠겼으면 (4번) 모은다
                  find_missing_tickets   : 실행했는데 티켓이 없으면 (5번) 모은다
                  run_checks             : 점검 네 가지를 한꺼번에 실행한다 (미리 채움)
                  judge                  : 위반이 없으면 PASS 를 리턴한다 (6번)
실행 파일         day06_4-1_run.py       : 로그를 읽고 (7번) 점검에 실패하면 (8번) 세고, 결과를 저장한다 (9번)
```

> ✍️ **여기부터 문제입니다.**

### <mark>✍️ 문제 4-1 · 엔진 로그 3개를 정책 네 가지로 점검해 PASS · FAIL 표 만들기 (정책 준수 점검)</mark>

**📍 이런 상황이 있습니다**

- **지금은**: <mark>엔진은 로그를 남기지만, 승인 게이트와 허용 목록 · VIP 예외가 지켜졌는지 자동으로 확인하는 점검이 없습니다</mark>.
- **만드는 것**: 점검 네 가지와 PASS · FAIL 판정(`policy_check.py`), 로그 세 개를 읽어 점검하고 결과를 저장하기(`day06_4-1_run.py`).
- **실행하면**: <mark>단계 1: 점검할 로그 수, 단계 2: 로그마다 네 점검의 PASS · FAIL 과 위반한 알림 번호, 단계 3: FAIL 이 나온 점검 수, 단계 4: 저장한 파일이 나옵니다.</mark>

**🎯 할 일**: 데이터 파일 한 개와 코드 파일 두 개를 만들어 붙여 넣고 번호 주석 바로 아래에 직접 코드를 씁니다. 실행해서 단계 2 를 읽은 뒤, 회고 문서를 쓰고 깃허브에 올립니다.

**`gate_off_log.json`** — 시험 운영 때 승인 게이트를 끄고(모든 조치 요청의 결정을 「자동」으로 바꾸고) 알림 5건을 처리한 로그입니다.

- 알림 한 건이 한 줄입니다. 2교시 `engine_log.json` 과 같은 꼴이고, 조치마다 `executed` · `before` · `after` 와 승인 게이트가 본 조치 요청 `request` 가 들어 있습니다.
- 모든 `decision` 이 「자동」이고 이유가 「승인 게이트 끔」입니다.

```
[
  {"incident": "INC-401", "entity": "dami", "grade": "high", "playbook": "PB-001", "outcome": "자동 실행", "steps": [{"action": "계정 잠금", "target": "dami", "decision": "자동", "reasons": ["승인 게이트 끔"], "executed": true, "before": "잠기지 않음", "after": "잠김", "request": {"id": "INC-401", "incident": "INC-401", "action": "계정 잠금", "target": "dami", "grade": "high", "users_on_ip": 0, "target_count": 1}}], "ticket": "TCK-1", "error": ""},
  {"incident": "INC-403", "entity": "198.51.100.45", "grade": "low", "playbook": "PB-003", "outcome": "자동 실행", "steps": [{"action": "IP 차단", "target": "198.51.100.45", "decision": "자동", "reasons": ["승인 게이트 끔"], "executed": true, "before": "차단되지 않음", "after": "차단됨", "request": {"id": "INC-403", "incident": "INC-403", "action": "IP 차단", "target": "198.51.100.45", "grade": "low", "users_on_ip": 0, "target_count": 1}}], "ticket": "TCK-2", "error": ""},
  {"incident": "INC-404", "entity": "203.0.113.80", "grade": "high", "playbook": "PB-003", "outcome": "자동 실행", "steps": [{"action": "IP 차단", "target": "203.0.113.80", "decision": "자동", "reasons": ["승인 게이트 끔"], "executed": true, "before": "차단되지 않음", "after": "차단됨", "request": {"id": "INC-404", "incident": "INC-404", "action": "IP 차단", "target": "203.0.113.80", "grade": "high", "users_on_ip": 2, "target_count": 1}}], "ticket": "TCK-3", "error": ""},
  {"incident": "INC-405", "entity": "192.0.2.41", "grade": "mid", "playbook": "PB-003", "outcome": "자동 실행", "steps": [{"action": "IP 차단", "target": "192.0.2.41", "decision": "자동", "reasons": ["승인 게이트 끔"], "executed": true, "before": "차단되지 않음", "after": "차단됨", "request": {"id": "INC-405", "incident": "INC-405", "action": "IP 차단", "target": "192.0.2.41", "grade": "mid", "users_on_ip": 2, "target_count": 1}}], "ticket": "TCK-4", "error": ""},
  {"incident": "INC-406", "entity": "gaeun", "grade": "high", "playbook": "PB-001", "outcome": "자동 실행", "steps": [{"action": "계정 잠금", "target": "gaeun", "decision": "자동", "reasons": ["승인 게이트 끔"], "executed": true, "before": "변경 없음", "after": "변경 없음", "request": {"id": "INC-406", "incident": "INC-406", "action": "계정 잠금", "target": "gaeun", "grade": "high", "users_on_ip": 0, "target_count": 1}}], "ticket": "TCK-5", "error": ""}
]
```

**`policy_check.py`** — 정책 점검 함수 모음입니다. 직접 쓰는 곳은 1 ~ 6번입니다.

- 2번 · 3번 · 4번 · 5번 · 6번은 `if` 한 줄만 쓰고, 그 아래 미리 채운 줄이 `if` 안쪽입니다. 1번과 2번은 같은 함수에 있고 둘 다 같은 들여쓰기에서 시작합니다.

```python
from approval_gate import decide_gate                                                      # 금요일 파일의 승인 게이트 함수를 불러온다


def count_executed(result):                                                                # 결과 기록 한 건을 받는 함수
    """결과 기록에서 실제로 실행한 조치가 몇 개인지 센다. 실행한 조치가 있는데 티켓이 없는 알림을 찾을 때 쓴다."""
    executed_count = 0                                                                     # 실행한 조치 수 : 처음에는 0
    for step in result["steps"]:                                                           # 조치 결과를 하나씩 꺼낸다
        if step["executed"]:                                                               # 실행한 조치이면
            executed_count = executed_count + 1                                            # 실행한 조치 수를 1 늘린다
    return executed_count                                                                  # 실행한 조치 수를 리턴한다


def find_gate_bypass(results, policy):                                                     # 결과 기록 리스트와 승인 정책을 받는 함수
    """저장된 조치 요청으로 승인 게이트의 결정을 다시 구해, 자동이 아닌데 실행된 조치가 있는 알림 번호를 리스트로 리턴한다. 게이트를 거치지 않았거나 결정을 바꿔 쓴 실행을 찾을 때 쓴다."""
    violations = []                                                                        # 위반한 알림 번호를 모을 빈 리스트 — 미리 채운 줄
    for result in results:                                                                 # 결과 기록을 하나씩 꺼낸다 — 미리 채운 줄
        for step in result["steps"]:                                                       # 조치 결과를 하나씩 꺼낸다 — 미리 채운 줄
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            # 1. decide_gate(step["request"], policy) 의 두 결과를 new_decision, new_reasons 에 저장한다
            # 2. new_decision 이 "자동" 이 아니고(and) step["executed"] 가 참이면 (if, !=, and)
                violations.append(result["incident"])                                      # 알림 번호를 위반 리스트에 추가한다 — 미리 채운 줄
    return violations                                                                      # 위반한 알림 번호 리스트를 리턴한다 — 미리 채운 줄


def find_allowlist_blocks(results, allowlist_ips):                                         # 결과 기록 리스트와 허용 목록을 받는 함수
    """허용 목록 IP 를 실제로 차단한 알림 번호를 리스트로 리턴한다. 승인 게이트와 별개로, 업무에 필요한 IP 가 차단되지 않았는지 확인할 때 쓴다."""
    violations = []                                                                        # 위반한 알림 번호를 모을 빈 리스트 — 미리 채운 줄
    for result in results:                                                                 # 결과 기록을 하나씩 꺼낸다 — 미리 채운 줄
        for step in result["steps"]:                                                       # 조치 결과를 하나씩 꺼낸다 — 미리 채운 줄
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            # 3. step["target"] 이 allowlist_ips 안에 있고(and) step["after"] 가 "차단됨" 이면 (if, in, ==, and)
                violations.append(result["incident"])                                      # 알림 번호를 위반 리스트에 추가한다 — 미리 채운 줄
    return violations                                                                      # 위반한 알림 번호 리스트를 리턴한다 — 미리 채운 줄


def find_vip_locks(results, vip_accounts):                                                 # 결과 기록 리스트와 VIP 계정 리스트를 받는 함수
    """VIP 계정을 실제로 잠근 알림 번호를 리스트로 리턴한다. 승인 게이트와 별개로, VIP 계정이 자동으로 잠기지 않았는지 확인할 때 쓴다."""
    violations = []                                                                        # 위반한 알림 번호를 모을 빈 리스트 — 미리 채운 줄
    for result in results:                                                                 # 결과 기록을 하나씩 꺼낸다 — 미리 채운 줄
        for step in result["steps"]:                                                       # 조치 결과를 하나씩 꺼낸다 — 미리 채운 줄
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            # 4. step["target"] 이 vip_accounts 안에 있고(and) step["after"] 가 "잠김" 이면 (if, in, ==, and)
                violations.append(result["incident"])                                      # 알림 번호를 위반 리스트에 추가한다 — 미리 채운 줄
    return violations                                                                      # 위반한 알림 번호 리스트를 리턴한다 — 미리 채운 줄


def find_missing_tickets(results):                                                         # 결과 기록 리스트를 받는 함수
    """조치를 실행했는데 티켓이 없는 알림 번호를 리스트로 리턴한다. 실행한 조치가 담당자에게 인계되지 않고 사라지지 않았는지 확인할 때 쓴다."""
    violations = []                                                                        # 위반한 알림 번호를 모을 빈 리스트 — 미리 채운 줄
    for result in results:                                                                 # 결과 기록을 하나씩 꺼낸다 — 미리 채운 줄
        executed_count = count_executed(result)                                            # 실행한 조치 수를 센다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. executed_count 가 0 보다 크고(and) result["ticket"] 이 "" 이면 (if, >, ==, and)
            violations.append(result["incident"])                                          # 알림 번호를 위반 리스트에 추가한다 — 미리 채운 줄
    return violations                                                                      # 위반한 알림 번호 리스트를 리턴한다 — 미리 채운 줄


def run_checks(results, policy):                                                           # 결과 기록 리스트와 승인 정책을 받는 함수
    """점검 네 가지를 모두 실행해 점검 이름마다 위반한 알림 번호 리스트를 담은 딕셔너리를 리턴한다. 로그 하나를 정책에 비추어 한 번에 점검할 때 쓴다."""
    checks = {}                                                                            # 점검 이름 → 위반한 알림 번호 리스트 — 미리 채운 줄
    checks["게이트 우회 실행"] = find_gate_bypass(results, policy)                         # 점검 ① — 미리 채운 줄
    checks["허용 목록 IP 차단"] = find_allowlist_blocks(results, policy["allowlist_ips"])  # 점검 ② — 미리 채운 줄
    checks["VIP 계정 잠금"] = find_vip_locks(results, policy["vip_accounts"])              # 점검 ③ — 미리 채운 줄
    checks["티켓 없는 조치"] = find_missing_tickets(results)                               # 점검 ④ — 미리 채운 줄
    return checks                                                                          # 점검 결과 딕셔너리를 리턴한다 — 미리 채운 줄


def judge(violations):                                                                     # 위반한 알림 번호 리스트를 받는 함수
    """위반이 하나도 없으면 「PASS」, 하나라도 있으면 「FAIL」을 리턴한다. 점검 결과를 한눈에 보이게 출력할 때 쓴다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 6. violations 가 빈 리스트 [] 이면 (if, ==)
        return "PASS"                                                                      # 위반이 없으면 PASS 를 리턴한다 — 미리 채운 줄
    return "FAIL"                                                                          # 위반이 있으면 FAIL 을 리턴한다 — 미리 채운 줄
```

**`day06_4-1_run.py`** — 7 · 8 · 9번만 직접 쓰고 나머지는 그대로 붙여 넣습니다.

```python
from incident import load_json, save_json                                                   # 월요일 파일의 JSON 읽기 · 쓰기 함수를 불러온다
from policy_check import run_checks, judge                                                  # 방금 만든 점검 함수를 불러온다

LOG_FILES = ["engine_log.json", "risk_engine_log.json", "gate_off_log.json"]                # 점검할 엔진 로그 파일 세 개
CHECK_PATH = "policy_check.json"                                                            # 점검 결과를 저장할 파일 이름

policy = load_json("config/approval_policy.json")                                           # 승인 정책 파일을 딕셔너리로 읽는다
print("--- 단계 1: 점검할 로그", len(LOG_FILES), "개 · 점검 4가지")                         # 단계 1 시작을 알리는 줄

rows = []                                                                                   # 점검 결과 한 줄씩 모을 빈 리스트
fail_count = 0                                                                              # FAIL 이 나온 점검 수 : 처음에는 0
print("--- 단계 2: 로그마다 점검 결과")                                                     # 단계 2 시작을 알리는 줄
for log_path in LOG_FILES:                                                                  # 로그 파일을 하나씩 꺼낸다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. load_json(log_path) 의 결과를 results 에 저장한다
    checks = run_checks(results, policy)                                                    # 점검 네 가지를 실행한다 — 미리 채운 줄
    print("[" + log_path + "] 알림", len(results), "건")                                    # 로그 이름과 알림 수를 출력한다
    for check_name in checks:                                                               # 점검 이름을 하나씩 꺼낸다
        violations = checks[check_name]                                                     # 그 점검에서 위반한 알림 번호 리스트 — 미리 채운 줄
        verdict = judge(violations)                                                         # 통과 여부를 구한다 — 미리 채운 줄
        # 8. verdict 가 "FAIL" 이면 (if, ==)
            fail_count = fail_count + 1                                                     # FAIL 이 나온 점검 수를 1 늘린다 — 미리 채운 줄
        print("  ", check_name, ":", verdict, "· 위반", len(violations), "건", violations)  # 점검 이름 · 결과 · 위반한 알림 번호 리스트를 출력한다
        rows.append({"log": log_path, "check": check_name, "result": verdict, "violations": violations})  # 점검 결과 한 줄을 추가한다 — 미리 채운 줄

print("--- 단계 3: FAIL 이 나온 점검", fail_count, "개 · 전체 점검", len(rows), "개")       # 단계 3 시작을 알리는 줄과 개수
# ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
# 9. rows 를 CHECK_PATH 파일에 저장한다 (save_json)
print("--- 단계 4:", CHECK_PATH, "에", len(rows), "개 저장")                                # 단계 4 시작을 알리는 줄과 저장한 수
```

**순서**

1. **[터미널]** 먼저 2 · 3교시 로그가 있는지 확인합니다. <mark>`ls` 결과에 `engine_log.json` 과 `risk_engine_log.json` 이 보이면</mark> 됩니다. 없으면 `python day06_2-1_run.py` 와 `python day06_3-1_run.py` 를 먼저 실행합니다(맥북은 `python3`). 그다음 파일 세 개를 만들고 **[VS Code]** 에서 열어 붙여 넣습니다.
   ```bash
   pwd
   ls
   touch gate_off_log.json policy_check.py day06_4-1_run.py
   ```
2. **[VS Code]** `policy_check.py` 1 ~ 6번, `day06_4-1_run.py` 7 ~ 9번을 씁니다. 막히면 아래 「4교시 한눈에」를 봅니다.
3. **[터미널]** <mark>`pwd` 가 `soar_response` 로 끝나는지</mark> 확인하고 실행합니다(맥북은 `python3`).
   ```bash
   python day06_4-1_run.py
   ```
4. 출력은 네 단계입니다. 제목 줄은 줄 수에 넣지 않습니다.
   - 단계 1 · 단계 3 · 단계 4 는 숫자가 제목 줄에 함께 나와 그 아래 줄이 없습니다.
   - 단계 2 는 로그마다 제목 줄 1줄과 점검 결과 4줄이라 모두 15줄입니다.
5. **[VS Code]** 새로 생긴 `policy_check.json` 을 열어 <mark>12개 점검이 들어 있는지</mark> 봅니다.
6. **[VS Code]** 5일간의 회고 문서 `day05_final_retrospective.md` 를 만듭니다. 파일 이름의 `day05` 는 강의계획서의 Day 5(오늘)입니다. **[터미널]** 에서 `touch day05_final_retrospective.md` 로 빈 파일을 만든 뒤, 아래 틀을 붙여 넣고 `…` 를 채웁니다. 틀은 지우지 않고 그대로 둡니다.

   - 1절은 엔진이 각 날의 파일을 어디에 쓰는지 한 문장씩 씁니다(2교시 `soar_engine.py` 의 `import` 줄과 오늘 만든 파일이 근거입니다).
   - 2절은 <mark>오늘 출력이나 코드에서 근거를 찾아</mark> 운영에서 깨질 수 있는 곳 세 가지와 막는 방법을 씁니다.
   - 3절은 캡스톤 주제 가운데 하나를 고르고, 새 코드를 쓰지 않고 설정 파일만 바꿔 시작할 수 있는 것을 씁니다.

   ````markdown
   # 5과목 Day 5 최종 회고 (이름 · 2026-11-16(월))

   ## 1. 5일 동안 만든 것

   엔진이 각 날의 파일을 어디에 쓰는지 한 문장씩 씁니다.

   | Day | 날짜 | 엔진과 연결된 파일 | 엔진에서 하는 일 |
   |---|---|---|---|
   | 1 | 11/9(월) · 11/10(화) | `incident.py` · `config/playbook_registry.json` | … |
   | 2 | 11/11(수) | `account_actions.py` · `ip_actions.py` | … |
   | 3 | 11/12(목) | `ticketing.py` | … |
   | 4 | 11/13(금) | `approval_gate.py` | … |
   | 5 | 11/16(월) | `soar_engine.py` · `engine_input.py` · `policy_check.py` | … |

   ## 2. 운영하면 깨질 수 있는 곳 3가지

   오늘 출력이나 코드에서 근거를 찾아 씁니다.

   | 깨질 곳 | 근거(오늘의 파일 · 단계) | 막는 방법 |
   |---|---|---|
   | … | … | … |
   | … | … | … |
   | … | … | … |

   ## 3. 캡스톤 주제와 내 모듈

   | 캡스톤 주제 | 쓰는 과목 모듈 |
   |---|---|
   | 과다권한 자동 회수봇 | `access_control` + `agent_core` |
   | 이상행위 자동 차단 에이전트 | `anomaly_detection` + `soar_response` |
   | ZT 보안 자세 점검 · 스코어링 | `network_zt` + `agent_core` |
   | AI 보안 이벤트 분류 · 초동대응봇 | `anomaly_detection` + `soar_response` + `agent_core` |

   - 내가 고르고 싶은 주제: …
   - 캡스톤 첫날 새 코드 없이 바꿔 볼 설정 파일 2개: …
   - 그대로 가져다 쓸 내 파일 3개: …
   ````
7. **[보고서]** `day06_am_report.md` 의 `## 4교시` 아래를 채웁니다.
   - (가) 실행한 출력 전체를 붙여 넣고, FAIL 이 나온 로그와 FAIL 이 나온 점검 이름 · 위반한 알림 번호를 적어 주세요.
   - (나) 🔍 `gate_off_log.json` 의 `INC-405` 는 `decision` 이 「자동」인데 점검 ①에서 위반으로 나옵니다. 그 `request` 의 `users_on_ip` 와 승인 정책의 점수를 근거로 다시 구한 결정을 적고, 로그의 `decision` 만 읽으면 위반을 놓치는 이유를 적어 주세요.
   - (다) 🔍 `INC-406`(`gaeun`)은 점검 ①은 FAIL 인데 점검 ③은 PASS 입니다. 그 알림의 `before` · `after` 를 근거로 `gaeun` 이 잠기지 않은 이유를 수요일 `lock_account` 와 연결해 적고, 점검 ③이 게이트와 별도로 필요한 이유를 적어 주세요.

### 4교시 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 두 결과를 함께 받기 | `new_decision, new_reasons = decide_gate(step["request"], policy)` |
| 다르고 그리고 참이면 | `if new_decision != "자동" and step["executed"]:` |
| 리스트 안에 있고 그리고 같으면 | `if step["target"] in allowlist_ips and step["after"] == "차단됨":` |
| 크고 그리고 같으면 | `if executed_count > 0 and result["ticket"] == "":` |
| 빈 리스트와 같으면 | `if violations == []:` |
| 함수 결과를 변수에 저장하기 | `results = load_json(log_path)` |
| 리스트를 파일에 저장하기 | `save_json(rows, CHECK_PATH)` |

---

### 마무리 · 오늘 만든 것을 깃허브에 올리기

<mark>문제가 아니라 5일간 만든 것을 저장소에 올리는 마무리입니다.</mark> 4교시 마지막 약 10분에 합니다. 어느 터미널을 써도 됩니다. 먼저 `pwd` 로 위치를 확인하고, 결과가 `soar_response` 로 끝나면 아래 1번의 `cd ..` 를 칩니다.

**📍 이런 상황이 있습니다**

- **지금은**: <mark>팀장이 「5일간 만든 SOAR 모듈과 엔진 · 점검 · 회고 문서를 저장소에 남겨 달라」고 합니다</mark>.
- **그래서 하는 것**: `git status` 로 올라갈 파일을 확인한 뒤(`.env` 같은 비밀 키 파일이 섞이면 안 됩니다) `git add` → `git commit` → `git push` 순서로 올립니다.
- **끝나면**: 깃허브 저장소의 `soar_response` 폴더에 `soar_engine.py` · `engine_input.py` · `policy_check.py` · `day05_final_retrospective.md` 와 로그 · 요약 파일(`engine_log.json` · `risk_engine_log.json` · `engine_summary.json` · `policy_check.json`)이 보입니다.

**순서**

0. **[터미널]** 오늘 만든 파일이 있는지 `soar_response` 폴더에서 확인합니다. 두 명령을 하나씩 칩니다. `day06_am_report.md` 의 모든 질문에서 `답:` 뒤와 코드 상자가 채워졌는지, `day05_final_retrospective.md` 의 `…` 가 모두 채워졌는지도 확인합니다(마무리 (가)는 3번에서 채웁니다).

   ① 지금 위치를 확인합니다.

   ```bash
   pwd
   ```

   - 하는 일: 지금 있는 폴더의 위치를 보여 줍니다.
   - 나오는 것: <mark style="background:#bde3ff">`soar_response` 로 끝나야</mark> 합니다.

   ② 폴더 안의 파일을 봅니다.

   ```bash
   ls
   ```

   - 하는 일: 폴더 안의 파일 이름을 보여 줍니다.
   - 나오는 것: `soar_engine.py` · `engine_input.py` · `policy_check.py` · `day05_final_retrospective.md` · `engine_log.json` · `risk_engine_log.json` · `engine_summary.json` · `policy_check.json` · `config` 가 보이면 됩니다.

1. **[터미널]** `security-agent-toolkit` 폴더로 이동합니다. 0번의 `pwd` 결과가 `soar_response` 로 끝날 때만 `cd ..` 를 칩니다. 이미 `…/security-agent-toolkit` 으로 끝나면 `cd ..` 는 건너뛰고 `pwd` 만 칩니다.

   ① 한 단계 위 폴더로 이동합니다.

   ```bash
   cd ..
   ```

   - 하는 일: 한 단계 위 폴더로 이동합니다.
   - 나오는 것: 아무것도 나오지 않습니다.

   ② 지금 위치를 확인합니다.

   ```bash
   pwd
   ```

   - 하는 일: 지금 있는 폴더의 위치를 보여 줍니다.
   - 나오는 것: <mark style="background:#bde3ff">`…/security-agent-toolkit` 으로 끝나면</mark> 됩니다. 결과가 다르면 VS Code 왼쪽 목록에서 `security-agent-toolkit` 폴더를 오른쪽 클릭 › **Open in Integrated Terminal** 로 터미널을 새로 엽니다.

2. **[터미널]** 무엇이 바뀌었는지 먼저 봅니다. <mark style="background:#ffc4d6">빨간 글씨 줄이나 `Untracked files:` 아래에 `.env`(API 키가 들어 있는 파일) 나 `.venv`(가상환경이 들어 있는 폴더)가 보이면 올리지 말고(`.env` 를 올리면 키가 공개되기 때문입니다),</mark> 아래 안내대로 `.gitignore`(깃이 올리지 않을 파일 이름을 적어 두는 파일)를 고친 뒤 `git status` 를 다시 봅니다.

   ① 올릴 파일의 상태를 봅니다.

   ```bash
   git status
   ```

   - 하는 일: 올릴 파일의 상태를 보여 줍니다.
   - 나오는 것: 바뀐 파일의 이름이 나옵니다. `soar_response/` 아래의 새 파일들이 보이면 됩니다.

   - `.env` 가 보이면: VS Code 왼쪽 목록에서 `security-agent-toolkit` 바로 아래의 `.gitignore` 를 열어 맨 아래에 `.env` 한 줄을 적고 저장한 뒤 `git status` 를 다시 칩니다.
     - `.venv` 는 `.venv/` 한 줄을 같은 방법으로 적습니다.
   - `soar_response/__pycache__/` (파이썬이 실행하면서 자동으로 만드는 임시 폴더)가 보이면 `.gitignore` 맨 아래에 `__pycache__/` 한 줄을 적고 저장한 뒤 `git status` 를 다시 봅니다.

3. **[보고서]** `day06_am_report.md` 의 `### 마무리 · 오늘 만든 것을 깃허브에 올리기` 아래를 채웁니다. <mark>올리기 전에 채워야</mark> 깃허브에 빈칸 없이 올라갑니다.
   - (가) `git status` 를 쳤을 때 `.env` 나 `.venv` 가 보였는지, 보였다면 어떻게 했는지 적어 주세요.
   - <mark>앞 교시에서 못 적은 보고서 칸이 있으면 `모름 — 막힌 곳: …` 으로 적고 올립니다.</mark> 올린 뒤에 이어서 적어 다시 올려도 됩니다.
4. **[터미널]** 바뀐 파일을 모두 올릴 목록에 추가하고(`add`), 기록하고(`commit`), 올립니다(`push`). 세 명령을 순서대로 하나씩 칩니다.

   ① 바뀐 파일을 모두 올릴 목록에 추가합니다.

   ```bash
   git add .
   ```

   - 하는 일: 바뀐 파일을 올릴 대상에 추가합니다.
   - 나오는 것: 아무것도 나오지 않습니다.

   ② 기록으로 저장합니다.

   ```bash
   git commit -m "Add SOAR engine, engine input check, policy check and final retrospective"
   ```

   - 하는 일: 따옴표 안의 설명을 붙여 기록으로 저장합니다.
   - 나오는 것: 바뀐 파일 수가 적힌 줄이 나옵니다.

   ③ 깃허브로 올립니다.

   ```bash
   git push
   ```

   - 하는 일: 저장한 기록을 깃허브로 올립니다.
   - 나오는 것: 올라간 내용이 몇 줄 나옵니다.

   - <mark style="background:#ffc4d6">`git push` 가 거절(`rejected`)되면 깃허브에 내 PC 에 없는 기록이 있다는 뜻입니다.</mark> `git pull --no-rebase`(깃허브의 새 기록을 내 PC 로 받아 와 합치는 명령)를 입력한 뒤 `git push` 를 다시 합니다.
   - 편집기 화면이 뜨면 `Esc` → `:wq`(저장하고 나가기) → `Enter` 를 합니다.
   - `git pull` 만 입력했을 때 `fatal: Need to specify how to reconcile divergent branches` 가 나오면, 내 기록과 깃허브 기록이 갈라졌다는 뜻이므로 `git pull --no-rebase` 를 입력합니다.

5. **[브라우저]** 깃허브의 내 저장소를 새로 고쳐 `soar_response` 폴더를 열고, VS Code 왼쪽 목록의 `soar_response` 폴더에 있는 파일들이 깃허브에도 보이는지 확인합니다. <mark>`__pycache__` 폴더는 없어도 됩니다</mark>.
   - 깃허브에 안 보이는 파일이 있으면, 그 파일이 VS Code 왼쪽 목록의 `soar_response` 폴더에 내 PC 에도 있는지 봅니다.
     - 없으면 다른 폴더에 만든 것이니 `soar_response` 안으로 이동하고, `pwd` 로 위치를 확인한 뒤 2번의 `git status` 부터 다시 합니다.

### 마무리 한눈에

| 하려는 일 | 코드 · 말 |
|---|---|
| 올릴 파일 확인 | `git status` (`.env` · `.venv` 가 보이면 멈춤) |
| 올리기 | `git add .` → `git commit -m "…"` → `git push` |
| 올린 뒤 | 브라우저에서 `soar_response` 폴더와 파일이 있는지 확인 |

---

## 오늘 오전 마무리

| 확인 | 문제 |
|---|---|
| 알림을 승인 게이트를 거쳐 조치하고 티켓을 남기며, 오류가 난 알림은 실패로 격리하는 통합 엔진을 만들었다 | 오전 2-1 |
| 4과목 탐지 결과를 점검해 엔진의 입력으로 바꾸고, 실행해 운영 요약을 만들었다 | 오전 3-1 |
| 엔진 로그를 정책 네 가지로 점검하고, 5일간의 회고 문서를 쓰고, 깃허브에 올렸다 | 오전 4-1 · 마무리 |

**강의계획서 평가 기준 확인**

| 기준 | 확인할 곳 |
|---|---|
| 4과목 탐지 결과부터 5과목 대응까지 종단간으로 오류 없이 동작한다 | 오전 3교시 단계 3 ~ 5 <mark style="background:#bde3ff">(4과목 5건 → 알림 5건 → 자동 실행 2건 · 조치 없음 3건 · 실패 0건)</mark> |
| 승인 게이트가 위험도에 따라 정확히 작동한다 | 오전 2교시 단계 2 · 3 <mark style="background:#bde3ff">(자동 실행 2 · 승인 대기 2 · 차단 금지 1)</mark>, 오전 4교시 점검 ① |
| 모듈이 서로 이어져 하나의 흐름으로 동작한다 | 오전 2교시 `soar_engine.py` 의 `import` 6줄, 회고 문서 1절 |

---

---

# 정답 · 먼저 풀어 본 뒤에 봅니다

아래 답은 한 예이고, <mark>핵심이 같으면 맞습니다.</mark> 줄 수가 달라도 주석이 말한 일을 하면 맞습니다.

---

### 정답 2-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day06_2-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예)

`soar_engine.py` 의 1 ~ 8번입니다.

```python
        # 1. count_users_on_ip(alert["entity"], context["ip_users"]) 의 결과를 users_on_ip 에 저장한다
        users_on_ip = count_users_on_ip(alert["entity"], context["ip_users"])  # 그 IP 를 쓰는 계정 수를 센다
        # 2. lock_account(request["target"], state, vip_accounts, request["incident"], ENGINE_REASON) 의 결과를 record 에 저장한다
        record = lock_account(request["target"], state, vip_accounts, request["incident"], ENGINE_REASON)  # 계정을 잠그고 조치 기록을 받는다
        # 3. block_ip(request["target"], state, request["incident"], ENGINE_REASON, DEFAULT_TTL) 의 결과를 record 에 저장한다
        record = block_ip(request["target"], state, request["incident"], ENGINE_REASON, DEFAULT_TTL)  # IP 를 차단하고 조치 기록을 받는다
    # 4. decide_gate(request, context["policy"]) 의 두 결과를 decision, reasons 에 저장한다
    decision, reasons = decide_gate(request, context["policy"])                # 승인 게이트의 결정과 이유 리스트를 함께 받는다
    # 5. decision 이 "자동" 이면 (if, ==)
    if decision == "자동":                                                     # 게이트가 자동으로 정했으면
            # 6. action 이 CONTAINMENT_ACTIONS 안에 있으면 (if, in)
            if action in CONTAINMENT_ACTIONS:                                  # 게이트를 거쳐 실행하는 조치이면
            # 7. run_soar_pipeline(alert, context) 의 결과를 result 에 저장한다
            result = run_soar_pipeline(alert, context)                         # 알림 한 건을 처음부터 끝까지 처리한다
        # 8. 어떤 종류의 오류든 error 에 저장해 받는다 (except, Exception, as)
        except Exception as error:                                             # 어떤 종류의 오류든 error 에 저장해 받는다
```

위 줄만으로는 `if` · `else` · `try` 안에 들어가는 줄이 어느 것인지 알기 어려우니, 미리 채운 줄까지 넣은 네 함수의 완성된 모양을 함께 봅니다.

**전체 모양 — `execute_action`**

```python
def execute_action(request, context):                 # 조치 요청과 엔진 재료를 받는 함수
    """계정 잠금이면 lock_account, IP 차단이면 block_ip 로 조치를 실행하고 조치 기록 한 건을 리턴한다. 승인 게이트가 자동으로 정한 조치를 실제로 실행할 때 쓴다."""
    state = context["state"]                          # 연습용 시스템 상태 — 미리 채운 줄
    vip_accounts = context["policy"]["vip_accounts"]  # VIP 계정 리스트 — 미리 채운 줄
    if request["action"] == "계정 잠금":              # 조치가 계정 잠금이면 — 미리 채운 줄
        record = lock_account(request["target"], state, vip_accounts, request["incident"], ENGINE_REASON)  # 계정을 잠그고 조치 기록을 받는다
    else:                                             # 아니면 IP 차단이다 — 미리 채운 줄
        record = block_ip(request["target"], state, request["incident"], ENGINE_REASON, DEFAULT_TTL)  # IP 를 차단하고 조치 기록을 받는다
    return record                                     # 조치 기록을 리턴한다 — 미리 채운 줄
```

**전체 모양 — `run_step`**

```python
def run_step(alert, action, context):                            # 알림 · 조치 이름 · 엔진 재료를 받는 함수
    """조치 하나를 승인 게이트에 묻고, 자동으로 정해졌을 때만 실행해서 결정 · 이유 · 실행 여부를 담은 딕셔너리를 리턴한다. 조치마다 한 번씩 쓴다."""
    request = make_request(alert, action, context)               # 승인 게이트에 보낼 조치 요청을 만든다 — 미리 채운 줄
    decision, reasons = decide_gate(request, context["policy"])  # 승인 게이트의 결정과 이유 리스트를 함께 받는다
    step = {                                                     # 조치 하나의 결과 : 처음에는 실행하지 않은 것으로 적는다 — 미리 채운 줄
        "action": action,                                        # 조치 이름
        "target": alert["entity"],                               # 조치 대상
        "decision": decision,                                    # 승인 게이트의 결정
        "reasons": reasons,                                      # 결정 이유 리스트
        "executed": False,                                       # 실행했는지
        "before": "",                                            # 조치 전 상태
        "after": "",                                             # 조치 후 상태
        "request": request,                                      # 승인 게이트가 본 조치 요청(나중에 점검할 때 다시 쓴다)
    }
    if decision == "자동":                                       # 게이트가 자동으로 정했으면
        record = execute_action(request, context)                # 조치를 실행하고 조치 기록을 받는다 — 미리 채운 줄
        step["executed"] = True                                  # 실행했다고 적는다 — 미리 채운 줄
        step["before"] = record["before"]                        # 조치 전 상태를 적는다 — 미리 채운 줄
        step["after"] = record["after"]                          # 조치 후 상태를 적는다 — 미리 채운 줄
    return step                                                  # 조치 하나의 결과를 리턴한다 — 미리 채운 줄
```

**전체 모양 — `run_soar_pipeline`**

```python
def run_soar_pipeline(alert, context):                                 # 알림 한 건과 엔진 재료를 받는 함수
    """알림 한 건을 플레이북 찾기 → 조치마다 승인 게이트 → 티켓 만들기 순서로 처리하고 결과 기록 한 건을 리턴한다. 알림마다 한 번씩 쓴다."""
    playbooks = match_playbooks(alert, context["registry"])            # 월요일 함수로 맞는 플레이북을 찾는다 — 미리 채운 줄
    playbook_id = "없음"                                               # 맞는 플레이북이 없으면 「없음」으로 남긴다 — 미리 채운 줄
    steps = []                                                         # 조치마다 결과를 모을 빈 리스트 — 미리 채운 줄
    for playbook in playbooks:                                         # 맞는 플레이북을 하나씩 꺼낸다 — 미리 채운 줄
        playbook_id = playbook["id"]                                   # 플레이북 번호를 적는다 — 미리 채운 줄
        for action in playbook["actions"]:                             # 플레이북의 액션을 하나씩 꺼낸다 — 미리 채운 줄
            if action in CONTAINMENT_ACTIONS:                          # 게이트를 거쳐 실행하는 조치이면
                step = run_step(alert, action, context)                # 승인 게이트를 거쳐 실행한다 — 미리 채운 줄
                steps.append(step)                                     # 조치 결과를 추가한다 — 미리 채운 줄
    outcome = decide_outcome(steps)                                    # 알림 전체의 처리 결과를 정한다 — 미리 채운 줄
    ticket = open_ticket(alert, steps, playbook_id, outcome, context)  # 티켓을 만든다 — 미리 채운 줄
    result = {                                                         # 알림 한 건의 결과 기록 — 미리 채운 줄
        "incident": alert["id"],                                       # 알림 번호
        "entity": alert["entity"],                                     # 대상
        "grade": alert["grade"],                                       # 등급
        "playbook": playbook_id,                                       # 플레이북 번호
        "outcome": outcome,                                            # 처리 결과
        "steps": steps,                                                # 조치마다 결과 리스트
        "ticket": ticket["id"],                                        # 티켓 번호
        "error": "",                                                   # 오류 문장 : 정상이면 비어 있다
    }
    return result                                                      # 결과 기록을 리턴한다 — 미리 채운 줄
```

**전체 모양 — `run_all`**

```python
def run_all(alerts, context):                           # 알림 리스트와 엔진 재료를 받는 함수
    """알림을 하나씩 처리하되, 오류가 난 알림은 실패 기록만 남기고 다음 알림으로 넘어간다. 알림 하나의 오류가 나머지 알림의 처리를 막지 않게 할 때 쓴다."""
    results = []                                        # 알림마다 결과 기록을 모을 빈 리스트 — 미리 채운 줄
    for alert in alerts:                                # 알림을 하나씩 꺼낸다 — 미리 채운 줄
        try:                                            # 오류가 날 수 있는 처리를 시작한다 — 미리 채운 줄
            result = run_soar_pipeline(alert, context)  # 알림 한 건을 처음부터 끝까지 처리한다
        except Exception as error:                      # 어떤 종류의 오류든 error 에 저장해 받는다
            result = make_failure_result(alert, error)  # 실패 기록을 만든다 — 미리 채운 줄
        results.append(result)                          # 정상 결과든 실패 기록이든 결과 리스트에 추가한다 — 미리 채운 줄
    return results                                      # 결과 기록 리스트를 리턴한다 — 미리 채운 줄
```

`day06_2-1_run.py` 의 9번입니다.

```python
    # 9. counts[outcome] 에 counts[outcome] + 1 을 저장한다 (1 늘린다)
    counts[outcome] = counts[outcome] + 1  # 이 처리 결과의 알림 수를 1 늘린다
```

**결과**

- (가) 출력은 다음과 같습니다. 자동 실행 <mark style="background:#bde3ff">**2건**</mark> · 승인 대기 <mark style="background:#bde3ff">**2건**</mark> · 차단 금지 <mark style="background:#bde3ff">**1건**</mark> · 조치 없음 <mark style="background:#bde3ff">**2건**</mark> · 실패 <mark style="background:#bde3ff">**1건**</mark>이고, 승인 대기는 <mark style="background:#bde3ff">`INC-405` · `INC-406`</mark> 입니다.

```
--- 단계 1: 불러온 알림 8 건 · 플레이북 3 개 · 승인 기준 3 점
--- 단계 2: 알림마다 처리 결과
INC-401 dami high → 자동 실행 · PB-001 · 티켓 TCK-1
    계정 잠금 dami → 자동 · 등급 high +2, 합계 2점
    실행: 잠기지 않음 → 잠김
INC-402 hana → 실패 · KeyError: 'grade'
INC-403 198.51.100.45 low → 자동 실행 · PB-003 · 티켓 TCK-2
    IP 차단 198.51.100.45 → 자동 · 등급 low +0, 합계 0점
    실행: 차단되지 않음 → 차단됨
INC-404 203.0.113.80 high → 차단 금지 · PB-003 · 티켓 TCK-3
    IP 차단 203.0.113.80 → 차단 금지 · 허용 목록 대상
INC-405 192.0.2.41 mid → 승인 대기 · PB-003 · 티켓 TCK-4
    IP 차단 192.0.2.41 → 승인 필요 · 등급 mid +1, 함께 쓰는 IP +2, 합계 3점
INC-406 gaeun high → 승인 대기 · PB-001 · 티켓 TCK-5
    계정 잠금 gaeun → 승인 필요 · 등급 high +2, VIP 계정 +3, 합계 5점
INC-407 seoyeon mid → 조치 없음 · PB-002 · 티켓 TCK-6
INC-408 jiwoo mid → 조치 없음 · 없음 · 티켓 TCK-7
--- 단계 3: 처리 결과별 알림 수
자동 실행 : 2 건
승인 대기 : 2 건
차단 금지 : 1 건
조치 없음 : 2 건
실패 : 1 건
--- 단계 4: engine_log.json 에 8 건 · engine_tickets.json 에 티켓 7 장 저장
```

- (나) `INC-402` 는 `grade` 키가 없어서 `match_playbooks` 가 `incident["grade"]` 를 읽을 때 <mark style="background:#bde3ff">`KeyError: 'grade'`</mark> 가 납니다. `run_all` 의 `except Exception as error` 가 그 오류를 받고 `make_failure_result` 가 오류 이름과 내용을 기록하므로, 엔진은 `INC-403` 부터 계속 처리합니다.
  - `try` / `except` 가 없으면 오류가 `run_all` 밖으로 나와 프로그램이 멈춥니다. <mark style="background:#ffc4d6">단계 2 이후가 출력되지 않고, 로그와 티켓 파일도 저장되지 않으며, `INC-403` ~ `INC-408` 6건이 처리되지 않습니다.</mark> `INC-401` 은 이미 `dami` 를 잠갔는데 그 기록이 남지 않습니다. 아래는 `run_all` 에서 `try` / `except` 를 뺀 채 실행한 결과입니다.

```
KeyError: 'grade'
```

- (다) `INC-404` 의 `203.0.113.80` 은 허용 목록에 있어서 `decide_gate` 가 점수를 보지 않고 「차단 금지」로 정합니다. `INC-406` 의 `gaeun` 은 VIP 라서 <mark style="background:#bde3ff">등급 high +2 와 VIP +3 을 더한 합계 5점</mark>이 승인 기준(3점) 이상이라 「승인 필요」입니다.
  - 허용 목록은 점수와 상관없이 실행하지 않는 대상이고, VIP 는 점수로 사람의 승인을 받는 대상이라 결과가 다릅니다.
  - 조치를 실행한 뒤에는 이미 잠기거나 차단된 계정과 IP 가 업무를 막을 수 있어서, <mark>승인 게이트는 `execute_action` 보다 먼저 판단해야 합니다.</mark> 아래 「자주 틀리는 곳」의 5번처럼 순서나 조건이 거꾸로 되면 허용 목록 IP 가 차단됩니다.

**왜**

- <mark>엔진은 「실행하기 전에 정책으로 막고, 실행한 뒤에는 기록을 남기고, 오류는 알림 한 건에 한정한다」는 순서입니다.</mark> 승인 게이트를 엔진 안에 고정하면 사람이 함수를 직접 호출하면서 게이트를 건너뛰는 실수를 막을 수 있습니다. 오류를 알림 한 건에 한정하면 한 건의 문제가 나머지 알림의 처리를 멈추지 않습니다. 대신 코드의 실수도 실패로 나타나므로(아래 4번), 실패 건수를 매번 확인해야 합니다.

**자주 틀리는 곳**

아래 결과는 해당 번호의 줄을 비우고 실행한 것입니다(비운 줄의 주석은 남겨 둔 상태입니다).

- 1번을 비워 두면 `if` 아래에 실행할 줄이 없어 실행하기 전에 멈춥니다. 2번 · 3번 · 7번을 비워도 같은 오류가 납니다(`if` · `else` · `try` 아래가 빕니다). 파이썬 버전에 따라 뒤에 `after 'if' statement on line …` 같은 설명이 붙습니다.

```
IndentationError: expected an indented block
```

- 4번을 비워 두면 프로그램은 멈추지 않지만 <mark style="background:#ffc4d6">**조치를 처리하는 알림이 모두 실패로 나옵니다.**</mark> `except Exception` 이 코드의 실수까지 받아서 알림마다 실패로 적기 때문입니다. 단계 2 에 `INC-401` 의 실패와 단계 3 의 `실패 : 6 건` 이 나오는 것이 이 실수의 결과입니다.

```
INC-401 dami → 실패 · NameError: name 'decision' is not defined
실패 : 6 건
```

- 5번을 비워 두면 그 아래 미리 채운 줄이 앞줄보다 들여써져 있어 실행하기 전에 멈춥니다.

```
IndentationError: unexpected indent
```

- 5번에서 `==` 대신 `!=` 를 쓰면 오류 없이 <mark style="background:#ffc4d6">**자동이 아닌 조치가 실행됩니다.**</mark> 허용 목록 IP(`INC-404`)가 차단되고, 자동이어야 하는 `dami` 는 잠기지 않습니다. 게이트가 「차단 금지」라고 적었어도 실행 줄이 같이 나오는 것이 이 실수의 결과입니다. 아래는 관련 알림만 발췌한 출력입니다.

```
INC-401 dami high → 자동 실행 · PB-001 · 티켓 TCK-1
    계정 잠금 dami → 자동 · 등급 high +2, 합계 2점
INC-404 203.0.113.80 high → 차단 금지 · PB-003 · 티켓 TCK-3
    IP 차단 203.0.113.80 → 차단 금지 · 허용 목록 대상
    실행: 차단되지 않음 → 차단됨
INC-406 gaeun high → 승인 대기 · PB-001 · 티켓 TCK-5
    계정 잠금 gaeun → 승인 필요 · 등급 high +2, VIP 계정 +3, 합계 5점
    실행: 변경 없음 → 변경 없음
```

- 6번을 비워 두면 오류 없이 <mark style="background:#ffc4d6">**`티켓 생성` · `담당자 알림` 까지 조치로 취급돼 `dami` · `seoyeon` 이라는 이름이 IP 로 차단됩니다.**</mark> 계정 이름을 IP 차단 함수에 넣은 결과입니다.

```
INC-401 dami high → 자동 실행 · PB-001 · 티켓 TCK-1
    계정 잠금 dami → 자동 · 등급 high +2, 합계 2점
    실행: 잠기지 않음 → 잠김
    티켓 생성 dami → 자동 · 등급 high +2, 합계 2점
    실행: 차단되지 않음 → 차단됨
INC-407 seoyeon mid → 자동 실행 · PB-002 · 티켓 TCK-6
    담당자 알림 seoyeon → 자동 · 등급 mid +1, 합계 1점
    실행: 차단되지 않음 → 차단됨
    티켓 생성 seoyeon → 자동 · 등급 mid +1, 합계 1점
    실행: 차단되지 않음 → 차단됨
```

- 8번을 비워 두면 `try` 만 있고 `except` 가 없어서 실행하기 전에 멈춥니다. 파이썬 3.10 이상에서는 `SyntaxError: expected 'except' or 'finally' block` 문구로 나옵니다.

```
SyntaxError: invalid syntax
```

- 9번을 비워 두면 오류 없이 <mark style="background:#ffc4d6">**처리 결과별 알림 수가 모두 0건으로 나옵니다.**</mark> 단계 2 의 알림은 정상으로 나오는데 단계 3 만 틀립니다.

```
--- 단계 3: 처리 결과별 알림 수
자동 실행 : 0 건
승인 대기 : 0 건
차단 금지 : 0 건
조치 없음 : 0 건
실패 : 0 건
```

**관제에서는**

- 알림 하나의 오류가 전체 처리를 멈추지 않게 하는 방식은 SOAR 에서 흔히 쓰는 설계입니다. 다만 오류를 받은 뒤에는 <mark>실패 건수를 모니터링하고 실패한 알림을 담당자에게 넘기는 절차</mark>를 함께 둬야 실패가 확인되지 않은 채 남지 않습니다. 오늘의 처리 결과 다섯 가지 이름은 이 수업에서 정한 것입니다.

---

### 정답 3-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day06_3-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예)

`engine_input.py` 의 1 ~ 8번입니다.

```python
        # 1. key 가 record 안에 없으면 (if, not in)
        if key not in record:                                  # 필수 키가 기록에 없으면
    # 2. record["grade"] 가 GRADES 안에 없으면 (if, not in)
    if record["grade"] not in GRADES:                          # 등급 이름을 엔진이 모르면
    # 3. "INC-" 뒤에 str(number) 를 이어 붙여 alert_id 에 저장한다
    alert_id = "INC-" + str(number)                            # 번호 앞에 INC- 를 붙인다
    # 4. 키 "id"(alert_id) · "entity" · "grade" · "score" · "reasons"(record 의 같은 이름 키의 값), "status"("탐지됨") 를 가진 딕셔너리를 alert 에 저장한다
    alert = {                                                  # 엔진이 읽는 알림 딕셔너리
        "id": alert_id,                                        # 알림 번호
        "entity": record["entity"],                            # 대상
        "grade": record["grade"],                              # 등급
        "score": record["score"],                              # 점수
        "reasons": record["reasons"],                          # 탐지된 규칙 이름 리스트
        "status": "탐지됨",                                    # 처음 상태
    }
        # 5. find_schema_problem(record) 의 결과를 problem 에 저장한다
        problem = find_schema_problem(record)                  # 모양 점검 결과를 받는다
        # 6. problem 이 "" 이면 (if, ==)
        if problem == "":                                      # 문제가 없으면
        # 7. outcome_counts[outcome] 에 outcome_counts[outcome] + 1 을 저장한다 (1 늘린다)
        outcome_counts[outcome] = outcome_counts[outcome] + 1  # 이 처리 결과의 알림 수를 1 늘린다
            # 8. step["executed"] 가 참이면 (if)
            if step["executed"]:                               # 실행한 조치이면
```

위 줄만으로는 `if` 안에 들어가는 줄이 어느 것인지 알기 어려우니, 미리 채운 줄까지 넣은 세 함수의 완성된 모양을 함께 봅니다.

**전체 모양 — `find_schema_problem`**

```python
def find_schema_problem(record):                      # 4과목 결과 기록 한 건을 받는 함수
    """엔진이 읽을 수 없는 기록이면 그 이유 문장을, 문제가 없으면 빈 문자열("")를 리턴한다. 4과목 파일의 모양이 바뀌었을 때 엔진이 오류를 내기 전에 걸러 낼 때 쓴다."""
    for key in REQUIRED_KEYS:                         # 필수 키를 하나씩 꺼낸다 — 미리 채운 줄
        if key not in record:                         # 필수 키가 기록에 없으면
            return "필수 키 없음: " + key             # 어떤 키가 없는지 이유로 리턴한다 — 미리 채운 줄
    if record["grade"] not in GRADES:                 # 등급 이름을 엔진이 모르면
        return "알 수 없는 등급: " + record["grade"]  # 등급 이름을 이유로 리턴한다 — 미리 채운 줄
    if record["reasons"] == []:                       # 탐지된 규칙 리스트가 비어 있으면 — 미리 채운 줄
        return "탐지된 규칙이 없음"                   # 이유를 리턴한다 — 미리 채운 줄
    return ""                                         # 문제가 없으면 빈 문자열를 리턴한다 — 미리 채운 줄
```

**전체 모양 — `split_records`**

```python
def split_records(records):                                          # 4과목 결과 기록 리스트를 받는 함수
    """기록마다 모양을 점검해 엔진에 넣을 알림 리스트와 거절한 기록 리스트를 만들고 두 리스트를 함께 리턴한다. 거절한 기록을 이유와 함께 남겨 기록 없이 빠지지 않게 할 때 쓴다."""
    alerts = []                                                      # 엔진에 넣을 알림을 모을 빈 리스트 — 미리 채운 줄
    rejected = []                                                    # 거절한 기록과 이유를 모을 빈 리스트 — 미리 채운 줄
    number = FIRST_NUMBER                                            # 다음에 붙일 알림 번호 — 미리 채운 줄
    for record in records:                                           # 기록을 하나씩 꺼낸다 — 미리 채운 줄
        problem = find_schema_problem(record)                        # 모양 점검 결과를 받는다
        if problem == "":                                            # 문제가 없으면
            alert = make_alert(record, number)                       # 알림 모양으로 바꾼다 — 미리 채운 줄
            alerts.append(alert)                                     # 알림 리스트에 추가한다 — 미리 채운 줄
            number = number + 1                                      # 다음 번호로 넘어간다 — 미리 채운 줄
        else:                                                        # 문제가 있으면 — 미리 채운 줄
            rejected.append({"record": record, "problem": problem})  # 기록과 이유를 거절 리스트에 추가한다 — 미리 채운 줄
    return alerts, rejected                                          # 두 리스트를 함께 리턴한다 — 미리 채운 줄
```

**전체 모양 — `summarize`**

```python
def summarize(results):                                        # 엔진 결과 기록 리스트를 받는 함수
    """결과 기록을 모아 처리 결과별 알림 수 · 만든 티켓 수 · 실제로 실행한 조치 문장 리스트를 담은 요약 딕셔너리를 리턴한다. 운영 담당자가 한 번에 볼 요약이 필요할 때 쓴다."""
    outcome_counts = {"자동 실행": 0, "승인 대기": 0, "차단 금지": 0, "조치 없음": 0, "실패": 0}  # 처리 결과마다 알림 수 : 처음에는 모두 0 — 미리 채운 줄
    ticket_count = 0                                           # 만든 티켓 수 : 처음에는 0 — 미리 채운 줄
    executed_actions = []                                      # 실제로 실행한 조치 문장을 모을 빈 리스트 — 미리 채운 줄
    for result in results:                                     # 결과 기록을 하나씩 꺼낸다 — 미리 채운 줄
        outcome = result["outcome"]                            # 이 알림의 처리 결과 — 미리 채운 줄
        outcome_counts[outcome] = outcome_counts[outcome] + 1  # 이 처리 결과의 알림 수를 1 늘린다
        if result["ticket"] != "":                             # 티켓이 있으면 — 미리 채운 줄
            ticket_count = ticket_count + 1                    # 티켓 수를 1 늘린다 — 미리 채운 줄
        for step in result["steps"]:                           # 조치 결과를 하나씩 꺼낸다 — 미리 채운 줄
            if step["executed"]:                               # 실행한 조치이면
                action_text = result["incident"] + " " + step["action"] + " " + step["target"] + ": " + step["before"] + " → " + step["after"]  # 알림 · 조치 · 대상 · 전 · 후 상태를 한 문장으로 만든다 — 미리 채운 줄
                executed_actions.append(action_text)           # 문장을 추가한다 — 미리 채운 줄
    summary = {"outcome_counts": outcome_counts, "ticket_count": ticket_count, "executed_actions": executed_actions}  # 요약 딕셔너리 — 미리 채운 줄
    return summary                                             # 요약을 리턴한다 — 미리 채운 줄
```

`day06_3-1_run.py` 의 9번입니다.

```python
# 9. run_all(alerts, context) 의 결과를 results 에 저장한다
results = run_all(alerts, context)  # 알림을 하나씩 엔진으로 처리한다
```

**결과**

- (가) 출력은 다음과 같습니다. 단계 5 의 처리 결과는 자동 실행 <mark style="background:#bde3ff">**2건**</mark> · 승인 대기 <mark style="background:#bde3ff">**0건**</mark> · 차단 금지 <mark style="background:#bde3ff">**0건**</mark> · 조치 없음 <mark style="background:#bde3ff">**3건**</mark> · 실패 <mark style="background:#bde3ff">**0건**</mark>이고, 실제로 실행한 조치는 <mark style="background:#bde3ff">`INC-501` 의 `dami` 계정 잠금 · `INC-505` 의 `198.51.100.90` 차단</mark>입니다.

```
--- 단계 1: 4과목 탐지 결과 5 건
--- 단계 2: 모양 점검 시험 (일부러 틀린 기록)
hana → 필수 키 없음: grade
minsu → 알 수 없는 등급: critical
--- 단계 3: 엔진에 넣을 알림 5 건 · 거절한 기록 0 건
INC-501 dami high 60 ['퇴사한 계정']
INC-502 seoyeon mid 45 ['평소와 다른 IP', '대량 다운로드']
INC-503 gaeun mid 40 ['규칙은 허용인데 서버가 거절', '여러 로그 연결']
INC-504 jiwoo mid 35 ['업무 시간 밖 로그인', '평소와 다른 IP']
INC-505 198.51.100.90 low 30 ['경로 스캔']
--- 단계 4: 엔진 처리 결과
INC-501 dami → 자동 실행 · PB-001 · 티켓 TCK-1
INC-502 seoyeon → 조치 없음 · PB-002 · 티켓 TCK-2
INC-503 gaeun → 조치 없음 · 없음 · 티켓 TCK-3
INC-504 jiwoo → 조치 없음 · 없음 · 티켓 TCK-4
INC-505 198.51.100.90 → 자동 실행 · PB-003 · 티켓 TCK-5
--- 단계 5: 운영 요약
자동 실행 2 건 · 승인 대기 0 건 · 차단 금지 0 건 · 조치 없음 3 건 · 실패 0 건
티켓 5 건 · 실제로 실행한 조치 2 건
INC-501 계정 잠금 dami: 잠기지 않음 → 잠김
INC-505 IP 차단 198.51.100.90: 차단되지 않음 → 차단됨
--- 단계 6: risk_engine_log.json · engine_summary.json · risk_tickets.json 저장
```

- (나) `seoyeon`(`INC-502`)은 플레이북 `PB-002`(대량 다운로드)가 맞지만, 그 플레이북의 액션이 `담당자 알림` · `티켓 생성` 뿐이라 승인 게이트를 거칠 조치(계정 잠금 · IP 차단)가 없습니다. `gaeun`(`INC-503`)과 `jiwoo`(`INC-504`)는 단계 4 의 플레이북 번호가 <mark style="background:#bde3ff">「없음」</mark>입니다. 월요일 플레이북 3개의 트리거 규칙은 퇴사한 계정 · 대량 다운로드 · 경로 스캔이고, 두 대상의 이유(`규칙은 허용인데 서버가 거절` · `여러 로그 연결` / `업무 시간 밖 로그인` · `평소와 다른 IP`)는 그 규칙에 없기 때문입니다.
  - 티켓이 없으면 세 알림은 엔진이 한 일도 남은 기록도 없어서 담당자가 알 방법이 없습니다. <mark style="background:#ffc4d6">티켓이 조치 없는 알림을 사람에게 넘기는 유일한 경로입니다.</mark> 세 알림의 티켓(`TCK-2` ~ `TCK-4`)에는 다음 할 일로 「자동 조치가 없는 알림이니 직접 보고 조치가 필요한지 정한다」가 적힙니다.
- (다) `minsu` 기록은 등급이 `critical` 이라 엔진이 아는 등급(`GRADES`: high · mid · low)에 없어서 <mark style="background:#bde3ff">`알 수 없는 등급: critical`</mark> 로 거절됩니다. 거절하면 거절 리스트에 이유가 남아 4과목 쪽을 고칠 수 있습니다.
  - 거절 없이 엔진에 넣으면 `match_playbooks` 가 `GRADE_ORDER["critical"]` 을 찾다가 오류를 내고, 2교시 `INC-402` 처럼 그 알림만 실패로 기록됩니다. 조치도 티켓도 없고 원인은 오류 문장에만 남습니다. 아래는 그렇게 실행한 결과입니다.

```
실패 · KeyError: 'critical'
```

**왜**

- <mark>입력 검증은 엔진이 오류를 내기 전에 문제를 이유와 함께 남기고, 오류 격리는 걸러지지 않은 문제를 알림 한 건에 한정합니다.</mark> 둘 중 하나만 있으면 잘못된 기록이 조치도 티켓도 없이 사라지거나, 엔진이 멈춥니다. 운영 요약은 처리 결과를 한 장으로 모아, 근무 인계와 보고에서 「무엇을 실행했고 무엇이 사람에게 남았는지」를 바로 알게 합니다.

**자주 틀리는 곳**

아래 결과는 해당 번호의 줄을 비우고 실행한 것입니다(비운 줄의 주석은 남겨 둔 상태입니다).

- 1번을 비워 두면 오류 없이 <mark style="background:#ffc4d6">**모든 기록이 「필수 키 없음: entity」로 거절됩니다.**</mark> `return` 줄이 `if` 없이 첫 번째 키에서 바로 실행되기 때문입니다. 4과목 기록 5건이 모두 거절되어 엔진에 넣을 알림이 0건입니다.

```
hana → 필수 키 없음: entity
minsu → 필수 키 없음: entity
--- 단계 3: 엔진에 넣을 알림 0 건 · 거절한 기록 5 건
```

- 2번을 비워 두면 `return` 줄이 `for` 안쪽에서 실행되어, 첫 번째 키만 보고 `record["grade"]` 를 읽다가 `grade` 키가 없는 시험 기록에서 오류가 납니다.

```
KeyError: 'grade'
```

- 2번에서 `not in` 대신 `in` 을 쓰면 오류 없이 <mark style="background:#ffc4d6">**엔진이 아는 등급(high · mid · low)이 모두 거절됩니다.**</mark> 단계 3 에서 엔진에 넣을 알림이 0건입니다.

```
--- 단계 3: 엔진에 넣을 알림 0 건 · 거절한 기록 5 건
```

- 3번을 비워 두면 `alert_id` 를 만들지 못해 오류가 납니다. 4번을 비우면 `alert` 가 만들어지지 않아 `return alert` 에서 오류가 나고, 5번을 비우면 `problem` 이 만들어지지 않아 오류가 납니다.

```
NameError: name 'alert_id' is not defined
```

```
NameError: name 'alert' is not defined
```

```
NameError: name 'problem' is not defined
```

- 6번을 비워 두면 그 아래 미리 채운 줄이 앞줄보다 들여써져 있어 실행하기 전에 멈춥니다.

```
IndentationError: unexpected indent
```

- 7번을 비워 두면 오류 없이 <mark style="background:#ffc4d6">**처리 결과별 알림 수가 모두 0건으로 나옵니다.**</mark> 티켓 수와 실행한 조치는 정상입니다.

```
--- 단계 5: 운영 요약
자동 실행 0 건 · 승인 대기 0 건 · 차단 금지 0 건 · 조치 없음 0 건 · 실패 0 건
티켓 5 건 · 실제로 실행한 조치 2 건
INC-501 계정 잠금 dami: 잠기지 않음 → 잠김
INC-505 IP 차단 198.51.100.90: 차단되지 않음 → 차단됨
```

- 8번을 비워 두면 오류는 나지 않고 출력도 정답과 같습니다. 오늘 샘플은 조치가 모두 실행된 것이라 `if` 가 없어도 같은 결과가 나옵니다. <mark style="background:#ffc4d6">**승인 대기 · 차단 금지 알림이 있는 결과에서는 실행하지 않은 조치까지 「실행한 조치」에 들어갑니다.**</mark> 출력이 맞아도 코드를 다시 읽어 확인합니다.
- 9번을 비워 두면 `results` 가 만들어지지 않아 오류가 납니다.

```
NameError: name 'results' is not defined
```

**관제에서는**

- 탐지와 대응은 다른 팀이나 다른 제품이 만드는 경우가 많아서 데이터 모양이 어긋나기 쉽습니다. 둘 사이에 입력 검증을 두고 <mark>거절한 기록 수를 모니터링</mark>하면, 거절이 갑자기 늘었을 때 상류의 형식이 바뀐 것을 알 수 있습니다. 오늘의 필수 키 네 개와 등급 세 가지는 이 수업의 공통 스키마입니다.

---

### 정답 4-1

💻 **터미널에 입력합니다.**

```bash
pwd
python day06_4-1_run.py
```
- 명령 풀이: `pwd` 지금 있는 폴더의 위치 확인 · `python 파일이름` 파이썬으로 실행 파일 실행

**채운 코드** (한 예)

`policy_check.py` 의 1 ~ 6번입니다.

```python
            # 1. decide_gate(step["request"], policy) 의 두 결과를 new_decision, new_reasons 에 저장한다
            new_decision, new_reasons = decide_gate(step["request"], policy)   # 저장된 조치 요청으로 게이트의 결정을 다시 구한다
            # 2. new_decision 이 "자동" 이 아니고(and) step["executed"] 가 참이면 (if, !=, and)
            if new_decision != "자동" and step["executed"]:                    # 다시 구한 결정이 자동이 아닌데 실행했으면
            # 3. step["target"] 이 allowlist_ips 안에 있고(and) step["after"] 가 "차단됨" 이면 (if, in, ==, and)
            if step["target"] in allowlist_ips and step["after"] == "차단됨":  # 허용 목록 IP 가 차단되었으면
            # 4. step["target"] 이 vip_accounts 안에 있고(and) step["after"] 가 "잠김" 이면 (if, in, ==, and)
            if step["target"] in vip_accounts and step["after"] == "잠김":     # VIP 계정이 잠겼으면
        # 5. executed_count 가 0 보다 크고(and) result["ticket"] 이 "" 이면 (if, >, ==, and)
        if executed_count > 0 and result["ticket"] == "":                      # 실행한 조치가 있는데 티켓이 없으면
    # 6. violations 가 빈 리스트 [] 이면 (if, ==)
    if violations == []:                                                       # 위반이 없으면
```

위 줄만으로는 `if` 안에 들어가는 줄이 어느 것인지 알기 어려우니, 미리 채운 줄까지 넣은 두 함수의 완성된 모양을 함께 봅니다. 3 · 4 · 5번도 `if` 아래의 미리 채운 `violations.append(…)` 줄이 `if` 안쪽입니다.

**전체 모양 — `find_gate_bypass`**

```python
def find_gate_bypass(results, policy):                                        # 결과 기록 리스트와 승인 정책을 받는 함수
    """저장된 조치 요청으로 승인 게이트의 결정을 다시 구해, 자동이 아닌데 실행된 조치가 있는 알림 번호를 리스트로 리턴한다. 게이트를 거치지 않았거나 결정을 바꿔 쓴 실행을 찾을 때 쓴다."""
    violations = []                                                           # 위반한 알림 번호를 모을 빈 리스트 — 미리 채운 줄
    for result in results:                                                    # 결과 기록을 하나씩 꺼낸다 — 미리 채운 줄
        for step in result["steps"]:                                          # 조치 결과를 하나씩 꺼낸다 — 미리 채운 줄
            new_decision, new_reasons = decide_gate(step["request"], policy)  # 저장된 조치 요청으로 게이트의 결정을 다시 구한다
            if new_decision != "자동" and step["executed"]:                   # 다시 구한 결정이 자동이 아닌데 실행했으면
                violations.append(result["incident"])                         # 알림 번호를 위반 리스트에 추가한다 — 미리 채운 줄
    return violations                                                         # 위반한 알림 번호 리스트를 리턴한다 — 미리 채운 줄
```

**전체 모양 — `judge`**

```python
def judge(violations):    # 위반한 알림 번호 리스트를 받는 함수
    """위반이 하나도 없으면 「PASS」, 하나라도 있으면 「FAIL」을 리턴한다. 점검 결과를 한눈에 보이게 출력할 때 쓴다."""
    if violations == []:  # 위반이 없으면
        return "PASS"     # 위반이 없으면 PASS 를 리턴한다 — 미리 채운 줄
    return "FAIL"         # 위반이 있으면 FAIL 을 리턴한다 — 미리 채운 줄
```

`day06_4-1_run.py` 의 7 ~ 9번입니다. 8번 아래 미리 채운 `fail_count` 줄이 `if` 안쪽입니다.

```python
    # 7. load_json(log_path) 의 결과를 results 에 저장한다
    results = load_json(log_path)  # 로그 파일을 리스트로 읽는다
        # 8. verdict 가 "FAIL" 이면 (if, ==)
        if verdict == "FAIL":      # 점검에 실패했으면
# 9. rows 를 CHECK_PATH 파일에 저장한다 (save_json)
save_json(rows, CHECK_PATH)        # 점검 결과를 파일에 저장한다
```

**결과**

- (가) 출력은 다음과 같습니다. FAIL 이 나온 로그는 <mark style="background:#bde3ff">`gate_off_log.json`</mark> 하나이고, FAIL 점검은 <mark style="background:#bde3ff">게이트 우회 실행(`INC-404` · `INC-405` · `INC-406`)과 허용 목록 IP 차단(`INC-404`)</mark> 두 개입니다.

```
--- 단계 1: 점검할 로그 3 개 · 점검 4가지
--- 단계 2: 로그마다 점검 결과
[engine_log.json] 알림 8 건
   게이트 우회 실행 : PASS · 위반 0 건 []
   허용 목록 IP 차단 : PASS · 위반 0 건 []
   VIP 계정 잠금 : PASS · 위반 0 건 []
   티켓 없는 조치 : PASS · 위반 0 건 []
[risk_engine_log.json] 알림 5 건
   게이트 우회 실행 : PASS · 위반 0 건 []
   허용 목록 IP 차단 : PASS · 위반 0 건 []
   VIP 계정 잠금 : PASS · 위반 0 건 []
   티켓 없는 조치 : PASS · 위반 0 건 []
[gate_off_log.json] 알림 5 건
   게이트 우회 실행 : FAIL · 위반 3 건 ['INC-404', 'INC-405', 'INC-406']
   허용 목록 IP 차단 : FAIL · 위반 1 건 ['INC-404']
   VIP 계정 잠금 : PASS · 위반 0 건 []
   티켓 없는 조치 : PASS · 위반 0 건 []
--- 단계 3: FAIL 이 나온 점검 2 개 · 전체 점검 12 개
--- 단계 4: policy_check.json 에 12 개 저장
```

- (나) `INC-405` 의 `request` 는 등급 mid 에 `users_on_ip` 가 2 입니다. 승인 정책에서 mid <mark style="background:#ffdcb0">1점</mark>과 함께 쓰는 IP(2개 이상) <mark style="background:#ffdcb0">2점</mark>을 더한 <mark style="background:#bde3ff">합계 3점</mark>이 `approval_score`(3점) 이상이라, `decide_gate` 를 다시 호출하면 「승인 필요」입니다. 그런데 `executed` 가 참이라서 위반입니다.
  - 로그의 `decision` 은 게이트를 끈 엔진이 적은 값(「자동」, 이유 「승인 게이트 끔」)이라 <mark style="background:#ffc4d6">`decision` 만 읽으면 위반이 보이지 않습니다.</mark> 저장된 입력(`request`)으로 다시 구해야 엔진이 적은 값과 상관없이 확인할 수 있습니다.
- (다) `INC-406` 은 `before` 와 `after` 가 모두 <mark style="background:#bde3ff">「변경 없음」</mark>입니다. 수요일의 `lock_account` 가 VIP 계정(`gaeun`)이면 잠그지 않고 「VIP 계정이라 자동 조치 대상이 아님」을 기록하기 때문에 `gaeun` 은 잠기지 않았습니다. 점검 ①은 그래도 조치 함수를 호출한 것(`executed`)이라서 FAIL 입니다.
  - 점검 ③은 게이트나 `lock_account` 와 별도로 결과(`after`)만 봅니다. `lock_account` 에 VIP 리스트를 잘못 전달하거나 함수가 바뀌면 같은 로그에서도 VIP 가 잠길 수 있는데, 그때는 ③이 FAIL 로 잡습니다. <mark>한 겹의 통제가 깨져도 다른 겹의 점검이 잡도록 각각 점검합니다.</mark>

**왜**

- <mark>통제는 만들어 두는 것만으로는 부족하고, 작동했다는 증거를 로그로 확인해야 합니다.</mark> ①은 재수행으로 엔진이 적은 값을 믿지 않고, ②③은 불변 조건으로 게이트의 계산과 무관하게 결과를 봅니다. 점검을 코드로 만들어 두면 알림이 늘어도 같은 방식으로 반복해서 확인할 수 있습니다.

**자주 틀리는 곳**

아래 결과는 해당 번호의 줄을 비우고 실행한 것입니다(비운 줄의 주석은 남겨 둔 상태입니다).

- 1번을 비워 두면 `new_decision` 을 만들지 못해 오류가 납니다.

```
NameError: name 'new_decision' is not defined
```

- 2번 · 5번 · 6번 · 8번을 비워 두면 그 아래 미리 채운 줄이 앞줄보다 들여써져 있어 실행하기 전에 멈춥니다.

```
IndentationError: unexpected indent
```

- 2번에서 `!=` 대신 `==` 를 쓰면 오류 없이 <mark style="background:#ffc4d6">**정상인 로그에서 위반이 나옵니다.**</mark> 자동으로 정해져 실행한 `INC-401` · `INC-403` 이 게이트 우회로 나옵니다. 아래는 첫 번째 로그의 결과입니다.

```
[engine_log.json] 알림 8 건
   게이트 우회 실행 : FAIL · 위반 2 건 ['INC-401', 'INC-403']
   허용 목록 IP 차단 : PASS · 위반 0 건 []
   VIP 계정 잠금 : PASS · 위반 0 건 []
   티켓 없는 조치 : PASS · 위반 0 건 []
```

- 3번을 비워 두면 오류 없이 <mark style="background:#ffc4d6">**조치 요청이 있는 알림이 모두 위반으로 나옵니다.**</mark> `if` 가 없어서 조건과 상관없이 `append` 가 실행되기 때문입니다. 4번을 비워도 같은 꼴이 점검 ③에 나타납니다.

```
[engine_log.json] 알림 8 건
   게이트 우회 실행 : PASS · 위반 0 건 []
   허용 목록 IP 차단 : FAIL · 위반 5 건 ['INC-401', 'INC-403', 'INC-404', 'INC-405', 'INC-406']
   VIP 계정 잠금 : PASS · 위반 0 건 []
   티켓 없는 조치 : PASS · 위반 0 건 []
```

- 3번에서 `and step["after"] == "차단됨"` 을 빠뜨리면 오류 없이 <mark style="background:#ffc4d6">**차단하지 않은 알림도 위반으로 나옵니다.**</mark> `INC-404` 는 허용 목록 IP 라서 승인 게이트가 차단 금지로 막았는데도 위반입니다. 허용 목록에 있는지만 보고 실제로 차단됐는지는 보지 않았기 때문입니다.

```
[engine_log.json] 알림 8 건
   게이트 우회 실행 : PASS · 위반 0 건 []
   허용 목록 IP 차단 : FAIL · 위반 1 건 ['INC-404']
   VIP 계정 잠금 : PASS · 위반 0 건 []
   티켓 없는 조치 : PASS · 위반 0 건 []
```

- 6번에서 `==` 대신 `!=` 를 쓰면 오류 없이 <mark style="background:#ffc4d6">**위반이 없는 점검이 모두 FAIL 로 나옵니다.**</mark> 판정이 거꾸로 되어, 위반이 있는 로그(승인 게이트를 끈 로그)가 PASS 가 됩니다.

```
[engine_log.json] 알림 8 건
   게이트 우회 실행 : FAIL · 위반 0 건 []
   허용 목록 IP 차단 : FAIL · 위반 0 건 []
   VIP 계정 잠금 : FAIL · 위반 0 건 []
   티켓 없는 조치 : FAIL · 위반 0 건 []
```

- 7번을 비워 두면 `results` 가 만들어지지 않아 오류가 납니다.

```
NameError: name 'results' is not defined
```

- 9번을 비워 두면 오류 없이 화면에는 저장했다고 나오지만 <mark style="background:#ffc4d6">**`policy_check.json` 파일이 만들어지지 않습니다.**</mark> 실행한 뒤 `ls` 로 파일이 생겼는지 확인합니다.

```
--- 단계 4: policy_check.json 에 12 개 저장
```

**관제에서는**

- 자동화가 정책대로 동작했는지는 사람이 가끔 읽는 것으로 확인하지 않고, 같은 점검을 로그에 정기적으로 실행해서 확인합니다. 점검에서 FAIL 이 나오면 위반한 알림 번호로 원인을 찾고 담당자에게 알립니다. 승인 게이트를 끈 시험 운영 로그처럼 <mark>통제를 일부러 끈 기록이 운영에 섞이지 않았는지</mark>도 같은 방식으로 확인합니다. 오늘의 네 가지 점검은 예시이고, 실제 점검 내용은 고객사 정책마다 다릅니다.
