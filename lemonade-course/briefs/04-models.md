# Module 4 Brief: 159 Models, One Catalog

## Meta
- **File to write:** `modules/04-models.html`
- **Module ID:** `module-4`
- **Background:** `var(--color-bg-warm)` (warm — even module)
- **Previous module:** Module 3 — The Control Tower
- **Next module:** Module 5 — Plug In Anything

## Teaching Arc
**Metaphor:** A vinyl record shop. server_models.json is the store's catalog — every record (model) listed with its label (checkpoint/source), genre (recipe), and format (size). You can browse the catalog, order a record (lemonade pull), and the store plays it on the right turntable (backend) when you ask.

**Opening hook:** "There are 159 AI models in Lemonade's built-in catalog. They cover text, image, speech, and audio — from 340 MB whisper models to 69 GB image generators. But they all share one secret: they're described in a single JSON file that controls everything from download source to which chip runs them."

**Key insight:** server_models.json is the "single source of truth" for the entire model ecosystem. It's the file you'd edit to add your own custom model or troubleshoot why a model isn't available.

**Learning goal:** Learners can read and understand a server_models.json entry, know what checkpoint/recipe/backends mean, understand how Hugging Face integrates, and know how to add a custom GGUF model.

## Screens (5 total)

### Screen 1: The Catalog — server_models.json
Open with the vinyl record shop metaphor.

Then show a "stat wall" (big numbers as hero visual):
- **159** total models in the catalog
- **5** recipe types (llamacpp, ryzenai-llm, whispercpp, sd-cpp, kokoro)
- **81** AMD-optimized models (amd/ prefix on Hugging Face)
- **36** third-party GGUF models (unsloth/, etc.)
- **4** modalities: text, image, speech, TTS

Callout (callout-info): "The catalog is stored in `src/cpp/resources/server_models.json` — a plain text file you can open in any editor. Each model is one entry with 4-5 fields."

### Screen 2: Anatomy of a Model Entry
Show side-by-side translation for TWO model entries — one simple (Kokoro TTS) and one complex (Whisper with NPU cache):

**Entry 1 — Simple (kokoro-v1):**
```json
"kokoro-v1": {
  "checkpoint": "mikkoph/kokoro-onnx",
  "recipe": "kokoro",
  "suggested": true,
  "labels": ["tts", "speech"],
  "size": 0.34
}
```
English:
- `"kokoro-v1"` → Model's name — what you type: `lemonade run kokoro-v1`
- `"checkpoint": "mikkoph/kokoro-onnx"` → Download from Hugging Face: user "mikkoph", repo "kokoro-onnx"
- `"recipe": "kokoro"` → Use the Kokoro ONNX inference engine (specialized for TTS)
- `"suggested": true` → Show in the "Recommended" list in the Model Manager UI
- `"labels": ["tts", "speech"]` → Tags for filtering in the UI
- `"size": 0.34` → Only 340 MB — tiny! Great for laptops.

**Entry 2 — With NPU acceleration (Whisper-Large-v3-Turbo):**
```json
"Whisper-Large-v3-Turbo": {
  "checkpoints": {
    "main": "ggerganov/whisper.cpp:ggml-large-v3-turbo.bin",
    "npu_cache": "amd/whisper-large-turbo-onnx-npu:ggml-large-v3-turbo-encoder-vitisai.rai"
  },
  "recipe": "whispercpp"
}
```
English:
- `"checkpoints"` (plural!) → Two separate files to download — one for CPU/GPU, one for NPU
- `"main"` → The base Whisper model in GGUF format — used when no NPU is present
- `"npu_cache"` → An AMD-compiled NPU-optimized encoder — downloaded separately, used automatically when XDNA is detected
- `"recipe": "whispercpp"` → Use whisper.cpp as the inference engine

Callout (callout-accent): "Notice 'npu_cache' — this is a pre-compiled version of Whisper's audio encoder, optimized specifically for AMD XDNA NPU. Lemonade downloads BOTH files and switches between them automatically based on your hardware."

### Screen 3: The Hugging Face Connection
**Metaphor:** GitHub is where code lives. Hugging Face is where AI models live.

Show a visual diagram:
- Box 1: "Hugging Face Hub (huggingface.co)" — "82,000+ AI models, publicly hosted. Free to download."
- Box 2: "AMD's HF Organization (amd/)" — "81 models, pre-converted and optimized for Ryzen AI hardware. Official AMD releases."
- Box 3: "Third-party models (unsloth/, stabilityai/, etc.)" — "Community-quantized models, wider variety"
- Arrow from each → server_models.json → Lemonade Model Manager

Show lemonade pull in action:
```
lemonade pull Phi-4-mini-instruct-Hybrid
```
Step cards:
1. Look up "Phi-4-mini-instruct-Hybrid" in server_models.json → find checkpoint: "amd/Phi-4-mini-instruct-onnx-ryzenai-1.7-hybrid"
2. Connect to Hugging Face and download the ONNX model files (~5.1 GB)
3. Cache locally at `~/.lemonade/models/`
4. Model is ready — appear in the UI and `lemonade list`

Callout (callout-info): "You can also import custom models. Drop any GGUF file in the Lemonade models folder, or add a Hugging Face model URL in the Model Manager's 'Add Custom Model' panel."

### Screen 4: The Model Manager UI
Show the Model Manager as an interactive architecture diagram (click to learn each part):

```html
<div class="arch-diagram">
  <div class="arch-zone arch-zone-browser">
    <h4 class="arch-zone-label">Model Manager UI</h4>
    <div class="arch-component" data-desc="Browseable list of all 159 built-in models. Filter by recipe, size, or hardware. Click to download.">
      <div class="arch-icon">📋</div>
      <span>Browse Catalog</span>
    </div>
    <div class="arch-component" data-desc="Shows download progress, size, and estimated time. Downloads happen in the background — you can still chat while a model downloads.">
      <div class="arch-icon">⬇️</div>
      <span>Download Manager</span>
    </div>
    <div class="arch-component" data-desc="Add any GGUF or ONNX model from Hugging Face by pasting its URL. Lemonade auto-detects the recipe.">
      <div class="arch-icon">➕</div>
      <span>Add Custom Model</span>
    </div>
    <div class="arch-component" data-desc="See which models are currently loaded in memory and how much VRAM they're using. One click to unload.">
      <div class="arch-icon">🗂️</div>
      <span>Loaded Models</span>
    </div>
  </div>
  <div class="arch-description" id="arch-desc">Click any component to learn what it does</div>
</div>
```

### Screen 5: Quiz — Working with the Model Catalog
Multiple-choice quiz (id="quiz-module4"):

Question 1: "You find a GGUF model on Hugging Face that is NOT in Lemonade's built-in catalog. How can you use it in Lemonade?"
- data-correct="option-b"
- a) You cannot — Lemonade only supports models in server_models.json
- b) Use the Add Custom Model panel in the Model Manager, or paste the Hugging Face URL  ✓
- c) Manually edit server_models.json and add the recipe
- explanation-right: "Correct! Lemonade supports custom models via the Add Custom Model panel. You paste the Hugging Face URL (or file path) and Lemonade downloads and registers it — no JSON editing required."
- explanation-wrong: "While editing server_models.json is technically possible, the Model Manager UI has a dedicated Add Custom Model panel that handles this without touching config files."

Question 2: "A model shows 'npu_cache' in its checkpoints. What does this mean for your system?"
- data-correct="option-c"
- a) The model requires an NPU — it will fail on CPU-only systems
- b) The model will only run on the NPU, not the GPU
- c) The model has two versions: one for CPU/GPU and one optimized for NPU. Lemonade downloads both and picks automatically.  ✓
- explanation-right: "Exactly! The npu_cache is an AMD-compiled NPU-optimized encoder that runs alongside the main model. On systems without NPU, Lemonade just uses the main checkpoint. This is automatic — you never have to choose."
- explanation-wrong: "npu_cache is additive, not exclusive. The model works fine without NPU; the cache just makes it faster when NPU is present."

Question 3: "You want to compare two models for response quality. Which config setting in the CLI would let you keep both loaded in memory at the same time?"
- data-correct="option-a"
- a) lemonade config set max-loaded-models=2  ✓
- b) lemonade pull --dual-model
- c) Add both models to server_models.json with "simultaneous": true
- explanation-right: "Right — max-loaded-models is the Router's limit for how many model backends can stay in memory. Set it to 2 and both models stay warm, ready to respond instantly without waiting for a reload."
- explanation-wrong: "The Model Manager and server_models.json don't control how many models stay loaded in memory — that's the Router's job, controlled via the config setting."

## Interactive Elements Checklist
- [x] Stat Wall / Hero Visual (Screen 1) — big numbers
- [x] Code ↔ English Translation (Screen 2) — TWO model entries (kokoro + whisper)
- [x] Numbered Step Cards (Screen 3) — lemonade pull flow
- [x] Interactive Architecture Diagram (Screen 4) — Model Manager UI
- [x] Multiple-Choice Quiz (Screen 5) — 3 practical questions

## Tooltips Required
- "JSON" — JavaScript Object Notation — a human-readable file format for structured data. Like a well-organized spreadsheet but as a text file. Used everywhere in software for configuration and data exchange.
- "ONNX" — Open Neural Network Exchange — a standardized file format for AI models. AMD pre-converts models to ONNX format optimized for their NPU hardware.
- "GGUF" — A compressed AI model file format used by llama.cpp. Stores model weights efficiently — a 7B parameter model might be 4-8 GB in GGUF format.
- "checkpoint" — In AI, a checkpoint is a saved snapshot of a model's learned weights. The "checkpoint" field in server_models.json tells Lemonade where to download those weights from.
- "quantization" — Compressing an AI model by reducing the precision of its numbers. A full-precision model uses 32-bit numbers; quantized versions use 4-8 bits, making them 4-8x smaller with minimal quality loss.
- "Hugging Face" — The primary platform for sharing AI models — like GitHub but for AI. Free to use. Most open-source models are published here.
- "VRAM" — Video RAM — the memory on a GPU. Loading an AI model means copying its weights into VRAM. A 7B model needs ~4-8 GB of VRAM depending on quantization.
- "recipe" — In Lemonade, a recipe specifies which inference engine to use. Like choosing a cooking method: you can cook the same ingredients (model) differently (different engines).
- "TTS" — Text-to-Speech — AI that converts written text into spoken audio.
- "encoder" — In AI models, the encoder processes the input (e.g., audio) and converts it to a compact representation. The NPU cache for Whisper accelerates this encoding step.
