"""Process-memory sampling for local case measurement; no product dependency."""

from __future__ import annotations

import ctypes
import os
import statistics
import threading
import time
from pathlib import Path


def process_memory(pid: int) -> dict:
    """Return current RSS/private bytes and lifetime OS RSS peak when available."""
    if os.name == "nt":
        from ctypes import wintypes

        size_t = ctypes.c_size_t

        class Counters(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", size_t), ("WorkingSetSize", size_t),
                ("QuotaPeakPagedPoolUsage", size_t), ("QuotaPagedPoolUsage", size_t),
                ("QuotaPeakNonPagedPoolUsage", size_t), ("QuotaNonPagedPoolUsage", size_t),
                ("PagefileUsage", size_t), ("PeakPagefileUsage", size_t),
                ("PrivateUsage", size_t),
            ]

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        psapi.GetProcessMemoryInfo.argtypes = [
            wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD,
        ]
        handle = kernel.OpenProcess(0x0400 | 0x0010, False, pid)
        if not handle:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            counters = Counters()
            counters.cb = ctypes.sizeof(counters)
            if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
                raise ctypes.WinError(ctypes.get_last_error())
            return {
                "rss_bytes": counters.WorkingSetSize,
                "private_bytes": counters.PrivateUsage,
                "os_lifetime_peak_rss_bytes": counters.PeakWorkingSetSize,
            }
        finally:
            kernel.CloseHandle(handle)
    values = {}
    for line in Path(f"/proc/{pid}/status").read_text().splitlines():
        if line.startswith(("VmRSS:", "VmHWM:")):
            key, amount, *_ = line.split()
            values[key.rstrip(":")] = int(amount) * 1024
    if "VmRSS" not in values:
        raise RuntimeError("Current process RSS is unavailable on this platform")
    return {
        "rss_bytes": values["VmRSS"], "private_bytes": None,
        "os_lifetime_peak_rss_bytes": values.get("VmHWM"),
    }


class MemorySampler:
    def __init__(self, pid: int, interval: float = 0.05):
        self.pid = pid
        self.interval = interval
        self.samples = []
        self.errors = []
        self.started = time.perf_counter()
        self.stopping = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def snapshot(self):
        sample = {"at_ms": (time.perf_counter() - self.started) * 1000,
                  "epoch_ms": time.time() * 1000,
                  **process_memory(self.pid)}
        self.samples.append(sample)
        return sample

    def _run(self):
        while not self.stopping.wait(self.interval):
            try:
                self.snapshot()
            except (OSError, RuntimeError) as error:
                self.errors.append(str(error))
                return

    def start(self):
        self.snapshot()
        self.thread.start()

    def stop(self):
        self.stopping.set()
        self.thread.join(timeout=2)
        self.snapshot()

    def summary(self, baseline_count: int = 1):
        baseline = self.samples[:baseline_count]
        rss = [sample["rss_bytes"] for sample in self.samples]
        base_rss = statistics.median(sample["rss_bytes"] for sample in baseline)
        private = [s["private_bytes"] for s in self.samples if s["private_bytes"] is not None]
        return {
            "sample_interval_ms": self.interval * 1000,
            "sample_count": len(self.samples),
            "baseline_sample_count": len(baseline),
            "baseline_rss_bytes": base_rss,
            "sampled_peak_rss_bytes": max(rss),
            "sampled_peak_delta_bytes": max(rss) - base_rss,
            "end_rss_bytes": self.samples[-1]["rss_bytes"],
            "sampled_peak_private_bytes": max(private) if private else None,
            "os_lifetime_peak_rss_bytes": self.samples[-1]["os_lifetime_peak_rss_bytes"],
            "sampling_errors": self.errors,
        }
