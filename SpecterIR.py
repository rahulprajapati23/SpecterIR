import os
import platform
import psutil
import socket
import subprocess
import json
import hashlib
import zipfile
from datetime import datetime

# -----------------------------
# GLOBAL CONFIG
# -----------------------------

TOOL_NAME = "SpecterIR"
VERSION = "2.0"
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
BASE_DIR = f"{TOOL_NAME}_{TIMESTAMP}"
os.makedirs(BASE_DIR, exist_ok=True)

OS_TYPE = platform.system()

# -----------------------------
# UTIL FUNCTIONS
# -----------------------------

def run_command(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
    except:
        return "Command failed or unsupported."

def save_json(name, data):
    path = os.path.join(BASE_DIR, name)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    return path

# ANSI color codes
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
GRAY   = "\033[90m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

W = 58  # total inner width (between ║ and ║)

def _trunc(s, n):
    """Truncate string to n chars, adding '…' if needed."""
    s = str(s).replace("\n", " ").replace("\r", "")
    return s[:n-1] + "…" if len(s) > n else s

def box_top(title):
    title_plain = f"  {title}  "
    line = "═" * (W - len(title_plain))
    print(f"\n{CYAN}╔{BOLD}{CYAN}{title_plain}{RESET}{CYAN}{'═'*len(line)}╗{RESET}")

def box_sep():
    print(f"{CYAN}╠{'═'*W}╣{RESET}")

def box_bot():
    print(f"{CYAN}╚{'═'*W}╝{RESET}")

def box_row(key, value):
    """Key-value row. Pad plain strings FIRST, then colorize."""
    KEY_W = 20
    VAL_W = W - KEY_W - 3   # 3 for "  " + " "
    key_p = _trunc(str(key), KEY_W).ljust(KEY_W)
    val_p = _trunc(str(value), VAL_W).ljust(VAL_W)
    print(f"{CYAN}║{RESET}  {GREEN}{key_p}{RESET} {YELLOW}{val_p}{RESET}{CYAN}║{RESET}")

def box_text(text, color=None):
    """Single plain-text line inside the box."""
    c = color or GRAY
    inner = W - 2          # content area = W minus 2 border chars
    text = str(text).replace("\n", " ").replace("\r", "").strip()
    if not text:
        text = " "
    while len(text) > 0:
        chunk = text[:inner].ljust(inner)   # pad plain string first
        text  = text[inner:]
        print(f"{CYAN}║{RESET} {c}{chunk}{RESET}{CYAN}║{RESET}")

def box_label(text):
    """A highlighted label row (entry header)."""
    inner = W - 2
    label = _trunc(str(text), inner).center(inner)
    print(f"{CYAN}╠{RESET}{BLUE}{BOLD}{label}{RESET}{CYAN}╣{RESET}")

def print_result(name, data):
    box_top(name)
    if isinstance(data, dict):
        for k, v in data.items():
            box_row(k, v)

    elif isinstance(data, list):
        limit = 20
        for i, item in enumerate(data[:limit], 1):
            box_label(f" Entry #{i} ")
            if isinstance(item, dict):
                for k, v in item.items():
                    box_row(f"  {k}", v)
            else:
                box_text(str(item))
        if len(data) > limit:
            box_sep()
            box_text(f"  … {len(data)-limit} more entries saved to report JSON", YELLOW)

    else:
        lines = str(data).strip().splitlines()
        shown = [l for l in lines if l.strip()][:45]
        for line in shown:
            box_text(line)
        if len([l for l in lines if l.strip()]) > 45:
            box_sep()
            box_text("  … output truncated — full data in report JSON", YELLOW)

    box_bot()

def sha256_file(filepath):
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    return sha.hexdigest()

# -----------------------------
# MODULES
# -----------------------------

def system_info():
    return {
        "OS": OS_TYPE,
        "Release": platform.release(),
        "Version": platform.version(),
        "Architecture": platform.machine(),
        "Hostname": socket.gethostname(),
        "Boot_Time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
    }

def bytes_to_gib(b):
    return f"{b / (1024**3):.2f} GiB"

def memory_info():
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "Total_RAM"     : bytes_to_gib(mem.total),
        "Used_RAM"      : bytes_to_gib(mem.used),
        "Available_RAM" : bytes_to_gib(mem.available),
        "Usage_%"       : f"{mem.percent}%",
        "Swap_Total"    : bytes_to_gib(swap.total),
        "Swap_Used"     : bytes_to_gib(swap.used),
        "Swap_Free"     : bytes_to_gib(swap.free),
    }

def disk_info():
    disks = []
    for p in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(p.mountpoint)
            disks.append({
                "Device"    : p.device,
                "Mountpoint": p.mountpoint,
                "FS"        : p.fstype,
                "Total"     : bytes_to_gib(usage.total),
                "Used"      : bytes_to_gib(usage.used),
                "Free"      : bytes_to_gib(usage.free),
                "Usage_%"   : f"{usage.percent}%"
            })
        except:
            continue
    return disks

def process_info():
    plist = []
    for proc in psutil.process_iter(['pid','name','username','cpu_percent','memory_percent']):
        try:
            plist.append(proc.info)
        except:
            continue
    return plist

def network_info():
    conns = []
    for conn in psutil.net_connections():
        conns.append({
            "Local": str(conn.laddr),
            "Remote": str(conn.raddr),
            "Status": conn.status,
            "PID": conn.pid
        })
    return conns

def user_info():
    users = []
    for u in psutil.users():
        users.append({
            "User": u.name,
            "Terminal": u.terminal,
            "Started": datetime.fromtimestamp(u.started).isoformat()
        })
    return users

def startup_info():
    if OS_TYPE == "Windows":
        return run_command("wmic startup get caption,command")
    elif OS_TYPE == "Linux":
        return run_command("ls -la /etc/init.d/")
    elif OS_TYPE == "Darwin":
        return run_command("ls -la /Library/LaunchAgents")
    return "Unsupported"

def event_logs():
    if OS_TYPE == "Windows":
        return run_command("wevtutil qe System /c:20 /f:text")
    elif OS_TYPE == "Linux":
        return run_command("journalctl -n 20")
    elif OS_TYPE == "Darwin":
        return run_command("log show --last 1h")
    return "Unsupported"

def cpu_info():
    freq = psutil.cpu_freq()
    return {
        "Physical_Cores": psutil.cpu_count(logical=False),
        "Logical_Cores": psutil.cpu_count(logical=True),
        "CPU_Usage_%": psutil.cpu_percent(interval=1),
        "Max_Freq_MHz": round(freq.max, 2) if freq else "N/A",
        "Current_Freq_MHz": round(freq.current, 2) if freq else "N/A",
        "CPU_Model": run_command("wmic cpu get name").strip() if OS_TYPE == "Windows" else run_command("lscpu | grep 'Model name'").strip()
    }

def network_interfaces():
    ifaces = []
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            ifaces.append({
                "Interface": iface,
                "Family": str(addr.family),
                "Address": addr.address,
                "Netmask": addr.netmask,
                "Broadcast": addr.broadcast
            })
    return ifaces

def installed_software():
    if OS_TYPE == "Windows":
        return run_command("wmic product get name,version")
    elif OS_TYPE == "Linux":
        return run_command("dpkg -l 2>/dev/null || rpm -qa")
    elif OS_TYPE == "Darwin":
        return run_command("brew list --versions")
    return "Unsupported"

def running_services():
    if OS_TYPE == "Windows":
        return run_command("sc query state= all")
    elif OS_TYPE == "Linux":
        return run_command("systemctl list-units --type=service --state=running --no-pager")
    elif OS_TYPE == "Darwin":
        return run_command("launchctl list")
    return "Unsupported"

def scheduled_tasks():
    if OS_TYPE == "Windows":
        return run_command("schtasks /query /fo LIST")
    elif OS_TYPE == "Linux":
        return run_command("crontab -l 2>/dev/null; ls /etc/cron*")
    elif OS_TYPE == "Darwin":
        return run_command("crontab -l 2>/dev/null")
    return "Unsupported"

def dns_cache():
    if OS_TYPE == "Windows":
        return run_command("ipconfig /displaydns")
    elif OS_TYPE == "Linux":
        return run_command("systemd-resolve --statistics")
    return "Unsupported"

def arp_cache():
    return run_command("arp -a")

def env_vars():
    return dict(os.environ)

# -----------------------------
# MENU SYSTEM
# -----------------------------

MODULE_MAP = {
    "1":  ("System Info",          system_info),
    "2":  ("CPU Info",              cpu_info),
    "3":  ("Memory Info",           memory_info),
    "4":  ("Disk Info",             disk_info),
    "5":  ("Network Interfaces",    network_interfaces),
    "6":  ("Active Connections",    network_info),
    "7":  ("ARP Cache",             arp_cache),
    "8":  ("DNS Cache",             dns_cache),
    "9":  ("Running Services",      running_services),
    "10": ("Scheduled Tasks",       scheduled_tasks),
    "11": ("Startup Persistence",   startup_info),
    "12": ("Process Info",          process_info),
    "13": ("User Info",             user_info),
    "14": ("Installed Software",    installed_software),
    "15": ("Environment Variables", env_vars),
    "16": ("Recent Event Logs",     event_logs),
}

def print_menu():
    print("\n" + "="*40)
    print(f"  SpecterIR v2  |  OS: {OS_TYPE}")
    print("="*40)
    for key, val in MODULE_MAP.items():
        print(f"  {key:>2}. {val[0]}")
    print("-"*40)
    print("   A. Collect EVERYTHING")
    print("   Q. Exit")
    print("="*40)

def main():

    collected_data = {
        "Tool": TOOL_NAME,
        "Version": VERSION,
        "Timestamp": datetime.now().isoformat()
    }

    while True:
        print_menu()
        choice = input("\nSelect option: ").strip().upper()

        if choice == "Q":
            break

        elif choice == "A":
            for key, val in MODULE_MAP.items():
                print(f"[+] Collecting {val[0]}...")
                result = val[1]()
                collected_data[val[0]] = result
                print_result(val[0], result)
            break

        elif choice in MODULE_MAP:
            name, func = MODULE_MAP[choice]
            print(f"[+] Collecting {name}...")
            result = func()
            collected_data[name] = result
            print_result(name, result)

        else:
            print("Invalid selection. Enter 1-16, A, or Q.")

    if len(collected_data) <= 3:
        print("No modules selected. Exiting.")
        return

    report_path = save_json("final_report.json", collected_data)

    hash_value = sha256_file(report_path)
    with open(os.path.join(BASE_DIR, "hash.txt"), "w") as f:
        f.write(hash_value)

    zip_name = f"{BASE_DIR}.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                z.write(os.path.join(root, file))

    print("\nCollection Complete.")
    print(f"Evidence Folder: {BASE_DIR}")
    print(f"Compressed File: {zip_name}")
    print(f"SHA256: {hash_value}")

if __name__ == "__main__":
    main()
