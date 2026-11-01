import csv
import time
from datetime import datetime

import psutil

PROCESS_NAME = "python.exe"
OUTPUT_FILE = "cpu_ram_log.csv"
INTERVAL_SECONDS = 2


def main():
    processes = []

    for process in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            name = process.info["name"] or ""
            command = " ".join(process.info["cmdline"] or [])

            if name.lower() == PROCESS_NAME and "uvicorn" in command.lower():
                processes.append(psutil.Process(process.info["pid"]))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not processes:
        print("FastAPI/Uvicorn process not found. Start the API first.")
        return

    print("Monitoring FastAPI processes. Press Ctrl+C to stop.")
    for process in processes:
        process.cpu_percent(interval=None)

    try:
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "PID", "CPU_Percent", "RAM_MB"])

            while True:
                timestamp = datetime.now().isoformat(timespec="seconds")

                for process in processes:
                    try:
                        cpu = process.cpu_percent(interval=None)
                        ram_mb = process.memory_info().rss / (1024 * 1024)

                        writer.writerow(
                            [
                                timestamp,
                                process.pid,
                                round(cpu, 2),
                                round(ram_mb, 2),
                            ]
                        )
                        file.flush()

                        print(
                            f"{timestamp} | PID={process.pid} | "
                            f"CPU={cpu:.2f}% | RAM={ram_mb:.2f} MB"
                        )
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                time.sleep(INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print(f"\nResults saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
