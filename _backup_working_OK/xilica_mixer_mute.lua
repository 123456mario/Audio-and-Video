local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

if G_MixerState == nil then G_MixerState = {} end
local cmds = {}

local function AddCmd(key, val)
    table.insert(cmds, string.format("set %s %s", key, tostring(val)))
end

-- 1. Process Channels 1-9 (Updated to include Ch9)
for i = 1, 9 do
    local ch_str = tostring(i)
    local raw_mute = InTable[ch_str .. "_Logic"]
    if raw_mute == nil then raw_mute = InTable[i .. "_Logic"] end 
    if raw_mute == nil then raw_mute = InTable[i] end
    
    if raw_mute ~= nil then
        local mute_val = 0
        if raw_mute == 1 or raw_mute == true or raw_mute == 1.0 then
             mute_val = 1
        end
        
        local state_key = "ch" .. i .. "m"
        if G_MixerState[state_key] ~= mute_val then
            AddCmd(state_key, mute_val)
            G_MixerState[state_key] = mute_val
        end
    end
end

-- 2. Process Main Mute (Usually Input 10 or named "Main_Mute")
local mn_mute_raw = InTable["Main_Mute"]
if mn_mute_raw == nil then mn_mute_raw = InTable[10] end -- Input 10 for Main
if mn_mute_raw == nil then mn_mute_raw = InTable["10_Logic"] end

if mn_mute_raw ~= nil then
    local mmute_val = 0
    if mn_mute_raw == 1 or mn_mute_raw == true then
        mmute_val = 1
    end
    
    local k = "mmute"
    if G_MixerState[k] ~= mmute_val then
        AddCmd(k, mmute_val)
        G_MixerState[k] = mmute_val
    end
end

if #cmds > 0 then
    local sep = string.char(13)
    local final_str = table.concat(cmds, sep) .. sep
    
    OutTable[1] = final_str
    OutTable["1_String"] = final_str
    OutTable["1_Binary"] = final_str
    
    OutTable[2] = 1
    OutTable["2_Logic"] = true
    
    return OutTable, "Sent: " .. final_str
else
    OutTable[2] = 0
    OutTable["2_Logic"] = false
    return OutTable
end
