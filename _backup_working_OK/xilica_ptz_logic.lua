local in_t = ...
if type(in_t) ~= "table" then in_t = {} end
local out_t = {}

local cam = "CAM1" 
local dirs = {"LEFT", "RIGHT", "UP", "DOWN", "HOME", "ZOOMIN", "ZOOMOUT"}

local cmd = ""
for i, d in ipairs(dirs) do
    local v = in_t[i] or in_t[tostring(i)] or in_t[i.."_Logic"]
    local is_down = (v == 1 or v == true or v == 1.0)
    
    if is_down then
        if cmd == "" then
             if d == "HOME" then
                 cmd = cam .. " HOME ON"
             else
                 cmd = cam .. " REL_" .. d .. " ON"
             end
        end
    end
end

if G_LastCmd ~= cmd then
    if cmd ~= "" then
        local final = cmd .. string.char(13)
        out_t[1] = final
        out_t["1_Binary"] = final
        out_t["1_String"] = final
        
        out_t[2] = 1
        out_t["2_Logic"] = true
        
        G_LastCmd = cmd
        return out_t, "Sent: " .. cmd
    else
        local stop_cmd = cam .. " STOP OFF" .. string.char(13)
        out_t[1] = stop_cmd
        out_t["1_Binary"] = stop_cmd
        out_t["1_String"] = stop_cmd
        
        out_t[2] = 1
        out_t["2_Logic"] = true
        
        G_LastCmd = cmd
        return out_t, "Sent: STOP"
    end
end

out_t[2] = 0
out_t["2_Logic"] = false
return out_t
