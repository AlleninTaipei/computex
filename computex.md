  COMPUTEX Demo 建議

  1. 主打「Hybrid GPU+NPU」的速度優勢

  Lemonade 已支援 AMD RyzenAI Hybrid 模式（GPU+NPU 同時運算），這是最大亮點。可以做三路對比 benchmark：

  ┌────────────────┬────────────────────────────────────┬──────────┐
  │      模式      │              模型範例              │ 展示重點 │
  ├────────────────┼────────────────────────────────────┼──────────┤
  │ CPU only       │ Qwen2.5-0.5B-Instruct-CPU          │ baseline │
  ├────────────────┼────────────────────────────────────┼──────────┤
  │ NPU only       │ DeepSeek-R1-Distill-Qwen-7B-NPU    │ 省電     │
  ├────────────────┼────────────────────────────────────┼──────────┤
  │ GPU+NPU Hybrid │ DeepSeek-R1-Distill-Qwen-7B-Hybrid │ 最快     │
  └────────────────┴────────────────────────────────────┴──────────┘

  指標來自現成的 /v1/stats endpoint，回傳 tokens_per_second + time_to_first_token，可以直接做即時儀表板。

  ---
  2. 多模態 Pipeline（視覺衝擊最強）

  全程本地，全跑 AMD 硬體：

  麥克風語音 → Whisper (NPU) → LLM → Kokoro TTS (CPU)
                                  ↓
                 圖片上傳 → Gemma-3-4b-it-mm-NPU (視覺理解)
                                  ↓
                     SD.cpp ROCm → 圖片生成

  - Vision 模型：Gemma-3-4b-it-mm-NPU（已在 registry 裡，標記 vision）
  - 語音輸入：Whisper NPU
  - TTS 輸出：Kokoro
  - 圖片生成：SD.cpp with ROCm

  ---
  3. 目前可能缺少的功能（建議補強）

  a. 即時 benchmark 比較面板
  - 現有 /v1/stats 只回傳最近一次請求的 TPS
  - 建議新增：同時跑兩個模型（GPU vs NPU）並排顯示 TPS，需要改 /stats 支援 per-model 統計

  b. 展示用 Demo Script
  - 目前沒有一鍵 demo 腳本，建議寫一個 Python script，依序：
    a. pull 幾個 showcase 模型
    b. 跑固定 prompt，印出 TPS
    c. 顯示 GPU vs NPU vs Hybrid 比較表

  c. Web App 的即時 TPS 顯示
  - Electron app 現有 UI (ModelManager.tsx, ChatWindow.tsx) 但沒有即時 tokens/sec 顯示
  - 展示時加上這個數字，視覺效果很好

  ---
  4. 最建議的 COMPUTEX 展示 Flow

  1. 開場：lemonade list → 展示支援的 AMD 模型數量（~60+ 個）
  2. 拉模型：lemonade pull DeepSeek-R1-Distill-Qwen-7B-Hybrid
  3. 對話：用 Web App 做即時 streaming chat，螢幕上看到 token 生成速度
  4. 切換：同樣問題問 CPU 版，對比速度差異
  5. 多模態：上傳圖片 → Gemma NPU 視覺理解 → 語音朗讀答案

  ---
  你比較想先做哪個方向？我可以幫你：
  - 寫 benchmark 比較腳本
  - 改 /v1/stats 支援 per-model 統計
  - 在 Web App 加 TPS 顯示
