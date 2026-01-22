# LED 전광판 (Novastar VX1000 Pro) 끊김 방지 솔루션

**장비**: Novastar VX1000 Pro (LED Controller)  
**제어 주체**: Xilica Solaro (TCP/IP Binary Control)  
**해결책**: "Auto-Loop Timer"를 이용한 "Read Mode" 패킷 주기적 전송.

---

## 🛠️ 구현 단계 (Step-by-Step)

### 1단계: Lua 스크립트 수정 (Auto-Loop)
타이머 모듈을 열어 아래 코드를 추가합니다. (100이 되면 0으로 자동 리셋)
```lua
    -- [자동 리셋 로직 추가]
    elseif G_SysState == STATE_DONE then
        G_Timer = 0              -- 0으로 초기화
        G_SysState = STATE_WAIT  -- 다시 카운트 시작
    end
```

### 2단계: 모듈 준비
-   **Binary Data Constant**:
    -   내용: `55 aa 00 00 fe 00 00 00 00 00 00 00 02 00 00 00 02 00 57 56`
    -   *(이것은 화면에 영향을 주지 않는 '상태 확인' 명령어입니다)*
-   **Binary Data Input Selector**:
    -   2-Port Selector 사용.

### 3단계: 배선 연결 (Wiring)
1.  **[Constant]** ---> **Selector 입력 1번**
2.  **[Timer]의 3번 핀 (Show_Next)** ---> **Selector의 [S] 포트 (제어핀)**
    -   *주의: 2번 핀(Show_Start) 아님! 3번 핀에 연결해야 합니다.*
3.  **Selector 출력** ---> 기존 **TCP Client Connection** 입력에 합류.

### ✅ 최종 확인
타이머가 계속 숫자가 올라가다가, 끝에 도달하면 잠시 깜빡(3번 핀)하고 다시 0부터 시작하는지 확인하세요.
깜빡일 때마다 전광판으로 "생존 신고"가 전송됩니다.
