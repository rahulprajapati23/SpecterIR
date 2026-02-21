# SpecterIR v2 — Pseudocode & Summary

## Tool Overview

**SpecterIR** is a Python-based Incident Response (IR) data collection tool.  
It collects forensic information from the host system, displays it on the terminal,  
and saves everything into a JSON report with a SHA256 integrity hash and a ZIP archive.

---

## Flow Diagram

```
Run tool.py
    │
    ▼
Show Interactive Menu (Options 1–16 / A / Q)
    │
    ├── Enter 1–16 → Run selected module → Display result → Loop back
    │
    ├── Enter A   → Run ALL 16 modules in sequence
    │                   ↓
    │             Save final_report.json
    │             Compute SHA256 → hash.txt
    │             Compress folder → .zip
    │             Print summary
    │
    └── Enter Q   → Exit
```

---

## Pseudocode

```
IMPORTS: os, platform, psutil, socket, subprocess,
         json, hashlib, zipfile, datetime

CONFIG:
  TOOL_NAME = "SpecterIR"
  BASE_DIR  = "SpecterIR_<timestamp>"
  create folder BASE_DIR

─────────────────────────────────────────
UTILITY FUNCTIONS
─────────────────────────────────────────

run_command(cmd):
  → execute shell command, return output as string

save_json(filename, data):
  → write collected data as JSON to BASE_DIR/filename

sha256_file(filepath):
  → compute and return SHA256 hash of file

─────────────────────────────────────────
COLLECTION MODULES
─────────────────────────────────────────

system_info()        → OS, hostname, version, arch, boot time
cpu_info()           → cores, frequency, usage %, CPU model
memory_info()        → total/used/free RAM in GiB, swap info
disk_info()          → partitions, filesystem, total/used/free GiB
network_interfaces() → IP address, MAC address per adapter
network_info()       → active connections (local, remote, status, PID)
arp_cache()          → run "arp -a" → IP-to-MAC mapping table
dns_cache()          → run "ipconfig /displaydns"
running_services()   → run "sc query state= all"
scheduled_tasks()    → run "schtasks /query /fo LIST"
startup_info()       → run "wmic startup get caption,command"
process_info()       → all PIDs, names, user, CPU%, RAM%
user_info()          → logged-in users and session start times
installed_software() → run "wmic product get name,version"
env_vars()           → all system environment variables
event_logs()         → run "wevtutil qe System /c:20"

─────────────────────────────────────────
MAIN FLOW
─────────────────────────────────────────

main():
  collected_data = { tool, version, timestamp }

  loop:
    display_menu()         # show options 1-16, A, Q
    choice = input()

    if choice == "Q"  → break
    if choice == "A"  → run all 16 modules → break
    if choice in 1–16 → run that module only

    after each module:
      print_result()       # display formatted box on terminal
      store in collected_data

  save_json("final_report.json", collected_data)
  hash = sha256_file("final_report.json")
  save hash → "hash.txt"
  zip BASE_DIR folder → BASE_DIR.zip

  print: Evidence Folder, ZIP name, SHA256
```

---

## Module Summary Table

| No. | Module | Data Collected | Method Used |
|-----|--------|----------------|-------------|
| 1 | System Info | OS, hostname, version, arch, boot time | platform, psutil |
| 2 | CPU Info | Cores, speed (MHz), usage % | psutil.cpu_freq() |
| 3 | Memory Info | RAM total/used/free in GiB, swap | psutil.virtual_memory() |
| 4 | Disk Info | Partitions, filesystem, GiB, usage % | psutil.disk_partitions() |
| 5 | Network Interfaces | IP address, MAC per adapter | psutil.net_if_addrs() |
| 6 | Active Connections | Local/remote address, port, PID | psutil.net_connections() |
| 7 | ARP Cache | IP-to-MAC mapping table | arp -a |
| 8 | DNS Cache | Cached DNS entries | ipconfig /displaydns |
| 9 | Running Services | All Windows services + status | sc query state= all |
| 10 | Scheduled Tasks | All scheduled jobs | schtasks /query /fo LIST |
| 11 | Startup Persistence | Programs that auto-run on boot | wmic startup |
| 12 | Process Info | All PIDs, names, user, CPU/RAM% | psutil.process_iter() |
| 13 | User Info | Logged-in users, session start time | psutil.users() |
| 14 | Installed Software | All installed apps + versions | wmic product |
| 15 | Environment Variables | All system environment variables | os.environ |
| 16 | Recent Event Logs | Last 20 System event log entries | wevtutil |

---

## Output Files

| File | Description |
|------|-------------|
| `SpecterIR_<timestamp>/final_report.json` | All collected data in JSON format |
| `SpecterIR_<timestamp>/hash.txt` | SHA256 hash of the report (integrity check) |
| `SpecterIR_<timestamp>.zip` | Compressed evidence archive |

---

## How to Run

```bash
python tool.py
```

Select a module number (1–16), **A** to collect everything, or **Q** to exit.
