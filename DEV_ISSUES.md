# Development Issues & Status Log

## 🔴 Active Issues

### 1. Xilica Page Flip Automation
- **Problem**: Automatic page navigation on XTouch panels via timer events is failing.
- **Symptoms**:
  - Page changes do not trigger when the timer completes.
  - Xilica Designer crashes when attempting to associate panels or save presets.
- **Planned Solutions**:
  - Investigate "Global Presets" as an alternative to panel-specific association.
  - Explore internal loopback mechanisms to trigger page flips without external hardware.
  - Verify "Action Trigger" logic connection to `Logic Out 1` (Lua block).

### 2. PTZ Camera Integration
- **Context**: Integrating Zoom control into the Xilica-Wing bridge.
- **Current Status**:
  - Need to ensure `osc_bridge.py` correctly parses and forwards `CAM1 ZOOMIN` and `CAM1 ZOOMOUT` commands.
  - Lua script needs validation for syntax errors regarding these new commands.

## 🟡 In Progress / Enhancements

### 1. UI/UX Redesign
- **Goal**: Modernize Camera Control UI.
- **Requirements**:
  - Clean white background with green accents.
  - New assets for "CAM (Front)", "CAM (Side)", PTZ, and Zoom controls.
  - **Logic**: Implement mutual exclusivity so only one camera is active at a time.

### 2. Lua Script Logic (Timer LED Bar)
- **Goal**: Create a cumulative progress bar using 60 LEDs.
- **Details**:
  - Use pins 2-61 for individual LED control.
  - Logic must output `true` cumulatively (e.g., at 10 seconds, LEDs 1-10 are ON).
  - **Configuration**: Ensure pins 2-61 are set to 'Logic' type in the Lua block for direct UI connection.

## ✅ Resolved / Notes

### 1. Image & Timer Synchronization
- **Constraint**: The `Numeric 2` output (Image Number) increments identically to the Timer value (0-60).
- **Warning**: If fewer than 60 images are provided (e.g., 32), the animation will stop or vanish after the corresponding second. Full 60-second animation requires 60 images.

### 2. Page Jump "Snapshot" Setup
- **Workaround**: Use Xilica "Presets" to capture a specific page view.
  - Create a preset while viewing the target page.
  - Link this preset to an Action Trigger connected to the Lua script's logic output.
