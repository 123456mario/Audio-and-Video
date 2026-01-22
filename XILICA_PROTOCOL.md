# Xilica - Wing Bridge Control Protocol

이 문서는 Xilica 프로세서(Lua Script)와 Python Bridge 간의 통신 프로토콜을 정의합니다.
통신 방식은 TCP 소켓을 사용하며, 아래 명령어 포맷을 따릅니다.

## 기본 형식
모든 명령어는 ASCII 텍스트로 전송되며, 줄바꿈 문자 `\r` (CR)로 종료됩니다.
**명령어와 키는 대소문자를 구분하지 않습니다.** (예: `SET`, `set`, `Set` 모두 가능)

```
SET [KEY] [VALUE]\r
```

---

## 1. 채널별 제어 (Channel 1 ~ 8)
채널 번호(`n`)는 1부터 8까지 할당됩니다.

### 볼륨 (Volume)
*   **키 형식**: `CH[n]_VOL`
*   **값 범위**: `-90.0` ~ `+10.0` (dB)
*   **설명**: 해당 채널의 페이더 레벨을 설정합니다.

| 채널 번호 | 명령어 예시 | 설명 |
| :--- | :--- | :--- |
| **CH 1** | `SET CH1_VOL -10.0` | 채널 1 볼륨을 -10.0dB로 설정 |
| **CH 2** | `SET CH2_VOL 0.0` | 채널 2 볼륨을 0.0dB로 설정 |
| **CH ...** | `...` | ... |
| **CH 8** | `SET CH8_VOL -40.5` | 채널 8 볼륨을 -40.5dB로 설정 |

### 뮤트 (Mute)
*   **키 형식**: `CH[n]_MUTE`
*   **값**: `1` (Muted), `0` (Unmuted)
*   **설명**: 해당 채널의 음소거 상태를 제어합니다.

| 채널 번호 | 명령어 예시 | 설명 |
| :--- | :--- | :--- |
| **CH 1** | `SET CH1_MUTE 1` | 채널 1 음소거 (소리 끔) |
| **CH 2** | `SET CH2_MUTE 0` | 채널 2 음소거 해제 (소리 켬) |
| **CH ...** | `...` | ... |
| **CH 8** | `SET CH8_MUTE 1` | 채널 8 음소거 |

---

## 2. 메인 믹스 제어 (Main Mix)
메인 스테레오 출력(L/R)을 제어합니다.

### 메인 볼륨 (Main Volume)
*   **키 형식**: `MAIN_VOL`
*   **값 범위**: `-90.0` ~ `+10.0` (dB)

| 명령어 예시 | 설명 |
| :--- | :--- |
| `SET MAIN_VOL -5.0` | 메인 볼륨을 -5.0dB로 설정 |
| `SET MAIN_VOL 0.0` | 메인 볼륨을 0.0dB로 설정 |

### 메인 뮤트 (Main Mute)
*   **키 형식**: `MAIN_MUTE`
*   **값**: `1` (Muted), `0` (Unmuted)
*   **주의**: Wing 믹서 내부 로직과 다를 수 있으나, 브릿지에서 자동으로 변환 처리됩니다 (1=Mute).

| 명령어 예시 | 설명 |
| :--- | :--- |
| `SET MAIN_MUTE 1` | 메인 출력 전체 음소거 |
| `SET MAIN_MUTE 0` | 메인 출력 음소거 해제 |

---

## 3. PTZ 카메라 제어 (PTZ Camera)
동일한 TCP 연결을 통해 카메라 제어 명령도 전송할 수 있습니다.

*   **형식**: `CAM[n] [DIRECTION] [STATE]`
*   **카메라**: `CAM1`, `CAM2`

| 명령어 예시 | 설명 |
| :--- | :--- |
| `CAM1 UP ON` | 카메라 1번 위로 이동 시작 |
| `CAM1 UP OFF` | 카메라 1번 위로 이동 정지 |
| `CAM1 ZOOMIN ON` | 카메라 1번 줌-인 시작 |
| `CAM1 ZOOMIN OFF` | 카메라 1번 줌-인 정지 |
| `CAM1 HOME ON` | 카메라 1번 홈 위치로 이동 |

---

## 4. 페이지 전환 (Page Flip Loopback)
Xilica 로직에서 Python Bridge로 페이지 전환 요청을 보내면, Bridge가 다시 Xilica의 버튼을 눌러주는 방식입니다.

*   **형식**: `PAGE [PAGE_NAME]`
*   **동작**:
    1. Bridge가 `PAGE [PAGE_NAME]` 수신
    2. Bridge가 Xilica로 `SET [PAGE_NAME]_BTN 1` 전송 (누름)
    3. 0.2초 후 `SET [PAGE_NAME]_BTN 0` 전송 (뗌)

| 명령어 예시 | 설명 |
| :--- | :--- |
| `PAGE MAIN_VIEW` | `MAIN_VIEW_BTN` 버튼을 눌렀다 떼서 'Main View' 페이지로 이동 |
| `PAGE CAM_CTRL` | `CAM_CTRL_BTN` 버튼을 눌렀다 떼서 'Camera Control' 페이지로 이동 |
