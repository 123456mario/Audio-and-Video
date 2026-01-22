-- [실습 02] 해답 (Solution)

local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

local active_count = 0

-- 1. 1~5번 입력 확인
for i = 1, 5 do
    local val = tonumber(InTable[i])
    if val == 1 then
        active_count = active_count + 1
    end
end

-- 2. 조건 판단
local result = ""
if active_count >= 3 then
    result = "WARNING"
else
    result = "OK"
end

-- 3. 출력
OutTable[1] = result
OutTable["1_String"] = result

return OutTable
