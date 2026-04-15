# Module 2 Brief: Three Chips, Three Jobs

## Meta
- **File to write:** `modules/02-chips.html`
- **Module ID:** `module-2`
- **Background:** `var(--color-bg-warm)` (slightly warmer)
- **Previous module:** Module 1 — Your PC as an AI Factory
- **Next module:** Module 3 — The Control Tower

## Teaching Arc
**Metaphor:** A film crew. A film set has different specialists who each handle their domain: the sound engineer (NPU), the cinematographer (GPU), and the director (CPU orchestrating it all). You wouldn't ask the sound engineer to operate the camera — each specialist does what they're best at.

**Opening hook:** "Your modern PC has three completely different types of processors sitting inside it. Most apps only use one. Lemonade uses all three at once — and assigns each a different AI job based on what it's best at."

**Key insight:** The NPU, GPU, and CPU have fundamentally different architectures. The NPU is power-efficient but narrow. The GPU is massively parallel and general. The CPU is flexible but relatively slow for AI math. Lemonade's brilliance is matching each AI task to the right chip.

**Learning goal:** Learners can explain which chip handles which AI task and WHY (based on what each chip is good at). They understand the three software stacks: ryzenai-llm (NPU), llamacpp+Vulkan (GPU), kokoro/whispercpp (CPU/NPU).

## Screens (5 total)

### Screen 1: The Three Chips
Open with the film crew metaphor. Then show a visual diagram of the three chips as "department offices":

Use pattern-cards with 3 cards (stagger-children):
- 🧠 **NPU (Neural Processing Unit)**
  - Color: var(--color-actor-2) [teal]
  - "AMD XDNA — built *specifically* for AI math. Incredibly power-efficient. Like a dedicated calculator that only knows how to multiply matrices."
  - Best for: Low-power, sustained AI tasks
  - Badge: "55 TOPS"
- 🎮 **GPU (Graphics Processing Unit)**
  - Color: var(--color-actor-5) [forest green]
  - "AMD Radeon — massively parallel. Can do thousands of calculations simultaneously. Originally built for games, now great for AI."
  - Best for: Parallel AI tasks, image generation
  - Badge: "iGPU / dGPU"
- 💻 **CPU (Central Processing Unit)**
  - Color: var(--color-actor-4) [golden]
  - "x86_64 — the general-purpose brain. Flexible but not specialized for AI. Good for coordination and lighter AI tasks."
  - Best for: Orchestration, TTS, fallback

Callout (callout-info): "On AMD Ryzen AI laptops, all three chips are on the same processor die — they share memory and can work *simultaneously* without copying data between them."

### Screen 2: Who Does What — The Job Board
Show a visual "job board" matching each AI task to its chip. Use a 2-column layout.

Left column (Task):
- 🎤 Speech Recognition (Whisper)
- 🧠 LLM Chat (Hybrid mode)
- 🔊 Text to Speech (Kokoro)
- 🎨 Image Generation (SD-Turbo)
- 💬 Multi-model Debate (5x GGUF)

Right column (Chip + Why):
- NPU (XDNA) — "Most efficient for sustained audio encoding"
- NPU + iGPU — "Model split: NPU runs some layers, iGPU runs the rest simultaneously"
- CPU — "Light computation; CPU is free while NPU/GPU are busy"
- GPU (Vulkan / ROCm) — "Parallel computation for image synthesis"
- GPU (Vulkan) — "5 models in parallel; Vulkan is cross-platform"

Intro sentence: "In the COMPUTEX demo, three chips divide the work so efficiently that none of them sit idle:"

### Screen 3: The Software Stack — What Bridges Chips and AI
Intro: "Here's the part that matters for vibe coders: each chip requires completely different software to talk to it. Lemonade abstracts this away — you just name the model, and Lemonade handles the rest."

Flow animation showing the stack:

data-steps:
1. {"highlight":"flow-actor-1","label":"You request: lemonade run Gemma-3-4b-it-GGUF"}
2. {"highlight":"flow-actor-2","label":"Lemonade looks up the recipe: llamacpp + Vulkan","packet":true,"from":"actor-1","to":"actor-2"}
3. {"highlight":"flow-actor-3","label":"llama.cpp loads the GGUF model file","packet":true,"from":"actor-2","to":"actor-3"}
4. {"highlight":"flow-actor-4","label":"Vulkan backend sends work to the GPU","packet":true,"from":"actor-3","to":"actor-4"}
5. {"highlight":"flow-actor-5","label":"GPU returns tokens → you get your response","packet":true,"from":"actor-4","to":"actor-5"}

Actors:
- flow-actor-1: You (🧑) [actor-1 vermillion]
- flow-actor-2: Lemonade Router (🔀) [actor-2 teal]
- flow-actor-3: llama.cpp (📦) [actor-3 plum]
- flow-actor-4: Vulkan (🎮) [actor-4 golden]
- flow-actor-5: GPU (⚡) [actor-5 forest]

### Screen 4: Code ↔ English — The Recipe System
Show actual code from server_models.json for Phi-4-mini-instruct-Hybrid:

```json
"Phi-4-mini-instruct-Hybrid": {
  "checkpoint": "amd/Phi-4-mini-instruct-onnx-ryzenai-1.7-hybrid",
  "recipe": "ryzenai-llm",
  "suggested": true,
  "size": 5.1
}
```

English translation:
- `"Phi-4-mini-instruct-Hybrid"` → The model's name — what you type in the CLI or pick in the app
- `"checkpoint"` → Where to download the model from. "amd/" means AMD's Hugging Face org — pre-optimized for Ryzen AI
- `"recipe"` → Which inference engine to use. "ryzenai-llm" means: use AMD's special NPU/GPU runtime
- `"suggested": true` → Show this model as a recommended option in the UI
- `"size": 5.1` → 5.1 GB download. Displayed in the Model Manager so you know what you're downloading

Callout (callout-accent): "The 'recipe' field is the key idea. It's like specifying a cooking method: you can have the same ingredients (model weights) but cook them differently (CPU vs GPU vs NPU). Each recipe uses a different software engine."

### Screen 5: Quiz — Which Chip for Which Job?
Multiple-choice quiz (id="quiz-module2"):

Question 1: "You want to run 5 AI models simultaneously and all of them are GGUF format. Which backend makes the most sense?"
- data-correct="option-b"
- a) ryzenai-llm (NPU runtime)
- b) llamacpp + Vulkan (GPU)  ✓
- c) kokoro (TTS engine)
- explanation-right: "Exactly! Vulkan on the GPU is designed for parallel workloads. The GPU can juggle multiple model threads simultaneously — that's why the 5-model debate in the COMPUTEX demo uses Vulkan."
- explanation-wrong: "Think about which chip handles parallel workloads best. The NPU is great for single-model efficiency; the GPU shines when you want to run many things at once."

Question 2: "Your app transcribes audio from a podcast. The laptop is on battery. Which chip should handle it for best battery life?"
- data-correct="option-a"
- a) NPU (XDNA)  ✓
- b) GPU (Vulkan)
- c) CPU
- explanation-right: "Right! The NPU is specifically designed for power-efficient AI math. Whisper on NPU draws a fraction of the power that the GPU would — critical for a laptop on battery."
- explanation-wrong: "Consider which chip was built for sustained, power-efficient AI tasks. Hint: it's not the GPU (power hungry) or the CPU (slow for AI math)."

Question 3: "You're building a voice assistant that needs to BOTH transcribe and speak. What's the smart architecture?"
- data-correct="option-c"
- a) Use NPU for everything
- b) Use GPU for everything
- c) NPU for Whisper (transcription) + CPU for Kokoro (TTS) — they run simultaneously  ✓
- explanation-right: "Exactly — this is exactly what the COMPUTEX demo does. The NPU handles Whisper while the CPU handles Kokoro. They don't compete for the same hardware, so both run in parallel. Zero waiting."
- explanation-wrong: "The magic of having three chips is that they can run *independently* at the same time. Transcription and TTS use different chips — no need to share."

## Interactive Elements Checklist
- [x] Pattern Cards (Screen 1) — three chips
- [x] Flow Animation (Screen 3) — software stack journey
- [x] Code ↔ English Translation (Screen 4) — server_models.json entry
- [x] Multiple-Choice Quiz (Screen 5) — 3 questions

## Tooltips Required
- "TOPS" — Tera Operations Per Second — a measure of how many AI calculations a chip can do per second. 55 TOPS is roughly how many multiplications AMD's NPU can do in one second.
- "GGUF" — A file format for storing AI model weights, popularized by llama.cpp. Think of it as a compressed container for an AI model's "memory."
- "Vulkan" — A cross-platform graphics API that works on AMD, NVIDIA, and Intel GPUs. Lemonade uses it as a GPU backend that works on Windows AND Linux without requiring proprietary drivers.
- "ROCm" — AMD's compute platform, similar to NVIDIA's CUDA. Works mainly on Linux and datacenter GPUs. Lemonade uses Vulkan instead for consumer PCs because Vulkan is more widely compatible.
- "ONNX" — Open Neural Network Exchange — a file format for AI models that many different runtimes can load. AMD's ryzenai-llm uses ONNX format.
- "Hugging Face" — The GitHub of AI models — a website where researchers and companies publish AI models for anyone to download.
- "inference" — When an AI model processes input and generates output. Training (teaching the AI) is separate; inference is using the trained AI.
- "matrix multiplication" — The core math operation in AI. Neural networks are essentially billions of multiplications and additions — that's why specialized chips help so much.
- "iGPU" — Integrated GPU — a GPU built into the same chip as the CPU, sharing the system RAM. Less powerful than a dedicated GPU but much more power-efficient.
- "dGPU" — Dedicated GPU — a separate graphics card with its own video memory (like a Radeon RX 9070). More powerful but uses more power.

## Code Snippets
From `src/cpp/resources/server_models.json` (use in Screen 4):
```json
"Phi-4-mini-instruct-Hybrid": {
  "checkpoint": "amd/Phi-4-mini-instruct-onnx-ryzenai-1.7-hybrid",
  "recipe": "ryzenai-llm",
  "suggested": true,
  "size": 5.1
}
```

Also useful context — the 5 recipe types:
- `ryzenai-llm` → AMD's NPU/Hybrid runtime (ONNX format)
- `llamacpp` → llama.cpp (GGUF format, CPU/GPU via Vulkan or ROCm)
- `whispercpp` → whisper.cpp (speech recognition)
- `sd-cpp` → stable-diffusion.cpp (image generation)
- `kokoro` → Kokoro ONNX TTS (text to speech)

## Tone Notes
- This module is about "why does this design make sense?" — not just listing facts.
- The film crew metaphor should feel natural, not forced.
- Emphasize the SIMULTANEITY — three chips working at the same time is the key differentiator.
- The quiz should feel like "can I figure this out?" not a memory test.
