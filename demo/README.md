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
  Mode      Model                                      TPS   TTFT (ms)  Throughput
  ────────────────────────────────────────────────────────────────────────────────────────
  ⚡ NPU     DeepSeek-R1-Distill-Qwen-1.5B-NPU         27.7         349  █████████████████████████░░░░░
  🚀 Hybrid  DeepSeek-R1-Distill-Qwen-1.5B-Hybrid      33.4         216  ██████████████████████████████  ×1.2
  ────────────────────────────────────────────────────────────────────────────────────────

  ★  Winner:  Hybrid  (33.4 tokens/sec)
  Speedup vs NPU:  1.2x faster
```

> Numbers above are illustrative. Actual results depend on installed GPU and system memory configuration.
