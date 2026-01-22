-- test.lua: Xilica 스크립트 시뮬레이션 및 테스트 (Safe version - no format issues)
local InTable = {
  ["1_Logic"] = 1,      -- CH1 Mute ON
  ["1_Numeric"] = "4",  -- CH1 Volume level 4 (5.0 dB)
  ["2_Logic"] = 0,      -- CH2 Mute OFF
  ["2_Numeric"] = "3"   -- CH2 Volume level 3 (0 dB)
  -- Add more for testing
}

local OutTable = {}
local DebugMessage = "Script ready"

-- Persistent states (initialize if nil)
if G_volLevels == nil then G_volLevels = {} end
if G_muteStates == nil then G_muteStates = {} end

for i = 1, 9 do
  if G_volLevels[i] == nil then G_volLevels[i] = 3 end
  if G_muteStates[i] == nil then G_muteStates[i] = 0 end
end

-- VOL preset dB table
local vol_preset = {
  [0] = -80.0,
  [1] = -40.0,
  [2] = -10.0,
  [3] = 0.0,
  [4] = 5.0,
  [5] = 18.0
}

local commands = {}

for ch = 1, 9 do
  local ch_key = (ch <= 8 and "CH" .. ch or "MAIN")
  
  -- Mute
  local muteOn = InTable[tostring(ch) .. "_Logic"] or 0
  if muteOn ~= G_muteStates[ch] then
    local mute_cmd = "SET " .. ch_key .. "_MUTE " .. tostring(muteOn)
    table.insert(commands, mute_cmd)
    G_muteStates[ch] = muteOn
  end
  
  -- Volume
  local volLevel = tonumber(InTable[tostring(ch) .. "_Numeric"]) or 3
  if volLevel ~= G_volLevels[ch] then
    local db = vol_preset[volLevel] or 0.0
    local vol_str = tostring(db):sub(1, -2)
    local vol_cmd = "SET " .. ch_key .. "_VOL " .. vol_str
    table.insert(commands, vol_cmd)
    G_volLevels[ch] = volLevel
  end
end

if #commands > 0 then
  local cmd_str = table.concat(commands, " ")
  OutTable["1_Binary"] = cmd_str .. "\r\n"
  DebugMessage = "Sent: " .. string.sub(OutTable["1_Binary"], 1, 100)
else
  DebugMessage = "No change"
end

-- Test output (simulate return)
print("DebugMessage: " .. DebugMessage)
print("OutTable[1_Binary]: " .. (OutTable["1_Binary"] or "nil"))

return OutTable, DebugMessage
