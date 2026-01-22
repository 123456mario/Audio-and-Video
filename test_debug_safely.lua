-- Xilica Lua Diagnostic Script (English Only)

-- 1. Initialize variables
-- '...' receives the input table from Xilica
local InTable = ...
local OutTable = {}

-- 2. Validate Input
if InTable == nil then
    -- Treat nil as empty to avoid crashing
    InTable = {}
    print("Warning: Input Table is nil")
end

-- 3. Logic
-- Always set default outputs so the table is never empty
OutTable[1] = "TEST_STRING"
OutTable[2] = "DEBUG_ACTIVE"

-- Check if we have received any values and print them
for i, v in pairs(InTable) do
    local msg = "Input " .. tostring(i) .. ": " .. tostring(v)
    print(msg)
    
    -- Update Output 2 with the last input value
    OutTable[2] = msg
end

-- 4. Return (Critical Step)
-- Must always return TWO arguments: 1. The Output Table, 2. A Debug String
return OutTable, "Script executed successfully"
