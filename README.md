# Shocking-VRChat

Shocking-VRChat is a Python application designed to bridge VRChat with **DG-Lab 3** shock collars (Coyote 3). It detects interactions in VRChat via **OSC** and triggers haptic feedback (shocks/vibrations) on the collar through a local network connection.

The project features a modern **GUI** inspired by the "Nothing Phone" design language, offering a clean and dark interface for managing your device connection and settings.

## Features

- **Modern GUI:** A sleek, "Nothing Phone" style interface (monochrome, dot accents) built with Tkinter.
- **VRChat Integration:** Listens for standard OSC parameters to trigger actions.
- **DG-Lab 3 Support:** Native support for the DG-Lab 3 app protocol via WebSocket.
- **Dual Channel Support:** Independently control Channel A and Channel B.
- **Configurable:** extensive settings via YAML files (`settings-advanced-v0.2.yaml`) to tune strength, duration, and trigger modes.
- **Built-in Web Server:** Displays a QR code for easy connection with the mobile app.

## Requirements

- **Python 3.8+**
- **Hardware:** DG-Lab 3 (Coyote 3) Shock Collar.
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
   # Create virtual environment (optional but recommended)
   python -m venv venv
   # Activate it:
   #   Windows: venv\Scripts\activate
   #   Linux/Mac: source venv/bin/activate

   # Install requirements
   pip install -r requirements.txt
   ```

## Usage

1. **Start the Application:**
   Run the GUI version:
   ```bash
   python gui_app.py
   ```
   *(Alternatively, you can run `shocking_vrchat.py` for a CLI-only experience)*

2. **Connect the App:**
   - The application will start a local server.
   - A QR Code should appear (or navigate to `http://<YOUR_PC_IP>:8800` in your browser).
   - Open the **DG-Lab 3 App** on your phone.
   - Scan the QR code to connect your phone to the PC server.

3. **VRChat Setup:**
   - Ensure your avatar has the standard VRChat Contact Receivers or parameters set up.
   - The application listens on port **9001** for OSC messages by default.
   - Default monitored parameters include:
     - `/avatar/parameters/TouchAreaA` (Triggers Channel A)
     - `/avatar/parameters/TouchAreaB` (Triggers Channel B)

## Configuration

The application uses `settings-advanced-v0.2.yaml` for configuration. You can modify this file to change:
- **OSC Port:** Default is `9001`.
- **WebSocket Port:** Default is `28846`.
- **Strength Limits:** Safety limits for shock intensity.
- **Trigger Modes:** Customize how parameters map to shock patterns.

## Troubleshooting

- **No Connection:** Ensure your PC and Phone are on the **same Wi-Fi network**. Detailed firewalls logs might show blocked connections; ensure ports 8800 and 28846 are allowed.
- **VRChat not triggering:** Check your OSC Debugger in VRChat to ensure messages are being sent. Verify the "OSC" toggle is enabled in the VRChat Radial Menu.
