"""
Computex 2026 — Pre-Show Verification
======================================
Run once before the demo to confirm every model is pulled and every
backend is ready.  Exits with code 0 only if all required checks pass.

Usage:
    python demo/setup.py
    python demo/setup.py --host localhost --port 13305
"""

import argparse
import sys

import requests

# ---------------------------------------------------------------------------
# ANSI colours
# ---------------------------------------------------------------------------
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"

TIMEOUT = 15


def c(text, *codes):
    return f"{''.join(codes)}{text}{RESET}"


def ok(label, detail=""):
    d = f"  {c(detail, DIM)}" if detail else ""
    print(f"   {c('✔', GREEN)}  {c(label, WHITE)}{d}")


def warn(label, detail=""):
    d = f"  {c(detail, DIM)}" if detail else ""
    print(f"   {c('⚠', YELLOW)}  {c(label, WHITE)}{d}")


def err(label, detail=""):
    d = f"  {c(detail, DIM)}" if detail else ""
    print(f"   {c('✘', RED)}  {c(label, WHITE)}{d}")


def header(text):
    print()
    print(c(f"  {text}", CYAN, BOLD))
    print(c("  " + "─" * 56, DIM))


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def check_health(base_url):
    try:
        r = requests.get(f"{base_url}/v1/health", timeout=5)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False


def get_models(base_url):
    try:
        r = requests.get(f"{base_url}/v1/models", timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        return {m["id"] for m in data.get("data", [])}
    except Exception:
        return set()


def get_system_info(base_url):
    try:
        r = requests.get(f"{base_url}/v1/system-info", timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}


def get_max_loaded_models(base_url):
    try:
        r = requests.get(f"{base_url}/internal/config", timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json().get("max_loaded_models")
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Required models (grouped by act)
# ---------------------------------------------------------------------------

REQUIRED_MODELS = [
    # Act 1
    ("Whisper-Large-v3-Turbo", "Act 1  語音辨識  NPU"),
    # Act 2
    ("DeepSeek-R1-Distill-Qwen-1.5B-NPU",    "Act 2  Hybrid LLM  NPU"),
    ("DeepSeek-R1-Distill-Qwen-1.5B-Hybrid", "Act 2  Hybrid LLM  Hybrid"),
    # Act 3
    ("kokoro-v1",  "Act 3  TTS  CPU"),
    # Act 4
    ("SD-Turbo",   "Act 4  Image Gen  890M"),
    # Act 5
    ("Qwen3-0.6B-GGUF",               "Act 5  Debate  0.38 GB"),
    ("Qwen3-1.7B-GGUF",               "Act 5  Debate  1.06 GB"),
    ("LFM2-1.2B-GGUF",                "Act 5  Debate  0.73 GB"),
    ("Llama-3.2-1B-Instruct-GGUF",    "Act 5  Debate  0.83 GB"),
    ("Phi-4-mini-instruct-GGUF",      "Act 5  Debate  2.49 GB"),
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if sys.platform == "win32":
        import os
        os.system("")
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Computex demo pre-show verification")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=13305)
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"

    print()
    print(c("  Computex 2026 — Pre-Show Checklist", WHITE, BOLD))
    print(c(f"  Server : {base_url}", DIM))

    failures = 0

    # ── 1. Server health ──────────────────────────────────────────────────
    header("Server")
    if check_health(base_url):
        ok("Lemonade server is running")
    else:
        err("Server not reachable", f"Start with: lemonade launch")
        print()
        print(c("  Cannot continue without a running server.", RED))
        sys.exit(1)

    # ── 2. Server config ─────────────────────────────────────────────────
    header("Server Config")
    slots = get_max_loaded_models(base_url)
    if slots is None:
        warn("max_loaded_models", "could not read /internal/config")
    elif slots >= 9:
        ok(f"max_loaded_models = {slots}", "Act 5 辯論需要 9")
    else:
        err(f"max_loaded_models = {slots}  (需要 9)",
            "重啟：lemonade-server serve --max-loaded-models 9")
        failures += 1

    # ── 3. Models ─────────────────────────────────────────────────────────
    header("Models")
    available = get_models(base_url)

    if not available:
        warn("Could not fetch model list from /v1/models — checking anyway")

    for model_id, label in REQUIRED_MODELS:
        if available and model_id in available:
            ok(model_id, label)
        elif not available:
            warn(model_id, f"{label}  (could not verify)")
        else:
            err(model_id, f"{label}  →  run: lemonade pull {model_id}")
            failures += 1

    # ── 4. Backend states ─────────────────────────────────────────────────
    header("Backends")
    info    = get_system_info(base_url)
    recipes = info.get("recipes", {})

    # NPU (ryzenai-llm)
    npu_state = (
        recipes.get("ryzenai-llm", {})
               .get("backends", {})
               .get("npu", {})
               .get("state", "unknown")
    )
    _label_state("NPU  (ryzenai-llm)", npu_state, "Act 1 + 2")

    # Vulkan GPU (llamacpp)
    vulkan_state = (
        recipes.get("llamacpp", {})
               .get("backends", {})
               .get("vulkan", {})
               .get("state", "unknown")
    )
    _label_state("GPU  (llamacpp / Vulkan)", vulkan_state, "Act 5")

    # ROCm (stable-diffusion)
    rocm_state = (
        recipes.get("stable-diffusion", {})
               .get("backends", {})
               .get("rocm", {})
               .get("state", "unknown")
    )
    sd_cpu_state = (
        recipes.get("stable-diffusion", {})
               .get("backends", {})
               .get("cpu", {})
               .get("state", "unknown")
    )
    if rocm_state in ("installed", "supported"):
        _label_state("Image  (stable-diffusion / ROCm)", rocm_state, "Act 4  preferred")
    else:
        _label_state("Image  (stable-diffusion / CPU)", sd_cpu_state,
                     "Act 4  ROCm unavailable — will use CPU fallback")

    # ── Summary ───────────────────────────────────────────────────────────
    print()
    if failures == 0:
        print(c("  ★  All checks passed — ready to demo!", GREEN, BOLD))
    else:
        print(c(f"  ✘  {failures} model(s) missing — pull them before starting.", RED, BOLD))

    print()
    sys.exit(0 if failures == 0 else 1)


def _label_state(label, state, note=""):
    n = f"  {c(note, DIM)}" if note else ""
    if state in ("installed", "supported"):
        ok(label, note)
    elif state in ("installable",):
        warn(f"{label}  (installable){n}")
    elif state == "unknown":
        warn(f"{label}  (state unknown){n}")
    else:
        err(f"{label}  [{state}]{n}")


if __name__ == "__main__":
    main()
