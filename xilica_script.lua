-- Xilica Lua Script (Timer + Cumulative LEDs)
local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}
local DebugMessage = ""

-- =========================================================
-- CONFIGURATION
-- =========================================================
local PULSE_THRESH = -20
local TIMER_STOP_AT = 60

-- =========================================================
-- 1. READ INPUTS (ROBUST MODE)
-- =========================================================
-- Try to find Power (Logic) on Input 1
local RawPower = InTable["1_Logic"]
if RawPower == nil then RawPower = InTable[1] end
-- Fallback: If nil, assume OFF
if RawPower == nil then RawPower = 0 end

-- Try to find Pulse (Numeric) on Input 1 or 2
-- "1_Numeric" (if separated) or "2" (if linear)
local PulseKey = InTable["1_Numeric"] or InTable[2] or InTable["2_Numeric"] or InTable["1"]
local RawPulse = tonumber(PulseKey) or 0.0

-- =========================================================
-- 2. LOGIC (Timer)
-- =========================================================
local TimerActive = false
local PowerBool = false
if RawPower == 1 or RawPower == true or RawPower == "true" then PowerBool = true end

if PowerBool then
    TimerActive = true
    -- Edge Detection (Only count if Active)
    local PulseState = 0
    if RawPulse > PULSE_THRESH then PulseState = 1 else PulseState = 0 end

    if PulseState == 1 and G_prevPulse == 0 then
        if G_count < TIMER_STOP_AT then 
            G_count = G_count + 1 
        end
    end
    G_prevPulse = PulseState

else
    -- POWER OFF RESET
    TimerActive = false
    G_count = 0        -- Reset Timer
    G_prevPulse = 0    -- Reset Pulse State
end

-- =========================================================
-- 3. VISUALIZATION logic
-- =========================================================
-- Output Raw Timer Value as requested
local Frame_Index = G_count

local Page_Trigger = false
if G_count >= 60 then Page_Trigger = true end

-- =========================================================
-- 4. OUTPUTS (SHOTGUN APPROCH)
-- =========================================================
-- We will write to EVERY possible key to ensure connection

-- Output 1: Logic (Page Trigger)
if Page_Trigger then
    OutTable[1] = 1.0           -- Integer Index
    OutTable["1_Logic"] = true  -- String Key
else
    OutTable[1] = 0.0
    OutTable["1_Logic"] = false
end

-- Output 2: Numeric 1 (Timer Value)
OutTable[2] = G_count
OutTable["1_Numeric"] = G_count 

-- Output 3: Numeric 2 (Flooding all possible keys)
-- We brute force all reasonable keys to ensure signal
for i = 1, 10 do
    OutTable[i] = G_count
    OutTable[tostring(i)] = G_count
    OutTable[i .. "_Numeric"] = G_count
end

-- =========================================================
-- 5. DISCRETE LOGIC OUTPUTS (For Stacked Image Buttons)
-- =========================================================
-- Since "Multi-State Button" is missing, we use 16 stacked Toggle Buttons.
-- We output 16 separate Logic signals: Frame_1, Frame_2... Frame_16.
-- Only ONE is true at a time based on the timer.

-- Calculate Frame Index (1-16)
local Total_Frames = 16
local Steps_Per_Frame = TIMER_STOP_AT / Total_Frames -- 60 / 16 = 3.75 seconds per frame
local Current_Frame = math.floor(G_count / Steps_Per_Frame) + 1
if Current_Frame > Total_Frames then Current_Frame = Total_Frames end
if Current_Frame < 1 then Current_Frame = 1 end

for i = 1, Total_Frames do
    -- Cumulative Logic: Frame 1 stays ON, Frame 2 turns ON, etc.
    -- This allows stacking images on top of each other without gaps.
    local IsActive = (Current_Frame >= i)
    
    OutTable["Frame_" .. i] = IsActive
end

-- Also put the Calculated 1-10 Index on a distinct key if needed, but restore Pin 3 to G_count "like before"
-- OutTable[3] = Current_Frame -- REMOVED to restore G_count on Pin 3
OutTable["Frame_Index_Numeric"] = Current_Frame 
OutTable["Numeric_Frame_Index"] = Current_Frame

-- Debug
DebugMessage = string.format("Pwr:%s Val:%.1f T:%d F:%d", tostring(RawPower), RawPulse, G_count, Current_Frame)

return OutTable, DebugMessage
