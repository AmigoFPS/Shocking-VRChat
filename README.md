# Shocking-VRChat

Shocking-VRChat is a Python application designed to bridge **VRChat** with **DG-Lab 3** shock collars (Coyote 3) and **Tuya Smart Devices**. It detects interactions in VRChat via **OSC** and triggers haptic feedback (shocks/vibrations) or smart device actions through a local network connection.

The project features a modern **GUI** inspired by the "Nothing Phone" design language, offering a clean interface for managing your device connection and settings.

## Features

- **Modern GUI:** A sleek, "Nothing Phone" style interface (monochrome, dot accents) built with Tkinter.
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
  - **Wave Freq:** Custom update frequency.

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
