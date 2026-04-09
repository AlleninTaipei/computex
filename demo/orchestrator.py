"""
Computex 2026 — Five-Act Demo Orchestrator
==========================================
Guides the presenter through all five acts of the Computex demo, launching
the correct script for each act and displaying the narration cue.

Usage:
    python demo/orchestrator.py
    python demo/orchestrator.py --start-at 3    # resume from act 3
    python demo/orchestrator.py --host localhost --port 13305

Acts:
    1  語音進來      Whisper-Large-v3-Turbo    XDNA2 NPU
    2  大腦思考      DeepSeek-R1 Hybrid        NPU + CPU
    3  說話回來      kokoro-v1                 CPU
    4  畫出來        SD-Turbo                  Radeon 890M (ROCm / CPU)
    5  AI 辯論       5x GGUF                   Radeon 890M Vulkan
"""

import argparse
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
TIMEOUT   = 10

# ---------------------------------------------------------------------------
# ANSI colours
# ---------------------------------------------------------------------------
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
CYAN    = "\033[96m"
MAGENTA = "\033[95m"
WHITE   = "\033[97m"


def c(text, *codes):
    return f"{''.join(codes)}{text}{RESET}"


def _sep(char="─", width=68, color=DIM):
    print(c("  " + char * width, color))


def _blank():
    print()


# ---------------------------------------------------------------------------
# Act definitions
# ---------------------------------------------------------------------------

def build_acts(base_url, image_backend):
    """Return the five-act list.  image_backend is 'rocm' or 'cpu'."""
    py = sys.executable
    ex = REPO_ROOT / "examples"
    dm = REPO_ROOT / "demo"

    if image_backend == "rocm":
        img_cue = [
            "「Radeon 890M，RDNA 3.5 架構，ROCm 加速 Stable Diffusion。",
            " 沒有獨顯，一樣跑影像生成。」",
        ]
    else:
        img_cue = [
            "「SD-Turbo 在純 CPU 也能跑——這就是 Lemonade 的跨平台設計。",
            " 不需要 ROCm，不需要獨顯。」",
        ]

    return [
        {
            "num":      1,
            "title":    "語音進來",
            "subtitle": "Speech In",
            "hw":       "XDNA2 NPU  ·  Whisper-Large-v3-Turbo",
            "hw_color": BLUE,
            "cue": [
                "「55 TOPS 的 NPU 在跑 Whisper，",
                " CPU 和 GPU 完全沒動，留給後面用。」",
            ],
            "cmd":  [py, str(ex / "realtime_transcription.py"),
                     "--model", "Whisper-Large-v3-Turbo"],
            "mode": "interactive",   # presenter ends with Ctrl+C
            "hint": "對麥克風說話，大螢幕即時顯示逐字稿。按 Ctrl+C 結束錄音。",
        },
        {
            "num":      2,
            "title":    "大腦思考",
            "subtitle": "Hybrid LLM Benchmark",
            "hw":       "XDNA2 NPU + CPU  ·  DeepSeek-R1-Distill-Qwen-1.5B",
            "hw_color": CYAN,
            "cue": [
                "「模型的權重切割——部分層在 NPU 跑，剩餘層在 CPU 跑，",
                " 同時進行，這是 Ryzen AI 的 Hybrid 推論架構。」",
            ],
            "cmd":  [py, str(dm / "computex_benchmark.py"), "--skip-pull"],
            "mode": "wait",          # runs to completion automatically
            "hint": "Benchmark 自動執行，完成後顯示 NPU vs Hybrid 速度比較。",
        },
        {
            "num":      3,
            "title":    "說話回來",
            "subtitle": "Text-to-Speech",
            "hw":       "CPU  ·  kokoro-v1",
            "hw_color": YELLOW,
            "cue": [
                "「CPU 做語音合成，",
                " 剛才 NPU 和 iGPU 忙的時候，CPU 沒有閒著。」",
            ],
            "cmd":  [py, str(ex / "api_text_to_speech.py")],
            "mode": "wait",
            "hint": "合成語音將透過預設音訊裝置播放。",
        },
        {
            "num":      4,
            "title":    "畫出來",
            "subtitle": "Image Generation",
            "hw":       f"Radeon 890M (RDNA 3.5)  ·  SD-Turbo  [{image_backend.upper()}]",
            "hw_color": GREEN,
            "cue": img_cue,
            "cmd":  [py, str(ex / "api_image_generation.py"),
                     "--backend", image_backend],
            "mode": "wait",
            "hint": "生成完成後圖片存為 generated_image_openai.png（目前工作目錄）。",
        },
        {
            "num":      5,
            "title":    "5 個 AI 同時辯論",
            "subtitle": "Multi-Model Debate",
            "hw":       "Radeon 890M Vulkan  ·  5× GGUF",
            "hw_color": MAGENTA,
            "cue": [
                "「五個模型同時串流辯論，890M 一張 iGPU 全部扛起來。」",
                "「三個矽晶片各司其職——NPU 聽、CPU 說、iGPU 辯論。」",
                "「這套系統，就是一座完整的 AI 工廠。」",
            ],
            "cmd":  None,            # browser + manual server flag
            "mode": "browser",
            "hint": "瀏覽器開啟 llm-debate.html 後，在 UI 裡選 5 個模型並啟動辯論。",
        },
    ]


# ---------------------------------------------------------------------------
# Hardware detection
# ---------------------------------------------------------------------------

def detect_image_backend(base_url):
    """Return 'rocm' if stable-diffusion ROCm backend is ready, else 'cpu'."""
    try:
        r = requests.get(f"{base_url}/v1/system-info", timeout=TIMEOUT)
        r.raise_for_status()
        recipes = r.json().get("recipes", {})
        state = (
            recipes.get("stable-diffusion", {})
                   .get("backends", {})
                   .get("rocm", {})
                   .get("state", "unsupported")
        )
        return "rocm" if state in ("installed", "supported") else "cpu"
    except Exception:
        return "cpu"


def check_server(base_url):
    try:
        r = requests.get(f"{base_url}/v1/health", timeout=5)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False


def get_max_loaded_models(base_url):
    """Return the server's max_loaded_models setting, or None if unknown."""
    try:
        r = requests.get(f"{base_url}/internal/config", timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json().get("max_loaded_models")
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------

ACT_ICONS = {1: "🎤", 2: "🧠", 3: "🔊", 4: "🎨", 5: "⚔️ "}


def print_banner():
    _blank()
    print(c("  ╔══════════════════════════════════════════════════════╗", CYAN))
    print(c("  ║   Computex 2026  —  AMD Ryzen AI  Demo Orchestrator  ║", CYAN, BOLD))
    print(c("  ╚══════════════════════════════════════════════════════╝", CYAN))
    _blank()
    lines = [
        ("NPU 聽",     "XDNA2 55 TOPS",   BLUE),
        ("CPU 說",     "Ryzen AI 9 HX 375", YELLOW),
        ("iGPU 畫/辯", "Radeon 890M RDNA3.5", GREEN),
    ]
    for role, hw, col in lines:
        print(f"  {c(role, col, BOLD):<28}  {c(hw, DIM)}")
    _blank()
    print(c("  三個矽晶片各司其職——這套系統，就是一座完整的 AI 工廠。", WHITE))
    _blank()


def print_act_header(act):
    num      = act["num"]
    title    = act["title"]
    subtitle = act["subtitle"]
    hw       = act["hw"]
    hw_color = act["hw_color"]
    icon     = ACT_ICONS.get(num, "  ")

    _blank()
    _sep("═", color=hw_color)
    print(
        f"  {c(f'第{num}幕', hw_color, BOLD)}  "
        f"{icon}  {c(title, WHITE, BOLD)}  "
        f"{c(f'/ {subtitle}', DIM)}"
    )
    print(f"  {c('硬體：', DIM)}{c(hw, hw_color)}")
    _sep("═", color=hw_color)
    _blank()


def print_cue(cue_lines):
    """Display the narration cue in a highlighted box."""
    width = max(len(line) for line in cue_lines) + 4
    print(c("  ┌" + "─" * width + "┐", YELLOW))
    for line in cue_lines:
        padding = " " * (width - len(line))
        print(c(f"  │  {line}{padding}│", YELLOW))
    print(c("  └" + "─" * width + "┘", YELLOW))
    _blank()


def wait_for_enter(prompt="  按 Enter 開始 →"):
    try:
        input(c(prompt, CYAN, BOLD) + "  ")
    except KeyboardInterrupt:
        _blank()
        raise


def wait_between_acts(next_num=None):
    """Pause between acts with an optional preview of what's next."""
    _blank()
    _sep(color=DIM)
    if next_num:
        print(c(f"  準備進入第 {next_num} 幕…", DIM))
    try:
        input(c("  按 Enter 繼續，或 Ctrl+C 退出 → ", DIM) + "  ")
    except KeyboardInterrupt:
        _blank()
        print(c("  Demo 已手動中止。", YELLOW))
        sys.exit(0)


# ---------------------------------------------------------------------------
# Act runners
# ---------------------------------------------------------------------------

def run_interactive(act):
    """Launch a script; presenter ends it with Ctrl+C."""
    print(c(f"  {act['hint']}", DIM))
    _blank()
    wait_for_enter()

    print(c("  正在啟動…  (Ctrl+C 結束此幕)", DIM))
    _blank()
    try:
        subprocess.run(act["cmd"], cwd=str(REPO_ROOT))
    except KeyboardInterrupt:
        pass

    _blank()
    print(c(f"  ✔  第{act['num']}幕結束", GREEN, BOLD))


def run_wait(act):
    """Launch a script and wait for it to complete."""
    print(c(f"  {act['hint']}", DIM))
    _blank()
    wait_for_enter()

    try:
        result = subprocess.run(act["cmd"], cwd=str(REPO_ROOT))
        _blank()
        if result.returncode == 0:
            print(c(f"  ✔  第{act['num']}幕完成", GREEN, BOLD))
        else:
            print(c(f"  ⚠  第{act['num']}幕退出碼 {result.returncode}", YELLOW))
    except KeyboardInterrupt:
        _blank()
        print(c(f"  ⚠  第{act['num']}幕被中斷", YELLOW))


def run_browser(act, base_url):
    """Open the debate HTML.  Blocks until server has >= 9 LLM slots."""
    debate_html = REPO_ROOT / "examples" / "llm-debate.html"
    REQUIRED_SLOTS = 9

    models = [
        ("Qwen3-0.6B-GGUF",             "0.38 GB"),
        ("Qwen3-1.7B-GGUF",             "1.06 GB"),
        ("LFM2-1.2B-GGUF",              "0.73 GB"),
        ("Llama-3.2-1B-Instruct-GGUF",  "0.83 GB"),
        ("Phi-4-mini-instruct-GGUF",    "2.49 GB"),
    ]
    total = sum(float(sz.split()[0]) for _, sz in models)
    for m, sz in models:
        print(f"    {c(m, WHITE):<44}  {c(sz, DIM)}")
    _blank()
    print(f"  {c('總計：', DIM)}{c(f'{total:.2f} GB', GREEN, BOLD)}  {c('（890M 可承受）', DIM)}")
    _blank()

    # ── Check / wait for server slots ─────────────────────────────────────
    while True:
        slots = get_max_loaded_models(base_url)
        if slots is None:
            print(c("  ⚠  無法讀取 server slots 數 — 請手動確認", YELLOW))
            break
        if slots >= REQUIRED_SLOTS:
            print(c(f"  ✔  Server slots = {slots}  (需要 {REQUIRED_SLOTS})", GREEN, BOLD))
            break

        # Not enough slots — show restart instructions and wait
        _blank()
        print(c(f"  ✘  Server slots = {slots}，需要 {REQUIRED_SLOTS}", RED, BOLD))
        _blank()
        print(c("  請重新啟動 server：", WHITE))
        _blank()
        print(c("    # 方法 1 — 直接帶參數", DIM))
        print(c("    lemonade-server serve --max-loaded-models 9", WHITE, BOLD))
        _blank()
        print(c("    # 方法 2 — 環境變數", DIM))
        print(c("    set LEMONADE_MAX_LOADED_MODELS=9  &&  lemonade-server serve", WHITE, BOLD))
        _blank()
        try:
            input(c("  重啟後按 Enter 重新檢查 → ", CYAN, BOLD) + "  ")
        except KeyboardInterrupt:
            _blank()
            print(c("  Demo 已手動中止。", YELLOW))
            sys.exit(0)

    # ── Open browser ──────────────────────────────────────────────────────
    _blank()
    print(c(f"  {act['hint']}", DIM))
    _blank()
    wait_for_enter()

    try:
        webbrowser.open(debate_html.as_uri())
        print(c("  ✔  已在瀏覽器開啟 llm-debate.html", GREEN, BOLD))
    except Exception as exc:
        print(c(f"  ⚠  無法自動開啟瀏覽器：{exc}", YELLOW))
        print(c(f"     請手動開啟：{debate_html}", DIM))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if sys.platform == "win32":
        os.system("")
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Computex 2026 five-act demo orchestrator"
    )
    parser.add_argument("--host",     default="localhost")
    parser.add_argument("--port",     type=int, default=13305)
    parser.add_argument("--start-at", type=int, default=1,
                        metavar="N", help="Resume from act N (default: 1)")
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"

    # ── Enable VT100 / UTF-8 on Windows ──────────────────────────────────
    print_banner()

    # ── Server check ──────────────────────────────────────────────────────
    print(c(f"  Server : {base_url}", DIM))
    if not check_server(base_url):
        print()
        print(c("  ✘  無法連線到 Lemonade server。", RED, BOLD))
        print(c("     請先執行：lemonade launch", DIM))
        sys.exit(1)
    print(c("  ✔  Server 連線正常", GREEN))
    _blank()

    # ── Detect image backend ──────────────────────────────────────────────
    image_backend = detect_image_backend(base_url)
    if image_backend == "rocm":
        print(c("  ✔  ROCm 偵測到 — 第4幕使用 GPU 加速", GREEN))
    else:
        print(c("  ⚠  ROCm 不可用 — 第4幕改用 CPU backend", YELLOW))
    _blank()

    # ── Build acts ────────────────────────────────────────────────────────
    acts = build_acts(base_url, image_backend)

    # ── Overview ──────────────────────────────────────────────────────────
    print(c("  五幕流程：", WHITE, BOLD))
    for act in acts:
        icon = ACT_ICONS.get(act["num"], "  ")
        skip = c("  (跳過)", DIM) if act["num"] < args.start_at else ""
        num_label = f"第{act['num']}幕"
        print(f"    {c(num_label, act['hw_color'], BOLD)}"
              f"  {icon}  {c(act['title'], WHITE)}"
              f"  {c(act['subtitle'], DIM)}{skip}")
    _blank()

    if args.start_at > 1:
        print(c(f"  → 從第 {args.start_at} 幕開始", CYAN))
        _blank()

    wait_for_enter("  按 Enter 開始 Demo →")

    # ── Run each act ──────────────────────────────────────────────────────
    for act in acts:
        if act["num"] < args.start_at:
            continue

        print_act_header(act)
        print_cue(act["cue"])

        mode = act["mode"]
        if mode == "interactive":
            run_interactive(act)
        elif mode == "wait":
            run_wait(act)
        elif mode == "browser":
            run_browser(act, base_url)

        # Between acts (not after the last)
        if act["num"] < 5:
            wait_between_acts(next_num=act["num"] + 1)

    # ── Final ─────────────────────────────────────────────────────────────
    _blank()
    _sep("═", color=CYAN)
    print(c("  ★  五幕全部完成！", CYAN, BOLD))
    _sep("═", color=CYAN)
    _blank()
    print(c("  核心訊息：", WHITE, BOLD))
    print(c("  「三個矽晶片各司其職：NPU 聽、CPU 說、iGPU 畫」", CYAN))
    print(c("  「不需要獨顯——這就是 Ryzen AI 的意義」", CYAN))
    print(c("  「這套系統，就是一座完整的 AI 工廠」", CYAN))
    _blank()


if __name__ == "__main__":
    main()
