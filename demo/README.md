# AMD Hybrid Inference Benchmark — COMPUTEX 2026

A self-contained benchmark script that demonstrates AMD's hybrid inference advantage by comparing NPU-only, GPU-only, and GPU+NPU Hybrid inference on the same model family.

## Benchmark Design

### Hardware Detection

The script calls `/v1/system-info` on startup and selects a scenario based on detected hardware:

| Detected Hardware | Scenario |
|-------------------|----------|
| AMD XDNA 2 NPU (Ryzen AI 300+) | NPU benchmark (see below) |
| AMD Radeon GPU / iGPU (Vulkan), no NPU | CPU vs GPU benchmark |
| CPU only | CPU baseline only |

### NPU Scenario: 2-Way Comparison

When an XDNA 2 NPU is detected, the script runs two inference passes using the same model family:

```
⚡ NPU only    DeepSeek-R1-Distill-Qwen-1.5B-NPU      (ryzenai-llm, NPU-only)
🚀 GPU+NPU     DeepSeek-R1-Distill-Qwen-1.5B-Hybrid   (ryzenai-llm, NPU+GPU)
```

Both variants use the same `ryzenai-llm` recipe, making the TPS numbers directly comparable. The Hybrid model co-runs the model on the XDNA 2 NPU and the integrated GPU, demonstrating the advantage of AMD's hybrid inference path. Speedup is reported relative to the NPU baseline.

> **Why not compare against CPU or dGPU?**  
> The Hybrid recipe runs on NPU + integrated GPU (iGPU), not on a discrete Radeon GPU. Comparing against a dGPU (Vulkan GGUF) uses a different inference stack and different hardware, giving a misleading result. Comparing NPU vs Hybrid isolates the exact contribution of adding the iGPU to the NPU workload.

### GPU-Only Scenario: 2-Way Comparison

On systems with a Vulkan-capable GPU but no NPU:

```
🖥  CPU      <model>-GGUF    (llamacpp + cpu)
🎮 GPU      <model>-GGUF    (llamacpp + Vulkan)
```

## Model Selection

The NPU benchmark uses the **DeepSeek-R1-Distill-Qwen-1.5B** family. Both variants share the same `ryzenai-llm` recipe, making throughput directly comparable:

| Role | Model | Recipe | Size |
|------|-------|--------|------|
| NPU only | `DeepSeek-R1-Distill-Qwen-1.5B-NPU` | `ryzenai-llm` | ~3 GB |
| GPU+NPU Hybrid | `DeepSeek-R1-Distill-Qwen-1.5B-Hybrid` | `ryzenai-llm` | ~3 GB |

For the GPU-only scenario, the default model is `Qwen3-4B-GGUF` (configurable via `--gpu-model`).

## Requirements

```bash
pip install openai requests
```

A running Lemonade server is required:

```bash
lemonade launch
```

## Usage

```bash
# Auto-detect hardware and run the appropriate benchmark
python demo/computex_benchmark.py

# Override the GPU-only model
python demo/computex_benchmark.py --gpu-model Qwen3-1.7B-GGUF

# Skip model downloads (models already pulled)
python demo/computex_benchmark.py --skip-pull

# Skip backend installation
python demo/computex_benchmark.py --skip-install

# Connect to a non-default server
python demo/computex_benchmark.py --host localhost --port 13305
```

| Argument | Default | Description |
|----------|---------|-------------|
| `--host` | `localhost` | Lemonade server host |
| `--port` | `13305` | Lemonade server port |
| `--gpu-model` | `Qwen3-4B-GGUF` | GGUF model used in GPU-only scenario |
| `--skip-pull` | off | Skip model download step |
| `--skip-install` | off | Skip backend install step |
| `--prompt` | *(built-in)* | Override the inference prompt |

## Sample Output

```
  AMD Hybrid Inference Benchmark  —  COMPUTEX 2026
  Server : http://localhost:13305

  🔌  Checking Lemonade server  http://localhost:13305
     ✔  Server is running

  🔍  Detecting hardware
     AMD XDNA 2 NPU detected!
     Running: NPU model → GPU+NPU Hybrid  (if a supported GPU is installed)

  📥  Pulling NPU/Hybrid models  first run may take a few minutes
     NPU     →  DeepSeek-R1-Distill-Qwen-1.5B-NPU      ✔  ready
     Hybrid  →  DeepSeek-R1-Distill-Qwen-1.5B-Hybrid   ✔  ready

  🏁  Running inference  NPU → GPU+NPU Hybrid

  [NPU] ⚡ Inferring ...
     ✔  Wall: 13.2s  |  TPS: 27.7  |  TTFT: 349 ms  |  Tokens: 256

  [Hybrid] 🚀 Inferring ...
     ✔  Wall: 10.6s  |  TPS: 33.4  |  TTFT: 216 ms  |  Tokens: 256

══════════════════════════════════════════════════════════════════════
  AMD XDNA 2 NPU — DeepSeek-R1-Distill-Qwen-1.5B
══════════════════════════════════════════════════════════════════════
  Mode      Model          TPS   TTFT (ms)  Throughput
  ────────────────────────────────────────────────────────────────────────────────────────
  ⚡ NPU     DeepSeek-R1-Distill-Qwen-1.5B-NPU         27.7         349  █████████████████████████░░░░░
  🚀 Hybrid  DeepSeek-R1-Distill-Qwen-1.5B-Hybrid      33.4         216  ██████████████████████████████  ×1.2
  ────────────────────────────────────────────────────────────────────────────────────────

  ★  Winner:  Hybrid  (33.4 tokens/sec)
  Speedup vs NPU:  1.2x faster
```

> Numbers above are illustrative. Actual results depend on installed GPU and system memory configuration.

## Setup Instructions

* Install Lemonade Server
  * https://lemonade.ai/install_options.html#windows

* Start the server

```bash
lemonade config set max-loaded-models=9
```

* Download all demo models (`/demo/pullmodels.bat`)

* Install Python dependencies

```bash
python -m pip install pyaudio
python -m pip install websockets
python -m pip install numpy
python -m pip install openai[voice_helpers]
python -m pip install sounddevice
```

* demo/setup.py — Validate environment

```bash
  python demo/setup.py
```

* Outputs three checklist sections:
  * Server — connectivity health check
  * Models — verify all 9 models are pulled (grouped by stage)
  * Backends — NPU / Vulkan / ROCm status with automatic fallback hints

* demo/orchestrator.py — Five-act host script

```bash
  python demo/orchestrator.py           # start from act 1
  python demo/orchestrator.py --start-at 3   # resume from act 3
```

## Learning

### NPU Only — Dedicated NPU Path

* Example: Phi-4-mini-instruct-NPU
* Runs entirely on Ryzen AI NPU (XDNA) using AMD's own runtime (ryzenai-llm), no GPU or CPU involved
* Characteristics: lowest power consumption (critical for laptops), silent / low temperature, stable latency (but throughput is usually lower)
* Limitations: model must be converted to NPU-supported format (usually INT8 / special compilation), does not support large models (memory + NPU compute constraints)

### GPU Only — GPU Inference Path

* Example: Phi-4-mini-instruct-GGUF
* Model converted to GGUF and run with llama.cpp, using Vulkan backend for GPU
* Much faster than CPU, broadest model compatibility, most mature ecosystem with largest community
* This is a "cross-platform GPU" solution (Vulkan), not an AMD-specific stack

### GPU + NPU — Hybrid Inference

* Example: Phi-4-mini-instruct-Hybrid
* Some layers run on NPU, some on GPU (or CPU), runtime automatically splits the workload
* Balances performance vs power efficiency — faster than NPU-only, more power-efficient than GPU-only

### Why "No ROCm"? (Key Insight)

* This is an intentional design choice
  * 1️⃣ ROCm ≠ mainstream consumer Windows solution
    * ROCm is AMD's CUDA equivalent, primarily Linux-based
    * Geared toward datacenter (MI300), AI training / HPC
    * Windows support is limited / unstable

  * 2️⃣ llama.cpp chose Vulkan for "portability". Vulkan backend advantages:
    * Supports AMD / NVIDIA / Intel
    * Runs on Windows / Linux
    * No ROCm / CUDA required
    * This path intentionally avoids ROCm

  * 3️⃣ Ryzen AI software stack does not rely on ROCm. AMD's AI PC strategy:
    * NPU → ryzenai-llm
    * GPU → Vulkan / DirectML (sometimes)
    * ROCm is not pushed

  * 4️⃣ ROCm is not suitable for "edge / client AI". ROCm's issues:
    * Heavy installation
    * Compatibility constraints (specific GPUs)
    * Driver + kernel coupling
    * Not suitable for OEM / end-user distribution

* "Out-of-box AI PC experience". These three modes represent three product strategies:
  * NPU → power efficiency, AI PC differentiation
  * GPU (Vulkan) → maximum compatibility
  * Hybrid → best experience
  * ❗ ROCm is intentionally excluded — it is not the optimal path for consumer AI PCs

* This reveals AMD's strategic direction:
  * ROCm → datacenter (competing against CUDA)
  * Ryzen AI → client AI (a completely separate stack)

### AMD AI Software Stack (ROCm vs Ryzen AI vs Vulkan)

```plaintext
                    ┌──────────────────────────┐
                    │   Application Layer      │
                    │  Chatbot / Copilot / RAG │
                    └────────────┬─────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼

 ┌───────────────┐     ┌────────────────┐     ┌──────────────────┐
 │  Ryzen AI SDK │     │   llama.cpp    │     │   PyTorch / ONNX │
 │ (NPU Runtime) │     │ (GGUF runtime) │     │  (Training/Infer)│
 └──────┬────────┘     └──────┬─────────┘     └─────────┬────────┘
        │                     │                         │
        ▼                     ▼                         ▼

 ┌───────────────┐     ┌────────────────┐     ┌──────────────────┐
 │ ryzenai-llm   │     │ Vulkan backend │     │      ROCm        │
 │ (NPU driver)  │     │ (Cross GPU)    │     │ (HIP / OpenCL)   │
 └──────┬────────┘     └──────┬─────────┘     └─────────┬────────┘
        │                     │                         │
        ▼                     ▼                         ▼

 ┌───────────────┐     ┌────────────────┐     ┌──────────────────┐
 │   XDNA NPU    │     │   RDNA GPU     │     │   CDNA / RDNA    │
 │ (Ryzen AI)    │     │ (Consumer GPU) │     │ (MI300 / HPC)    │
 └───────────────┘     └────────────────┘     └──────────────────┘
```

### Why Are They Not Integrated? AMD's Biggest Structural Challenge

* Three completely incompatible execution models

| Dimension | Ryzen AI | Vulkan | ROCm |
|:----------|:---------|:-------|:-----|
| API | Proprietary | Universal | HIP |
| OS | Windows-first | Cross-platform | Linux |
| HW | NPU | GPU | Datacenter GPU |
| Model Format | Compiled | GGUF | PyTorch |

* Result: models must be converted 3 times, runtimes are not shared, fragmented developer experience

* From a product strategy perspective, this pattern suggests AMD is deliberately segmenting its stack — keeping ROCm in the datacenter, separate from the client AI stack:
  * Datacenter (competing against NVIDIA CUDA)
    * ROCm + MI300
    * Target: OpenAI / hyperscalers
  * AI PC (competing against Intel / Apple)
    * Ryzen AI + NPU
    * Target: Copilot+ PC / OEM
  * Developer / Open-source community
    * Vulkan / llama.cpp
    * Target: local AI / hobby / prototyping
  
### Opportunity? Or Simply a Consequence of the Chip Product Line?

| Vendor | Status |
| ------ | ------ |
| NVIDIA | CUDA (unified) |
| AMD    | Fragmented (ROCm / Ryzen AI / Vulkan) |
| Intel  | oneAPI (but weak) |
| Apple  | CoreML (closed) |

### @src/cpp/resources/server_models.json

> Model entry properties ("keys")

#### checkpoint

Points to the download source for model weight files, in the format `HuggingFace repo/model-name[:filename]`. When Lemonade runs `lemonade pull <model-name>`, it fetches from this path.

| Source Prefix | Count | Description |
|-|-|-|
| amd | 81 | Official AMD quantized versions, optimized for Ryzen AI |
| unsloth | 36 | Third-party GGUF quantization |
| stabilityai | 3 | Stability AI official |
| mikkoph | 1 | kokoro TTS |
| (none) | 12 | Whisper series etc., download handled by recipe |

#### recipe

Specifies which inference engine to use for this model.

| Recipe | Engine | Description |
|-|-|-|
| ryzenai-llm | AMD RyzenAI ONNX runtime | Hybrid LLM |
| llamacpp | llama.cpp (Vulkan/CPU) | |
| whispercpp | whisper.cpp | Speech recognition |
| sd-cpp | stable-diffusion.cpp | Image generation |
| kokoro | kokoro ONNX | TTS |
| experience | Bundled composite | |
