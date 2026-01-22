-- =============================================================
-- Xilica Lua Script: Camera PTZ Control (VISCA Protocol)
-- =============================================================
-- 용도: 카메라 팬/틸트/줌 제어 (버튼 누르면 이동, 떼면 정지)
-- 연결: Output 1 -> TCP/UDP Client (Camera IP: 192.168.1.x, Port: 52381 or 1259)

local InTable = ...
local OutTable = {}

-- 1. 전역 상태 변수 초기화 (이전 버튼 상태 기억용)
if G_LastState == nil then
    G_LastState = {}
    for i=1, 20 do G_LastState[i] = 0 end 
end

-- 2. VISCA 커맨드 정의 (Hex String)
-- [속도 설정] VV: Pan Speed (01~18), WW: Tilt Speed (01~14)
-- Hex 10 = Decimal 16 (꽤 빠른 속도)
local P_SPD = "\x10" 
local T_SPD = "\x10"

local CMD_MAP = {
    [1] = "\x81\x01\x06\x01" .. P_SPD .. T_SPD .. "\x03\x01\xFF", -- Pan Up
    [2] = "\x81\x01\x06\x01" .. P_SPD .. T_SPD .. "\x03\x02\xFF", -- Pan Down
    [3] = "\x81\x01\x06\x01" .. P_SPD .. T_SPD .. "\x01\x03\xFF", -- Pan Left
    [4] = "\x81\x01\x06\x01" .. P_SPD .. T_SPD .. "\x02\x03\xFF", -- Pan Right
    [5] = "\x81\x01\x04\x07\x25\xFF", -- Zoom In (Standard)
    [6] = "\x81\x01\x04\x07\x35\xFF", -- Zoom Out (Standard)
    -- [7]~[9]: Presets
    [7] = "\x81\x01\x04\x3F\x02\x00\xFF", -- Recall Preset 0 (Cam 1)
    [8] = "\x81\x01\x04\x3F\x02\x01\xFF", -- Recall Preset 1 (Cam 2)
    [9] = "\x81\x01\x04\x3F\x02\x02\xFF", -- Recall Preset 2 (Cam 3)
}

-- 3. 정지 커맨드 (STOP) - 버튼 뗐을 때 전송
local CMD_STOP_PT = "\x81\x01\x06\x01" .. P_SPD .. T_SPD .. "\x03\x03\xFF" -- Pan/Tilt Stop
local CMD_STOP_ZM = "\x81\x01\x04\x07\x00\xFF" -- Zoom Stop

-- 4. 로직 실행
local cmd_to_send = ""

if InTable then
  for pin, cmd_hex in pairs(CMD_MAP) do
      local current_val = tonumber(InTable[pin])
      if current_val == nil then current_val = 0 end
      
      local last_val = G_LastState[pin]
      if last_val == nil then last_val = 0 end
      
      -- (1) 버튼을 막 눌렀을 때 (Rising Edge): 0 -> 1
      if current_val == 1 and last_val == 0 then
          cmd_to_send = cmd_hex
          G_LastState[pin] = 1
          break -- 동시 입력을 막기 위해 하나 처리하면 탈출
      
      -- (2) 버튼을 막 뗐을 때 (Falling Edge): 1 -> 0
      elseif current_val == 0 and last_val == 1 then
          -- 팬/틸트 핀(1~4)이면 PT 정지, 줌 핀(5,6)이면 줌 정지
          -- 프리셋(7~9)은 정지 명령 필요 없음
          if pin >= 1 and pin <= 4 then
              cmd_to_send = CMD_STOP_PT
          elseif pin >= 5 and pin <= 6 then
              cmd_to_send = CMD_STOP_ZM
          end
          G_LastState[pin] = 0
          break
      end
  end
end

-- 5. 출력 전송
if cmd_to_send ~= "" then
    OutTable[1] = cmd_to_send
else
    OutTable[1] = ""
end

return OutTable, ""
