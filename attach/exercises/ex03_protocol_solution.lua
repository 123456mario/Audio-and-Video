-- [실습 03] 해답 (Solution)

local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

-- 1. 입력 받기
local ch_num = tonumber(InTable[1]) or 1
local level = tonumber(InTable[2]) or 0

-- 2. 명령어 포맷팅
-- %d: 정수, %02d: 2자리 정수(0 채움)
local cmd_str = string.format("CH%d_LVL:%02d", ch_num, level)

-- 3. 종료 문자(CR) 붙이기
cmd_str = cmd_str .. string.char(13)

-- 4. 출력
OutTable[1] = cmd_str
OutTable["1_String"] = cmd_str

return OutTable
