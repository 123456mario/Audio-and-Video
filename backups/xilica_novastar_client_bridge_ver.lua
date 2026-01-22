-- =========================================================
-- BACKUP: STRING-BASED CLIENT (Talking to UDP Bridge)
-- =========================================================
-- This script sends simple strings ("POWER_ON", "BRI_100") 
-- to the Raspberry Pi Bridge (UDP 10008). 
-- Use this if Direct Control is too complex or unstable.

local in_t = ...
if type(in_t) ~= "table" then in_t = {} end
local out_t = {}

local Commands = {
    [1] = "POWER_OFF", 
    [2] = "BRI_20",    
    [3] = "BRI_40",    
    [4] = "BRI_60",    
    [5] = "BRI_80",    
    [6] = "BRI_100",   
    [7] = "PRESET_1",  
    [8] = "PRESET_2",  
    [9] = "PRESET_3"   
}

local active_cmd_str = ""

for pin_idx, cmd_str in pairs(Commands) do
    local v = in_t[pin_idx] or in_t[tostring(pin_idx)] or in_t[pin_idx.."_Logic"]
    if v == 1 or v == true or v == 1.0 or v == "true" then
        active_cmd_str = cmd_str
        break 
    end
end

if G_LastNovaCmd == nil then G_LastNovaCmd = "" end

if G_LastNovaCmd ~= active_cmd_str then
    if active_cmd_str ~= "" then
        -- Send Simple String to UDP Bridge
        out_t[1] = active_cmd_str
        out_t["1_String"] = active_cmd_str
        
        -- Feedback LED ON
        out_t[2] = 1
        G_LastNovaCmd = active_cmd_str
    else
        -- Released
        out_t[2] = 1 -- Keep LED on? Or Off? (Logic varied)
        G_LastNovaCmd = ""
    end
end

return out_t
