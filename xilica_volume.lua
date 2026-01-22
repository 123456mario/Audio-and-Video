-- Xilica VOLUME Logic Only (Wing Control)
-- Supports Channels 1-12 and Main 1-3
local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

-- Persistent State
if G_VolState == nil then G_VolState = {} end

local cmds = {}
local function AddCmd(key, val)
    table.insert(cmds, string.format("set %s %s", key, tostring(val)))
end

-- =========================================================
-- 1. Input Channels (1-12)
-- =========================================================
local CH_COUNT = 12

for i = 1, CH_COUNT do
    local ch_str = tostring(i)
    -- Input Priority: "1_Numeric" -> "1"
    local raw_vol = InTable[ch_str .. "_Numeric"]
    if raw_vol == nil then raw_vol = InTable[i .. "_Numeric"] end
    if raw_vol == nil then raw_vol = InTable[i] end
    
    if raw_vol ~= nil then
        local vol_val = tonumber(raw_vol)
        local state_key = "ch" .. i .. "v"
        
        local last_val = G_VolState[state_key] or -999.0
        if math.abs(last_val - vol_val) > 0.1 then
            AddCmd(state_key, vol_val)
            G_VolState[state_key] = vol_val
        end
    end
end

-- =========================================================
-- 2. Main Busses (1, 2, 3)
-- =========================================================

-- Main 1 (Keys: Main_Vol, mvol)
local m1_raw = InTable["Main_Vol"] or InTable["Main1_Vol"] or InTable["mvol"]
if m1_raw ~= nil then
    local val = tonumber(m1_raw)
    local last_v = G_VolState["MAIN_VOL"] or -999.0
    if math.abs(last_v - val) > 0.1 then
        AddCmd("MAIN_VOL", val)
        G_VolState["MAIN_VOL"] = val
    end
end

-- Main 2
local m2_raw = InTable["Main2_Vol"]
if m2_raw ~= nil then
    local val = tonumber(m2_raw)
    local last_v = G_VolState["MAIN2_VOL"] or -999.0
    if math.abs(last_v - val) > 0.1 then
        AddCmd("MAIN2_VOL", val)
        G_VolState["MAIN2_VOL"] = val
    end
end

-- Main 3
local m3_raw = InTable["Main3_Vol"]
if m3_raw ~= nil then
    local val = tonumber(m3_raw)
    local last_v = G_VolState["MAIN3_VOL"] or -999.0
    if math.abs(last_v - val) > 0.1 then
        AddCmd("MAIN3_VOL", val)
        G_VolState["MAIN3_VOL"] = val
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
