local in_t = ...
if type(in_t) ~= "table" then in_t = {} end
local out_t = {}

-- =========================================================
-- NOVASTAR DIRECT CONTROL (HEX + KEEPALIVE)
-- =========================================================
-- This script replaces the Raspberry Pi Bridge.
-- Connect Xilica "Network Client" Module directly to Novastar IP.
-- Settings: TCP, Port 15200 (or 5200 if legacy)

-- 1. Verified Hex Commands (Pre-calculated Checksum)
-- Note: Lua uses \xHH format for binary
local CMDS = {
    POWER_OFF = "\x55\xaa\x00\x00\xfe\xff\x01\xff\xff\xff\x01\x00\x01\x00\x00\x02\x01\x00\x00\x55\x5a", -- 0% (Verified 55 5A)
    BRI_20    = "\x55\xaa\x00\x00\xfe\xff\x01\xff\xff\xff\x01\x00\x01\x00\x00\x02\x01\x00\x33\x55\x8d", -- 20%
    BRI_40    = "\x55\xaa\x00\x00\xfe\xff\x01\xff\xff\xff\x01\x00\x01\x00\x00\x02\x01\x00\x66\x55\xc0", -- 40%
    BRI_60    = "\x55\xaa\x00\x00\xfe\xff\x01\xff\xff\xff\x01\x00\x01\x00\x00\x02\x01\x00\x99\x55\xf3", -- 60%
    BRI_80    = "\x55\xaa\x00\x00\xfe\xff\x01\xff\xff\xff\x01\x00\x01\x00\x00\x02\x01\x00\xcc\x56\x26", -- 80%
    BRI_100   = "\x55\xaa\x00\x00\xfe\xff\x01\xff\xff\xff\x01\x00\x01\x00\x00\x02\x01\x00\xff\x54\x5b", -- 100% (Verified 54 5B)
    PING      = "\x55\xaa\x00\x00\xfe\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x57\x56"    -- Heartbeat
}

-- 2. Input Mapping (1-9)
local InputMap = {
    [1] = "POWER_OFF",
    [2] = "BRI_20",
    [3] = "BRI_40",
    [4] = "BRI_60",
    [5] = "BRI_80",
    [6] = "BRI_100",
    [7] = "PING", -- Manual Ping trigger (optional)
    [8] = "PING",
    [9] = "PING"
}

-- 3. State Maintenance
if G_LastNovaCmd == nil then G_LastNovaCmd = "" end
if G_NovaTimer == nil then G_NovaTimer = 0 end

-- =========================================================
-- LOGIC
-- =========================================================

-- A. Detect Button Press
local active_cmd_key = nil

for pin, key in pairs(InputMap) do
    local v = in_t[pin] or in_t[tostring(pin)] or in_t[pin.."_Logic"]
    if v == 1 or v == true or v == 1.0 or v == "true" then
        active_cmd_key = key
        break
    end
end

-- B. Tick Timer for Heartbeat (Approx 1 sec per call depending on Poll)
-- Xilica Lua usually runs on event or fast poll. We'll assume fast poll.
-- We use a rough counter. If poll is 100ms, 100 ticks = 10s.
G_NovaTimer = G_NovaTimer + 1

local data_to_send = nil

-- C. Event Processing
if active_cmd_key then
    -- User pressed something
    if G_LastNovaCmd ~= active_cmd_key then
        -- New Press -> Send Command
        data_to_send = CMDS[active_cmd_key]
        G_LastNovaCmd = active_cmd_key
        -- Reset Timer on manual action
        G_NovaTimer = 0 
    end
else
    -- Released
    G_LastNovaCmd = ""
end

-- D. Heartbeat Check (Automatic)
-- If no action for ~200 cycles (adjust based on speed), send PING
-- Assuming script runs ~10-20 times/sec? Let's try 300.
if G_NovaTimer > 300 then
    data_to_send = CMDS["PING"]
    G_NovaTimer = 0
end

-- E. Output to Network Client
if data_to_send then
    -- Send Binary String
    out_t[1] = data_to_send
    out_t["1_String"] = data_to_send -- Bind this to Network Client
end

return out_t
