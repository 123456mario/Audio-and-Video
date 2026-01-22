local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

if G_VolState == nil then G_VolState = {} end
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
-- 1. PROCESS UI INPUTS (Send to Python)
-- =========================================================

-- 1.1 Channels 1-9
for i = 1, 9 do
    local ch_str = tostring(i)
    local raw_vol = InTable[ch_str .. "_Numeric"]
    if raw_vol == nil then raw_vol = InTable[i .. "_Numeric"] end
    if raw_vol == nil then raw_vol = InTable[i] end
    
    if raw_vol ~= nil then
        local vol_val = SafeNum(raw_vol, -999.0)
        -- [CHANGED] Use "1chv" format to match Native Control Name
        local state_key = i .. "chv"
        
        local last_val = G_VolState[state_key] or -999.0
        
        if math.abs(last_val - vol_val) > 0.1 then
            AddCmd(state_key, vol_val)
            G_VolState[state_key] = vol_val
        end
    end
end

-- 2.2 Main Mix (Input 10)
local mn_vol_raw = InTable["Main_Vol"]
if mn_vol_raw == nil then mn_vol_raw = InTable[10] end
if mn_vol_raw == nil then mn_vol_raw = InTable["10_Numeric"] end

if mn_vol_raw ~= nil then
    local mvol_val = SafeNum(mn_vol_raw, -999.0)
    local last_mvol = G_VolState["mvol"] or -999.0
    
    if math.abs(last_mvol - mvol_val) > 0.1 then
        AddCmd("mv", mvol_val)
        G_VolState["mvol"] = mvol_val
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
