# Shocking-VRChat

Shocking-VRChat is a Python application designed to bridge **VRChat** with **DG-Lab 3** shock collars (Coyote 3) and **Tuya Smart Devices**. It detects interactions in VRChat via **OSC** and triggers haptic feedback (shocks/vibrations) or smart device actions through a local network connection.

The project features a modern **GUI** inspired by the "Nothing Phone" design language, offering a clean interface for managing your device connection and settings.

## Features

- **Modern GUI:** A sleek, "Nothing Phone" style interface (monochrome, dot accents) built with Tkinter.
- **Presets & Sharing:** Save your favorite tuning configurations and share them instantly with friends using short **Share Codes**.
- **VRChat Integration:** Listens for standard OSC parameters to trigger actions.
- **DG-Lab 3 Support:** Native support for the DG-Lab 3 app protocol via WebSocket.
- **Tuya IoT Support:** Control Tuya-enabled smart devices (e.g., smart plugs, shockers) via Tuya Cloud API.
- **Dual Channel Support:** Independently control Channel A and Channel B for DG-Lab 3.
- **Dynamic Power:** Configurable sensitivity, threshold, and randomized impact boosts.
- **Power Visualizer:** Real-time graph showing base power, random boosts, and limits.
- **Advanced Pattern Tuning:** Fine-tune velocity and acceleration sensitivity, boost decay, and wave frequency.
- **Built-in Web Server:** Displays a QR code for easy connection with the mobile app.

## Requirements

- **Python 3.8+**
- **Hardware:** 
  - DG-Lab 3 (Coyote 3) Shock Collar.
  - (Optional) Tuya Smart Devices.
- **Software:** 
  - VRChat (PC VR or Desktop).
  - DG-Lab 3 Mobile App (iOS/Android).

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AmigoFPS/Shocking-VRChat.git
   cd Shocking-VRChat
   ```

2. **Install dependencies:**
   It is recommended to use a virtual environment.
   ```bash
   # Create virtual environment (optional)
   python -m venv venv
   # Activate it:
   #   Windows: venv\Scripts\activate
   #   Linux/Mac: source venv/bin/activate

   # Install requirements
   pip install -r requirements.txt
   ```

## Usage

### 1. Start the Application
Run the GUI version for the best experience:
```bash
python gui_app.py
```
*(Alternatively, run `shocking_vrchat.py` for CLI/Server only mode)*

### 2. Connect DG-Lab 3 App
1. The application will start a local server and display a QR Code in the GUI.
2. Open the **DG-Lab 3 App** on your phone.
3. Scan the QR code to connect your phone to the PC server.
4. Ensure your phone and PC are on the **same Wi-Fi network**.

### 3. Power Controls & Tuning
- **Power Visualizer:** Monitor real-time power output (Base vs Boost) and limits. Toggle with the **ON/OFF** button.
- **Pattern Modes:**
  - **PROXIMITY:** Power based on distance.
  - **IMPACT:** Power based on velocity (speed of movement).
  - **RECOIL:** Power based on acceleration (sudden stops/starts).
- **Advanced Settings:** Click **▸ ADVANCED** to fine-tune:
  - **Boost Tuning:** Cooldowns, decay rates, and trigger thresholds.
  - **Pattern Ranges:** Adjust sensitivity for velocity/acceleration mapping.
  - **Wave Freq:** Custom update frequency (10ms - 100ms).

### 4. VRChat Setup
Ensure your avatar has the appropriate Contact Receivers or parameters. The app listens on **UDP Port 9001**.

**Default Monitored Parameters:**

**Channel A:**
- `/avatar/parameters/pcs/contact/enterPass`
- `/avatar/parameters/TouchAreaA`
- `/avatar/parameters/TouchAreaB`
- `/avatar/parameters/wildcard/*`

**Channel B:**
- `/avatar/parameters/TouchAreaC`
- `/avatar/parameters/TouchAreaD`
- `/avatar/parameters/lms-penis-proximityA*`

## GUI Controls Reference

This section details every button and slider available in the interface.

### Presets & Share Panel
Located on the left side, this panel allows you to manage configurations.
- **Code Field:** Paste a shared code here or copy one generated from your settings.
- **⬆ EXPORT:** Generates a short text code representing your current settings for all channels.
- **📋 COPY:** Copies the code from the field to your clipboard.
- **📋 PASTE:** Pastes text from your clipboard into the code field.
- **⬇ IMPORT:** Applies the settings from the code field to your app.
- **💾 SAVE PRESET:** Saves your current configuration with the name entered in the "Preset" field.
- **Preset List:** Quick-access buttons to load saved presets instantly. Click **✕** to delete a preset.

### Power Monitor
- **POWER MONITOR Toggle (ON/OFF):** Enables or disables the real-time power visualization graph.
  - **Base (Green):** Shows the power output calculated from your movement or proximity.
  - **Boost (Orange):** Shows the *additional* power added by the random boost system.
  - **Limit (Red Line):** Visualizes the current safety limit.
  - *Note: If a boost occurs, the limit line may temporarily rise above your set slider value. This is intentional behavior to allow impacts to feel stronger.*

### Channel Controls (A & B)
Each channel has its own limit slider and control buttons.
- **CHANNEL LIMIT Slider:** The main safety limit.
  - **Result:** The shock intensity will scale between 0 and this value based on your in-game actions.
  - **Example:** If set to 50, even maximum in-game interaction will only result in 50% power (unless a random boost is active).
- **◀ / ▶ Buttons:** Fine-tune the limit by ±1.
- **-10 / -5 / +5 / +10:** Quickly adjust the limit by fixed amounts.
- **RESET:** Instantly resets the limit to the default safe value (100).
- **⚡ TEST SHOCK:** Sends a short pulse at the current limit level to verify the device is working.

### Global Power Settings
These settings define how the app translates your VRChat avatar parameters into shock intensity.

- **Device Limit (Slider 0-200):** The global "ceiling" for power output.
  - **Result:** Acts as a hard cap for the base power.
  - *Important:* Random boosts *add* to this limit, allowing for dynamic "critical hits" that feel distinct from normal operation.

- **Sensitivity (Slider 0-200%):** A multiplier for the input signal.
  - **Result:**
    - **100%:** Linear response (0.5 input = 50% power).
    - **200%:** High sensitivity. You reach maximum power with only half the movement/distance. Good for subtle interactions.
    - **50%:** Low sensitivity. You must interact fully/violently to reach meaningful power levels.

- **Threshold (Slider 0-100%):** The minimum input level required to feel anything.
  - **Result:** Acts as a "noise gate". Signals below this level are ignored (0 power).
  - **Example:** Set to 10% to prevent the collar from buzzing due to tiny tracking jitters or idle animations.

### Random Boost Settings
This system simulates "impact" physics by adding extra power when sudden changes are detected.

- **Min (Slider 0-100):** The *lowest possible* random bonus added on impact.
- **Max (Slider 0-100):** The *highest possible* random bonus added on impact.
  - **Result:** When an impact triggers, the app picks a random number between Min and Max and adds it to your power limit.
  - **Example:** Min=10, Max=30. An impact might add +22 to your power for a split second, making that specific hit feel stronger than others.

### Advanced Settings (Hidden by default)
Click **▸ ADVANCED** to reveal fine-tuning controls.

**Boost Tuning (How boosts behave):**
- **Cooldown (0.1s - 3.0s):** The "refractory period" after a boost.
  - **Result:** Prevents the system from spamming boosts during a single continuous motion. Higher values = boosts happen less often (e.g., only on the first hit of a combo).
- **Decay (0.5s - 10.0s):** How long the extra boost power lasts.
  - **Result:**
    - **Short (0.5s):** A sharp "snap" that disappears instantly.
    - **Long (5.0s):** The hit leaves a lingering "sting" that keeps power elevated for a few seconds.
- **Trigger (1% - 100%):** Sensitivity to changes.
  - **Result:** Checks how *fast* the signal increases. Lower values mean even gentle taps can trigger a boost. Higher values require a violent spike in signal to trigger.

**Pattern Settings (Physics normalization):**
- **Vel Range (IMPACT Mode):** Reference speed for 100% power.
  - **Result:**
    - **Low (e.g. 10):** Very sensitive. Slow hand movements will max out the power.
    - **High (e.g. 100):** You must punch/thrust extremely fast to reach full power.
- **Acc Range (RECOIL Mode):** Reference stopping force for 100% power.
  - **Result:** Similar to velocity, but measures how *quickly* you stop. Lower values make it easier to trigger power with soft stops.
- **Wave Freq (10ms - 100ms):** The update rate of the shock signal.
  - **Result:**
    - **10ms:** Very smooth, "analog" feeling changes in intensity. High network usage.
    - **100ms:** "Stepped" or "pulsing" feel. Lower network usage.

### System & Logs
- **BASIC / ADVANCED Buttons:** Switch between editing the basic (`settings.yaml`) or advanced (`settings-advanced.yaml`) configuration files.
- **Reload (↻):** Reloads the settings from the currently selected configuration file without restarting the app.
- **SAVE (💾):** Saves the current text in the editor to the selected configuration file.
- **Copy (📋):** Copies the current system logs to the clipboard.
- **CLEAR:** Clears the current log display window.
- **AUTO↓:** Toggles auto-scrolling of the log window. When unchecked, the view will stay in place even as new logs arrive.

## Configuration

The application uses two configuration files:
1. `settings-v0.2.yaml` (Basic settings: limits, sensitivity, avatar parameters).
2. `settings-advanced-v0.2.yaml` (Advanced: internal wave patterns, network ports).

### Tuya Support (Advanced)
To enable Tuya smart device support, you must manually add the `machine` section to your configuration (usually in `settings-advanced-v0.2.yaml` or merged into the main loaded config).

Add this to your YAML config:

```yaml
machine:
  tuya:
    access_id: "YOUR_TUYA_ACCESS_ID"
    access_key: "YOUR_TUYA_ACCESS_KEY"
    device_ids:
      - "YOUR_DEVICE_ID_1"
      - "YOUR_DEVICE_ID_2"
    avatar_params:
      - "/avatar/parameters/Your_Tuya_Trigger_Param"
```

*Note: You need to register on the Tuya IoT Platform to get your Access ID and Key.*

## Troubleshooting

- **No Connection:** Ensure PC and Phone are on the same Wi-Fi. Check Firewall settings (Allow python/GUI app).
- **VRChat not triggering:** enable the OSC Debugger in VRChat to verify messages are sending. Check the "OSC" toggle in the Radial Menu.
- **Tuya Error:** Check your API quota and ensuring the device is online in the Tuya app.
