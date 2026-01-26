# Shocking-VRChat

Shocking-VRChat is a powerful and intuitive bridge between **VRChat** and **DG-Lab 3** (Coyote 3) shock collars. It enables real-time haptic feedback in VR by translating VRChat OSC parameters into precise shock and vibration patterns.

Featuring a modern GUI inspired by the "Nothing Phone" design language, the application provides a clean, monochrome, and user-friendly interface for managing your device connections and settings.

## ✨ Key Features

- **Modern Nothing-Style GUI:** A sleek, minimalist interface with monochrome colors and dot accents.
- **VRChat OSC Integration:** Seamlessly listens to standard VRChat contact receivers and parameters.
- **DG-Lab 3 Support:** Full native support for the DG-Lab 3 protocol via WebSocket.
- **Dual Channel Control:** Independently configure and trigger Channel A and Channel B.
- **Advanced Mapping:** Highly customizable trigger modes (Shock, Distance, Touch) with adjustable strength and duration.
- **Easy Connection:** Built-in web server with QR code generation for quick pairing with the DG-Lab mobile app.
- **Safety First:** Built-in hardware and software power limits to ensure a safe experience.

## 🚀 Quick Start (EXE Version)

1. **Download:** Get the latest `Shocking-VRChat.exe` from the [Releases](https://github.com/AmigoFPS/Shocking-VRChat/releases) page.
2. **Run:** Launch the executable. No Python installation is required.
3. **Connect Mobile App:**
   - Ensure your PC and Phone are on the **same Wi-Fi network**.
   - The application will display a QR code or provide a link (typically `http://<YOUR_PC_IP>:8800`).
   - Open the **DG-Lab 3 App** on your phone and scan the QR code to establish a connection.
4. **VRChat Setup:**
   - Enable **OSC** in your VRChat Radial Menu (`Options > OSC > Enabled`).
   - The app listens on port **9001** by default.
   - Use compatible avatars or set up contact receivers using the default parameters:
     - `/avatar/parameters/TouchAreaA` -> Triggers Channel A
     - `/avatar/parameters/TouchAreaB` -> Triggers Channel B

## 🛠 Configuration

On first launch, the application generates `settings-v0.2.yaml` (Basic) and `settings-advanced-v0.2.yaml` (Advanced) in the same folder.

- **Basic Settings:** Manage parameter mappings and simple power limits.
- **Advanced Settings:** Fine-tune shock waves, trigger ranges, and connection ports.

## 🐍 For Developers (Source Code)

If you prefer running from source or want to contribute:

1. **Requirements:** Python 3.8+
2. **Setup:**
   ```bash
   git clone https://github.com/AmigoFPS/Shocking-VRChat.git
   cd Shocking-VRChat
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Run:**
   ```bash
   python gui_app.py
   ```

4. **Build EXE:**
   If you want to create your own executable:
   ```bash
   python build_exe.py
   ```
   The resulting file will be in the `dist/` directory.

## ❓ Troubleshooting

<<<<<<< HEAD
3. **VRChat Setup:**
   - Ensure your avatar has the standard VRChat Contact Receivers or parameters set up.
   - The application listens on port **9001** for OSC messages by default.
   - Default monitored parameters include:
     - `/avatar/parameters/TouchAreaA` (Triggers Channel A)
     - `/avatar/parameters/TouchAreaB` (Triggers Channel B)
=======
- **QR Code not appearing:** Check if port `8800` is blocked by your firewall.
- **Device not triggering:** 
  - Verify the phone is connected to the PC server via the DG-Lab app.
  - Check the VRChat OSC Debugger to ensure parameters are being sent.
  - Ensure your PC and Phone are on the same local network.
- **Ports:** The app uses port `9001` (OSC), `8800` (Web/QR), and `28846` (WebSocket). Ensure these are allowed in your firewall.
>>>>>>> 0c17c14 (new futures/bug fix)

---
*Disclaimer: Use this software responsibly and at your own risk. Always adhere to safety guidelines provided by the hardware manufacturer.*
