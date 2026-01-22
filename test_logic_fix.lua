-- [INPUTS]
--  1: Master_Power_Latch (Logic State: High=ON, Low=OFF)
--  2: Tick_1Hz (Logic/Numeric Pulse for Timer)

-- [OUTPUTS]
--  1: Blink (Numeric 1/0)
--  2: Show_Start (Logic 1/0 for Idle Text)
--  3: Show_Next (Logic 1/0 for Done State)
--  4: Fader_Val (0.0-1.0)
--  5: Timer_Val (Int 0-100)
--  6: Percent (Int 0-100)
--  7 ~ 16: Segment_1 ~ 10 (10% increments)
--  17: Percent_Str (String e.g. "90%")

local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

-- ========================================================
-- CONSTANTS & CONFIGURATION
-- ========================================================
local STATE_IDLE = 0
local STATE_WAIT = 1
local STATE_DONE = 2

local PULSE_THRESH = -20   -- Reverting to user's sensitive threshold
local TIMER_STOP_AT = 60
local WAIT_DURATION = TIMER_STOP_AT 
local BLINK_PERIOD = 2

-- ========================================================
-- STATE PERSISTENCE
-- ========================================================
if G_SysState == nil then G_SysState = STATE_IDLE end
if G_Timer == nil then G_Timer = 0 end
if G_LastTickState == nil then G_LastTickState = false end

-- ========================================================
-- READ INPUTS (Robust Version from User)
-- ========================================================
local In_Latch = InTable[1] or InTable["Master_Power_Latch"] or InTable["1_Logic"] or InTable["1_Numeric"] or InTable["1"]
local In_Tick = InTable[2] or InTable["Tick_1Hz"] or InTable["2_Logic"] or InTable["2_Numeric"] or InTable["2"]

-- Robust Latch Detection
local Is_Power_On = (In_Latch == 1 or In_Latch == true or In_Latch == "true")

-- ========================================================
-- LOGIC CORE
-- ========================================================
local IsTickHigh = false

if Is_Power_On == false then
    G_SysState = STATE_IDLE
    G_Timer = 0
else
    if G_SysState == STATE_IDLE then
        G_SysState = STATE_WAIT
        G_Timer = 0
    elseif G_SysState == STATE_WAIT then
        -- Robust Tick Detection
        if type(In_Tick) == "boolean" then
            IsTickHigh = In_Tick
        else
            local nm = tonumber(In_Tick)
            if nm then
                 if nm == 0 then IsTickHigh = false
                 elseif nm > PULSE_THRESH then IsTickHigh = true end
            end
        end
        
        -- Edge detection and increment
        if IsTickHigh and (G_LastTickState == false) then
            G_Timer = G_Timer + 1
        end
        G_LastTickState = IsTickHigh
        
        if G_Timer >= WAIT_DURATION then
            G_Timer = WAIT_DURATION
            G_SysState = STATE_DONE
        end

    elseif G_SysState == STATE_DONE then
        -- [STOP MODE]
        -- Do nothing. Wait for Power (Input 1) to be toggled OFF to reset.
    end
end

-- ========================================================
-- PREPARE OUTPUT VALUES
-- ========================================================
local out_blink = 0
local out_progress = G_Timer / WAIT_DURATION
if out_progress > 1.0 then out_progress = 1.0 end

-- Centralized Percentage Calculation
local val_percent = math.floor((out_progress * 100) + 0.5)

if G_SysState == STATE_WAIT then
    if (G_Timer % BLINK_PERIOD) == 0 then out_blink = 1 end
end

-- ========================================================
-- HELPER: SHOTGUN OUTPUT SETTER (User's Compatibility Version)
-- ========================================================
local function SetOut(pin, value, name)
    OutTable[pin] = value
    OutTable[tostring(pin)] = value
    if type(value) == "string" then
        OutTable[tostring(pin) .. "_String"] = value
    else
        OutTable[tostring(pin) .. "_Numeric"] = value
    end
    if name then OutTable[name] = value end
end

-- ========================================================
-- WRITE OUTPUTS
-- ========================================================
SetOut(1, out_blink, "Blink")
SetOut(2, (G_SysState == STATE_IDLE and 1 or 0), "Show_Start")
SetOut(3, (G_SysState == STATE_DONE and 1 or 0), "Show_Next")
SetOut(4, out_progress, "Fader_Val")
SetOut(5, val_percent, "Timer_Val")
SetOut(6, val_percent, "Percent")
SetOut(17, string.format("%d%%", val_percent), "Percent_Str")

-- Segment Bar (10 steps)
for i = 1, 10 do
    local is_on = 0
    if i <= math.floor(out_progress * 10) then is_on = 1 end
    SetOut(6 + i, is_on, "Segment_" .. i)
end

-- ========================================================
-- DEBUG INFO
-- ========================================================
local debug_str = string.format("ST:%d | T:%d | P6:%d | P17:%s", 
    G_SysState, G_Timer, val_percent, tostring(OutTable[17] or "0%"))

return OutTable, debug_str
