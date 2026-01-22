-- Xilica Lua Script: Power-On Default Trigger
-- Purpose: Detects when Power (Input 1) switches ON, and sends a Trigger Pulse (Output 1)
-- Usage: Connect Output 1 to a "Preset Trigger" or "Snapshot Load" module to set default values.

local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}
local DebugMessage = ""

-- =========================================================
-- CONFIGURATION
-- =========================================================
local PULSE_DURATION_FRAMES = 50 -- How long the trigger stays ON (approx 1-2 seconds)

-- =========================================================
-- 1. READ INPUTS
-- =========================================================
-- Input 1: Power Status (Logic)
local RawPower = InTable["1_Logic"]
if RawPower == nil then RawPower = InTable[1] end
if RawPower == nil then RawPower = 0 end -- Default to Off if disconnected

local PowerBool = false
if RawPower == 1 or RawPower == true or RawPower == "true" then 
    PowerBool = true 
end

-- =========================================================
-- 2. STATE MANAGEMENT (Global Variables)
-- =========================================================
if G_LastPowerState == nil then G_LastPowerState = false end
if G_TriggerCountdown == nil then G_TriggerCountdown = 0 end

-- =========================================================
-- 3. LOGIC: RISING EDGE DETECTION
-- =========================================================
-- Check if Power went from OFF (False) to ON (True)
if PowerBool == true and G_LastPowerState == false then
    -- Power Just Turned ON! Start the Trigger.
    G_TriggerCountdown = PULSE_DURATION_FRAMES
end

-- Update Last State for next frame
G_LastPowerState = PowerBool

-- =========================================================
-- 4. OUTPUT GENERATION
-- =========================================================
local TriggerOut = false

if G_TriggerCountdown > 0 then
    TriggerOut = true
    G_TriggerCountdown = G_TriggerCountdown - 1
else
    TriggerOut = false
end

-- Format Output
if TriggerOut then
    OutTable[1] = 1
    OutTable["1_Logic"] = true
else
    OutTable[1] = 0
    OutTable["1_Logic"] = false
end

-- Debug String
DebugMessage = string.format("Pwr:%s Trig:%s CD:%d", tostring(PowerBool), tostring(TriggerOut), G_TriggerCountdown)

return OutTable, DebugMessage
