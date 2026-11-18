"""Offline, non-invasive GitHub Actions runner-capacity measurement.

CLI:
    python scripts/audit_free_runner.py before
    python scripts/audit_free_runner.py after
    python scripts/audit_free_runner.py compare before.json after.json

No credentials, sensitive paths, gated data, model calls or downloads.
"""
from __future__ import annotations
import json
import os
import shutil
import sys

GIB = 1024**3
# The OFFICIAL PLE recommendations are 6 CPUs + 16.25 GiB memory plus
# 10 GiB base and about 17 GiB world images, plus additional task data.
MIN_FULL_CPUS = 6
MIN_FULL_RAM_GIB = 16.25
# 45 GiB is only an advisory scratch safety budget, not an official spec.
ADVISORY_DISK_GIB = 45


def current_capacity():
    cpu = os.cpu_count() or 0
    try:
        cpu = len(os.sched_getaffinity(0))
    except (AttributeError, OSError):
        pass
    ram_gib = 0
    try:
        with open("/proc/meminfo", encoding="utf-8") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    ram_gib = round(int(line.split()[1]) * 1024 / GIB, 2)
                    break
    except (OSError, ValueError, IndexError):
        pass
    space = shutil.disk_usage("/")
    return {
        "cpu_count": int(cpu),
        "physical_ram_gib": ram_gib,
        "disk_free_gib": round(space.free / GIB, 2),
        "disk_total_gib": round(space.total / GIB, 2),
        "docker_executable_found": bool(shutil.which("docker")),
        "is_github_hosted": os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted",
    }


def compare(before, after):
    for entry in (before, after):
        if not isinstance(entry, dict) or not all(
            name in entry for name in ("cpu_count", "physical_ram_gib", "disk_free_gib")
        ):
            raise ValueError("Invalid resource snapshot")
    enough_cpu = after["cpu_count"] >= MIN_FULL_CPUS
    enough_ram = after["physical_ram_gib"] >= MIN_FULL_RAM_GIB
    enough_disk = after["disk_free_gib"] >= ADVISORY_DISK_GIB
    return {
        "before": before, "after": after,
        "disk_reclaimed_gib": round(
            after["disk_free_gib"] - before["disk_free_gib"], 2
        ),
        "cpu_meets_full_ple_guideline": enough_cpu,
        "ram_meets_full_ple_guideline": enough_ram,
        "disk_meets_advisory_scratch_budget": enough_disk,
        "full_ple_runner_ready": (
            enough_cpu and enough_ram and enough_disk
            and bool(after["docker_executable_found"])
        ),
        "could_attempt_one_small_task": (
            enough_disk and after["cpu_count"] >= 4
            and after["physical_ram_gib"] >= 12
        ),
        "evaluator_trial_verified": False,
        "note": (
            "Single-task eligibility is only a resource estimate, not proof "
            "that Docker, the task world, judge or sponsored model will work."
        ),
    }


def main(argv):
    if argv == ["before"] or argv == ["after"]:
        print(json.dumps(current_capacity(), indent=2))
        return 0
    if len(argv) == 3 and argv[0] == "compare":
        with open(argv[1], encoding="utf-8") as f:
            before = json.load(f)
        with open(argv[2], encoding="utf-8") as f:
            after = json.load(f)
        print(json.dumps(compare(before, after), indent=2))
        return 0
    print("Usage: audit_free_runner.py before|after|compare before.json after.json")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
