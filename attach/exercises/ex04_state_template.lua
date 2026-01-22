-- [실습 04] 상태 관리와 에지 검출
-- 목표: 버튼의 누름/뗌 순간을 포착하기

local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

-- 전역 상태 저장소 (초기화)
if G_LastState == nil then
    G_LastState = 0
end

local current_btn = tonumber(InTable[1]) or 0
local last_btn = G_LastState
local output_msg = ""

-- [미션 1] Rising Edge (0 -> 1) 감지
-- 만약 현재값이 1이고 이전값이 0이라면 output_msg를 "START"로 설정


-- [미션 2] Falling Edge (1 -> 0) 감지
-- 만약 현재값이 0이고 이전값이 1이라면 output_msg를 "STOP"으로 설정


-- [미션 3] 상태 업데이트 (매우 중요!)
-- G_LastState를 현재 값으로 갱신하세요.


-- 출력
OutTable[1] = output_msg
OutTable["1_String"] = output_msg

return OutTable
