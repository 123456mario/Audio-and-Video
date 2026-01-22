-- [TIMER TYPE 2: KEEPALIVE LOOP & NOVASTAR HEARTBEAT]
-- Behavior: Counts 0-5s, sends Heartbeat, Resets.
-- Usage: For Novastar VX1000 Keepalive.

local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

-- ========================================================
-- CONFIGURATION
-- ========================================================
local TIMER_MAX = 60 -- 60 Second Cycle (Keepalive Interval)

-- ========================================================
-- STATE PERSISTENCE
-- ========================================================
if G_Keep_Timer == nil then G_Keep_Timer = 0 end
if G_Keep_LastTickState == nil then G_Keep_LastTickState = false end

-- ========================================================
-- INPUTS
-- ========================================================
local In_Latch = InTable[1] or InTable["Master_Power_Latch"] or InTable["1_Logic"] or InTable["1_Numeric"] or InTable["1"]
local In_Tick = InTable[2] or InTable["Tick_1Hz"] or InTable["2_Logic"] or InTable["2_Numeric"] or InTable["2"]

-- Robust Type Helpers
local function toBool(val)
    if val == 1 or val == "1" or val == true or val == "true" or val == "On" or val == "ON" then return true end
    return false
end

local function isTickActive(val)
    -- Accepts 1, "1", true, etc.
    if val == 1 or val == "1" or val == true or val == "true" or val == "On" then return true end
    local nm = tonumber(val)
    if nm and nm > 0 then return true end
    return false
end

local Is_Power_On = toBool(In_Latch)

-- ========================================================
-- LOGIC
-- ========================================================
local IsTickHigh = isTickActive(In_Tick)
local Fire_Heartbeat = 0

if Is_Power_On then
    -- Increment on Rising Edge
    if IsTickHigh and (G_Keep_LastTickState == false) then
        G_Keep_Timer = G_Keep_Timer + 1
    end
    G_Keep_LastTickState = IsTickHigh
    
    -- Cycle Logic
    if G_Keep_Timer >= TIMER_MAX then
        Fire_Heartbeat = 1
        G_Keep_Timer = 0 -- Reset
    else
        Fire_Heartbeat = 0
    end
else
    G_Keep_Timer = 0
    Fire_Heartbeat = 0
end

-- ========================================================
-- OUTPUTS (Simple Numeric)
-- ========================================================
-- 1: Blink (Numeric 1/0)
-- 2: Power (Numeric 1/0)
-- 3: Trigger (Numeric 1/0) - Connect to Binary Selector or Delay

OutTable[1] = (G_Keep_Timer % 2)
OutTable[2] = Is_Power_On and 1 or 0
OutTable[3] = Fire_Heartbeat

-- Debug String Construction
local keys_found = ""
for k,v in pairs(InTable) do
    keys_found = keys_found .. tostring(k) .. ","
end

local debug_str = string.format("T:%d/%d | Fire:%d | Pwr:%s | Tick:%s | KEYS:[%s]", 
    G_Keep_Timer, TIMER_MAX, Fire_Heartbeat, tostring(Is_Power_On), tostring(In_Tick), keys_found)
    
return OutTable, debug_str
