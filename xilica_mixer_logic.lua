-- Xilica Mixer Logic (Wing Control)
local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

-- =========================================================
-- CONFIGURATION
-- =========================================================
-- Channel Mapping
local CH_COUNT = 8
-- "1_Logic" -> Ch1 Mute
-- "1_Numeric" -> Ch1 Volume
-- ...
-- "9_Logic" -> Main Mute
-- "9_Numeric" -> Main Volume

-- Persistent State (to detect changes)
if G_MixerState == nil then G_MixerState = {} end

local cmds = {}

-- Helper to add command
local function AddCmd(key, val)
    -- Formatting: "set key value"
    table.insert(cmds, string.format("set %s %s", key, tostring(val)))
end

-- 1. Process Channels 1-8
for i = 1, CH_COUNT do
    local ch_str = tostring(i)
    
    -- MUTE (Logic)
    -- Input: 1.0 (On/Muted) or 0.0 (Off/Unmuted)
    local raw_mute = InTable[ch_str .. "_Logic"]
    if raw_mute == nil then raw_mute = InTable[i .. "_Logic"] end 
    
    if raw_mute ~= nil then
        -- Convert to 0 or 1 integer
        local mute_val = (raw_mute == 1 or raw_mute == true or raw_mute == 1.0) and 1 or 0
        local state_key = "ch" .. i .. "m"
        
        -- Check change
        if G_MixerState[state_key] ~= mute_val then
            AddCmd(state_key, mute_val)
            G_MixerState[state_key] = mute_val
        end
    end
    
    -- VOLUME (Numeric)
    -- Input: dB value (-90.0 to +10.0) directly from Fader
    local raw_vol = InTable[ch_str .. "_Numeric"]
    if raw_vol == nil then raw_vol = InTable[i .. "_Numeric"] end
    
    if raw_vol ~= nil then
        local vol_val = tonumber(raw_vol)
        local state_key = "ch" .. i .. "v"
        
        -- Check change (with small tolerance for float)
        local last_val = G_MixerState[state_key] or -999.0
        if math.abs(last_val - vol_val) > 0.1 then
            AddCmd(state_key, vol_val)
            G_MixerState[state_key] = vol_val
        end
    end
end

-- 2. Process Main Mix (Use Index 9 or special named inputs)
local MAIN_IDX = 9
local mn_mute_raw = InTable[MAIN_IDX .. "_Logic"] or InTable["Main_Mute"]
if mn_mute_raw ~= nil then
    local mmute_val = (mn_mute_raw == 1 or mn_mute_raw == true) and 1 or 0
    if G_MixerState["mmute"] ~= mmute_val then
        AddCmd("mmute", mmute_val)
        G_MixerState["mmute"] = mmute_val
    end
end

local mn_vol_raw = InTable[MAIN_IDX .. "_Numeric"] or InTable["Main_Vol"]
if mn_vol_raw ~= nil then
    local mvol_val = tonumber(mn_vol_raw)
    local last_mvol = G_MixerState["mvol"] or -999.0
    if math.abs(last_mvol - mvol_val) > 0.1 then
        AddCmd("mvol", mvol_val)
        G_MixerState["mvol"] = mvol_val
    end
end

-- 3. Output Command String
if #cmds > 0 then
    -- Join with newlines or send one by one?
    -- Python bridge usually handles line by line.
    -- Let's send one big string with \r\n
    local final_str = table.concat(cmds, "\r\n") .. "\r\n"
    OutTable[1] = final_str
    OutTable["1_String"] = final_str
    OutTable["1_Binary"] = final_str
    
    return OutTable, "Sent: " .. final_str
else
    return OutTable -- No debug output to avoid spam
end
