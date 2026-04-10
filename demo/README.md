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

## Learning

### NPU only — NPU 專用路徑

* Example : Phi-4-mini-instruct-NPU
* 完全跑在 Ryzen AI 的 NPU（XDNA）, 使用 AMD 自家的 runtime（ryzenai-llm）, 不走 GPU、不走 CPU
* 特點： 功耗最低（筆電超重要）, 靜音 / 低溫, 延遲穩定（但吞吐通常不高）
* 限制： 模型要轉成 NPU 支援格式（通常是 INT8 / 特殊編譯）, 不支援太大的模型（記憶體 + NPU算力限制）

### GPU only — GPU 推論路徑

* Examplel : Phi-4-mini-instruct-GGUF
* 模型轉成 GGUF 用 llama.cpp 跑, GPU 用的是 Vulkan backend
* 比 CPU 快很多, 支援模型種類最廣, 最成熟、社群最大
* 這裡是「跨平台 GPU」方案（Vulkan），不是 AMD 專用 stack

### GPU + NPU — Hybrid 混合推論

* Example : Phi-4-mini-instruct-Hybrid
* 一部分 layer 在 NPU, 一部分在 GPU（或 CPU）, runtime 會幫你切 workload
* 平衡效能 vs 功耗, 比純 NPU 快, 比純 GPU 省電

### 為什麼「沒有 ROCm」？（重點）

* 這是關鍵設計選擇
  * 1️⃣ ROCm ≠ 消費級 Windows 主流方案
    * ROCm 是 AMD 的 CUDA 對應平台，主要在 Linux
    * 偏向 Data center（MI300）, AI training / HPC
    * Windows 支援 有限 / 不穩定

  * 2️⃣ llama.cpp 選 Vulkan，是為了「通用性」, Vulkan backend 的優勢：
    * 支援 AMD / NVIDIA / Intel
    * Windows / Linux 都能跑
    * 不需要 ROCm / CUDA
    * 所以這條路刻意「避開 ROCm」

  * 3️⃣ Ryzen AI 軟體棧本來就不走 ROCm, AMD 在 AI PC 的策略是：
    * NPU → ryzenai-llm
    * GPU → Vulkan / DirectML（有時）
    * 不強推 ROCm

  * 4️⃣ ROCm 不適合這種「edge / client AI」, ROCm 的問題在這裡：
    * 安裝重
    * 相容性限制（特定 GPU）
    * driver + kernel 綁死
    * 不適合 OEM / end-user 發佈

* 「讓使用者開箱即用 AI PC」, 這三種模式其實代表三條產品策略：
  * NPU → 省電、AI PC differentiation
  * GPU (Vulkan) → 最大相容性
  * Hybrid → 最佳體驗
  * ❗ ROCm 被刻意排除，因為它不是「consumer AI PC」的最佳路徑

* 這其實透露 AMD 的方向：
  * ROCm → datacenter（對標 CUDA）
  * Ryzen AI → client AI（完全另一套 stack）

如果你想，我可以幫你畫一張：

### 「AMD AI Software Stack（ROCm vs Ryzen AI vs Vulkan）」的完整架構圖

```plaintext
                    ┌──────────────────────────┐
                    │        應用層 (Apps)      │
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

### 為什麼它們「沒有整合」？ 這是 AMD 現在最大結構問題 ?

* 三套完全不互通的 execution model

|層面|Ryzen AI|Vulkan|ROCm|
|:-|:-|:-|:-|
|API|專有|通用|HIP|
|OS|Windows-first|全平台|Linux|
|HW|NPU|GPU|Datacenter GPU|
|模型格式|編譯後|GGUF|PyTorch|

* 結果就是：模型要轉 3 次, runtime 不共用 ,developer 體驗割裂

* 從產品策略看, 現在看到的現象，其實代表 AMD 在做切割, 故意讓 ROCm 留在 datacenter，不進 client AI stack ?
  * Datacenter（對打 NVIDIA CUDA）
    * ROCm + MI300
    * target：OpenAI / hyperscaler
  * AI PC（對打 Intel / Apple）
    * Ryzen AI + NPU
    * target：Copilot+ PC / OEM
  * Developer / 開源社群
    * Vulkan / llama.cpp
    * target：local AI / hobby / prototyping
  
### 機會？ 還是根本是晶片產品線使然 ？

| 廠商     | 狀態                             |
| ------ | ------------------------------ |
| NVIDIA | CUDA（統一）                       |
| AMD    | 三裂（ROCm / Ryzen AI / Vulkan） |
| Intel  | oneAPI（但很弱）                     |
| Apple  | CoreML（封閉）                     |

### @src/cpp/resources/server_models.json

>「屬性（property）」或「鍵（key）」

#### checkpoint

指向模型權重檔案的下載來源，格式是 HuggingFace repo/模型名稱[:檔案名]。Lemonade 執行 lemonade pull <模型名> 時，就是去這個路徑抓檔案。

|來源前綴|數量|說明|
|-|-|-|
|amd| 81| AMD 官方量化版本，針對 Ryzen AI 優化|
|unsloth|     36|    第三方 GGUF 量化|
|stabilityai|  3|     SD 原廠|
|mikkoph|      1|     kokoro TTS| 
|  (無) |         12|    Whisper 系列等，由 recipe 自行處理下載| 

#### recipe  

指定用哪個推論引擎來執行這個模型

|recipe|引擎|說明|
|-|-|-|
|ryzenai-llm|  AMD RyzenAI ONNX runtime|Hybrid LLM|
|llamacpp|llama.cpp（Vulkan/CPU ||
|whispercpp|whisper.cpp| 語音辨識|
|sd-cpp|       stable-diffusion.cpp| 影像生成|
|kokoro|       kokoro ONNX |TTS|
|experience|   複合套裝||
