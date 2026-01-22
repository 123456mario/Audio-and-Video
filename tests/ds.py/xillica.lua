local InTable = ...
local OutTable = {}
local DebugMessage = "Ready"

if G_volLevels == nil then G_volLevels = {} end
if G_muteStates == nil then G_muteStates = {} end

for i = 1, 9 do
  if G_volLevels[i] == nil then G_volLevels[i] = 3 end
  if G_muteStates[i] == nil then G_muteStates[i] = 0 end
end

local vol_preset = {
  [0] = -80.0, [1] = -40.0, [2] = -10.0, [3] = 0.0, [4] = 5.0, [5] = 18.0
}

local commands = {}

for ch = 1, 9 do
  local ch_key = (ch <= 8 and "CH" .. ch or "MAIN")
  
  local muteOn = InTable[tostring(ch) .. "_Logic"] or 0
  if muteOn ~= G_muteStates[ch] then
    local mute_cmd = "SET " .. ch_key .. "_MUTE " .. tostring(muteOn)
    table.insert(commands, mute_cmd)
    G_muteStates[ch] = muteOn
  end
  
  local volLevel = tonumber(InTable[tostring(ch) .. "_Numeric"]) or 3
  if volLevel ~= G_volLevels[ch] then
    local db = vol_preset[volLevel] or 0.0
    local vol_cmd = "SET " .. ch_key .. "_VOL " .. tostring(db)
    table.insert(commands, vol_cmd)
    G_volLevels[ch] = volLevel
  end
end

if #commands > 0 then
  OutTable["1_Binary"] = table.concat(commands, " ") .. "\r\n"
  DebugMessage = "Sent"
else
  DebugMessage = "No change"
end

return OutTable, DebugMessage