<<<<<<< HEAD
# SpecterIR v2 — Documentation

## Overview

**SpecterIR** is an Incident Response (IR) data collection tool written in Python.  
It gathers forensic information from the host system — such as running processes, network connections, installed software, event logs, and more — and saves everything into a timestamped `.json` report with a SHA256 integrity hash and a `.zip` archive.

---

## Requirements

| Dependency | Purpose |
|---|---|
| `Python 3.x` | Runtime |
| `psutil` | System/process/network info |
| `socket`, `os`, `platform`, `subprocess`, `hashlib`, `zipfile` | Standard library (built-in) |

**Install dependency:**
```bash
pip install psutil
```

---

## How to Run

```bash
python tool.py
```

> **Note:** On Windows, use `python` (not `python3`).

---

## Menu & Syntax

When launched, the tool shows an interactive menu:

```
========================================
  SpecterIR v2  |  OS: Windows
========================================
   1. System Info
   2. CPU Info
   3. Memory Info
   4. Disk Info
   5. Network Interfaces
   6. Active Connections
   7. ARP Cache
   8. DNS Cache
   9. Running Services
  10. Scheduled Tasks
  11. Startup Persistence
  12. Process Info
  13. User Info
  14. Installed Software
  15. Environment Variables
  16. Recent Event Logs
----------------------------------------
   A. Collect EVERYTHING
   Q. Exit
========================================
Select option:
```

### Input Syntax

| Input | Action |
|---|---|
| `1` – `16` | Runs that specific module and prints result to terminal |
| `A` | Runs **all 16 modules** sequentially, then saves report |
| `Q` | Exit without saving (if nothing was collected) |

You can select **multiple individual modules** one by one — each result prints immediately after collection. Type `Q` when done to save the report.

---

## Modules Explained

| # | Module | What it Collects | Method Used |
|---|---|---|---|
| 1 | **System Info** | OS, version, hostname, architecture, boot time | `platform`, `psutil` |
| 2 | **CPU Info** | Cores, frequency, usage %, CPU model | `psutil.cpu_freq()`, `wmic cpu get name` |
| 3 | **Memory Info** | Total, used, available RAM and usage % | `psutil.virtual_memory()` |
| 4 | **Disk Info** | Partitions, mount points, filesystem, usage % | `psutil.disk_partitions()` |
| 5 | **Network Interfaces** | IP address, MAC address, netmask per adapter | `psutil.net_if_addrs()` |
| 6 | **Active Connections** | Local/remote address, port, status, PID | `psutil.net_connections()` |
| 7 | **ARP Cache** | IP-to-MAC mappings on the local network | `arp -a` |
| 8 | **DNS Cache** | Cached DNS entries | `ipconfig /displaydns` (Windows) |
| 9 | **Running Services** | All Windows services and their status | `sc query state= all` |
| 10 | **Scheduled Tasks** | All scheduled tasks (name, trigger, status) | `schtasks /query /fo LIST` |
| 11 | **Startup Persistence** | Programs set to auto-run on boot | `wmic startup get caption,command` |
| 12 | **Process Info** | PID, name, user, CPU%, memory% for all processes | `psutil.process_iter()` |
| 13 | **User Info** | Logged-in users, terminal, session start time | `psutil.users()` |
| 14 | **Installed Software** | All installed programs with version numbers | `wmic product get name,version` |
| 15 | **Environment Variables** | All system environment variables (PATH, TEMP, etc.) | `os.environ` |
| 16 | **Recent Event Logs** | Last 20 System event log entries | `wevtutil qe System /c:20 /f:text` |

---

## Output

After collection, three files are saved automatically:

```
SpecterIR_<YYYY-MM-DD_HH-MM-SS>/
├── final_report.json      ← All collected data in JSON format
└── hash.txt               ← SHA256 hash of the JSON report

SpecterIR_<YYYY-MM-DD_HH-MM-SS>.zip  ← Compressed evidence archive
```

### Example output at completion:
```
Collection Complete.
Evidence Folder : SpecterIR_2026-02-21_19-45-22
Compressed File : SpecterIR_2026-02-21_19-45-22.zip
SHA256          : 50ef959a580929c478db515eeab27302c2ed92c07b52c8fa0a2e118449a291ac
```

The **SHA256 hash** ensures the report has not been tampered with — a standard forensic chain-of-custody requirement.

---

## How it Works Internally

```
tool.py
├── run_command(cmd)      → Runs shell command, returns output as string
├── save_json(name, data) → Writes collected dict to JSON file
├── print_result(name, data) → Pretty-prints result to terminal
├── sha256_file(filepath) → Computes SHA256 hash of a file
│
├── [Module Functions]    → Each returns a dict/list/string of data
│
├── MODULE_MAP            → Dict mapping menu numbers to (name, function)
├── print_menu()          → Displays the interactive menu
└── main()                → Main loop: show menu → collect → save → hash → zip
```

### Flow Diagram

```
Run tool.py
    │
    ▼
Show Menu
    │
    ├─── Enter 1-16 ──► Run module ──► Print to terminal ──► Loop back
    │
    ├─── Enter A ─────► Run ALL modules in sequence
    │                        │
    │                        ▼
    │                  Save final_report.json
    │                  Compute SHA256 hash → hash.txt
    │                  Compress to .zip
    │                  Print summary
    │
    └─── Enter Q ─────► Exit (no save if nothing collected)
```

---

## Cross-Platform Support

The tool automatically detects the OS and uses the appropriate command:

| Feature | Windows | Linux | macOS |
|---|---|---|---|
| Startup | `wmic startup` | `ls /etc/init.d/` | `ls /Library/LaunchAgents` |
| Event Logs | `wevtutil` | `journalctl` | `log show` |
| Services | `sc query` | `systemctl` | `launchctl` |
| Scheduled Tasks | `schtasks` | `crontab` | `crontab` |
| DNS Cache | `ipconfig /displaydns` | `systemd-resolve` | N/A |
| Installed Software | `wmic product` | `dpkg -l` / `rpm -qa` | `brew list` |
=======
# SpecterIR
🔍 SpecterIR — Python-based Incident Response tool for host forensics. Collects system, network, process &amp; log data into a SHA256-verified report.
>>>>>>> 076aec56a5d7d2e81787fdbb990907cbd4d8b69f
