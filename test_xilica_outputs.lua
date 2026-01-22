-- Test Wrapper for xilica_script.lua
local script_path = "./xilica_script.lua"

-- Mock global if needed (G_count is global in script)
G_count = 0
G_prevPulse = 0

-- Load script chunk
local chunk, err = loadfile(script_path)
if not chunk then
    print("Error loading script: " .. err)
    os.exit(1)
end

print("Test: Running simulation for 60 seconds...")
local InTable = {}
InTable["1_Logic"] = 1 -- Power ON
InTable["1_Numeric"] = 0 -- Pulse (Low)

-- Simulate loop
for i = 1, 65 do
    -- Toggle pulse to increment timer
    InTable["1_Numeric"] = 1 -- High (Pulse)
    
    -- Execute
    local OutTable, Debug = chunk(InTable)
    
    -- Reset Pulse avoiding double count if script is edge triggered?
    -- Script is: if PulseState == 1 and G_prevPulse == 0 then count++
    
    -- In real Xilica, this runs continuously.
    -- Let's simulate Pulse toggle.
    -- Frame 1: Pulse High
    InTable["1_Numeric"] = 10 -- High
    local OutTable1, D1 = chunk(InTable)
    
    -- Frame 2: Pulse Low
    InTable["1_Numeric"] = -50 -- Low
    local OutTable2, D2 = chunk(InTable)
    
    -- Print status at certain intervals
    if i % 10 == 0 or i == 1 or i >= 59 then
        print(string.format("Step %d | Timer(Out2): %s | Frame(Out3): %s | Logic(Out1): %s", 
            i, tostring(OutTable1[2]), tostring(OutTable1[3]), tostring(OutTable1[1])))
    end
end
