-- Xilica Mixer Logic (Wing Control) - Expanded v2
-- Supports Channels 1-12 and Main Busses 1-3
local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

-- =========================================================
-- CONFIGURATION
-- =========================================================
-- Channel Mapping (Expanded to 12)
local CH_COUNT = 12

-- Persistent State (to detect changes)
if G_MixerState == nil then G_MixerState = {} end

local cmds = {}

-- Helper to add command
local function AddCmd(key, val)
    -- Formatting: "set key value"
    table.insert(cmds, string.format("set %s %s", key, tostring(val)))
end

-- =========================================================
-- 1. Process Input Channels (1-12)
-- =========================================================
for i = 1, CH_COUNT do
    local ch_str = tostring(i)
    
    -- MUTE (Logic)
    local raw_mute = InTable[ch_str .. "_Logic"]
    -- Fallback checks
    if raw_mute == nil then raw_mute = InTable[i .. "_Logic"] end 
    if raw_mute == nil then raw_mute = InTable[i] end
    
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

-- =========================================================
-- 2. Process Main Busses (1, 2, 3)
-- =========================================================

-- Helper for Main Processing
local function ProcessMain(idx, mute_key, vol_key, mute_out_cmd, vol_out_cmd)
    -- MUTE
    local m_raw = InTable[mute_key]
    if m_raw ~= nil then
        local m_val = (m_raw == 1 or m_raw == true) and 1 or 0
        if G_MixerState[mute_out_cmd] ~= m_val then
            AddCmd(mute_out_cmd, m_val)
            G_MixerState[mute_out_cmd] = m_val
        end
    end

    -- VOLUME
    local v_raw = InTable[vol_key]
    if v_raw ~= nil then
        local v_val = tonumber(v_raw)
        local last_v = G_MixerState[vol_out_cmd] or -999.0
        if math.abs(last_v - v_val) > 0.1 then
            AddCmd(vol_out_cmd, v_val)
            G_MixerState[vol_out_cmd] = v_val
        end
    end
end

-- Main 1 (Legacy Keys: mm, mvol, Main_Vol)
-- Input Keys (from Designer Pins): "Main1_Mute", "Main1_Vol" (or fallback to mm/mvol)
local m1_m = InTable["Main1_Mute"] or InTable["mm"] or InTable["Main_Mute"] or InTable[20]
local m1_v = InTable["Main1_Vol"] or InTable["mvol"] or InTable["Main_Vol"] or InTable[20] # Note: Pin numbers are examples
 
-- We process manually to support legacy 'mmute' command name
if m1_m ~= nil then
    local val = (m1_m == 1 or m1_m == true) and 1 or 0
    if G_MixerState["mmute"] ~= val then
        AddCmd("mmute", val)
        G_MixerState["mmute"] = val
    end
end
if m1_v ~= nil then
    local val = tonumber(m1_v)
    if math.abs((G_MixerState["MAIN_VOL"] or -999) - val) > 0.1 then
        AddCmd("MAIN_VOL", val)
        G_MixerState["MAIN_VOL"] = val
    end
end

-- Main 2
-- Input Keys: "Main2_Mute", "Main2_Vol"
-- Output Commands: "MAIN2_MUTE", "MAIN2_VOL"
local m2_m = InTable["Main2_Mute"]
local m2_v = InTable["Main2_Vol"]
if m2_m ~= nil then
    local val = (m2_m == 1 or m2_m == true) and 1 or 0
    if G_MixerState["MAIN2_MUTE"] ~= val then
        AddCmd("MAIN2_MUTE", val)
        G_MixerState["MAIN2_MUTE"] = val
    end
end
if m2_v ~= nil then
    local val = tonumber(m2_v)
    if math.abs((G_MixerState["MAIN2_VOL"] or -999) - val) > 0.1 then
        AddCmd("MAIN2_VOL", val)
        G_MixerState["MAIN2_VOL"] = val
    end
end

-- Main 3
-- Input Keys: "Main3_Mute", "Main3_Vol"
-- Output Commands: "MAIN3_MUTE", "MAIN3_VOL"
local m3_m = InTable["Main3_Mute"]
local m3_v = InTable["Main3_Vol"]
if m3_m ~= nil then
    local val = (m3_m == 1 or m3_m == true) and 1 or 0
    if G_MixerState["MAIN3_MUTE"] ~= val then
        AddCmd("MAIN3_MUTE", val)
        G_MixerState["MAIN3_MUTE"] = val
    end
end
if m3_v ~= nil then
    local val = tonumber(m3_v)
    if math.abs((G_MixerState["MAIN3_VOL"] or -999) - val) > 0.1 then
        AddCmd("MAIN3_VOL", val)
        G_MixerState["MAIN3_VOL"] = val
    end
end

-- =========================================================
-- 3. Output Command String
-- =========================================================
if #cmds > 0 then
    -- Use string.char(13) for safety
    local CR = string.char(13)
    local final_str = table.concat(cmds, CR) .. CR
    
    OutTable[1] = final_str
    OutTable["1_String"] = final_str
    OutTable["1_Binary"] = final_str
    
    -- Pulse Output 2 to trigger sending
    OutTable[2] = 1
    OutTable["2_Logic"] = true
    
    return OutTable, "Sent: " .. final_str
else
    OutTable[2] = 0
    OutTable["2_Logic"] = false
    return OutTable
end
