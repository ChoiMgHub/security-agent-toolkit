import json

with open("config/roles.json", encoding="utf-8") as f:
    ROLES = json.load(f)

with open("config/users.json", encoding="utf-8") as f:
    USERS = json.load(f)


def check_permission(user, resource, action):
    """허용 여부와 이유를 돌려준다."""

    # [1] 등록된 사용자인지 확인
    if user not in USERS:
        return False, "등록되지 않은 사용자"

    # [2]-1. 재직 중이 아니면 거부한다.
    if not USERS[user]["employed"]:
        return False, "퇴사한 계정"

    # [3]-1. 사용자의 역할을 role에 담는다.
    role = USERS[user]["role"]

    # [3]-2. 정의되지 않은 역할이면 거부한다.
    if role not in ROLES:
        return False, "역할이 없음"

    # [4]-1. 자원과 행위를 합쳐 permission에 담는다.
    permission = f"{resource}:{action}"

    # [4]-2. 역할에 해당 권한이 없으면 거부한다.
    if permission not in ROLES[role]:
        return False, "권한 없음"

    return True, "허용"