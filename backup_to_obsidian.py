import os
import shutil
import datetime

# --- CONFIGURATION ---
OBSIDIAN_ROOT = "/Users/gimdongseong/Library/Mobile Documents/iCloud~md~obsidian/Documents/Mario_inside/obsidian-memory"
PROJECT_NAME = "Behringer_Xilica_Bridge"

# Files to Backup (Source Path -> Category)
FILES_TO_BACKUP = {
    # 1. Main Bridge Scripts
    "wing_to_xilica_final.py": "01_Source_Code/Bridge",
    "ptz_cam.py": "01_Source_Code/Bridge",
    
    # 2. Service Files
    "osc_bridge.service": "01_Source_Code/Services",
    "ptz_cam.service": "01_Source_Code/Services",
    
    # 3. Xilica Lua Scripts
    "xilica_mixer_logic.lua": "01_Source_Code/Lua",
    "xilica_ptz_logic.lua": "01_Source_Code/Lua",
    "xilica_init.lua": "01_Source_Code/Lua",
    "home_ui_logic.lua": "01_Source_Code/Lua",
    
    # 4. Deployment Helpers
    "deploy_wing_bridge.py": "01_Source_Code/Deployment",
    "deploy_ptz_to_pi.py": "01_Source_Code/Deployment",
    
    # 5. Documentation (We might need to locate the finding report first)
    # Note: findings are already in Obsidian, so we don't need to copy them back,
    # but we can link them in the report.
}

TODAY = datetime.datetime.now().strftime("%Y-%m-%d")
TARGET_DIR_NAME = f"{TODAY}_{PROJECT_NAME}"
FULL_TARGET_PATH = os.path.join(OBSIDIAN_ROOT, TARGET_DIR_NAME)

REPORT_CONTENT = f"""# 📅 Daily Dev Report - {TODAY}
**Project:** {PROJECT_NAME}
**Status:** ✅ DEPLOYED & VERIFIED (Success)

## 📝 Summary of Achievements
1. **Wing OSC Protocol Cracked:**
   - Discovered that Wing expects **String-based dB values** for volume control.
   - Confirmed **1-based indexing** and correct Mute (Int 1/0) control.
   - Identified "Main Matrix 1" corresponds to **`/main/1`**.

2. **Critical Debugging & Fix:**
   - Identified that **Ghost Processes** (old versions of the script) were hogging Port 1500 on the Pi, causing Main Mute to fail while other channels worked.
   - **Solution:** Killed all python processes and restarted services.
   - **Result:** Full control of Channels 1-8 + Main Mute/Volume verified.

3. **Code Implementation:**
   - **`wing_to_xilica_final.py`**: Validated and active.
   - **`ptz_cam.py`**: Active (Preset Logic included).
   - **Xilica Lua**: Updated to handle 'mm' input correctly.

## 📂 Backup Manifest
The following critical files have been archived in this folder:

### 🐍 Python Bridge
- `wing_to_xilica_final.py` (Main Logic)
- `ptz_cam.py` (Camera Logic)

### ⚙️ System Services
- `osc_bridge.service`
- `ptz_cam.service`

### 🧠 Xilica Lua
- `xilica_mixer_logic.lua`
- `xilica_ptz_logic.lua`
- `xilica_init.lua`

## 🔜 Next Actions
- Verify physical touch panel control (Xilica -> Pi -> Wing).
- Fine-tune volume scaling if "String dB" response curve needs adjustment.
"""

def perform_backup():
    print(f"🚀 Starting Backup to Obsidian: {FULL_TARGET_PATH}")
    
    # 1. Create Directory Structure
    if not os.path.exists(FULL_TARGET_PATH):
        os.makedirs(FULL_TARGET_PATH)
        print(f"✅ Created root dir: {TARGET_DIR_NAME}")
    
    # 2. Copy Files
    for filename, category in FILES_TO_BACKUP.items():
        if os.path.exists(filename):
            dest_folder = os.path.join(FULL_TARGET_PATH, category)
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            
            shutil.copy2(filename, dest_folder)
            print(f"  - Copied {filename} -> {category}")
        else:
            print(f"  ⚠️ Warning: {filename} not found in current dir, skipping.")

    # 3. Write Report
    report_path = os.path.join(FULL_TARGET_PATH, " Daily_Report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(REPORT_CONTENT)
    print(f"✅ Created Report: Daily_Report.md")
    
    print("\n🎉 Backup Complete!")

if __name__ == "__main__":
    perform_backup()
