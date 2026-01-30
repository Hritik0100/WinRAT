# 🖥️ VASHU EXPLOIT - Advanced Screen Sharing Tool

**Professional Remote Desktop Sharing Solution with Cloudflare Tunnel Integration**

---

## 🎯 Overview

VASHU EXPLOIT is a powerful screen sharing and remote desktop tool that allows you to:
- Share your screen with anyone, anywhere in the world
- Control remote computers securely
- Access your computer from anywhere
- Provide remote technical support
- Collaborate on projects in real-time

Built with Python and powered by Cloudflare Tunnel for enterprise-grade security and performance.

---

## 🚀 Key Features

- **🔐 Enterprise Security** - Uses Cloudflare Tunnel for encrypted connections
- **⚡ Real-time Performance** - 60 FPS smooth screen sharing
- **🖱️ Full Remote Control** - Mouse and keyboard control capabilities
- **🔊 Audio Support** - Share system audio with viewers
- **🎛️ Easy Management** - Simple command-line interface
- **🌐 Global Access** - Works from anywhere with internet
- **👥 Multi-user Support** - Multiple viewers can watch simultaneously
- **🛡️ Firewall Friendly** - Works behind corporate firewalls

---

## 📋 System Requirements

### Server (Your Computer)
- **OS**: Windows 10/11, macOS 10.15+, Linux
- **Python**: 3.8 or higher
- **Internet**: Stable broadband connection
- **Permissions**: Admin rights for installation

### Client (Viewer Computer)
- **Browser**: Any modern web browser (Chrome, Firefox, Safari, Edge)
- **Internet**: Stable connection
- **No software installation required**

---

## 🛠️ Installation & Setup

### 1. Install Python Dependencies

```bash
# Install required Python packages
pip install pyautogui
pip install opencv-python
pip install pillow
pip install numpy
pip install cloudflared
pip install websockets
```

### 2. Download Cloudflared

**Windows:**
```bash
# Download from official Cloudflare website
# Or use PowerShell:
winget install Cloudflare.cloudflared
```

**macOS:**
```bash
# Using Homebrew
brew install cloudflared

# Or download manually from:
# https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
```

**Linux:**
```bash
# Download and install
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
sudo cp ./cloudflared-linux-amd64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared
```

### 3. Configure the Tool

1. **Edit the Python file**:
   ```python
   # In vashu_Exploit.pyw, set your configuration:
   HOST = "127.0.0.1"        # Local server address
   PORT = 8765               # WebSocket port
   QUALITY = 70              # Image quality (1-100)
   MAX_FPS = 60             # Frames per second
   ```

2. **Ensure cloudflared is in PATH**:
   - Windows: Add to System Environment Variables
   - macOS/Linux: Should be in `/usr/local/bin` or `/usr/bin`

---

## ▶️ How to Use

### Starting Screen Sharing

**Method 1: Double-click (Windows)**
- Simply double-click on `vashu_Exploit.pyw`
- The tool will automatically start and show you the sharing URL

**Method 2: Command Line**
```bash
# Run the script
python vashu_Exploit.pyw

# Or with custom port
python vashu_Exploit.pyw 8765
```

### What Happens When You Start:

1. **🟢 Server starts** on `localhost:8765`
2. **🔗 Cloudflare Tunnel connects** - creates secure public URL
3. **📋 URL displayed** in terminal/command prompt
4. **🟡 Status: RUNNING** - screen sharing is active
5. **🔐 Secure connection** established through Cloudflare

### For Viewers:

1. **Share the URL** displayed in your terminal
2. **Viewers open** the URL in any web browser
3. **No installation required** on viewer side
4. **Real-time screen sharing** begins immediately

---

## 🎮 Complete Command List

### Primary Commands

| Command | Action | Description |
|---------|--------|-------------|
| `python vashu_Exploit.pyw` | Start sharing | Begin screen sharing session |
| `python vashu_Exploit.pyw [port]` | Custom port | Start on specific port (e.g., 9000) |
| **Ctrl+C** (in terminal) | Stop sharing | End the current session |
| **Close window** | Stop sharing | Exit the application |

### Keyboard Shortcuts (During Sharing)

| Key | Function | Description |
|-----|----------|-------------|
| `Q` or `ESC` | Quit | Stop sharing and close application |
| `P` | Toggle mouse | Enable/disable remote mouse control |
| `C` | Toggle click | Enable/disable remote clicks |
| `R` | Toggle remote control | Toggle full remote desktop control |

### In-App Controls

- **🔴 Red Circle Button**: Stop sharing and close tunnel
- **Status Indicators**: Show connection status
- **Live URL Display**: Shows current public sharing URL

---

## ☁️ Cloudflare Tunnel Setup

Cloudflare Tunnel provides secure, firewall-friendly connections without port forwarding.

### How it works:
1. **Local server** runs on your computer (localhost)
2. **Cloudflared** creates secure tunnel to Cloudflare
3. **Public URL** is generated (e.g., `https://your-app.cloudflare tunnel.com`)
4. **Viewers access** through secure Cloudflare network
5. **Enterprise encryption** protects all data

### Benefits:
- 🔐 **No port forwarding** required
- 🛡️ **Firewall compatible** - works behind corporate firewalls
- ⚡ **Fast global network** - optimized routing
- 🔒 **End-to-end encryption** - data protected in transit
- 🌍 **Global accessibility** - access from anywhere

### URL Examples:
```
✓ https://screen-share-12345.trycloudflare.com
✓ https://my-desktop.companyname.pages.dev
✓ https://remote-access-user123.trycloudflare.com
```

---

## 📱 Viewer Instructions (For Recipients)

### What Viewers Need:
- Any modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- **No software installation required**

### How Viewers Connect:
1. Receive the public URL from you
2. Open the URL in their web browser
3. Wait for the connection to establish
4. View your screen in real-time

### Viewer Features:
- **🖥️ Live screen viewing** - see your desktop in real-time
- **🖱️ Optional mouse control** - move mouse cursor remotely (if enabled)
- **🔊 Audio support** - hear system sounds (if enabled)
- **📱 Mobile compatible** - works on phones and tablets

---

## 🛡️ Security Features

### Enterprise-grade Protection:
- **Cloudflare Tunnel Encryption** - Military-grade encryption
- **No direct IP exposure** - Your real IP is hidden
- **Token-based authentication** - Secure session management
- **Automatic SSL/TLS** - HTTPS encryption by default
- **Rate limiting** - Protection against abuse

### Best Security Practices:
- ⚠️ Only share URL with trusted people
- 🕒 Use for limited time sessions
- 🚪 Close sharing when done
- 🔄 Regular security updates
- 👁️ Monitor active connections

---

## 🎥 Demo & Screenshots

### Live Demo
To see EXE_IS_NOT_RAT in action:

1. **Clone the repository**:
   ```bash
git clone https://github.com/Hritik0100/EXE_IS_NOT_RAT.git
cd EXE_IS_NOT_RAT
```

2. **Run the tool**:
   ```bash
python Exe_is_not_RAT.pyw
```

3. **View the demo**: The tool will automatically generate a public URL via Cloudflare tunnel that you can share with others to view your screen live.

### Screenshots

**Main Interface**:
![Main Interface](https://raw.githubusercontent.com/Hritik0100/EXE_IS_NOT_RAT/master/screenshots/main_interface.png)

**Live Streaming**:
![Live Streaming](https://raw.githubusercontent.com/Hritik0100/EXE_IS_NOT_RAT/master/screenshots/live_stream.png)

**Web Viewer**:
![Web Viewer](https://raw.githubusercontent.com/Hritik0100/EXE_IS_NOT_RAT/master/screenshots/web_viewer.png)

*Note: Screenshots will be added after first demo recording*

---

## 🤝 Common Use Cases

### Technical Support:
- Help family/friends with computer issues
- IT department assisting remote employees
- Software debugging and troubleshooting

### Education & Training:
- Online classes and tutorials
- Software demonstrations
- Remote teaching sessions

### Collaboration:
- Team meetings with screen sharing
- Pair programming sessions
- Project collaboration
- Remote work scenarios

### Personal Use:
- Share gameplay with friends
- Remote assistance
- Accessing your computer from elsewhere
- Presentations and demos

---

## ⚠️ Important Notes

### Before Using:
- 🔌 Ensure stable internet connection
- 🔐 Keep URL private - only share with trusted people
- ⚠️ Be aware of what's visible on your screen
- 🕐 Sessions automatically end when you close the app

### Limitations:
- Quality depends on internet speed
- Audio sharing requires proper system configuration
- Some corporate networks may block WebSocket connections
- Mobile browsers may have limited control capabilities

### Troubleshooting:
- **Connection issues**: Check internet and firewall settings
- **Poor quality**: Reduce QUALITY setting in code
- **Slow performance**: Lower MAX_FPS value
- **Audio problems**: Check system audio settings

---

## 🆘 Support & Help

### Common Issues:

**1. "cloudflared not found"**
```bash
# Solution: Add cloudflared to system PATH
# Windows: System Properties → Environment Variables
# macOS/Linux: Ensure in /usr/local/bin
```

**2. "Port already in use"**
```bash
# Solution: Use different port
python vashu_Exploit.pyw 9000
```

**3. "Connection failed"**
```bash
# Check:
# - Internet connection
# - Firewall settings
# - Cloudflare status
```

**4. "Poor video quality"**
```python
# In code, adjust:
QUALITY = 80  # Increase for better quality
MAX_FPS = 30  # Reduce for smoother performance
```

---

## 📄 License

This tool is for educational and legitimate remote access purposes only. Users are responsible for:
- Complying with local laws and regulations
- Obtaining proper consent before accessing systems
- Using the tool ethically and responsibly

---

## 🚀 Quick Start Checklist

- [ ] Install Python 3.8+
- [ ] Install required packages (`pip install pyautogui opencv-python pillow numpy websockets`)
- [ ] Install cloudflared
- [ ] Download Exe_is_not_RAT.pyw
- [ ] Run: `python Exe_is_not_RAT.pyw`
- [ ] Copy the public URL
- [ ] Share URL with viewers
- [ ] Start collaborating!

---

## 📞 Contact

For issues, suggestions, or feedback, please reach out through appropriate channels.

---

**Made with ❤️ for secure, easy remote collaboration**

*EXE_IS_NOT_RAT - Professional Screen Sharing Solution*