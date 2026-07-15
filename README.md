# lima-template

macOS [Lima](https://lima-vm.io/) VM을 재사용 가능한 템플릿으로 관리하는 프로젝트.

- **런타임**: `vmType: vz` (Apple Virtualization)
- **기본 이미지**: 로컬 Rocky Linux aarch64 (`~/virt/lima/rocky-lima.qcow2`)
- **네트워크**: `vzNAT` (호스트에서 게스트 IP 직접 접근)
- **제어**: [Task](https://taskfile.dev/) (`task up`, `task shell`, …)

## 준비물

```bash
brew install lima go-task
```

로컬 이미지가 없다면 경로를 맞추거나 `IMAGE=` 로 지정하세요.

```bash
# 기본 기대 경로
ls ~/virt/lima/rocky-lima.qcow2
```

## 빠른 시작

```bash
cd ~/dev/lima-template

# 현재 변수 확인
task vars

# 생성 + 시작
task up

# 셸
task shell

# 상태 / IP
task status
task ip
```

## 변수 (템플릿 파라미터)

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `VM` | `rocky` | lima 인스턴스 이름 |
| `CONFIG` | `rocky.yaml` | 템플릿 YAML |
| `IMAGE` | `~/virt/lima/rocky-lima.qcow2` | 게스트 디스크 이미지 |
| `CPUS` | `2` | vCPU |
| `MEMORY` | `14GiB` | 메모리 |
| `DISK` | `50GiB` | 디스크 크기 |
| `USER` | `dev` | 게스트 사용자 (비번: provision 스크립트 기본 `dev:dev`) |

예시:

```bash
# 다른 이름 / 스펙으로 띄우기
task up VM=lab CPUS=4 MEMORY=8GiB DISK=100GiB

# 이미지 경로 지정
task up VM=rocky2 IMAGE=/path/to/rocky.qcow2

# 여러 변수 조합
task recreate VM=lab CPUS=8 MEMORY=16GiB
```

> `create` / `up` / `recreate` 시 `limactl --set` 으로 스펙이 반영됩니다.
> **이미 만든 인스턴스**의 CPU/메모리 변경은 `task edit` 또는 삭제 후 `recreate`가 필요합니다.

## 주요 태스크

| 태스크 | 설명 |
|--------|------|
| `task up` | 없으면 생성 후 시작 |
| `task stop` | 정상 종료 |
| `task restart` | 재시작 |
| `task shell` | 게스트 셸 (`task shell -- ls`) |
| `task ssh-info` | SSH config 조각 출력 |
| `task ip` | vzNAT IP 확인 |
| `task status` / `list` / `info` | 상태 조회 |
| `task delete` | 인스턴스 삭제 (확인 프롬프트) |
| `task recreate` | 삭제 후 재생성 |
| `task logs` | serial 로그 follow |
| `task clone-template DEST=...` | 이 템플릿을 다른 디렉터리로 복사 |

## 템플릿 재사용

새 프로젝트로 복사:

```bash
task clone-template DEST=~/dev/my-lab-vm
cd ~/dev/my-lab-vm
task up VM=my-lab
```

또는 직접 복사:

```bash
cp -R ~/dev/lima-template ~/dev/my-lab-vm
```

## 파일 구성

```
lima-template/
├── README.md        # 이 문서
├── Taskfile.yaml    # up/shell/delete 등 + 변수
└── rocky.yaml       # Lima 인스턴스 템플릿
```

## 게스트 provision 요약

`rocky.yaml` system provision:

1. `dev` 사용자 비밀번호 `dev` 설정
2. hostname을 인스턴스명(`{{.Name}}`)으로 변경
3. `avahi` 설치·기동 (mDNS)

비밀번호/패키지를 바꾸려면 `rocky.yaml`의 `provision` 블록을 수정한 뒤 `task recreate` 하세요.

## 노트

- **아키텍처**: 기본 `aarch64` (Apple Silicon). Intel이면 `rocky.yaml`의 `arch` / 이미지를 바꿔야 합니다.
- **이미지**: git에 qcow2를 넣지 마세요. 호스트 로컬 경로 또는 내부 아티팩트 저장소를 쓰세요.
- **기존 virt 트리**: 원본 작업 디렉터리는 `~/virt/lima` 에 남아 있습니다. 이 레포는 그 설정을 템플릿화한 것입니다.
