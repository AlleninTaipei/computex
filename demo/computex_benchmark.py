"""
Lemonade COMPUTEX Demo: AMD GPU+NPU Speed Benchmark
====================================================

Automatically detects available hardware and runs the best comparison:

  • AMD XDNA 2 NPU (Ryzen AI 300+):
        CPU model  →  NPU model  →  GPU+NPU Hybrid model

  • AMD GPU / iGPU only (Radeon, Vulkan):
        CPU (x86)  →  GPU (Vulkan / Radeon)

Usage:
    python demo/computex_benchmark.py
    python demo/computex_benchmark.py --model Qwen3-4B-GGUF      # GPU mode model
    python demo/computex_benchmark.py --skip-install              # skip backend install
    python demo/computex_benchmark.py --skip-pull                 # skip model download
    python demo/computex_benchmark.py --host localhost --port 13305

Requirements:
    pip install openai requests
"""

import argparse
import sys
import time
import requests

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not found. Run: pip install openai requests")
    sys.exit(1)

# ---------------------------------------------------------------------------
# ANSI colors (Windows 10+ and all UNIX terminals)
# ---------------------------------------------------------------------------
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
WHITE = "\033[97m"

TIMEOUT_INSTALL = 600   # backend binary download
TIMEOUT_PULL = 600      # model download (can be large)
TIMEOUT_LOAD = 600      # model load (includes auto-download on first run)
TIMEOUT_INFER = 180     # inference call
TIMEOUT_DEFAULT = 30

# ---------------------------------------------------------------------------
# NPU benchmark: same model family in CPU / NPU / Hybrid variants
# ---------------------------------------------------------------------------
NPU_FAMILIES = {
    "DeepSeek-R1-Distill-Qwen-7B": {
        "CPU":    "DeepSeek-R1-Distill-Qwen-7B-CPU",
        "NPU":    "DeepSeek-R1-Distill-Qwen-7B-NPU",
        "Hybrid": "DeepSeek-R1-Distill-Qwen-7B-Hybrid",
    },
    "DeepSeek-R1-Distill-Llama-8B": {
        "CPU":    "DeepSeek-R1-Distill-Llama-8B-CPU",
        "NPU":    "DeepSeek-R1-Distill-Llama-8B-NPU",
        "Hybrid": "DeepSeek-R1-Distill-Llama-8B-Hybrid",
    },
    "Phi-4-mini-instruct": {
        "CPU":    "Phi-4-mini-instruct-CPU",
        "NPU":    "Phi-4-mini-instruct-NPU",
        "Hybrid": "Phi-4-mini-instruct-Hybrid",
    },
    "Qwen3-8B": {
        "CPU":    "Qwen3-8B-Hybrid",   # use Hybrid as CPU stand-in if no pure-CPU variant
        "NPU":    "Qwen3-8B-Hybrid",
        "Hybrid": "Qwen3-8B-Hybrid",
    },
}
DEFAULT_NPU_FAMILY = "DeepSeek-R1-Distill-Qwen-7B"

# ---------------------------------------------------------------------------
# GPU-only benchmark: same GGUF model loaded with cpu vs vulkan backend
# ---------------------------------------------------------------------------
GPU_MODELS = {
    "Qwen3-1.7B-GGUF": "Qwen3-1.7B-GGUF",
    "Qwen3-4B-GGUF":   "Qwen3-4B-GGUF",
    "Qwen3-8B-GGUF":   "Qwen3-8B-GGUF",
}
DEFAULT_GPU_MODEL = "Qwen3-4B-GGUF"

GPU_TARGETS = [
    {"label": "CPU",    "backend": "cpu",    "color": YELLOW},
    {"label": "GPU",    "backend": "vulkan", "color": GREEN},
]

# ---------------------------------------------------------------------------
# Benchmark prompt
# ---------------------------------------------------------------------------
DEFAULT_PROMPT = (
    "You are a helpful AI assistant running locally on AMD hardware. "
    "Briefly explain (in 4-5 sentences) why edge AI inference on AMD "
    "silicon is important for privacy and performance."
)

COMPUTE_COLORS = {"CPU": YELLOW, "NPU": BLUE, "Hybrid": GREEN, "GPU": GREEN}
COMPUTE_ICONS  = {"CPU": "🖥 ", "NPU": "⚡", "Hybrid": "🚀", "GPU": "🎮"}


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _c(text, *codes):
    return f"{''.join(codes)}{text}{RESET}"


def _header(text):
    w = 70
    print()
    print(_c("═" * w, CYAN))
    print(_c(f"  {text}", CYAN, BOLD))
    print(_c("═" * w, CYAN))


def _step(icon, label, detail=""):
    d = f"  {_c(detail, DIM)}" if detail else ""
    print(f"\n  {icon}  {_c(label, BOLD)}{d}")


def _ok(msg):   print(f"     {_c('✔', GREEN)}  {msg}")
def _warn(msg): print(f"     {_c('⚠', YELLOW)}  {msg}")
def _err(msg):  print(f"     {_c('✘', RED)}  {msg}")


def _bar(value, max_value, width=30, color=GREEN):
    filled = int(round(width * min(value / max_value, 1.0))) if max_value > 0 else 0
    return _c("█" * filled + "░" * (width - filled), color)


# ---------------------------------------------------------------------------
# Server helpers
# ---------------------------------------------------------------------------

def get(base_url, path, timeout=TIMEOUT_DEFAULT):
    r = requests.get(f"{base_url}{path}", timeout=timeout)
    r.raise_for_status()
    return r.json()


def post(base_url, path, body, timeout=TIMEOUT_DEFAULT):
    r = requests.post(
        f"{base_url}{path}",
        json=body,
        timeout=timeout,
    )
    return r.status_code, r.json() if r.content else {}


def check_server(base_url):
    try:
        r = requests.get(f"{base_url}/v1/health", timeout=5)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False


def get_system_info(base_url):
    try:
        return get(base_url, "/v1/system-info", timeout=10)
    except Exception:
        return {}


def detect_scenario(base_url):
    """
    Returns one of:
      "npu"   — XDNA 2 NPU is supported/installed (Ryzen AI 300+)
      "gpu"   — Vulkan GPU is available but no NPU
      "cpu"   — CPU only
    Also returns the full recipes dict.
    """
    info = get_system_info(base_url)
    recipes = info.get("recipes", {})

    # Check NPU (ryzenai-llm:npu)
    npu_state = (
        recipes.get("ryzenai-llm", {})
               .get("backends", {})
               .get("npu", {})
               .get("state", "unsupported")
    )
    if npu_state in ("installed", "installable", "supported"):
        return "npu", recipes

    # Check Vulkan GPU
    vulkan_state = (
        recipes.get("llamacpp", {})
               .get("backends", {})
               .get("vulkan", {})
               .get("state", "unsupported")
    )
    if vulkan_state in ("installed", "installable", "supported"):
        return "gpu", recipes

    return "cpu", recipes


def install_backend(base_url, recipe, backend):
    """Install a backend binary. Returns True on success."""
    code, body = post(
        base_url, "/v1/install",
        {"recipe": recipe, "backend": backend},
        timeout=TIMEOUT_INSTALL,
    )
    if code == 200:
        return True
    _err(f"Install {recipe}:{backend} failed ({code}): {body.get('error', body)}")
    return False


def pull_model(base_url, model_id):
    """Pull (download) a model. Returns True on success."""
    code, body = post(
        base_url, "/v1/pull",
        {"model": model_id},
        timeout=TIMEOUT_PULL,
    )
    if code == 200:
        return True
    _err(f"Pull {model_id} failed ({code}): {body.get('error', body)}")
    return False


def load_model(base_url, model_id, llamacpp_backend=None):
    """Load a model, optionally forcing a specific llamacpp backend."""
    body = {"model_name": model_id}
    if llamacpp_backend:
        body["llamacpp_backend"] = llamacpp_backend
    code, resp = post(base_url, "/v1/load", body, timeout=TIMEOUT_LOAD)
    if code == 200:
        return True
    _err(f"Load {model_id} failed ({code}): {resp.get('error', resp)}")
    return False


def unload_model(base_url, model_id):
    try:
        post(base_url, "/v1/unload", {"model": model_id}, timeout=TIMEOUT_DEFAULT)
    except Exception:
        pass


def get_stats(base_url):
    try:
        return get(base_url, "/v1/stats", timeout=10)
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Single benchmark run
# ---------------------------------------------------------------------------

def run_benchmark(client, base_url, model_id, prompt, label, color):
    """
    Run one inference pass, return result dict or None on failure.
    Assumes the model is already loaded.
    """
    icon = COMPUTE_ICONS.get(label, "  ")
    tag = _c(f"[{label}]", color, BOLD)
    print(f"\n  {tag} {icon} Inferring ...")

    wall_start = time.perf_counter()
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256,
            stream=False,
            timeout=TIMEOUT_INFER,
        )
    except Exception as exc:
        _err(f"Inference failed: {exc}")
        return None
    wall_secs = time.perf_counter() - wall_start

    stats = get_stats(base_url)
    tps = stats.get("tokens_per_second", 0.0)
    ttft = stats.get("time_to_first_token", 0.0)
    output_tokens = stats.get("output_tokens", 0)

    if tps == 0 and output_tokens > 0:
        tps = output_tokens / wall_secs

    if response.choices:
        text = (response.choices[0].message.content or "")
        preview = text[:100].replace("\n", " ") + ("…" if len(text) > 100 else "")
        print(f"       {_c(preview, DIM)}")

    _ok(
        f"Wall: {wall_secs:.1f}s  |  "
        f"TPS: {_c(f'{tps:.1f}', color, BOLD)}  |  "
        f"TTFT: {ttft*1000:.0f} ms  |  "
        f"Tokens: {output_tokens}"
    )
    return {"label": label, "model": model_id, "tps": tps,
            "ttft": ttft, "output_tokens": output_tokens, "wall_secs": wall_secs}


# ---------------------------------------------------------------------------
# Results table
# ---------------------------------------------------------------------------

def print_results_table(results, title):
    _header(title)
    if not results:
        _warn("No results.")
        return

    max_tps = max((r["tps"] for r in results), default=1.0) or 1.0
    COL = {"label": 8, "model": 36, "tps": 8, "ttft": 10, "bar": 30}

    col_label = COL["label"]
    col_model = COL["model"]
    col_tps   = COL["tps"]
    col_ttft  = COL["ttft"]

    hdr = (
        f"  {'Mode':<{col_label}}  "
        f"{'Model':<{col_model}}  "
        f"{'TPS':>{col_tps}}  "
        f"{'TTFT (ms)':>{col_ttft}}  Throughput"
    )
    print(_c(hdr, WHITE, BOLD))
    print(_c("  " + "─" * 88, DIM))

    baseline = None
    for r in results:
        color = COMPUTE_COLORS.get(r["label"], WHITE)
        icon  = COMPUTE_ICONS.get(r["label"], "  ")
        tps   = r["tps"]
        ttft_ms = r["ttft"] * 1000

        if baseline is None and tps > 0:
            baseline = tps

        speedup = ""
        if baseline and tps > 0 and r["label"] != "CPU":
            speedup = _c(f"  ×{tps/baseline:.1f}", GREEN, BOLD)

        bar = _bar(tps, max_tps, width=COL["bar"], color=color)
        label_str  = r["label"]
        model_str  = r["model"][:col_model]
        tps_str    = _c(f"{tps:>{col_tps}.1f}", color, BOLD)
        label_col  = _c(f"{label_str:<{col_label}}", color, BOLD)

        print(f"  {icon} {label_col}  {model_str:<{col_model}}  {tps_str}  "
              f"{ttft_ms:>{col_ttft}.0f}  {bar}{speedup}")

    print(_c("  " + "─" * 88, DIM))

    best = max(results, key=lambda r: r["tps"])
    best_color = COMPUTE_COLORS.get(best["label"], WHITE)
    print(
        f"\n  {_c('★  Winner:', GREEN, BOLD)}  "
        f"{_c(best['label'], best_color, BOLD)}  "
        f"({best['tps']:.1f} tokens/sec)"
    )
    if baseline and best["tps"] > baseline and best["label"] != "CPU":
        speedup_x = best["tps"] / baseline
        print(
            f"  {_c('Speedup vs CPU:', CYAN)}  "
            f"{_c(f'{speedup_x:.1f}x', CYAN, BOLD)} faster"
        )
    print()


# ---------------------------------------------------------------------------
# NPU scenario: CPU model → NPU model → Hybrid model
# ---------------------------------------------------------------------------

def run_npu_benchmark(base_url, client, family_name, family, prompt, skip_pull):
    _step("📥", "Pulling NPU/Hybrid models", "first run may take a few minutes")

    available = {}
    for target, model_id in family.items():
        print(f"\n     {target}  →  {_c(model_id, DIM)}")
        if skip_pull:
            available[target] = model_id
            _ok("(skipped pull)")
            continue
        if pull_model(base_url, model_id):
            available[target] = model_id
            _ok("ready")
        else:
            _warn(f"Skipping {target}")

    _step("🏁", "Running inference", "CPU → NPU → Hybrid")
    results = []
    for target in ["CPU", "NPU", "Hybrid"]:
        model_id = available.get(target)
        if not model_id:
            _warn(f"Skipping {target}")
            continue
        color = COMPUTE_COLORS.get(target, WHITE)
        r = run_benchmark(client, base_url, model_id, prompt, target, color)
        if r:
            results.append(r)
        unload_model(base_url, model_id)
        time.sleep(1)

    print_results_table(results, f"AMD XDNA 2 NPU — {family_name}")
    return results


# ---------------------------------------------------------------------------
# GPU scenario: same GGUF model, CPU backend vs Vulkan backend
# ---------------------------------------------------------------------------

def run_gpu_benchmark(base_url, client, model_id, prompt, skip_install, skip_pull):
    _step("📦", "Installing llamacpp backends", "cpu + vulkan")

    if not skip_install:
        for backend in ["cpu", "vulkan"]:
            print(f"\n     Installing llamacpp:{backend} ...")
            if install_backend(base_url, "llamacpp", backend):
                _ok(f"llamacpp:{backend} installed")

    if not skip_pull:
        _step("📥", "Pulling GGUF model", model_id)
        if not pull_model(base_url, model_id):
            _err("Could not pull model. Aborting GPU benchmark.")
            return []
        _ok(f"{model_id} ready")

    _step("🏁", "Running inference", "CPU x86  →  GPU Vulkan (Radeon)")
    results = []

    for target in GPU_TARGETS:
        label   = target["label"]
        backend = target["backend"]
        color   = target["color"]

        print(f"\n  Loading with backend={_c(backend, BOLD)} ...")
        if not load_model(base_url, model_id, llamacpp_backend=backend):
            _warn(f"Could not load with {backend}, skipping")
            continue

        r = run_benchmark(client, base_url, model_id, prompt, label, color)
        if r:
            results.append(r)
        unload_model(base_url, model_id)
        time.sleep(1)

    print_results_table(results, f"AMD Radeon (Vulkan) — {model_id}")
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if sys.platform == "win32":
        import os
        os.system("")   # enable VT100 on Windows
        # Force UTF-8 output so Unicode box-drawing chars render correctly
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Lemonade COMPUTEX Benchmark — auto-detects AMD NPU or GPU"
    )
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=13305)
    parser.add_argument(
        "--npu-model", default=DEFAULT_NPU_FAMILY,
        choices=list(NPU_FAMILIES.keys()),
        metavar="FAMILY",
        help=f"NPU model family (default: {DEFAULT_NPU_FAMILY}). "
             f"Choices: {', '.join(NPU_FAMILIES)}"
    )
    parser.add_argument(
        "--gpu-model", default=DEFAULT_GPU_MODEL,
        choices=list(GPU_MODELS.keys()),
        metavar="MODEL",
        help=f"GGUF model for GPU benchmark (default: {DEFAULT_GPU_MODEL}). "
             f"Choices: {', '.join(GPU_MODELS)}"
    )
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--skip-install", action="store_true",
                        help="Skip backend install step")
    parser.add_argument("--skip-pull", action="store_true",
                        help="Skip model download step")
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"

    # ── Banner ────────────────────────────────────────────────────────────
    print()
    print(_c("  ██╗     ███████╗███╗   ███╗ ██████╗ ███╗   ██╗ █████╗ ██████╗ ███████╗", CYAN))
    print(_c("  ██║     ██╔════╝████╗ ████║██╔═══██╗████╗  ██║██╔══██╗██╔══██╗██╔════╝", CYAN))
    print(_c("  ██║     █████╗  ██╔████╔██║██║   ██║██╔██╗ ██║███████║██║  ██║█████╗  ", CYAN))
    print(_c("  ██║     ██╔══╝  ██║╚██╔╝██║██║   ██║██║╚██╗██║██╔══██║██║  ██║██╔══╝  ", CYAN))
    print(_c("  ███████╗███████╗██║ ╚═╝ ██║╚██████╔╝██║ ╚████║██║  ██║██████╔╝███████╗", CYAN))
    print(_c("  ╚══════╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═════╝ ╚══════╝", CYAN))
    print()
    print(_c("  AMD Hybrid Inference Benchmark  —  COMPUTEX 2025", WHITE, BOLD))
    print(_c(f"  Server : {base_url}", DIM))

    # ── Check server ──────────────────────────────────────────────────────
    _step("🔌", "Checking Lemonade server", base_url)
    if not check_server(base_url):
        _err(
            f"Cannot reach server at {base_url}. "
            "Start it first with: lemonade launch"
        )
        sys.exit(1)
    _ok("Server is running")

    # ── Detect hardware ───────────────────────────────────────────────────
    _step("🔍", "Detecting hardware")
    scenario, recipes = detect_scenario(base_url)

    if scenario == "npu":
        print(f"     {_c('AMD XDNA 2 NPU detected!', GREEN, BOLD)}")
        print(f"     Running: CPU model → NPU model → GPU+NPU Hybrid")
    elif scenario == "gpu":
        vulkan_devices = (
            recipes.get("llamacpp", {})
                   .get("backends", {})
                   .get("vulkan", {})
                   .get("devices", [])
        )
        device_str = ", ".join(vulkan_devices) if vulkan_devices else "Vulkan GPU"
        print(f"     {_c('AMD Radeon GPU detected', YELLOW, BOLD)}  ({device_str})")
        print(f"     {_c('No XDNA 2 NPU on this system', DIM)}")
        print(f"     Running: CPU (x86)  →  GPU (Vulkan)")
    else:
        print(f"     {_c('CPU-only system — showing CPU baseline only', DIM)}")

    # ── Run benchmark ─────────────────────────────────────────────────────
    client = OpenAI(base_url=f"{base_url}/v1", api_key="lemonade")

    if scenario == "npu":
        results = run_npu_benchmark(
            base_url, client,
            family_name=args.npu_model,
            family=dict(NPU_FAMILIES[args.npu_model]),
            prompt=args.prompt,
            skip_pull=args.skip_pull,
        )
    else:
        results = run_gpu_benchmark(
            base_url, client,
            model_id=args.gpu_model,
            prompt=args.prompt,
            skip_install=args.skip_install,
            skip_pull=args.skip_pull,
        )

    if not results:
        _err("No successful runs. Check that the server is running and backends are installed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
