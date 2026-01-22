local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

if G_VolState == nil then G_VolState = {} end
local cmds = {}

local function AddCmd(key, val)
    table.insert(cmds, string.format("set %s %s", key, tostring(val)))
end

-- 1. Process Channels 1-9
for i = 1, 9 do
    local ch_str = tostring(i)
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

-- 2. Process Main Mix (Input 10)
local mn_vol_raw = InTable["Main_Vol"]
if mn_vol_raw == nil then mn_vol_raw = InTable[10] end
if mn_vol_raw == nil then mn_vol_raw = InTable["10_Numeric"] end

if mn_vol_raw ~= nil then
    local mvol_val = tonumber(mn_vol_raw)
    local last_mvol = G_VolState["mvol"] or -999.0
    if math.abs(last_mvol - mvol_val) > 0.1 then
        -- FIXED: Send "mv" instead of "mvol" to match Python Bridge
        AddCmd("mv", mvol_val)
        G_VolState["mvol"] = mvol_val
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
