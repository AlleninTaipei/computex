# Computex 動態展 — 完整計畫 v2

**硬體：** Ryzen AI 9 HX 375 | XDNA2 55 TOPS | Radeon 890M (16CU RDNA3.5) | 無 dGPU

---

## 硬體分工總覽

| 運算單元 | 負責項目 |
|---|---|
| XDNA2 NPU (55 TOPS) | 語音辨識、Hybrid LLM |
| Radeon 890M iGPU | 影像生成 (ROCm)、LLM 加速 (Vulkan) |
| CPU | TTS 語音合成、協調排程 |

三個運算單元全部有事做，敘事完整。

---

## 五幕劇本

### 第一幕：語音進來

**硬體：** XDNA2 NPU｜**模型：** Whisper-Large-v3-Turbo

```bash
python examples/realtime_transcription.py --model Whisper-Large-v3-Turbo
```

主持人對麥克風說話，大螢幕即時顯示逐字稿。

> 「55 TOPS 的 NPU 在跑 Whisper，CPU 和 GPU 完全沒動，留給後面用。」

---

### 第二幕：大腦思考

**硬體：** XDNA2 NPU + CPU Hybrid｜**模型：** Qwen3-8B-Hybrid

```bash
lemonade run Qwen3-8B-Hybrid
```

> 「模型的權重切割——部分層在 NPU 跑，剩餘層在 CPU 跑，同時進行，這是 Ryzen AI 的 Hybrid 推論架構。」

---

### 第三幕：說話回來

**硬體：** CPU｜**模型：** kokoro-v1

```bash
python examples/api_text_to_speech.py
```

> 「CPU 做語音合成，剛才 NPU 和 iGPU 忙的時候，CPU 沒有閒著。」

---

### 第四幕：畫出來

**硬體：** Radeon 890M ROCm｜**模型：** SD-Turbo

```bash
python examples/api_image_generation.py --backend rocm
```

> 「Radeon 890M，RDNA 3.5 架構，ROCm 加速 Stable Diffusion。沒有獨顯，一樣跑影像生成。」

---

### 第五幕：5 個 AI 同時辯論

**硬體：** Radeon 890M Vulkan｜**模型：** 小型 GGUF

```bash
lemonade serve --max-loaded-models 9
# 開啟 examples/llm-debate.html
```

890M 記憶體限制，選用輕量模型組合：

| 模型 | 大小 |
|---|---|
| Qwen3-0.6B-GGUF | 0.38 GB |
| Qwen3-1.7B-GGUF | 1.06 GB |
| LFM2-1.2B-GGUF | 0.73 GB |
| Llama-3.2-1B-Instruct-GGUF | 0.83 GB |
| Phi-4-mini-instruct-GGUF | 2.49 GB |

五個模型同時串流辯論，總計約 5.5 GB，890M 可以承受。

---

## 展前準備指令

* 安裝 Lemonade Server
  * https://lemonade.ai/install_options.html#windows


* 啟動 server
```bash
lemonade config set max-loaded-models=9
```

* 下載所有 demo 模型 (/demo/pullmodels.bat)
```bash
lemonade pull Whisper-Large-v3-Turbo
lemonade pull Qwen3-8B-Hybrid
lemonade pull kokoro-v1
lemonade pull SD-Turbo
lemonade pull Qwen3-0.6B-GGUF
lemonade pull Qwen3-1.7B-GGUF
lemonade pull LFM2-1.2B-GGUF
lemonade pull Llama-3.2-1B-Instruct-GGUF
lemonade pull Phi-4-mini-instruct-GGUF
lemonade pull Gemma-3-4b-it-GGUF
lemonade pull Qwen3-4B-Instruct-2507-GGUF
lemonade pull granite-4.0-h-tiny-GGUF
lemonade pull Jan-nano-128k-GGUF
lemonade pull SmolLM3-3B-GGUF
lemonade pull Ministral-3-3B-Instruct-2512-GGUF
lemonade pull Llama-3.2-3B-Instruct-GGUF
lemonade pull LFM2-1.2B-GGUF
```

* 安裝 Python 依賴
```bash
python -m pip install pyaudio
python -m pip install websockets
python -m pip install numpy
python -m pip install openai[voice_helpers]
python -m pip install sounddevice
```

---

## 核心話術

| 舊話術 | 修訂話術 |
|---|---|
| 「GPU 和 NPU 並行」 | 「三個矽晶片各司其職：NPU 聽、CPU 說、iGPU 畫」 |
| 「需要獨顯」 | 「不需要獨顯——這就是 Ryzen AI 的意義」 |
| 「雲端替代方案」 | 「這套系統，就是一座完整的 AI 工廠」 |

---

 ## demo/setup.py — 展前驗證

  python demo/setup.py

  輸出三個區塊的 checklist：
  - Server — 連線健康檢查
  - Models — 逐一確認 9 個模型已 pull（依幕分組標示）
  - Backends — NPU / Vulkan / ROCm 狀態，自動顯示 fallback 提示

  ## demo/orchestrator.py — 五幕主持腳本

  python demo/orchestrator.py           # 從第1幕開始
  python demo/orchestrator.py --start-at 3   # 從第3幕繼續

  每一幕的流程：
  1. 顯示幕頭（幕數、標題、硬體標示）
  2. 黃色框顯示話術提示（直接念）
  3. 按 Enter 啟動腳本
  4. 幕結束後按 Enter 繼續下一幕

  特別處理：
  - 第1幕（Whisper）— interactive，按 Ctrl+C 結束錄音，orchestrator 繼續
  - 第2幕（Benchmark）— 自動跑完，輸出 NPU vs Hybrid 比較表
  - 第4幕（影像）— 啟動時自動偵測 ROCm；不可用就 fallback CPU，話術也一起換
  - 第5幕（辯論）— 顯示 5 個模型清單 + 總記憶體、自動開啟瀏覽器