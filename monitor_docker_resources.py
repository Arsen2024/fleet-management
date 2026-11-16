import csv
import subprocess
import time
from datetime import datetime

CONTAINERS = [
    "fleet-management-fleet1-1",
    "fleet-management-fleet2-1",
    "fleet-management-fleet3-1",
]

OUTPUT_FILE = "docker_cpu_ram_log.csv"
INTERVAL_SECONDS = 2


def main():
    print("Monitoring Docker containers. Press Ctrl+C to stop.")

    try:
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "Timestamp",
                    "Container",
                    "CPU_Percent",
                    "RAM_Usage",
                    "RAM_Limit",
                    "RAM_Percent",
                ]
            )

            while True:
                timestamp = datetime.now().isoformat(timespec="seconds")

                result = subprocess.run(
                    [
                        "docker",
                        "stats",
                        "--no-stream",
                        "--format",
                        "{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}}",
                        *CONTAINERS,
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                for line in result.stdout.strip().splitlines():
                    parts = line.split(",")

                    if len(parts) != 4:
                        continue

                    name, cpu, memory, memory_percent = parts

                    ram_usage, ram_limit = memory.split(" / ")

                    writer.writerow(
                        [
                            timestamp,
                            name,
                            cpu,
                            ram_usage,
                            ram_limit,
                            memory_percent,
                        ]
                    )

                    print(
                        f"{timestamp} | {name} | "
                        f"CPU={cpu} | RAM={ram_usage} | "
                        f"RAM={memory_percent}"
                    )

                file.flush()
                time.sleep(INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print(f"\nResults saved to {OUTPUT_FILE}")

    except subprocess.CalledProcessError as error:
        print("Docker monitoring error:", error)


if __name__ == "__main__":
    main()
