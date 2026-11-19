import copy                                                           # 처음 상태를 복사해 쓰기 위해 copy 를 불러온다
from incident import load_json, save_json                             # 어제 파일의 파일 읽기 · 쓰기 함수를 불러온다

STATE_PATH = "containment_state.json"                                 # 연습용 시스템 상태를 저장할 파일 이름
LOG_PATH = "containment_log.json"                                     # 조치 기록을 저장할 파일 이름
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


def save_state(state):                                                # 연습용 시스템 상태를 받는 함수
    """상태를 파일에 저장한다.
    다음 프로그램이 이어서 읽을 수 있게 할 때 쓴다.
    """
    save_json(state, STATE_PATH)                                      # 상태를 JSON 파일로 저장한다


def load_state():                                                     # 인자가 없는 함수
    """저장해 둔 상태 파일을 읽어 리턴한다.
    저장이 제대로 됐는지 확인하거나 이어서 일할 때 쓴다.
    """
    return load_json(STATE_PATH)                                      # 상태 파일을 읽어 리턴한다


def reset_log():                                                      # 인자가 없는 함수
    """조치 기록 파일을 빈 리스트로 비운다.
    실행할 때마다 기록을 처음부터 쌓을 때 쓴다.
    """
    save_json([], LOG_PATH)                                           # 빈 리스트를 기록 파일로 저장한다


def make_record(action, target, incident_id, before, after, reason):  # 조치 이름 · 대상 · 인시던트 번호 · 조치 전 · 조치 후 · 이유를 받는 함수
    """조치 한 건(무엇을 · 누구에게 · 조치 전 · 조치 후 · 이유)의 기록을 딕셔너리로 만들어 리턴한다.
    조치 전과 후 상태를 함께 남겨 두고 싶을 때 쓴다.
    """
    record = {"action": action, "target": target, "incident": incident_id, "before": before, "after": after, "reason": reason}  # 조치 한 건의 기록을 딕셔너리로 만든다
    return record                                                     # 기록 한 건을 리턴한다


def append_log(record):                                               # 기록 한 건을 받는 함수
    """기록 파일을 읽어 기록 한 건을 더하고 다시 저장한다. 파일이 아직 없으면 빈 리스트로 시작한다.
    조치할 때마다 기록을 한 건씩 쌓아 둘 때 쓴다.
    """
    try:                                                              # 파일 읽기를 시도한다 — 미리 채운 줄
        log = load_json(LOG_PATH)                                     # 기록 파일을 읽는다 — 미리 채운 줄
    except FileNotFoundError:                                         # 파일이 없으면 — 미리 채운 줄
        log = []                                                      # 빈 리스트로 시작한다 — 미리 채운 줄
    log.append(record)                                                # 기록 한 건을 리스트에 추가한다
    save_json(log, LOG_PATH)                                          # 기록 파일로 다시 저장한다
