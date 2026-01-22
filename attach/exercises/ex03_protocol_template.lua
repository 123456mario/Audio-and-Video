-- [실습 03] 문자열 포맷팅
-- 목표: 프로토콜 포맷에 맞춰 명령어 생성하기

local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

-- 1. 입력 받기
local ch_num = tonumber(InTable[1]) or 1
local level = tonumber(InTable[2]) or 0

-- 2. 명령어 포맷팅
-- [미션 1] string.format을 사용하여 "CHxx_LVL:xx" 형식 만들기
-- 힌트: 채널은 %d, 레벨은 %02d (2자리 정수, 빈칸 0 채움)
local cmd_str = "" -- 여기에 작성


-- 3. 종료 문자(CR) 붙이기
-- [미션 2] cmd_str 뒤에 CR(ASCII 13) 붙이기


-- 4. 출력
OutTable[1] = cmd_str
OutTable["1_String"] = cmd_str

return OutTable
