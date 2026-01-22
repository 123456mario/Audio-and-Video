-- Xilica Initialization Script
-- Usage: Connect "Power On" Logic -> Delay (8s) -> Input Pin 1 of this Lua module
-- When Input 1 goes High (1), the script sends initialization commands.

local InTable = ...
if type(InTable) ~= "table" then InTable = {} end
local OutTable = {}

-- Define CR for clean transmission
local CR = string.char(13)

-- 1. Read Trigger Input (Pin 1)
-- Expecting a Logic High (1) signal from a Delay module
local Trigger = InTable["1_Logic"]
if Trigger == nil then Trigger = InTable[1] end
if Trigger == nil then Trigger = 0 end

-- Normalize Trigger
local TrigBool = false
if Trigger == 1 or Trigger == true or Trigger == "true" or Trigger == 1.0 then TrigBool = true end

-- 2. State Management (Prevent repeated firing)
if G_InitDone == nil then G_InitDone = false end
if G_PrevTrig == nil then G_PrevTrig = false end

-- 3. Execution Logic
-- Only fire on Rising Edge (0 -> 1)
if TrigBool and not G_PrevTrig then
    
    -- [MIXER COMMANDS]
    -- Mute All Channels 1-8
    for i = 1, 8 do
        -- Mute ON (Safety)
        write(string.format("SET ch%dm 1%s", i, CR))
        -- Volume to 0dB (Unity) -> Key 6 in Python Bridge Map
        write(string.format("SET ch%d_vol 6%s", i, CR))
    end
    
    -- Mute Main Channel (9)
    write(string.format("SET ch9m 1%s", CR))
    write(string.format("SET ch9_vol 6%s", CR))
    
    -- [CAMERA COMMANDS]
    -- Send PTZ Home (Preset 1)
    -- Using the same format as xilica_ptz_logic.lua? 
    -- Actually, direct Write is better if connected to the same TCP/IP bridge
    -- But Camera is usually on a different module. 
    -- If this script is connected to the Pi Bridge (TCP 1500), these SET commands work.
    -- Camera commands need to go to UDP 10001.
    -- Xilica Lua `write()` sends to the module it's connected to.
    -- If this module is connected to Mixer Bridge, it CANNOT send to Camera directly unless bridge forwards it.
    -- For now, we focus on Mixer Initialization. Camera Home can be done via separate Preset trigger in Xilica Designer.
    
    G_InitDone = true
end

-- Reset logic if Trigger goes Low? (Optional, allows re-triggering)
if not TrigBool then
    G_PrevTrig = false
    -- G_InitDone = false -- Uncomment if you want to allow re-init by toggling the input
else
    G_PrevTrig = true
end

-- Pass through status for LED feedback
OutTable[1] = G_InitDone
OutTable["1_Logic"] = G_InitDone

return OutTable
