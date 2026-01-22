# 제 3강: 문자열과 프로토콜 (Strings & Protocols)

## 1. 소개
대부분의 하드웨어 제어(TV, 카메라, 매트릭스)는 **문자열(String)** 기반의 프로토콜을 사용합니다. Lua의 강력한 문자열 처리 기능을 배워봅시다.

## 2. 문자열 합치기 (Concatenation)
두 문자열을 이을 때는 점 두 개(`..`)를 사용합니다.
```lua
local id = "01"
local cmd = "PWR ON"
local full = "ID:" .. id .. " CMD:" .. cmd
-- 결과: "ID:01 CMD:PWR ON"
```

## 3. 포맷팅 (String Format) - ★ 매우 중요
C언어의 `printf`와 비슷합니다. 복잡한 문자열을 깔끔하게 만들 수 있습니다.

*   `%s`: 문자열
*   `%d`: 정수 (Integer)
*   `%.1f`: 소수점 1자리 실수
*   `%02X`: 2자리 16진수 (Hex) - 중요!

```lua
local ch = 1
local vol = -5.0
local msg = string.format("SET CH%d VOL %.1f", ch, vol)
-- 결과: "SET CH1 VOL -5.0"
```

## 4. 제어 문자 (Control Characters)
명령어 끝에는 줄바꿈(`\r`, `\n`)이 필요한 경우가 많습니다.
*   `\r` (CR) = `string.char(13)`
*   `\n` (LF) = `string.char(10)`

```lua
local cmd = "POWER ON" .. string.char(13) -- CR 추가
```

## 5. 실습 예제 (Exercise)

`attach/course/exercises/ex03_protocol_template.lua` 파일을 열어 다음 미션을 수행하세요.

**미션 목표:**
1.  입력 1번(채널 번호, 1~4)과 입력 2번(레벨, 0~100)을 받으세요.
2.  `string.format`을 사용하여 다음 형식의 명령어를 만드세요.
    *   형식: `CH<채널번호>_LVL:<레벨값 2자리 정수><CR>`
    *   예: 채널 1, 레벨 5 -> `CH1_LVL:05<CR>`
3.  OutTable[1]로 출력하세요.
