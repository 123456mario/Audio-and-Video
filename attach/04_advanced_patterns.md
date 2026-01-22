# 제 4강: 고급 패턴 - 상태 관리와 에지 검출 (Advanced Patterns)

## 1. 소개
현장에서는 버튼을 "누르는 순간"에만 명령을 보내거나, 값이 "바뀔 때"만 통신해야 하는 경우가 많습니다. 이를 위해 **상태(State) 추적**과 **에지 검출(Edge Detection)** 패턴을 배웁니다.

## 2. 상태 저장의 필요성
Lua 스크립트는 매 프레임(또는 입력 변화 시)마다 처음부터 다시 실행됩니다.
이전 상태를 기억하려면 전역 테이블(Global Table)이 필요합니다.

```lua
if LastState == nil then
    LastState = {}
end
```

## 3. 에지 검출 (Edge Detection)
버튼을 누르고 있을 때 명령어가 계속 나가는 것을 방지하거나(Flooding), 누르는 순간(Rising Edge)과 떼는 순간(Falling Edge)을 구분할 때 사용합니다.

```lua
local current_val = InTable[1]
local last_val = LastState[1] or 0 -- 이전 값 불러오기

-- Rising Edge (0 -> 1): 버튼을 막 눌렀을 때
if current_val == 1 and last_val == 0 then
    print("Button Pressed!")
end

-- Falling Edge (1 -> 0): 버튼을 뗐을 때
if current_val == 0 and last_val == 1 then
    print("Button Released!")
end

LastState[1] = current_val -- 상태 업데이트 (필수!)
```

## 4. 변경 감지 (Change of Value)
값이 변했을 때만 명령어를 보내야 네트워크 부하를 줄일 수 있습니다.

```lua
if current_val ~= last_val then
    -- 값이 바뀌었을 때만 실행할 코드
    LastState[1] = current_val
end
```

## 5. 실습 예제 (Exercise)

`attach/course/exercises/ex04_state_template.lua` 파일을 열어 다음 미션을 수행하세요.

**미션 목표:**
1.  입력 1번(Button)을 모니터링하세요.
2.  버튼이 **눌리는 순간(Rising Edge)**에만 `OutTable[1]`에 "START"를 출력하세요.
3.  버튼이 **떼지는 순간(Falling Edge)**에만 `OutTable[1]`에 "STOP"을 출력하세요.
4.  변화가 없을 때는 빈 문자열("")을 출력하세요.
