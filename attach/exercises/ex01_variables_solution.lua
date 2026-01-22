-- [실습 01] 해답 (Solution)

local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

-- 1. 입력 1번(Volume) 받기
local raw_vol = InTable[1]
local vol = tonumber(raw_vol) -- 숫자로 변환
if vol == nil then vol = 0 end -- nil 체크

-- 2. 입력 2번(Mute) 받기
local raw_mute = InTable[2]
local is_muted = false
if tonumber(raw_mute) == 1 then
    is_muted = true
else
    is_muted = false
end

-- 3. 로직 처리
if vol < -60 then
    vol = -60
end

-- 4. 출력하기
OutTable[1] = vol
OutTable["1_Int"] = vol -- 타입 힌트

OutTable[2] = is_muted
OutTable["2_Logic"] = is_muted -- 타입 힌트

return OutTable
