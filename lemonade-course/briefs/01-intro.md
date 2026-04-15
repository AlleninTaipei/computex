# Module 1 Brief: Your PC as an AI Factory

## Meta
- **File to write:** `modules/01-intro.html`
- **Module ID:** `module-1`
- **Background:** `var(--color-bg)` (warm off-white)
- **Previous module:** none
- **Next module:** Module 2 — Three Chips, Three Jobs

## Teaching Arc
**Metaphor:** A concert hall. ChatGPT is a concert streamed live over the internet — your audio travels to a remote venue, gets processed, and streams back. Lemonade is a concert happening in *your own living room* — same music, zero internet required, completely private.

**Opening hook:** "Imagine asking your AI assistant something embarrassing — maybe a health question, or a business secret. Every word you type leaves your computer and travels to a server farm in another country. With Lemonade, the AI lives *on your PC*. Nothing leaves. Ever."

**Key insight:** Local AI isn't just about privacy — it's about owning your AI stack. No API bills, no rate limits, no internet required. And thanks to Lemonade, you don't need a PhD to set it up.

**Learning goal:** By the end, learners understand what Lemonade is, what "local AI" means, and can visualize the 5-act COMPUTEX demo as a concrete example of what the system can do.

## Screens (5 total)

### Screen 1: Cloud AI vs Local AI
- Intro paragraph (2 sentences max): The AI revolution created an invisible dependency — everything runs on someone else's server.
- Side-by-side visual comparison:
  - LEFT: Cloud AI — user → internet → data center → response back. Label: "Your words travel to a server farm. Latency. Cost. Privacy risk."
  - RIGHT: Local AI (Lemonade) — user → your PC → response. Label: "Everything stays on your machine. Instant. Private. Free."
- Callout box (callout-info): "Lemonade is open-source, free, and runs on regular PC hardware — no special cloud account needed."

### Screen 2: What Lemonade Can Do (4 modalities as pattern-cards)
Intro: "Lemonade isn't just a chatbot. It's a full AI platform covering four totally different types of AI — all running on your PC."
- 4 pattern cards:
  1. 🗣️ **Speech to Text** — Talk into your mic, get a transcript. Powered by Whisper, runs on NPU.
  2. 🧠 **Text Generation (LLM)** — Chat, summarize, analyze. Like ChatGPT but on your machine.
  3. 🔊 **Text to Speech** — Turn text into lifelike voice. Powered by Kokoro, runs on CPU.
  4. 🎨 **Image Generation** — Create images from prompts. Powered by Stable Diffusion, runs on GPU.
- Below: "All four can run simultaneously on the same PC."

### Screen 3: The COMPUTEX Demo — 5 Acts
Intro: "At COMPUTEX 2026, AMD demonstrated Lemonade running a fully automated, 5-act live show on a single PC. Here's what each act did:"

Use numbered step cards:
1. 🎤 **Act 1: Speech In** — Whisper model converts voice to text, running entirely on the NPU chip. CPU and GPU sit idle.
2. 🧠 **Act 2: The Brain Thinks** — DeepSeek LLM processes the text. NPU handles part of the model, GPU handles the rest — simultaneously (Hybrid mode).
3. 🔊 **Act 3: Speech Out** — Kokoro model speaks the response aloud. Runs on CPU while NPU and GPU are free.
4. 🎨 **Act 4: Image Generated** — Stable Diffusion creates a visual. GPU takes over.
5. 💬 **Act 5: AI Debate** — 5 different AI models argue simultaneously, all running on the GPU.

Below: "Three different chips. Five different AI tasks. One laptop. No cloud."

### Screen 4: The Group Chat — Components Introducing Themselves
Group chat animation (id="chat-intro") where the main system components introduce themselves:

Messages:
- data-sender="app": "Hi! I'm the Desktop App (Electron). You talk to me when you browse models or start a chat."
- data-sender="server": "I'm the C++ Server — the engine running on port 13305. All AI requests come through me."
- data-sender="router": "I'm the Router. When a request arrives, I decide which AI backend handles it."
- data-sender="backend": "And I'm a Backend — could be llama.cpp, whisper.cpp, or the NPU runtime. I do the actual AI math."
- data-sender="app": "Together we make local AI feel like cloud AI — just without the cloud."

Actor colors:
- app: var(--color-actor-1)  [vermillion]
- server: var(--color-actor-2)  [teal]
- router: var(--color-actor-3)  [plum]
- backend: var(--color-actor-4)  [golden]

Avatar initials: App="🖥", Server="⚙", Router="🔀", Backend="🤖"

### Screen 5: Why This Matters for Vibe Coders
Intro: "You built something with AI. Now imagine making it run offline, instantly, privately — for free."

3 callout-style benefit cards (use pattern-cards):
- 💸 **No API bills** — Run 1,000 requests or 1,000,000. The cost is the same: $0.
- 🔒 **Total privacy** — Medical records, business secrets, personal notes — never leave your machine.
- ⚡ **No rate limits** — No "you've hit your limit" errors at 2am when you're in flow.

Callout box (callout-accent): "Key insight: Lemonade exposes an OpenAI-compatible API at `http://localhost:13305`. This means **any app built for ChatGPT works with Lemonade** — just change one URL."

## Interactive Elements Checklist
- [x] Group Chat Animation (Screen 4) — components introduce themselves
- [x] Pattern Cards (Screen 2) — 4 modalities; (Screen 5) — 3 benefits
- [x] Numbered Step Cards (Screen 3) — 5-act demo
- [x] Callout boxes (Screens 1, 5)
- NOTE: No quiz in module 1 — it's the hook. Tooltips throughout are mandatory.

## Tooltips Required
- "NPU" — Neural Processing Unit — a special chip designed specifically for AI math. Like a GPU but dedicated purely to AI tasks.
- "LLM" — Large Language Model — the type of AI behind ChatGPT. It's a giant program trained on billions of text examples that can understand and generate human language.
- "API" — Application Programming Interface — a standardized way for software to talk to other software. Like a menu at a restaurant: you order from the menu (API), the kitchen (server) does the work.
- "open-source" — Software where the code is publicly available for anyone to read, modify, or use for free.
- "Electron" — A framework for building desktop apps using web technologies (HTML, CSS, JavaScript). Used by VS Code, Slack, and many others.
- "Whisper" — An AI model made by OpenAI that converts spoken audio into text.
- "Stable Diffusion" — An AI model that generates images from text descriptions.
- "Kokoro" — A text-to-speech AI model that converts written text into spoken audio.
- "NPU" is most important — tooltip it every time it first appears in a new screen.
- "port 13305" — A "port" is like a door number on a building. Port 13305 is the specific door Lemonade's server listens at for incoming requests.

## Code Snippets (for reference, not required in this module)
None needed in module 1 — it's conceptual. Save code for modules 2+.

## Tone & Style Notes
- This is the "why should I care?" module. Keep it punchy and exciting.
- The learner may have never heard of Lemonade. Start with the relatable pain (privacy, cost, latency) before introducing the solution.
- Use concrete examples, not abstract explanations.
- Avoid jargon without tooltips.
