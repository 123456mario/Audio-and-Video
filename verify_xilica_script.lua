-- Verification Wrapper for Xilica Script
print("=== VERIFYING XILICA_SCRIPT.LUA ===")

-- 1. Initialize Global State (Simulating Xilica environment)
G_count = 0
G_prevPulse = 0

-- 2. Load the script
local script_chunk, err = loadfile("xilica_script.lua")
if not script_chunk then
    print("Error loading script: " .. err)
    os.exit(1)
end

-- Helper to run one step
local function RunStep(power, pulse, desc)
    -- Input table simulation
    local inputs = {
        ["1_Logic"] = power,
        ["2_Logic"] = pulse -- Simulating Logic connection
    }
    
    -- Xilica passes arguments as varargs (...)
    local out, debugMsg = script_chunk(inputs)
    
    print(string.format("Step [%s]: Pulse=%s -> G_count=%s", desc, tostring(pulse), tostring(out[1])))
    return out
end

-- 3. Run Test Sequence
RunStep(1, 0, "Init")       -- Count 0
RunStep(1, 1, "Rise 1")     -- Count 1
RunStep(1, 1, "Hold 1")     -- Count 1
RunStep(1, 0, "Fall")       -- Count 1
RunStep(1, 1, "Rise 2")     -- Count 2
RunStep(1, 0, "Fall")       -- Count 2
RunStep(1, 1, "Rise 3")     -- Count 3

if G_count == 3 then
    print("\nSUCCESS: Timer increments correctly with 0/1 logic inputs!")
else
    print("\nFAILURE: Final count should be 3, got " .. tostring(G_count))
    os.exit(1)
end
