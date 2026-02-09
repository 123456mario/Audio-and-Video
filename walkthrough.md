# Xilica 타이머 연동 가이드

## 1. ✅ 최종 연결도 (Wiring Map)
**업데이트 됨: 두 숫자 출력(Numeric 1, 2)이 이제 똑같은 값을 내보냅니다.**

| 물리 핀 위치 (Lua 블록) | 핀 이름 (설정) | 값 (Value) | 기능 (Function) | 비고 |
| :--- | :--- | :--- | :--- | :--- |
| **Logic 1 (맨 위)** | `"1_Logic"` | **켜짐 / 꺼짐** | **페이지 트리거** | 60초가 되면 켜짐 (True) |
| **Numeric 1 (중간)** | `"1_Numeric"` | **0 ~ 60** | **타이머 시간** | 실제 시간 표시용 |
| **Numeric 2 (맨 아래)** | `"2_Numeric"` | **0 ~ 60** | **이미지 번호** | 타이머와 동일하게 증가 |

## Changes Made

1.  **Process Cleanup:**
    *   Force-killed processes holding port 10025 on the Raspberry Pi.

2.  **Port Configuration Alignment:**
    *   Set **Port 10025** for Xilica -> Pi commands.
    *   Set **Port 10007** for Pi -> Xilica feedback.

3.  **Key Format & Volume Logic Fix (v5.1):**
    *   **Key Normalization:** 모든 신호를 `1chv`, `1chm`, `mv`, `mmute` 형식으로 통일하여 피드백 루프(떨림 현상)를 방지했습니다.
    *   **Command Format:** 실리카와 호환성을 높이기 위해 `set 1chv 5`와 같이 소문자 `set` 명령어를 사용합니다.
    *   **Volume Mapping:** 0-10 정수 값으로 변환하여 실리카 UI가 정확히 반영되도록 수정했습니다.

## Verification Results

*   **Command Format Check:** 로그 확인 결과 `set 6chv 10`, `set mv 0` 등 사용자님이 요청하신 `1chv` 형식이 정확히 송출되고 있습니다.
*   **Loop Prevention:** 내부 캐싱 및 시간 잠금 로직이 정상 작동하여 컨트롤이 떨리는 현상이 해결되었습니다.

## 2. ⚠️ 이미지 관련 주의사항
이미지 번호가 시간(0~60)과 똑같이 올라가도록 설정했습니다.
- 가지고 계신 이미지가 **32장**뿐이라면, **32초에 애니메이션이 끝납니다.**
- 33초부터 60초까지는 이미지가 사라지거나 마지막 그림에서 멈춰 있을 수 있습니다. (설정에 따라 다름)
- 60초를 꽉 채우려면 이미지가 60장 필요합니다.

## 3. 📸 페이지 점프 설정법 ("스냅샷"의 비밀)
1.  **XTouch Designer** (편집 모드)를 엽니다.
2.  디자인 화면에서 **마우스로 직접 눌러서 이동하고 싶은 페이지(예: 2페이지)를 화면에 띄웁니다.**
    *   *반드시 그 페이지가 눈에 보이고 있어야 합니다.*
3.  **Preset Manager** 창을 엽니다.
4.  **새 프리셋을 생성하고 저장**합니다 (이름 예: "GoToPage2").
    *   *이제 이 프리셋은 "2페이지를 보여줘!"라는 명령을 기억하게 됩니다.*
5.  **Design View (회로도)**로 돌아갑니다.
6.  **Logic Out 1 (Lua 블록 맨 위)** 핀을 **Action Trigger**에 연결합니다.
7.  Action Trigger 설정에서 방금 만든 **"GoToPage2" 프리셋**을 실행하도록 설정합니다.
