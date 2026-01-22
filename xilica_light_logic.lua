-- Light Control Logic
-- Input 1: Zone A (Universe 0) -> DMX Ch 2
-- Input 2: Zone B (Universe 1) -> DMX Ch 3
-- Output 1: Binary String (Connect to UDP Tx)
-- FINAL ALWAYS-ON SCRIPT (BINARY MODE)
-- Input: Fader/Button
-- Output: Binary \x00\xFF (Universe 0, Value 255)
-- Logic: ALWAYS outputs current state. NEVER clears output.
--        This ensures the UDP 'Tx Byte Stream' box is never empty.

-- 1. Initialize
-- 1. Initialize
local InTable = ...
local OutTable = {}

if InTable == nil then 
    InTable = {} 
    print("WARNING: InTable is nil")
end

-- 2. Process ALL Inputs
local debug_lines = {}

-- [[ DEBUG: DUMP ALL INPUTS ]]
-- This will show us exactly what is connected to the Lua block
print("=== INPUT DUMP START ===")
local input_count = 0
for k, v in pairs(InTable) do
    print("PIN " .. k .. ": " .. tostring(v) .. " (" .. type(v) .. ")")
    input_count = input_count + 1
end
if input_count == 0 then
    print("WARNING: NO INPUTS CONNECTED! Check your wires.")
end
print("=== INPUT DUMP END ===")
-- [[ END DEBUG ]]

-- Define how many channels we expect (e.g., 2) or just iterate what we have
for k, val in pairs(InTable) do
            -- Determine Channel Index from Key
    -- Key could be integer (1) or string ("1_Numeric", "dmx_2", "Input 2")
    local i = tonumber(k)
    if i == nil and type(k) == "string" then
        -- Find ANY sequence of digits in the string
        local s, e, cap = string.find(k, "(%d+)")
        if cap then 
            i = tonumber(cap)
        end
    end

    -- Process only if we found a valid channel index
    if i ~= nil then
        local u = i - 1 -- Universe 0 for Input 1, Univ 1 for Input 2...
        local v = 0     -- Default Value
        local status = "OFF"
        
        if val ~= nil then
            -- Convert Input (0-100) -> DMX (0-255)
            local num_val = tonumber(val)
            -- Handle Boolean Button Input (true = 100, false = 0)
            if val == true or val == "true" then num_val = 100 end
            if num_val == nil then num_val = 0 end
            
            -- Formula: (Input / 100) * 255
            local target_val = math.floor((num_val / 100) * 255)
            
            -- Clamp
            if target_val > 255 then target_val = 255 end
            if target_val < 0 then target_val = 0 end
            
            v = target_val
            status = string.format("IN:%s->%02X", tostring(val), v)
        else
            status = "Nil(00)"
        end
        
        -- Generate Binary Output for this Channel
        local payload = string.char(u, v)
        
        -- [CRITICAL FIX] Shotgun Output Strategy
        -- Output to ALL likely pin names to ensure connection
        OutTable[i] = payload              -- Integer Index (1)
        OutTable[i .. "_Binary"] = payload -- Named Key ("1_Binary")
        OutTable[i .. "_String"] = payload -- Named Key ("1_String")
        
        table.insert(debug_lines, string.format("CH%d(K:%s) U:%d V:%02X (%s)", i, k, u, v, status))
    end
end

-- 3. Final Debug Aggregation
-- Collect RAW DUMP for GUI visibility
local raw_dump = "FOUND:"
local count = 0
for k, v in pairs(InTable) do
    raw_dump = raw_dump .. " [" .. k .. "]=" .. tostring(v)
    count = count + 1
end
if count == 0 then raw_dump = "NO INPUTS DETECTED" end

-- Combine: Raw Dump | Loop Status
-- Put Dump FIRST so user sees it without scrolling
local final_debug_str = raw_dump .. " || " .. table.concat(debug_lines, " | ")
print(final_debug_str)

-- [FIX] Assign Debug String to Output Pin 3 (Integer Index)
-- This is much safer than using string keys.
OutTable[3] = final_debug_str

-- Return OutTable and the debug string (standard Xilica pattern)
return OutTable, final_debug_str
