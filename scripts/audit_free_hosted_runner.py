"""Read-only feasibility audit for free, ephemeral hosted PLE runners.

No private data, no model calls, no Hugging Face downloads, no Docker images
pulled, and no writes to the participant's personal computer.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

GIB = 1024 ** 3


def full_dev_feasibility(cpu: int, memory_gib: float, free_gib: float, docker: bool) -> dict:
    # Based on official PLE dev runner: 6 CPUs and 16.25 GiB
    # The 30 GiB free disk target is conservative and ADVISORY, NOT a
    # declared PLE minimum: official kit states 10 GiB base + world images.
    minimum = {"cpu": cpu >= 6, "memory": memory_gib >= 16.25,
               "advisory_disk": free_gib >= 30, "docker": docker}
    return {
        "requirements_met": minimum,
        "full_29_task_runner_plausible": all(minimum.values()),
        "single_lightweight_task_possible": "unverified; task-specific images and memory must be checked",
        "official_submission_accepted": False,
        "genuine_artifacts_present": False,
        "no_billing_or_model_inference_performed": True,
    }


def available_ram_gib() -> float:
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1]) / (1024 ** 2)
    except (ValueError, IndexError, OSError):
        pass
    return 0.0


def docker_ready() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        p = subprocess.run(["docker", "info", "--format", "{{.ServerVersion}}"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=8, check=False)
        return p.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args(argv)
    cpu = os.cpu_count() or 0
    ram = round(available_ram_gib(), 2)
    disk = round(shutil.disk_usage("/").free / GIB, 2)
    docker = docker_ready()
    result = {
        "compute": "ephemeral CI runner (NOT user's PC)",
        "cpu": cpu,
        "memory_gib": ram,
        "free_disk_gib": disk,
        "docker_available": docker,
        "analysis": full_dev_feasibility(cpu, ram, disk, docker),
    }
    out = json.dumps(result, indent=2) + "\n"
    print(out, end="")
    if args.output_json:
        args.output_json.write_text(out, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
