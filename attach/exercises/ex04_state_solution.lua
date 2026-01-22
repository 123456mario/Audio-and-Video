-- [실습 04] 해답 (Solution)

local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

-- 전역 상태 저장소
if G_LastState == nil then
    G_LastState = 0
end

local current_btn = tonumber(InTable[1]) or 0
local last_btn = G_LastState
local output_msg = ""

-- Rising Edge (눌렀을 때)
if current_btn == 1 and last_btn == 0 then
    output_msg = "START"
end

-- Falling Edge (뗐을 때)
if current_btn == 0 and last_btn == 1 then
    output_msg = "STOP"
end

-- 상태 업데이트
G_LastState = current_btn

-- 출력
OutTable[1] = output_msg
OutTable["1_String"] = output_msg

return OutTable
