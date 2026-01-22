# Xilica Volume Presets (dB Levels)

이 문서는 실리카 터치패널 UI 등에서 사용할 수 있는 각 채널별 8단계 볼륨 프리셋 값입니다.
모든 채널(1~8, Main)에 공통으로 적용하거나, 필요에 따라 수정하여 사용하십시오.

| 레벨 (Level) | dB 값 (Value) | 설명 (Description) |
| :---: | :---: | :--- |
| **0** | `-90.0` | Mute / Silence (Off) |
| **1** | `-60.0` | Very Low |
| **2** | `-40.0` | Background Low |
| **3** | `-30.0` | Background Normal |
| **4** | `-20.0` | Soft |
| **5** | `-10.0` | Nominal / Standard |
| **6** | `0.0` | Loud / Unity Gain |
| **7** | `+5.0` | Boost |
| **8** | `+10.0` | Max |

---

## 채널별 적용 예시 (Copy & Paste)

### CH 1 ~ CH 8
```
Level 0: SET CH1_VOL -90.0
Level 1: SET CH1_VOL -60.0
Level 2: SET CH1_VOL -40.0
Level 3: SET CH1_VOL -30.0
Level 4: SET CH1_VOL -20.0
Level 5: SET CH1_VOL -10.0
Level 6: SET CH1_VOL 0.0
Level 7: SET CH1_VOL 5.0
Level 8: SET CH1_VOL 10.0
```
(CH 번호만 1~8로 변경하여 사용)

### MAIN
```
Level 0: SET MAIN_VOL -90.0
Level 1: SET MAIN_VOL -60.0
Level 2: SET MAIN_VOL -40.0
Level 3: SET MAIN_VOL -30.0
Level 4: SET MAIN_VOL -20.0
Level 5: SET MAIN_VOL -10.0
Level 6: SET MAIN_VOL 0.0
Level 7: SET MAIN_VOL 5.0
Level 8: SET MAIN_VOL 10.0
```
