local in_t = ...
if type(in_t) ~= "table" then in_t = {} end
local out_t = {}

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

-- =========================================================
-- STATE MANAGEMENT
-- =========================================================
if G_LastCmd == nil then G_LastCmd = "" end
if G_PrevInputs == nil then G_PrevInputs = {} end

-- [NEW] Auto-Reset Timer Variables
if G_ResetActive == nil then G_ResetActive = false end
if G_ResetTimer == nil then G_ResetTimer = 0 end

-- =========================================================
-- CONFIGURATION
-- =========================================================
local cam = "CAM1" 
local dirs = {
    "LEFT",    -- 1
    "RIGHT",   -- 2
    "UP",      -- 3
    "DOWN",    -- 4
    "HOME",    -- 5
    "ZOOMIN",  -- 6
    "ZOOMOUT", -- 7
    "PRESET1", -- 8
    "PRESET2", -- 9
    "PRESET3"  -- 10
}

-- Actions that trigger only on RISING EDGE (Press)
local is_edge_action = {
  ["HOME"] = true,
  ["PRESET1"] = true,
  ["PRESET2"] = true,
  ["PRESET3"] = true
}

-- =========================================================
-- MAIN LOGIC
-- =========================================================
local cmd = ""
local trigger_happened = false

for i, d in ipairs(dirs) do
    -- Read Input (Binary 1/0 or Boolean)
    local raw_v = in_t[i] or in_t[tostring(i)] or in_t[i.."_Logic"]
    local v = SafeNum(raw_v, 0)
    local is_down = (v == 1 or raw_v == true or raw_v == "true")
    
    -- Track previous state for Edge Detection
    local was_down = G_PrevInputs[i] or false
    G_PrevInputs[i] = is_down
    
    -- Determine if this input should trigger a command
    local is_active = false
    
    if is_edge_action[d] then
        -- Edge Logic: Only True on the Frame it goes from OFF -> ON
        if is_down and (not was_down) then
            is_active = true
            trigger_happened = true -- Mark that we triggered something
        end
    else
        -- Hold Logic
        if is_down then
            is_active = true
        end
    end
    
    -- Priority: First active input wins
    if is_active then
        if cmd == "" then
             if is_edge_action[d] then
                 cmd = cam .. " " .. d .. " ON"
             else
                 cmd = cam .. " REL_" .. d .. " ON"
             end
        end
    end
end

-- =========================================================
-- [NEW] INTERNAL AUTO-RESET LOGIC
-- =========================================================
-- If a trigger happened, start the 'Bomb Timer'
if trigger_happened then
    G_ResetActive = true
    G_ResetTimer = 0
end

-- Timer Tick
local reset_signal = 0
if G_ResetActive then
    G_ResetTimer = G_ResetTimer + 1
    
    -- Delay: approx 30 frames (roughly 0.5~1.0 sec depending on polling rate)
    if G_ResetTimer > 30 then
        reset_signal = 1     -- FIRE! (Turn off button)
        G_ResetActive = false
        G_ResetTimer = 0
    end
end

-- Output 3: Reset Pulse (Connect this to Logic to Control)
out_t[3] = reset_signal
out_t["3_Logic"] = (reset_signal == 1)


-- =========================================================
-- COMMAND OUTPUT
-- =========================================================
if G_LastCmd ~= cmd then
    if cmd ~= "" then
        local final = cmd .. string.char(13)
        out_t[1] = final
        out_t["1_Binary"] = final
        out_t["1_String"] = final
        out_t[2] = 1
        
        G_LastCmd = cmd
        return out_t, "Sent: " .. cmd
    else
        local stop_cmd = cam .. " STOP OFF" .. string.char(13)
        out_t[1] = stop_cmd
        out_t["1_Binary"] = stop_cmd
        out_t["1_String"] = stop_cmd
        out_t[2] = 1
        
        G_LastCmd = cmd
        return out_t, "Sent: STOP"
    end
end

-- Idle State
out_t[2] = 0
return out_t
