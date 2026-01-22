-- FORCE SEND Script (Debug Mode)
-- This will send Art-Net packets CONTINUOUSLY.
-- Do not use for production! This is just to verify the connection.

local InTable = ...
local OutTable = {}

if type(InTable) ~= "table" then InTable = {} end

-- Function: Convert 0.0-1.0 to 0-255
function to_byte(val)
    local v = tonumber(val)
    if v == nil then return 0 end
    if v > 1.0 then v = 1.0 end -- Standardize to 1.0 max for ArtNet
    if v < 0.0 then v = 0.0 end
    return math.floor(v * 255)
end

-- Force output for Input 1 (Universe 0)
local val1 = InTable[1]

if val1 ~= nil then
    -- Convert Value
    -- Note: If your slider is 0-100, divide by 100. If 0-1.0, use as is.
    -- Xilica Native faders are usually 0.0-1.0? 
    -- The screenshot showed '100'. If it is 0-100, we clamp to 1.0 max in to_byte.
    -- Let's try to assume 0-100 and normalize it ourselves to be safe?
    -- Or just rely on clamp. If 100 -> 1.0 (Full On).
    
    local byte_val = to_byte(val1 / 100.0) -- Assuming Input is 0-100 based on screenshot
    if val1 <= 1.0 and val1 > 0.0 then
         -- If value is small (like 0.5), treat as 0-1.0
         byte_val = to_byte(val1)
    elseif val1 > 1.0 then
        -- If value is big (like 50, 100), treat as 0-100
         byte_val = to_byte(val1 / 100.0)
    end

    -- Create payload: Universe 0, Value X
    local payload = string.char(0, byte_val)
    
    -- Output ALWAYS
    OutTable[1] = payload
    
    -- Debug Log
    print("Input: " .. val1 .. " -> Sent Byte: " .. byte_val)
else
    print("Input 1 is Nil")
    OutTable[1] = ""
end

return OutTable, "Forcing Output..."
