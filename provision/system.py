#!/usr/bin/env python3
"""Lima system provision (mode: system, root 권한).

멱등(idempotent)하게 작성 — VM 재시작 시 여러 번 호출될 수 있음.
Lima 템플릿 변수({{.Name}} 등)는 인스턴스 생성 시점에 치환된다.
"""
import subprocess
from pathlib import Path

INSTANCE_NAME = "{{.Name}}"

SSHD_CLOUD_INIT = Path("/etc/ssh/sshd_config.d/50-cloud-init.conf")
SSHD_DROPIN_DIR = Path("/etc/ssh/sshd_config.d")
SSHD_PASSWORD_CONF = SSHD_DROPIN_DIR / "99-password-auth.conf"


def run(cmd, **kwargs):
    print(f"+ {' '.join(cmd)}")
    return subprocess.run(cmd, check=True, **kwargs)


def set_dev_password():
    run(["chpasswd"], input=b"dev:dev")


def enable_ssh_password_auth():
    # SSH 비밀번호 인증 허용 (클라우드 이미지 기본값 no)
    #  - sshd는 '첫 값 우선'이라 50-cloud-init.conf(no)가 이김 → 그 파일을 직접 yes로
    if SSHD_CLOUD_INIT.exists():
        text = SSHD_CLOUD_INIT.read_text()
        text = text.replace("PasswordAuthentication no", "PasswordAuthentication yes")
        SSHD_CLOUD_INIT.write_text(text)

    SSHD_DROPIN_DIR.mkdir(mode=0o755, parents=True, exist_ok=True)
    SSHD_PASSWORD_CONF.write_text("PasswordAuthentication yes\n")

    # sshd 이름이 배포판마다 다름 → 둘 다 시도
    for svc in ("sshd", "ssh"):
        if subprocess.run(["systemctl", "restart", svc]).returncode == 0:
            break


def set_hostname():
    # Lima 기본 hostname은 lima-<name> → mDNS 이름용으로 인스턴스명으로 변경
    run(["hostnamectl", "set-hostname", INSTANCE_NAME])


def enable_mdns():
    run(["dnf", "install", "-y", "avahi", "avahi-tools"])
    run(["systemctl", "enable", "--now", "avahi-daemon"])


def main():
    set_dev_password()
    enable_ssh_password_auth()
    set_hostname()
    enable_mdns()


if __name__ == "__main__":
    main()
