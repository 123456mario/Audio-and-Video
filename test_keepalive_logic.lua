-- Mock Xilica Environment
G_Keep_Timer = 0
G_Keep_LastTickState = false

-- Load the script function (simulating Xilica's "Call by reference" or similar inclusion)
-- Since the file returns a function or the result, we need to adapt.
-- The file calculates and returns. Typically Xilica scripts are chunks.

local function run_cycle(pwr, tick)
    -- Load the chunk
    local chunk, err = loadfile("timer_keepalive_loop.lua")
    if not chunk then 
        print("Error loading script: " .. err)
        return nil
    end
    
    -- Prepare Inputs: Simulate Xilica Key format
    -- Xilica typically sends a mix of indexed and string keys
    local InTable = { 
        [1] = pwr, 
        ["1_Logic"] = pwr, 
        [2] = tick, 
        ["2_Numeric"] = tick 
    }
    
    -- Execute
    return chunk(InTable)
end

print("=== STARTING KEEPALIVE SIMULATION ===")

-- Simulate 10 Seconds (1Hz Ticks)
for t = 1, 10 do
    -- 1. Tick LOW
    local out, dbg = run_cycle(1, 0)
    
    -- 2. Tick HIGH
    out, dbg = run_cycle(1, 1)
    
    -- Dump all output keys to verify SetOut behavior
    local out_keys = ""
    for k,v in pairs(out) do
        out_keys = out_keys .. tostring(k) .. ","
    end
    
    print(string.format("[SEC %02d] Debug:%s | OUT_KEYS:[%s]", t, dbg, out_keys))
    
    local trig = out[3] or ""
    if trig == "\x01" then
        print("   >>> HEARTBEAT FIRED! <<<")
    end
end
