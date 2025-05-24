import os
import json
import socket
import time
import platform
import sys
import psutil
import threading
from datetime import datetime
from websocket import WebSocketApp

CONFIG_FILE = "config.json"
COMPUTER_NAME = socket.gethostname()
update_interval = 30 

def add_to_startup():
    try:
        import win32com.client
        exe_path = os.path.abspath(sys.argv[0])
        startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        shortcut_path = os.path.join(startup_folder, "agent.lnk")

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = exe_path
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
        shortcut.IconLocation = exe_path
        shortcut.save()
        print(f"[AGENT] Added to Windows Startup.")
    except Exception as e:
        print(f"[AGENT] Failed to add to startup: {e}")

def get_server_url():
    if not os.path.exists(CONFIG_FILE):
        try:
            server_address = input("Enter full WebSocket URL (e.g., ws://1.2.3.4:5000 or wss://example.com): ").strip()
        except RuntimeError:
            import tkinter as tk
            from tkinter import simpledialog, Tk
            root = Tk()
            root.withdraw()
            server_address = simpledialog.askstring(
                "Server Address Required",
                "Enter full WebSocket URL (e.g., ws://IP:PORT or wss://example.com):"
            )
            root.destroy()
        if not server_address:
            raise Exception("No server address provided. Exiting...")
        if not (server_address.startswith("ws://") or server_address.startswith("wss://")):
            raise Exception("Invalid address. Must start with ws:// or wss://")
        with open(CONFIG_FILE, "w") as f:
            json.dump({"server": server_address}, f)
        add_to_startup()
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    server_address = config.get("server")
    if not server_address:
        raise Exception("No server address found in config file.")
    if not (server_address.startswith("ws://") or server_address.startswith("wss://")):
        raise Exception("Saved server address is invalid. Must start with ws:// or wss://")
    return server_address

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "0.0.0.0"

def get_system_info():
    ip = get_local_ip()
    boot_time_sec = psutil.boot_time()
    uptime_sec = time.time() - boot_time_sec
    hours = int(uptime_sec // 3600)
    minutes = int((uptime_sec % 3600) // 60)
    return {
        "computer_name": COMPUTER_NAME,
        "ip": ip,
        "start_time": int(boot_time_sec * 1000),
        "up_time": f"{hours}h {minutes}m",
        "uptime_seconds": int(uptime_sec),
        "lastSeen": int(time.time() * 1000),
        "status": "online",
    }

def send_update(ws):
    try:
        if ws.sock and ws.sock.connected:
            system_info = get_system_info()
            ws.send(json.dumps(system_info))
            print(f"[AGENT] Sent update at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"[AGENT] WebSocket not connected.")
    except Exception as e:
        print(f"[AGENT] Failed to send update: {e}")

def shutdown_computer():
    print(f"[AGENT] Executing shutdown sequence...")
    try:
        if platform.system() == "Windows":
            os.system("shutdown /s /f /t 1")
        elif platform.system() == "Linux":
            os.system("shutdown now")
    except Exception as e:
        print(f"[AGENT] Shutdown failed: {e}")

def on_message(ws, message):
    print(f"[AGENT] Message received: {message}")
    try:
        data = json.loads(message)
        if data.get("type") == "shutdown":
            shutdown_computer()
    except Exception as e:
        print(f"[AGENT] Message processing error: {e}")

def on_open(ws):
    print(f"[AGENT] Connected to server. Registering...")
    ws.send(json.dumps(get_system_info()))

    def run_updates():
        while True:
            send_update(ws)
            time.sleep(update_interval)
    threading.Thread(target=run_updates, daemon=True).start()

def on_error(ws, error):
    print(f"[AGENT] WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"[AGENT] Connection closed. Reconnecting in 5 seconds...")
    time.sleep(5)
    start_agent()

def start_agent():
    server_url = get_server_url()
    print(f"[AGENT] Connecting to: {server_url}")
    ws = WebSocketApp(
        server_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    while True:
        try:
            ws.run_forever()
        except Exception as e:
            print(f"[AGENT] Unexpected error: {e}. Reconnecting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    start_agent()