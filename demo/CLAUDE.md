# CLAUDE.md — Computex 2026 ASRock Demo

## What This Is

A five-act live demo showcasing AMD Ryzen AI on an ASRock PC at Computex 2026.
Three silicon units each play a role: **NPU listens → CPU speaks → iGPU debates/draws**.
The main presenter interface is `orchestrator.html` (browser-based, no framework).

---

## Hardware Requirements

- **AMD Ryzen AI 300+** with XDNA2 NPU (50 TOPS)
- Radeon iGPU (RDNA 3.5) — Vulkan-capable
- Windows 11

---

## Software Setup (in order)

### 1. Install Lemonade Server
Download from: https://lemonade.ai/install_options.html#windows

### 2. Configure server slots (required for Act 5)
```bat
lemonade config set max-loaded-models=9
```

### 3. Pull all demo models
```bat
demo\pullmodels.bat
```
This pulls 10 required models + 7 optional debate alternates.

### 4. Install Python dependencies
```bat
pip install pyaudio websockets numpy sounddevice requests
pip install openai[voice_helpers]
```

### 5. Verify everything
```bat
python demo/setup.py
```
Checks server health, model availability, and backend states (NPU / Vulkan / SD).
Exit code 0 = ready to demo.

---

## Running the Demo

### Option A — HTML orchestrator (primary, used on stage)
```bat
# Start lemonade server first
lemonade launch

# Open in browser
start demo\orchestrator.html
```
The page auto-connects to `localhost:13305`. URL params: `?host=X&port=Y&start-at=N`

### Option B — Python CLI (fallback)
```bat
python demo/orchestrator.py             # start from Act 1
python demo/orchestrator.py --start-at 3
```

---

## Demo Structure — Five Acts

| Act | Index | Title | Hardware | Key Model |
|-----|-------|-------|----------|-----------|
| 1 | 0 | AMD AI Stack Overview | — | static diagram |
| 2 | 1 | Brain Thinks (Benchmark) | XDNA2 NPU + CPU | DeepSeek-R1-Distill-Qwen-1.5B-NPU/Hybrid |
| 3 | 2 | Speech Out (TTS) | CPU | kokoro-v1 |
| 4 | 3 | Draw It (Image Gen) | Radeon iGPU / CPU | SD-Turbo |
| 5 | 4 | 5 AIs Debate | Radeon iGPU Vulkan | 5× GGUF models |

Act 5 opens `computex-debate.html` in a new tab.

---

## Key Files

| File | Role |
|------|------|
| `orchestrator.html` | Main demo UI — single HTML file, no build step |
| `orchestrator.py` | Python CLI fallback orchestrator |
| `computex-debate.html` | Multi-model debate page (Act 5) |
| `computex_benchmark.py` | Standalone benchmark script (CLI, not used in HTML demo) |
| `pullmodels.bat` | Pulls all required models via `lemonade pull` |
| `setup.py` | Pre-show verification: server + models + backends |

---

## Required Models (10 total)

```
Whisper-Large-v3-Turbo          # Act 1 — ASR, NPU
DeepSeek-R1-Distill-Qwen-1.5B-NPU     # Act 2 — NPU-only path
DeepSeek-R1-Distill-Qwen-1.5B-Hybrid  # Act 2 — NPU+iGPU hybrid path
kokoro-v1                       # Act 3 — TTS, CPU
SD-Turbo                        # Act 4 — image gen
Qwen3-0.6B-GGUF                 # Act 5 — debate
Qwen3-1.7B-GGUF                 # Act 5 — debate
LFM2-1.2B-GGUF                  # Act 5 — debate
Llama-3.2-1B-Instruct-GGUF      # Act 5 — debate
Phi-4-mini-instruct-GGUF        # Act 5 — debate
```

---

## Architecture Notes

- **Lemonade Server** (`localhost:13305`) is the single backend. All inference goes through its OpenAI-compatible REST API (`/v1/chat/completions`, `/v1/audio/speech`, `/v1/images/generations`).
- `orchestrator.html` uses SSE streaming for Act 2 LLM output, plain fetch for TTS/image.
- Act 2 strips `<think>...</think>` blocks (DeepSeek-R1 reasoning tokens) before displaying.
- Act 4 auto-detects ROCm vs CPU backend via `/v1/system-info` and adjusts cue text accordingly.
- Act 5 requires `max_loaded_models=9` — verified at runtime via `/internal/config`.
- The UI is bilingual (EN/ZH), toggled live. All strings live in the `I18N` object in `orchestrator.html`.

---

## Common Issues

| Symptom | Fix |
|---------|-----|
| Server not reachable | Run `lemonade launch`; check port 13305 |
| Act 5 slots warning | `lemonade config set max-loaded-models=9` then restart server |
| Act 2 shows blank response | Model may still be in `<think>` phase — wait for `</think>` |
| Image generation uses CPU fallback | ROCm not installed; expected on most setups |
| `setup.py` model missing | Run `lemonade pull <model-id>` |
