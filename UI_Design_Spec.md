# Home UI Implementation Guide

이 문서는 **홈 UI 시퀀스 (시작 -> 60초 대기 -> 다음 페이지)** 구현을 위한 상세 설계도입니다.

## 1. Lua Script Configuration (입/출력 정의)

Lua Script 모듈(`home_ui_logic.lua`)을 Xilica Designer의 "User Modules" 또는 "Lua Script" 블록에 로드하고, 아래와 같이 핀을 구성하세요.

### **설정 변수 (Configuration Variable)**
스크립트 상단에서 다음 값을 수정할 수 있습니다.
- `TIMER_STOP_AT = 60`: 대기 시간 (초 단위)
- `PULSE_THRESH = -20`: 오디오 신호 입력 시 Trigger 레벨 (dB)

### **입력 핀 (Inputs)**
| 핀 번호 | 이름 | 데이터 타입 | 연결 대상 | 설명 |
| :--- | :--- | :--- | :--- | :--- |
| **1** | `Master_Power_Latch` | **Logic** | **시스템 전원 토글 (Latch)** | **High(ON)**: 부팅 시작 / **Low(OFF)**: 즉시 종료 및 초기화 |
| **2** | `Tick_1Hz` | **Logic / Numeric** | **Square Wave / Level** | **Logic (0/1)** 또는 **Numeric (dB)** 모두 가능 (자동 감지) |
| **-** | `(Not Used)` | **-** | **-** | (입력 3번은 사용하지 않음) |

---

### **출력 핀 (Outputs)** - **[전체 Numeric 변경]**
| 핀 번호 | 이름 | 데이터 타입 | 연결 대상 | 기능 설명 |
| :--- | :--- | :--- | :--- | :--- |
| **1** | `Blink_Signal` | **Numeric** | **[Wait Active 이미지]** `Visible` 핀 | **1.0 (ON)** / **0.0 (OFF)** 깜빡임 신호 |
| **2** | `Show_Wait_Text` | **Numeric** | **[Wait Dim 이미지]** `Visible` 핀 | **1.0 (ON)** 대기 화면 표시 |
| **3** | `Show_Next` | **Numeric** | **[다음 페이지 버튼]** `Visible` 핀 | **1.0 (ON)** 60초 후 활성화 |
| **4** | `Progress_Val` | **Numeric** | **Progress Bar** | 0.0 ~ 1.0 실수값 출력 (진행률) |

---

## 2. 화면 배치 및 레이어 구성 (UI Layout)

모든 버튼과 텍스트는 **같은 위치(좌표)에 겹쳐서 배치**하고, 위에서 정의한 `Visible` 신호로 보이거나 숨겨지게 만듭니다.

### **[Center Zone] - 중앙 버튼 영역**
모두 동일한 좌표 (중앙 정렬)에 겹쳐 놓습니다.

1.  **시작/종료 스위치 (Start Switch)**
    *   **스타일**: **Toggle Image Button** (Latch)
    *   **Image On (켜짐)**: **투명 이미지** (보이지 않지만 터치 가능 / 또는 숨김)
    *   **Image Off (꺼짐)**: **"시작하기" 버튼 이미지**
    *   *설명: 스위치가 꺼져있으면 "시작하기"가 보이고, 켜면 이미지가 투명해지면서 뒤에 있는 대기 화면이 보이게 됩니다.*
2.  **Wait Dim (어두운 배경)** (`wait_dim.png`)
    *   **Visibility**: 연결 -> Lua Output **2** (`Show_Wait_Text`)
3.  **Wait Active (밝은 글씨)** (`wait_active.png`)
    *   **Visibility**: 연결 -> Lua Output **1** (`Blink_Signal`)
    *   *효과: Dim 이미지는 계속 켜져 있고, Active 이미지가 그 위에서 1초마다 나타났다 사라지며 깜빡이는 효과 연출.*
4.  **다음 페이지 버튼** (`Next Page Button`)
    *   **Visibility**: 연결 -> Lua Output **3** (`Show_Next`)

### **[Bottom Zone] - 하단 안내 문구 영역**
중앙 버튼 아래쪽에 텍스트 박스를 겹쳐 놓습니다.

1.  **안내 문구 1** ("제어를 시작하려면 시작하기 버튼을 눌러주세요")
    *   **Visibility**: 스위치 상태와 연동 (또는 시작 버튼 이미지에 포함시키는 것을 추천)
2.  **안내 문구 2** ("시스템 초기화 중입니다... 잠시만 기다려 주세요")
    *   **Visibility**: 연결 -> Lua Output **2** (`Show_Wait_Text`)
3.  **Progress Bar** (Bar Graph)
    *   **Value**: 연결 -> Lua Output **4** (`Progress_Val`)
    *   **Visibility**: 연결 -> Lua Output **2** (`Show_Wait_Text`) (대기 중에만 보이도록)
4.  **안내 문구 3** ("다음 페이지 버튼을 눌러주세요")
    *   **Visibility**: 연결 -> Lua Output **3** (`Show_Next`)

---

## 3. 전체 시나리오 흐름 (Scenario Walkthrough) - **[수정됨 V2]**
 
 이 시스템은 **단일 전원 스위치(Latch Type)**의 상태에 따라 전체 시스템을 제어합니다.
 
 1.  **초기 상태 (Switch OFF)**
    *   **상황**: 전원 스위치가 **OFF** 상태입니다.
    *   **화면**: **"시스템 전원을 켜주세요"** 또는 **"시작하기"** 안내 문구가 표시됩니다. (IDLE 상태)
    *   **출력**: `System_Power_On` (Output 5)은 **OFF (Low)**입니다.

2.  **전원 투입 (Switch ON)**
    *   **사용자 동작**: 전원 스위치를 올려서 **ON**으로 만듭니다. (Latch High)
    *   **시스템 동작**:
        *   `Master_Power_Latch` 입력이 High가 되는 즉시 `System_Power_On` (Output 5) 출력이 켜집니다.
        *   **부팅 시퀀스(Wait State)**가 바로 시작됩니다.

3.  **부팅 대기 (Booting Delay, 0 ~ 60초)**
    *   **상황**: 스위치는 계속 **ON** 상태입니다. 장비가 부팅되는 동안 안전 대기 시간이 흐릅니다.
    *   **화면**: "시스템 초기화 중..." 문구와 Progress Bar가 나타납니다.

4.  **부팅 완료 (System Ready)**
    *   **상황**: 60초 경과. 스위치 **ON** 유지 중.
    *   **화면**: 대기 문구가 사라지고 제어 버튼(다음 페이지)이 활성화됩니다.

5.  **시스템 종료 (Switch OFF)**
    *   **사용자 동작**: 언제든지 전원 스위치를 **OFF**로 내립니다.
    *   **결과**:
        *   `System_Power_On` 출력이 즉시 **OFF**가 되어 장비 전원이 꺼집니다.
        *   화면은 즉시 0초로 리셋되고 초기 상태로 돌아옵니다.
