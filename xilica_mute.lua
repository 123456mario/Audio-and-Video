-- Xilica MUTE Logic Only (Wing Control)
-- Supports Channels 1-12 and Main 1-3
local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

-- =========================================================
-- CONFIGURATION
-- =========================================================
local CH_COUNT = 12  -- Channels 1-12

-- Persistent State
if G_MuteState == nil then G_MuteState = {} end

local cmds = {}
local function AddCmd(key, val)
    table.insert(cmds, string.format("set %s %s", key, tostring(val)))
end

-- 1. Input Channels Check (1-12)
for i = 1, CH_COUNT do
    local ch_str = tostring(i)
    -- Input Priority: "1_Logic" -> "1"
    local raw_mute = InTable[ch_str .. "_Logic"]
    if raw_mute == nil then raw_mute = InTable[i .. "_Logic"] end 
    if raw_mute == nil then raw_mute = InTable[i] end
    
    if raw_mute ~= nil then
        local mute_val = (raw_mute == 1 or raw_mute == true) and 1 or 0
        local state_key = "ch" .. i .. "m"
        
        if G_MuteState[state_key] ~= mute_val then
            AddCmd(state_key, mute_val)
            G_MuteState[state_key] = mute_val
        end
    end
end

-- 2. Main Busses Check (1, 2, 3)

-- Main 1 (Keys: mm, Main_Mute)
local m1_raw = InTable["mm"] or InTable["Main_Mute"] or InTable["Main1_Mute"]
if m1_raw ~= nil then
    local val = (m1_raw == 1 or m1_raw == true) and 1 or 0
    if G_MuteState["mmute"] ~= val then
        AddCmd("mmute", val)
        G_MuteState["mmute"] = val
    end
end

-- Main 2
local m2_raw = InTable["Main2_Mute"]
if m2_raw ~= nil then
    local val = (m2_raw == 1 or m2_raw == true) and 1 or 0
    if G_MuteState["MAIN2_MUTE"] ~= val then
        AddCmd("MAIN2_MUTE", val)
        G_MuteState["MAIN2_MUTE"] = val
    end
end

-- Main 3
local m3_raw = InTable["Main3_Mute"]
if m3_raw ~= nil then
    local val = (m3_raw == 1 or m3_raw == true) and 1 or 0
    if G_MuteState["MAIN3_MUTE"] ~= val then
        AddCmd("MAIN3_MUTE", val)
        G_MuteState["MAIN3_MUTE"] = val
    end
end

-- 3. Output
if #cmds > 0 then
    local CR = string.char(13)
    local final_str = table.concat(cmds, CR) .. CR
    OutTable[1] = final_str
    
    -- Pulse Output 2
    OutTable[2] = 1
    
    return OutTable, "Sent: " .. final_str
else
    OutTable[2] = 0
    return OutTable
end
