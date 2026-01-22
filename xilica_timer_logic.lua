-- [TIMER TYPE 2: KEEPALIVE LOOP - ALWAYS ON]
-- Behavior: Counts regardless of Power Latch. 
-- Modified: Removed 'Is_Power_On' check. Logic runs continuously.

local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

-- ========================================================
-- CONFIGURATION
-- ========================================================
local STATE_IDLE = 0
local STATE_WAIT = 1
local STATE_DONE = 2

local PULSE_THRESH = -20   
local TIMER_STOP_AT = 60
local WAIT_DURATION = TIMER_STOP_AT 
local BLINK_PERIOD = 2

-- ========================================================
-- STATE PERSISTENCE
-- ========================================================
if G_Keep_SysState == nil then G_Keep_SysState = STATE_IDLE end
if G_Keep_Timer == nil then G_Keep_Timer = 0 end
if G_Keep_LastTickState == nil then G_Keep_LastTickState = false end

-- ========================================================
-- READ INPUTS
-- ========================================================
-- Input 1 is the Tick Source (Logic/Numeric Pulse)
local In_Tick = InTable[1] or InTable["Tick_1Hz"] or InTable["1_Logic"] or InTable["1_Numeric"] or InTable["1"]

-- Force Power to be treated as TRUE always
local Is_Power_On = true 

-- ========================================================
-- LOGIC CORE
-- ========================================================
local IsTickHigh = false

-- [REMOVED IF/ELSE BLOCK FOR POWER CHECK]
-- Direct Logic Execution:

if G_Keep_SysState == STATE_IDLE then
    G_Keep_SysState = STATE_WAIT
    G_Keep_Timer = 0
elseif G_Keep_SysState == STATE_WAIT then
    -- Tick Detection
    if type(In_Tick) == "boolean" then
        IsTickHigh = In_Tick
    else
        local nm = tonumber(In_Tick)
        if nm then
                if nm == 0 then IsTickHigh = false
                elseif nm > PULSE_THRESH then IsTickHigh = true end
        end
    end
    
    -- Increment
    if IsTickHigh and (G_Keep_LastTickState == false) then
        G_Keep_Timer = G_Keep_Timer + 1
    end
    G_Keep_LastTickState = IsTickHigh
    
    -- Logic: Count to 60 -> Trigger HIGH -> Count to 63 -> Reset
    local trigger_point = 60
    local reset_point = 63
    
    if G_Keep_Timer >= reset_point then
        G_Keep_Timer = 0
        -- Remain in STATE_WAIT, just loop
    end

elseif G_Keep_SysState == STATE_DONE then
    -- Logic moved to STATE_WAIT for continuous looping with hold
    G_Keep_SysState = STATE_WAIT
end

-- ========================================================
-- OUTPUTS
-- ========================================================
local out_blink = 0
local out_timer_clamped = G_Keep_Timer
if out_timer_clamped > 60 then out_timer_clamped = 60 end 

local out_progress = out_timer_clamped / 60.0
if out_progress > 1.0 then out_progress = 1.0 end
local val_percent = math.floor((out_progress * 100) + 0.5)

if G_Keep_SysState == STATE_WAIT then
    if (G_Keep_Timer % BLINK_PERIOD) == 0 then out_blink = 1 end
end

-- Output 3 Logic: High only when we are in the "Overtime" zone (60-63)
local out_trigger = 0
if G_Keep_Timer >= 60 then out_trigger = 1 end

local function SetOut(pin, value, name)
    OutTable[pin] = value
    OutTable[tostring(pin)] = value
    if type(value) == "string" then
        OutTable[tostring(pin) .. "_String"] = value
    else
        OutTable[tostring(pin) .. "_Numeric"] = value
    end
end

SetOut(1, out_blink, "Blink")
SetOut(2, (G_Keep_SysState == STATE_IDLE and 1 or 0), "Show_Start")
SetOut(3, out_trigger, "Show_Next") -- THIS IS THE TRIGGER PIN (1 during 60s-63s)
SetOut(4, out_progress, "Fader_Val")
SetOut(5, val_percent, "Timer_Val")
SetOut(6, val_percent, "Percent")
SetOut(17, string.format("%d%%", val_percent), "Percent_Str")

for i = 1, 10 do
    local is_on = 0
    if i <= math.floor(out_progress * 10) then is_on = 1 end
    SetOut(6 + i, is_on, "Segment_" .. i)
end

local debug_str = string.format("State:%d | Timer:%d | Pwr:%s | Tick:%s | Blink:%d", 
    G_Keep_SysState, G_Keep_Timer, tostring(Is_Power_On), tostring(In_Tick), out_blink)
return OutTable, debug_str
