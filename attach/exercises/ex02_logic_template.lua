-- [실습 02] 흐름 제어 (반복문과 조건문)
-- 목표: 여러 개의 입력을 검사하여 상태 판단하기

local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

-- 켜진 입력 개수를 셀 변수
local active_count = 0

-- 1. for 루프를 사용하여 1번부터 5번까지 입력 확인
-- [미션 1] for 루프 작성 (1~5)
    -- [미션 2] InTable[i]가 1인지 확인하고, 1이면 active_count를 1 증가


-- 2. 조건별 출력
-- [미션 3] active_count가 3 이상이면 "WARNING", 아니면 "OK"를 result 변수에 저장
local result = ""


-- 3. 결과 내보내기
OutTable[1] = result
OutTable["1_String"] = result

return OutTable
