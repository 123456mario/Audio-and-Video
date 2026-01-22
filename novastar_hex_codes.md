# Novastar VX1000 Pro Hex Codes

## 1. Hex 문자열 (Raw Hex Strings)
Xilica Constant 모듈이나 일반 TCP 터미널에서 사용할 때 유용한 포맷입니다.

| 기능 (Function) | 설명 (Description) | Hex Code (Command + Checksum) |
| :--- | :--- | :--- |
| **Pwr OFF** | 화면 끄기 (Black Screen, Brightness 0%) | `55 AA 00 00 FE FF 01 FF FF FF 01 00 01 00 00 02 01 00 00 55 5A` |
| **Bright 20%** | 밝기 20% | `55 AA 00 00 FE FF 01 FF FF FF 01 00 01 00 00 02 01 00 33 55 8D` |
| **Bright 40%** | 밝기 40% | `55 AA 00 00 FE FF 01 FF FF FF 01 00 01 00 00 02 01 00 66 55 C0` |
| **Bright 60%** | 밝기 60% | `55 AA 00 00 FE FF 01 FF FF FF 01 00 01 00 00 02 01 00 99 55 F3` |
| **Bright 80%** | 밝기 80% | `55 AA 00 00 FE FF 01 FF FF FF 01 00 01 00 00 02 01 00 CC 56 26` |
| **Bright 100%** | 밝기 100% | `55 AA 00 00 FE FF 01 FF FF FF 01 00 01 00 00 02 01 00 FF 54 5B` |
| **Keepalive** | 연결 유지 (PING / Read Mode ID) | `55 AA 00 00 FE 00 00 00 00 00 00 00 02 00 00 00 00 00 57 56` |

---

## 2. Lua 스크립트용 코드 (Lua Format)
Xilica Designer의 Lua 스크립트에서 바로 사용할 수 있는 `\xHH` 포맷입니다.

```lua
local CMDS = {
    -- Power / Black Screen
    POWER_OFF = "\x55\xaa\x00\x00\xfe\xff\x01\xff\xff\xff\x01\x00\x01\x00\x00\x02\x01\x00\x00\x55\x5a",
    
    -- Brightness Levels
    BRI_20    = "\x55\xaa\x00\x00\xfe\xff\x01\xff\xff\xff\x01\x00\x01\x00\x00\x02\x01\x00\x33\x55\x8d",
    BRI_40    = "\x55\xaa\x00\x00\xfe\xff\x01\xff\xff\xff\x01\x00\x01\x00\x00\x02\x01\x00\x66\x55\xc0",
    BRI_60    = "\x55\xaa\x00\x00\xfe\xff\x01\xff\xff\xff\x01\x00\x01\x00\x00\x02\x01\x00\x99\x55\xf3",
    BRI_80    = "\x55\xaa\x00\x00\xfe\xff\x01\xff\xff\xff\x01\x00\x01\x00\x00\x02\x01\x00\xcc\x56\x26",
    BRI_100   = "\x55\xaa\x00\x00\xfe\xff\x01\xff\xff\xff\x01\x00\x01\x00\x00\x02\x01\x00\xff\x54\x5b",
    
    -- Heartbeat (Keepalive)
    PING      = "\x55\xaa\x00\x00\xfe\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x57\x56"
}
```
