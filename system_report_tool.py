from flask import Flask, render_template_string, send_file
import platform, psutil, socket, os
from time import ctime, time
from threading import Timer
from datetime import timedelta
import logging, webbrowser

app = Flask(__name__)

# Directories for logs and reports
LOG_DIR = "log"
REPORT_DIR = "report"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "system_report.log")
REPORT_FILE = os.path.join(REPORT_DIR, "system_report.txt")

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')

def format_bytes(bytes_value):
    return f"{bytes_value / (1024 ** 3):.2f} GB"

def get_uptime():
    uptime_sec = time() - psutil.boot_time()
    return str(timedelta(seconds=int(uptime_sec)))

def get_hardware_status():
    return {
        "CPU": psutil.cpu_count(logical=True) > 0,
        "Memory": psutil.virtual_memory().total > 0,
        "Disk": len(psutil.disk_partitions()) > 0,
        "Battery": psutil.sensors_battery() is not None,
        "Temperature": bool(psutil.sensors_temperatures()),
        "Network": any(psutil.net_if_addrs().values())
    }

def top_processes(n=5):
    processes = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try: _ = p.info
        except: continue
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try: processes.append(p.info)
        except: continue
    return sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:n]

def generate_report(sys_info, cpu_info, mem_info, disks, net_info, battery, processes):
    with open(REPORT_FILE, "w") as f:
        f.write("===== SYSTEM REPORT =====\n\n")
        for k, v in sys_info.items(): f.write(f"{k}: {v}\n")
        f.write("\n===== CPU INFO =====\n")
        for k, v in cpu_info.items():
            if isinstance(v, list):
                for i, core in enumerate(v):
                    f.write(f"Core {i}: {core}%\n")
            else:
                f.write(f"{k}: {v}\n")
        f.write("\n===== MEMORY INFO =====\n")
        for section, values in mem_info.items():
            f.write(f"{section} Memory:\n")
            for k, v in values.items(): f.write(f"  {k}: {v}\n")
        f.write("\n===== DISK INFO =====\n")
        for d in disks:
            for k, v in d.items(): f.write(f"{k}: {v}\n")
            f.write("\n")
        f.write("===== NETWORK INFO =====\n")
        for k, v in net_info.items(): f.write(f"{k}: {v}\n")
        f.write("\n===== BATTERY INFO =====\n")
        for k, v in battery.items(): f.write(f"{k}: {v}\n")
        f.write("\n===== TOP PROCESSES =====\n")
        for p in processes: f.write(f"{p['name']} (PID: {p['pid']}) - {p['cpu_percent']}%\n")

@app.route("/")
def system_report():
    sys_info = {
        "System": platform.system(),
        "Node Name": platform.node(),
        "Release": platform.release(),
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "Boot Time": ctime(psutil.boot_time()),
        "Uptime": get_uptime()
    }

    cpu_info = {
        "Physical Cores": psutil.cpu_count(logical=False),
        "Logical CPUs": psutil.cpu_count(logical=True),
        "Per-Core Usage": psutil.cpu_percent(percpu=True, interval=1),
        "Total CPU Usage": psutil.cpu_percent()
    }

    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    mem_info = {
        "Virtual": {
            "Total": format_bytes(vm.total),
            "Available": format_bytes(vm.available),
            "Used": format_bytes(vm.used),
            "Free": format_bytes(vm.free),
            "Usage %": vm.percent
        },
        "Swap": {
            "Total": format_bytes(swap.total),
            "Used": format_bytes(swap.used),
            "Free": format_bytes(swap.free),
            "Usage %": swap.percent
        }
    }

    disks = []
    for p in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(p.mountpoint)
            disks.append({
                "Device": p.device,
                "Mount": p.mountpoint,
                "FS": p.fstype,
                "Total": format_bytes(usage.total),
                "Used": format_bytes(usage.used),
                "Free": format_bytes(usage.free),
                "Usage": f"{usage.percent}%"
            })
        except:
            continue

    try: ip = socket.gethostbyname(socket.gethostname())
    except: ip = "Unavailable"
    net_io = psutil.net_io_counters()
    net_info = {
        "Hostname": socket.gethostname(),
        "IP Address": ip,
        "Bytes Sent": f"{net_io.bytes_sent / (1024 ** 2):.2f} MB",
        "Bytes Received": f"{net_io.bytes_recv / (1024 ** 2):.2f} MB"
    }

    batt = psutil.sensors_battery()
    battery = {
        "Status": "Battery not available"
    } if not batt else {
        "Percent": f"{batt.percent}%",
        "Plugged In": batt.power_plugged,
        "Time Left (min)": batt.secsleft // 60 if batt.secsleft > 0 else "N/A"
    }

    hardware_status = get_hardware_status()
    working_count = sum(1 for v in hardware_status.values() if v)
    not_working_count = len(hardware_status) - working_count
    hardware_summary = {
        "Working Components": working_count,
        "Not Detected": not_working_count
    }

    processes = top_processes()

    # Generate text report
    generate_report(sys_info, cpu_info, mem_info, disks, net_info, battery, processes)

    return render_template_string(TEMPLATE,
        sys_info=sys_info, cpu_info=cpu_info, mem_info=mem_info,
        disks=disks, net_info=net_info, battery=battery,
        hardware_status=hardware_status, hardware_summary=hardware_summary,
        processes=processes)

@app.route("/download_report")
def download_report():
    return send_file(REPORT_FILE, as_attachment=True) if os.path.exists(REPORT_FILE) else ("Report not found", 404)

@app.route("/download_logs")
def download_logs():
    return send_file(LOG_FILE, as_attachment=True) if os.path.exists(LOG_FILE) else ("Log not found", 404)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>System Report Dashboard</title>
    <meta http-equiv="refresh" content="15">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        .hardware-bar {
            background: #edf2f7;
            padding: 0.75rem 1rem;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 1rem;
            font-weight: 600;
        }
        .hardware-status {
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
        }
        .ok { background-color: #d1fae5; color: #065f46; }
        .fail { background-color: #fee2e2; color: #991b1b; }
    </style>
</head>
<body class="bg-gray-50 text-gray-900">
    <div class="hardware-bar">
        {% for comp, status in hardware_status.items() %}
            <div class="hardware-status {{ 'ok' if status else 'fail' }}">
                {{ comp }}: {{ "✅ Working" if status else "❌ Not Detected" }}
            </div>
        {% endfor %}
    </div>

    <div class="max-w-7xl mx-auto px-4 py-6">
        <h1 class="text-3xl font-bold text-center text-blue-800 mb-6">🧾 System Report Dashboard</h1>

        <div class="flex justify-center gap-4 mb-6">
            <a href="/download_report" class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded shadow">📄 Download Report</a>
            <a href="/download_logs" class="bg-gray-600 hover:bg-gray-700 text-white font-semibold py-2 px-4 rounded shadow">📁 Download Logs</a>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <div class="bg-white rounded-xl shadow p-4 border">
                <h2 class="text-lg font-semibold mb-3">System Info</h2>
                <ul class="text-sm space-y-1">
                    {% for k, v in sys_info.items() %}
                    <li><strong>{{ k }}:</strong> {{ v }}</li>
                    {% endfor %}
                </ul>
            </div>

            <div class="bg-white rounded-xl shadow p-4 border">
                <h2 class="text-lg font-semibold mb-3">Battery Info</h2>
                <ul class="text-sm space-y-1">
                    {% for k, v in battery.items() %}
                    <li><strong>{{ k }}:</strong> {{ v }}</li>
                    {% endfor %}
                </ul>
            </div>

            <div class="bg-white rounded-xl shadow p-4 border">
                <h2 class="text-lg font-semibold mb-3">Hardware Summary</h2>
                <ul class="text-sm space-y-1">
                    {% for k, v in hardware_summary.items() %}
                    <li><strong>{{ k }}:</strong> {{ v }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-white rounded-xl shadow p-4 border">
                <h2 class="text-lg font-semibold mb-3">CPU Info</h2>
                <ul class="text-sm">
                    <li><strong>Physical Cores:</strong> {{ cpu_info['Physical Cores'] }}</li>
                    <li><strong>Logical CPUs:</strong> {{ cpu_info['Logical CPUs'] }}</li>
                    {% for core in cpu_info['Per-Core Usage'] %}
                    <li><strong>Core {{ loop.index0 }}:</strong> {{ core }}%</li>
                    {% endfor %}
                    <li><strong>Total CPU Usage:</strong> {{ cpu_info['Total CPU Usage'] }}%</li>
                </ul>
                <hr class="my-3">
                <h3 class="text-sm font-bold text-blue-700 mb-2">Top 5 Processes</h3>
                <ul class="text-sm">
                    {% for proc in processes %}
                    <li>{{ proc.name }} (PID: {{ proc.pid }}) - {{ proc.cpu_percent }}%</li>
                    {% endfor %}
                </ul>
            </div>

            <div class="bg-white rounded-xl shadow p-4 border">
                <h2 class="text-lg font-semibold mb-3">Memory Info</h2>
                {% for title, values in mem_info.items() %}
                    <h3 class="font-bold text-blue-600 mt-3">{{ title }} Memory</h3>
                    <ul class="text-sm">
                    {% for k, v in values.items() %}
                        <li><strong>{{ k }}:</strong> {{ v }}</li>
                    {% endfor %}
                    </ul>
                {% endfor %}
            </div>
        </div>

        <div class="bg-white rounded-xl shadow p-4 border mt-6">
            <h2 class="text-lg font-semibold mb-3">Disk Info</h2>
            <div class="grid sm:grid-cols-2 gap-4 text-sm">
                {% for disk in disks %}
                <div class="border rounded p-2">
                    <p><strong>Device:</strong> {{ disk.Device }}</p>
                    <p><strong>Mount:</strong> {{ disk.Mount }}</p>
                    <p><strong>FS:</strong> {{ disk.FS }}</p>
                    <p><strong>Total:</strong> {{ disk.Total }}</p>
                    <p><strong>Used:</strong> {{ disk.Used }}</p>
                    <p><strong>Free:</strong> {{ disk.Free }}</p>
                    <p><strong>Usage:</strong> {{ disk.Usage }}</p>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <div class="bg-white rounded-xl shadow p-4 border">
                <h2 class="text-lg font-semibold mb-3">Network Info</h2>
                <ul class="text-sm">
                    {% for k, v in net_info.items() %}
                    <li><strong>{{ k }}:</strong> {{ v }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        Timer(1, lambda: webbrowser.open("http://127.0.0.1:5000/")).start()
    app.run(debug=True)
