# Module 5 Brief: Plug In Anything

## Meta
- **File to write:** `modules/05-apps.html`
- **Module ID:** `module-5`
- **Background:** `var(--color-bg)` (warm off-white — odd module)
- **Previous module:** Module 4 — 159 Models, One Catalog
- **Next module:** none (final module)

## Teaching Arc
**Metaphor:** A universal power outlet adapter. Lemonade's OpenAI-compatible API is like a travel adapter — it lets any device (app) built for one standard (OpenAI) plug into a completely different power source (local AI) without rewiring anything inside the device.

**Opening hook:** "You know that button in n8n that says 'OpenAI model'? You can point it at Lemonade. You know the GitHub Copilot extension in VS Code? You can feed it local AI. The secret is that Lemonade speaks the exact same language as ChatGPT — so every app that works with OpenAI works with Lemonade."

**Key insight:** The OpenAI API became the de facto standard for AI communication. By being fully compatible, Lemonade inherits an entire ecosystem of apps, tools, and integrations — for free. This is the most important architectural decision in the whole codebase.

**Learning goal:** Learners can connect any OpenAI-compatible app to Lemonade, understand the Python client pattern, know what the ecosystem looks like, and can describe how to build their own app on top.

## Screens (6 total)

### Screen 1: One URL to Rule Them All
Open with the power adapter metaphor.

Show a large visual: a "plug board" with 10 apps connecting to Lemonade:
- n8n, VS Code Copilot, Open WebUI, Continue, Morphik, Dify, OpenHands...
- All connected via the same wire labeled: `http://localhost:13305/api/v1`
- Central hub labeled: "Lemonade Server (OpenAI-compatible)"

Below, two text blocks side by side:
- LEFT: "Cloud AI" — `https://api.openai.com/v1` — "$$$, rate limits, sends your data to OpenAI"
- RIGHT: "Lemonade" — `http://localhost:13305/api/v1` — "$0, no limits, stays on your machine"

Callout (callout-accent): "Change ONE line. That is all it takes to switch any OpenAI app to run entirely on your PC."

### Screen 2: The Python Client — Line by Line
Show the Python example from the README. This is the core code translation of the module.

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:13305/api/v1",
    api_key="lemonade"
)

completion = client.chat.completions.create(
    model="Llama-3.2-1B-Instruct-Hybrid",
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(completion.choices[0].message.content)
```

English translation:
- `from openai import OpenAI` → "Import OpenAI's official Python library — no Lemonade-specific SDK needed"
- `client = OpenAI(...)` → "Create a client that talks to an AI server"
- `base_url="http://localhost:13305/api/v1"` → "But instead of OpenAI's servers, point it at Lemonade running on this machine"
- `api_key="lemonade"` → "OpenAI normally needs a secret key. Lemonade ignores it — any string works"
- `client.chat.completions.create(...)` → "Send a chat message to the AI"
- `model="Llama-3.2-1B-Instruct-Hybrid"` → "Use THIS specific model (must be downloaded first with lemonade pull)"
- `messages=[{"role": "user", ...}]` → "The conversation history — this is the standard chat format"
- `print(completion.choices[0].message.content)` → "Print the first response the AI gave"

Callout (callout-info): "The openai Python library is made by OpenAI and is available via `pip install openai`. Lemonade reuses it entirely — no separate SDK to install."

### Screen 3: The App Ecosystem — Group Chat
Group chat animation (id="chat-ecosystem") showing different apps connecting to Lemonade:

Actors:
- n8n: var(--color-actor-1) [vermillion], avatar "n8"
- VSCode: var(--color-actor-2) [teal], avatar "VS"
- OpenWebUI: var(--color-actor-3) [plum], avatar "OW"
- Lemonade: var(--color-actor-5) [forest], avatar "🍋"

Messages:
- data-sender="lemonade": "I am now listening on http://localhost:13305. OpenAI API is live."
- data-sender="n8n": "I am n8n workflow automation. I will send tasks through your OpenAI node."
- data-sender="lemonade": "Understood. Send your requests — I will route them to the loaded model."
- data-sender="vscode": "I am VS Code with Continue extension. I need code completions."
- data-sender="lemonade": "No problem. I see you are requesting Llama-3.2. Streaming tokens back to you now."
- data-sender="openwebui": "I am Open WebUI. I want to display a full chat interface."
- data-sender="lemonade": "Connected. You can now browse and chat with all 159 models through my API."

### Screen 4: The Realtime API — Going Beyond Text
Intro: "Lemonade isn't just text. It supports the OpenAI Realtime API for streaming audio — the same protocol used for voice assistants."

Show the realtime transcription example:

```python
# From examples/realtime_transcription.py
async with websockets.connect(
    f"ws://{host}:{port}/v1/realtime",
    subprotocols=["realtime"],
) as ws:
    await send_audio(ws, audio_queue)
```

English:
- `websockets.connect(...)` → "Open a persistent connection to Lemonade — unlike HTTP requests, this stays open the whole time"
- `f"ws://{host}:{port}/v1/realtime"` → "The realtime endpoint — ws:// means WebSocket, a two-way streaming connection"
- `subprotocols=["realtime"]` → "Identify ourselves as using the realtime protocol (OpenAI's standard)"
- `await send_audio(ws, audio_queue)` → "Stream audio chunks to Lemonade as the microphone captures them"

Pattern cards showing what the Realtime API enables:
- 🎤 **Live Transcription** — Speak into your mic, get real-time text as Whisper processes your audio
- 🗣️ **Voice Assistants** — Build Siri-like apps that listen, think, and speak back
- 📞 **Call Analysis** — Process phone calls or meetings as they happen

### Screen 5: Build Your Own — The Vibe Coder's Cheat Sheet
Three numbered step cards for building an app on Lemonade:

1. **Pick your model** — `lemonade pull Llama-3.2-1B-Instruct-Hybrid` (or browse the Model Manager UI). Choose based on: size vs quality, your hardware, CPU/GPU/NPU.
2. **Connect your tool** — Change `base_url` to `http://localhost:13305/api/v1`. Works with Python's openai library, LangChain, LlamaIndex, n8n, Open WebUI — anything OpenAI-compatible.
3. **Ship locally** — Your app now runs without internet. No API key to protect. No data leaving your machine. No monthly bill.

Callout (callout-accent): "When describing your project to an AI coding assistant, say: 'I want to use an OpenAI-compatible local endpoint at localhost:13305' — and the AI will know exactly what to do."

### Screen 6: Quiz — Building on Lemonade
Multiple-choice quiz (id="quiz-module5"):

Question 1: "You built a LangChain agent that uses OpenAI. You want to run it locally with Lemonade. What is the minimum code change needed?"
- data-correct="option-b"
- a) Replace all LangChain calls with Lemonade's SDK calls
- b) Set the OpenAI base_url to http://localhost:13305/api/v1 in your LangChain config  ✓
- c) Export your LangChain prompts and re-import into Lemonade's UI
- explanation-right: "Exactly! LangChain uses OpenAI under the hood. Redirecting the base_url is a one-line change. LangChain never knows it switched to Lemonade."
- explanation-wrong: "LangChain, like most AI frameworks, uses the openai library internally. Changing the base_url in the OpenAI client config propagates to all LangChain calls automatically."

Question 2: "Your app needs to process audio in real-time (voice commands). Which Lemonade feature enables this?"
- data-correct="option-c"
- a) The standard /v1/chat/completions endpoint with audio attachments
- b) A Python script that records audio to a file and then sends the file
- c) The WebSocket Realtime API at ws://localhost:13305/v1/realtime  ✓
- explanation-right: "Right. The Realtime API uses WebSockets for persistent, two-way streaming. Audio chunks flow to Lemonade continuously, and transcription text flows back — without waiting for the full recording to finish."
- explanation-wrong: "Real-time audio requires a persistent streaming connection, not a one-shot HTTP request. The /v1/realtime WebSocket endpoint is designed specifically for this."

Question 3: "You want to tell an AI coding agent to build a Python chatbot using Lemonade. Which description gives the clearest instructions?"
- data-correct="option-a"
- a) 'Build a chatbot using the openai Python library with base_url set to http://localhost:13305/api/v1 and api_key set to lemonade'  ✓
- b) 'Build a chatbot using Lemonade local AI'
- c) 'Build a chatbot that works offline'
- explanation-right: "This description is precise and actionable. It names the specific library (openai), the exact parameter (base_url), and the value to use. An AI coding agent can write correct code from this description without any ambiguity."
- explanation-wrong: "Vague descriptions lead to AI hallucinating APIs or asking follow-up questions. The more specific you are — library name, parameter names, exact values — the better the result."

## Interactive Elements Checklist
- [x] Pattern Cards (Screen 1) — app ecosystem visual
- [x] Code ↔ English Translation (Screen 2) — Python client example
- [x] Group Chat Animation (Screen 3) — apps connecting to Lemonade
- [x] Code ↔ English Translation (Screen 4) — Realtime WebSocket API
- [x] Numbered Step Cards (Screen 5) — build your own cheat sheet
- [x] Multiple-Choice Quiz (Screen 6) — 3 practical building scenarios

## Tooltips Required
- "OpenAI API" — The programming interface that OpenAI uses for ChatGPT and GPT-4. It has become the standard that hundreds of tools and frameworks are built around.
- "base_url" — In the openai Python library, this setting tells the client which server to talk to. Normally it points to OpenAI's cloud; you override it to point at Lemonade.
- "api_key" — A secret password used to identify yourself to an API. OpenAI requires a real key. Lemonade accepts any string because it runs locally — there is no account to authenticate against.
- "WebSocket" — A type of internet connection that stays open and allows two-way streaming. Unlike HTTP (ask-then-answer), WebSocket lets both sides send messages continuously — essential for real-time audio.
- "LangChain" — A popular Python framework for building AI applications. It connects LLMs, tools, databases, and APIs into chains of operations.
- "LlamaIndex" — Another Python framework for building AI apps, specializing in connecting LLMs to your own data (documents, PDFs, databases).
- "n8n" — A workflow automation tool (like Zapier but open-source). It can connect hundreds of services together, including AI models via the OpenAI node.
- "streaming" — Sending data in chunks as it is generated, rather than waiting for the complete result. LLMs stream tokens so you see the response word by word, not all at once.
- "endpoint" — A specific URL path on a server that handles a particular type of request. `/v1/chat/completions` is the endpoint for chat; `/v1/realtime` is for streaming audio.
- "subprotocol" — An additional layer of protocol on top of WebSocket that defines the message format. `realtime` is the subprotocol that follows OpenAI's specification for real-time audio streaming.

## Code Snippets
From `README.md` (Python client):
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:13305/api/v1",
    api_key="lemonade"
)

completion = client.chat.completions.create(
    model="Llama-3.2-1B-Instruct-Hybrid",
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(completion.choices[0].message.content)
```

From `examples/realtime_transcription.py` (WebSocket realtime):
```python
async with websockets.connect(
    f"ws://{host}:{port}/v1/realtime",
    subprotocols=["realtime"],
) as ws:
    await send_audio(ws, audio_queue)
```
