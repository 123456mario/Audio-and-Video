local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

if G_MixerState == nil then G_MixerState = {} end
local cmds = {}

-- =========================================================
-- HELPER: Safe Number Wrapper
-- =========================================================
local function SafeNum(val, default)
    if default == nil then default = 0 end
    if val == nil then return default end
    local n = tonumber(val)
    if n == nil then return default end
    return n
end

local function AddCmd(key, val)
    table.insert(cmds, string.format("set %s %s", key, tostring(val)))
end

-- =========================================================
-- 1. PROCESS UI INPUTS
-- =========================================================

-- 1.1 Channels 1-9
for i = 1, 9 do
    local ch_str = tostring(i)
    local raw_mute = InTable[ch_str .. "_Logic"]
    if raw_mute == nil then raw_mute = InTable[i .. "_Logic"] end 
    if raw_mute == nil then raw_mute = InTable[i] end
    
    if raw_mute ~= nil then
        local mute_val = 0
        if raw_mute == 1 or raw_mute == true or raw_mute == 1.0 or raw_mute == "true" then
             mute_val = 1
        end
        
        -- [CHANGED] Use "1chm" format to match Native Control Name
        local state_key = i .. "chm"
        local last_val = G_MixerState[state_key] or 0
        
        if last_val ~= mute_val then
            AddCmd(state_key, mute_val)
            G_MixerState[state_key] = mute_val
        end
    end
end

-- 2.2 Main Mute
local mn_mute_raw = InTable["Main_Mute"]
if mn_mute_raw == nil then mn_mute_raw = InTable[10] end
if mn_mute_raw == nil then mn_mute_raw = InTable["10_Logic"] end

if mn_mute_raw ~= nil then
    local mmute_val = 0
    if mn_mute_raw == 1 or mn_mute_raw == true or mn_mute_raw == "true" then
        mmute_val = 1
    end
    
    local k = "mmute"
    local last_m = G_MixerState[k] or 0
    
    if last_m ~= mmute_val then
        AddCmd(k, mmute_val)
        G_MixerState[k] = mmute_val
    end
end

-- =========================================================
-- 3. FINAL OUTPUT
-- =========================================================
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
