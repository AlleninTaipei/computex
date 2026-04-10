@echo off
REM Computex 2026 — Pull all demo models

REM Act 1: 語音辨識 (NPU)
lemonade pull Whisper-Large-v3-Turbo

REM Act 2: Hybrid LLM Benchmark (NPU + CPU)
lemonade pull DeepSeek-R1-Distill-Qwen-1.5B-NPU
lemonade pull DeepSeek-R1-Distill-Qwen-1.5B-Hybrid

REM Act 3: TTS (CPU)
lemonade pull kokoro-v1

REM Act 4: Image Generation (890M ROCm)
lemonade pull SD-Turbo

REM Act 5: Multi-Model Debate (890M Vulkan) — 必要 5 個
lemonade pull Qwen3-0.6B-GGUF
lemonade pull Qwen3-1.7B-GGUF
lemonade pull LFM2-1.2B-GGUF
lemonade pull Llama-3.2-1B-Instruct-GGUF
lemonade pull Phi-4-mini-instruct-GGUF

REM Act 5: 備用辯論模型
lemonade pull Gemma-3-4b-it-GGUF
lemonade pull Qwen3-4B-Instruct-2507-GGUF
lemonade pull granite-4.0-h-tiny-GGUF
lemonade pull Jan-nano-128k-GGUF
lemonade pull SmolLM3-3B-GGUF
lemonade pull Ministral-3-3B-Instruct-2512-GGUF
lemonade pull Llama-3.2-3B-Instruct-GGUF