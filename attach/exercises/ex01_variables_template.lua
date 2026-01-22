-- [실습 01] 변수와 입출력 기초
-- 목표: 입력을 받아 가공하여 출력하기

local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

-- 1. 입력 1번(Volume) 받기 (기본값 0)
local raw_vol = InTable[1]
-- [미션 1] raw_vol이 nil이면 0으로, 아니면 숫자로 변환하여 'vol' 변수에 저장하세요.
local vol = 0 -- 여기에 코드 작성


-- 2. 입력 2번(Mute) 받기 (1 또는 0)
local raw_mute = InTable[2]
-- [미션 2] raw_mute가 1이면 true, 아니면 false가 되도록 'is_muted' 변수를 만드세요.
local is_muted = false -- 여기에 코드 작성


-- 3. 로직 처리 (예: 볼륨이 -infinity보다 작으면 -infinity로 고정)
if vol < -60 then
    vol = -60
end

-- 4. 출력하기
-- [미션 3] OutTable[1]에 vol 값을, OutTable[2]에 is_muted 값을 저장하세요.


return OutTable
