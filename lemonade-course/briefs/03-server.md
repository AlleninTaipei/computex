# Module 3 Brief: The Control Tower

## Meta
- **File to write:** `modules/03-server.html`
- **Module ID:** `module-3`
- **Background:** `var(--color-bg)` (warm off-white — odd module)
- **Previous module:** Module 2 — Three Chips, Three Jobs
- **Next module:** Module 4 — 159 Models, One Catalog

## Teaching Arc
**Metaphor:** Air traffic control. An airport has dozens of planes (AI models) that want to use the runway (hardware). The control tower (C++ Server / Router) decides which plane lands when, prevents collisions (exclusive NPU access), and keeps the whole system safe and efficient.

**Opening hook:** "When you type a message into the Lemonade chat and hit Enter, where does it go? It travels to a C++ program running silently in the background — a server that's managing multiple AI models, routing requests, and making sure two models don't try to use the NPU at the same time."

**Key insight:** Lemonade's server is OpenAI-compatible — it speaks the exact same language as ChatGPT's API. This means any app built for OpenAI works with Lemonade by changing one line of code.

**Learning goal:** Learners understand the request-to-response journey, what the Router does (model loading, LRU eviction, NPU exclusivity), and why OpenAI API compatibility matters enormously for their own apps.

## Screens (5 total)

### Screen 1: The Server — Your Local AI Control Tower
Open with the airport metaphor. Then establish what the server IS:

Pattern cards (2 columns):
- ⚙️ **The C++ Server** — Runs on port 13305. Always listening. Receives AI requests from any app and dispatches them to the right backend.
- 🔀 **The Router** — The traffic director inside the server. Manages which models are loaded, unloads old ones, prevents conflicts.
- 📋 **ModelManager** — Knows about all 159 models. Handles downloading, caching, and describing models.
- 🔌 **BackendManager** — Knows how to install and launch inference engines (llama.cpp, whisper.cpp, etc.).

Callout (callout-info): "The server is a compiled C++ binary — it starts in milliseconds and uses almost no CPU when idle. It's designed to run quietly in the background, always ready."

### Screen 2: Data Flow — A Request's Journey
Full data flow animation from app to response.

data-steps (NO single quotes inside labels — use apostrophes avoided or &apos;):
1. {"highlight":"flow-actor-1","label":"You type a message and hit send"}
2. {"highlight":"flow-actor-2","label":"App sends an OpenAI-format HTTP request to localhost:13305","packet":true,"from":"actor-1","to":"actor-2"}
3. {"highlight":"flow-actor-3","label":"Server receives the request, identifies the target model","packet":true,"from":"actor-2","to":"actor-3"}
4. {"highlight":"flow-actor-4","label":"Router checks: is the model loaded? If not, load it first","packet":true,"from":"actor-3","to":"actor-4"}
5. {"highlight":"flow-actor-5","label":"Backend (llama.cpp / ryzenai-llm) runs the AI inference","packet":true,"from":"actor-4","to":"actor-5"}
6. {"highlight":"flow-actor-1","label":"Tokens stream back to you in real time","packet":true,"from":"actor-5","to":"actor-1"}

Actors:
- flow-actor-1: You / App (🧑) [actor-1 vermillion]
- flow-actor-2: HTTP Layer (🌐) [actor-2 teal]
- flow-actor-3: Server (⚙️) [actor-3 plum]
- flow-actor-4: Router (🔀) [actor-4 golden]
- flow-actor-5: Backend (🤖) [actor-5 forest]

### Screen 3: Code ↔ English — The Router's Load Logic
Show actual code from `src/cpp/server/router.cpp` lines 211-240:

```cpp
void Router::load_model(const std::string& model_name,
                       const ModelInfo& model_info,
                       RecipeOptions options,
                       bool do_not_upgrade) {

    std::unique_lock<std::mutex> lock(load_mutex_);

    while (is_loading_) {
        load_cv_.wait(lock);
    }

    is_loading_ = true;

    WrappedServer* existing = find_server_by_model_name(model_name);
    if (existing) {
        existing->update_access_time();
        is_loading_ = false;
        load_cv_.notify_all();
        return;
    }
```

English translation (line by line):
- `void Router::load_model(...)` → "A function that loads an AI model into memory so it can be used"
- `std::unique_lock<std::mutex> lock(load_mutex_)` → "Grab a lock — like a 'do not disturb' sign. Only one model can load at a time."
- `while (is_loading_)` → "If another model is currently loading, wait patiently"
- `load_cv_.wait(lock)` → "Sleep until the other load finishes, then wake up"
- `is_loading_ = true` → "Mark ourselves as 'loading in progress'"
- `WrappedServer* existing = find_server_by_model_name(model_name)` → "Check if this model is already loaded"
- `if (existing)` → "If it IS already in memory..."
- `existing->update_access_time()` → "Note the current time (for LRU tracking — more on this below)"
- `return` → "Nothing to do — model is already ready"

Callout (callout-accent): "The mutex (locking mechanism) prevents two models from loading simultaneously — which could corrupt GPU memory or crash the NPU driver. This is a real engineering safety measure, not boilerplate."

### Screen 4: LRU Eviction — The Hotel with Limited Rooms
**Metaphor switch:** Hotel rooms. The server has limited GPU memory (like a hotel with a fixed number of rooms). When a new model wants to "check in" but the hotel is full, the model that was used longest ago ("Least Recently Used") gets its room given away.

Visual diagram — a "hotel" with 3 slots:
- Show 3 boxes: "Room 1: Gemma-3 (loaded 5 min ago)", "Room 2: Phi-4 (loaded 1 min ago)", "Room 3: EMPTY"
- New request comes in: "DeepSeek-R1 wants to load"
- Room 3 is empty → DeepSeek loads in
- Another request: "Mistral wants to load" — no room! → Gemma-3 (oldest) gets evicted
- Mistral loads in Room 1

NPU special rule callout (callout-warning): "The NPU is different from GPU. The NPU operates on strict exclusivity — only ONE model can use the NPU at a time. When a new NPU model loads, ALL current NPU models are immediately evicted. No exceptions."

Show the NPU exclusivity code from router.cpp:
```cpp
if (device_type & DEVICE_NPU) {
    if (model_info.recipe == "ryzenai-llm" || 
        model_info.recipe == "whispercpp") {
        if (has_npu_server()) {
            evict_all_npu_servers();
        }
    }
}
```
English:
- `if (device_type & DEVICE_NPU)` → "If this new model wants to use the NPU..."
- `if (model_info.recipe == "ryzenai-llm" || ...)` → "...and it's an exclusive-access recipe (ryzenai-llm or whispercpp)..."
- `if (has_npu_server())` → "...and there's already something on the NPU..."
- `evict_all_npu_servers()` → "...kick everything off the NPU. This new model gets sole access."

### Screen 5: Quiz — Debugging the Server
Multiple-choice quiz (id="quiz-module3"):

Question 1: "A user reports that switching between Whisper (speech) and a Hybrid LLM is slow — the first request after switching takes 10-15 seconds. Based on what you learned, what's happening?"
- data-correct="option-b"
- a) The server has a bug in its routing logic
- b) The NPU evicts the old model and loads the new one — this is expected behavior due to exclusive NPU access  ✓
- c) The GPU is overloaded
- explanation-right: "Exactly! Whisper and ryzenai-llm both require exclusive NPU access. Switching between them means the Router evicts the current NPU model and loads the new one — that load time is the 10-15 seconds. This is by design, not a bug."
- explanation-wrong: "Hint: think about what both Whisper and Hybrid LLMs have in common hardware-wise — and what the NPU exclusivity rule says about that."

Question 2: "You want to run 3 different LLMs at the same time (for a comparison app). The default max-loaded-models is set to 1. What command would help?"
- data-correct="option-a"
- a) lemonade config set max-loaded-models=3  ✓
- b) lemonade backends --parallel=3
- c) lemonade launch --gpu-split
- explanation-right: "Right. The Router respects the max-loaded-models configuration. Set it to 3 and the Router will allow up to 3 models loaded simultaneously in GPU memory. The COMPUTEX demo uses `lemonade config set max-loaded-models=9`."
- explanation-wrong: "The Router uses a configurable limit for how many models can stay loaded. The config command lets you change that limit."

Question 3: "You build an app with the Python openai library, pointing it at https://api.openai.com. You want to switch it to Lemonade. What do you change?"
- data-correct="option-c"
- a) Rewrite the entire app using Lemonade's custom SDK
- b) You cannot switch — Lemonade uses a different protocol
- c) Change base_url to http://localhost:13305/api/v1 and set api_key to any string  ✓
- explanation-right: "Exactly! Lemonade speaks OpenAI's API format. One URL change is all it takes. The api_key is required by the library but Lemonade ignores its value — any string works."
- explanation-wrong: "Lemonade was designed to be a drop-in replacement for the OpenAI API. Think about what that means for an app already using OpenAI."

## Interactive Elements Checklist
- [x] Pattern Cards (Screen 1) — 4 server components
- [x] Data Flow Animation (Screen 2) — request to response
- [x] Code ↔ English Translation (Screen 3) — load_model mutex logic
- [x] Code ↔ English Translation (Screen 4) — NPU exclusivity code
- [x] Multiple-Choice Quiz (Screen 5) — 3 debugging scenarios

## Tooltips Required
- "C++" — A compiled programming language known for speed. Unlike Python (interpreted line by line), C++ is converted to machine code before running — making it 10-100x faster for server workloads.
- "port 13305" — A "port" is like a door number on a network address. Programs listen for messages on specific ports. Lemonade picks 13305 as its dedicated listening port.
- "HTTP" — HyperText Transfer Protocol — the language of the web. When your browser fetches a webpage (or your app calls an API), it speaks HTTP.
- "mutex" — Short for "mutual exclusion." A mutex is a lock that ensures only one thread can access a shared resource at a time — preventing race conditions and crashes.
- "LRU" — Least Recently Used — a strategy where the item that was used longest ago gets removed first when space runs out. Used in caches and model managers everywhere.
- "eviction" — In the context of model loading, eviction means unloading a model from memory to make room for a new one.
- "token" — The basic unit of text in LLMs. One token is roughly one word or part of a word. "Tokens stream back" means the model sends words back one at a time as it generates them.
- "inference" — Running an AI model to get output. As opposed to training (teaching the model).
- "binary" — A compiled executable program — the final form of C++ code after it has been translated to machine instructions.
- "OpenAI API" — The interface that OpenAI provides for ChatGPT and other models. Lemonade mimics this interface exactly so existing apps work without changes.

## Code Snippets
From `src/cpp/server/router.cpp` lines 211-250:
```cpp
void Router::load_model(const std::string& model_name,
                       const ModelInfo& model_info,
                       RecipeOptions options,
                       bool do_not_upgrade) {

    std::unique_lock<std::mutex> lock(load_mutex_);

    while (is_loading_) {
        load_cv_.wait(lock);
    }
    is_loading_ = true;

    WrappedServer* existing = find_server_by_model_name(model_name);
    if (existing) {
        existing->update_access_time();
        is_loading_ = false;
        load_cv_.notify_all();
        return;
    }
```

NPU exclusivity code from `src/cpp/server/router.cpp`:
```cpp
if (device_type & DEVICE_NPU) {
    if (model_info.recipe == "ryzenai-llm" || 
        model_info.recipe == "whispercpp") {
        if (has_npu_server()) {
            evict_all_npu_servers();
        }
    }
}
```
