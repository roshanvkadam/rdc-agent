# 🖥️ Agent Script Documentation

This document explains how the agent script works, its features, setup, configuration, and how to compile it into a standalone executable.

---

## 📄 Overview

The agent is a Python script that:

* Collects basic system information (IP, uptime, computer name).
* Sends it periodically to a WebSocket server.
* Listens for a `shutdown` command from the server.
* Automatically adds itself to Windows Startup on first run.

---

## 📁 File Structure

```
RdcAgent.py          # Main agent script
config.json       # Created on first run to store WebSocket server URL
```

---

## ⚙️ Features

* 🖥️ System Info Collection
* 🔁 Periodic Update (every 30 seconds)
* 🧠 Auto-Configuration (stores server URL)
* 🚀 Auto-start with Windows
* 📴 Remote Shutdown support via WebSocket command

---

## 🚦 Behavior on First Run

1. If `config.json` is missing, prompts user to input WebSocket server URL.
2. Validates the URL format (`ws://` or `wss://`).
3. Saves the URL in `config.json`.
4. Adds itself to Windows Startup (requires admin rights).
5. Begins sending system info to server and listens for commands.

---

## 🔄 Periodic Update

The agent sends system info every 30 seconds to the WebSocket server:

* `computer_name`: Machine name
* `ip`: Local IP address
* `start_time`: Boot time in milliseconds
* `up_time`: Human-readable uptime
* `uptime_seconds`: Total uptime in seconds
* `lastSeen`: Timestamp of last heartbeat
* `status`: Always set to `online`

---

## 📡 Message Handling

When a message is received from the WebSocket server:

* If it's a JSON with `type: shutdown`, the machine will shut down immediately.
* Ignores other messages.

---

## 🧠 Functions Overview

| Function                  | Purpose                                      |
| ------------------------- | -------------------------------------------- |
| `add_to_startup()`        | Adds script to Windows startup folder        |
| `get_server_url()`        | Gets or prompts for WebSocket URL            |
| `get_local_ip()`          | Retrieves local IP address                   |
| `get_system_info()`       | Gathers and returns system info              |
| `send_update(ws)`         | Sends update to server via WebSocket         |
| `shutdown_computer()`     | Initiates OS shutdown                        |
| `on_message(ws, message)` | Processes incoming WebSocket messages        |
| `on_open(ws)`             | Runs when WebSocket is connected             |
| `on_error(ws, error)`     | Handles WebSocket errors                     |
| `on_close(ws, ...)`       | Handles WebSocket disconnections and retries |
| `start_agent()`           | Initiates connection to WebSocket server     |

---

## 🏗️ Building the `.exe` (Executable)

To convert the `RdcAgent.py` script into a Windows executable:

### 📦 Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

### ⚙️ Step 2: Create the Executable

```bash
pyinstaller --onefile --noconsole RdcAgent.py
```

> ✅ `--onefile`: Bundles everything into a single `.exe` file
> ❌ `--noconsole`: Hides the command prompt window (optional — use only if no console output is needed)

### 📁 Output

After running the above command:

* A `dist/agent.exe` file will be created — this is your final executable.
* Temporary build files will be in `build/` and a spec file like `agent.spec` will be generated.

---

## 📁 Files to Distribute

Distribute only:

```
dist/RdcAgent.exe
```

Ensure the following **are present or handled:**

* `config.json` will be auto-generated on the first run.
* The executable **must be run with admin rights** to allow:

  * Auto-start registration in Windows Startup folder.
  * Shutdown command to work.

---

## 🔐 Additional Considerations

* **Admin Rights**: On Windows, shutting down the PC or writing to the startup folder often requires administrator permissions.
* **Firewall/Antivirus**: May block unknown `.exe` files or WebSocket connections — whitelist if necessary.
* **`pywin32` dependency**: The `.exe` will include this, but for clean builds, ensure it is correctly installed in your Python environment before packaging:

```bash
pip install pywin32
```