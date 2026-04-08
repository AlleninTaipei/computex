 Computex 動態展 — 完整計畫 v2                                                 
                                                                                
  硬體：Ryzen AI 9 HX 375 | XDNA2 55 TOPS | Radeon 890M (16CU RDNA3.5) | 無 dGPU
                                                                                
  ---                                                                           
  硬體分工總覽                                                                  
                                                                                
  XDNA2 NPU (55 TOPS)    →  語音辨識、Hybrid LLM                                
  Radeon 890M iGPU       →  影像生成 (ROCm)、LLM 加速 (Vulkan)                  
  CPU                    →  TTS 語音合成、協調排程                              
                                                                                
  三個運算單元全部有事做，敘事完整。                                            
                                                                                
  ---                                                                           
  五幕劇本（全幕復活）                                                          
                                                                                
  第一幕：語音進來
                                                                                
  硬體：XDNA2 NPU ｜ 模型：Whisper-Large-v3-Turbo                             

  python examples/realtime_transcription.py --model Whisper-Large-v3-Turbo

  主持人對麥克風說話，大螢幕即時顯示逐字稿。

  ▎ 「55 TOPS 的 NPU 在跑 Whisper，CPU 和 GPU 完全沒動，留給後面用。」          
   
  ---                                                                           
  第二幕：大腦思考
                  
  硬體：XDNA2 NPU + CPU Hybrid ｜ 模型：Qwen3-8B-Hybrid
                                                                                
  lemonade-server run Qwen3-8B-Hybrid
                                                                                
  ▎ 「模型的權重切割——部分層在 NPU 跑，剩餘層在 CPU 跑，同時進行，這是 Ryzen AI 
  的 Hybrid 推論架構。」                                                        
                                                                                
  ---         
  第三幕：說話回來
                  
  硬體：CPU ｜ 模型：kokoro-v1
                                                                                
  python examples/api_text_to_speech.py
                                                                                
  ▎ 「CPU 做語音合成，剛才 NPU 和 iGPU 忙的時候，CPU 沒有閒著。」               
   
  ---                                                                           
  第四幕：畫出來

  硬體：Radeon 890M ROCm ｜ 模型：SD-Turbo

  python examples/api_image_generation.py --backend rocm
                                                                                
  ▎ 「Radeon 890M，RDNA 3.5 架構，ROCm 加速 Stable 
  Diffusion。沒有獨顯，一樣跑影像生成。」                                       
              
  ---
  第五幕：9 個 AI 同時辯論
                                                                                
  硬體：Radeon 890M Vulkan ｜ 模型：小型 GGUF
                                                                                
  lemonade-server serve --max-loaded-models 9
  # 開啟 examples/llm-debate.html

  890M 記憶體限制，選用輕量模型組合：

  ┌────────────────────────────┬─────────┐
  │            模型            │  大小   │
  ├────────────────────────────┼─────────┤
  │ Qwen3-0.6B-GGUF            │ 0.38 GB │
  ├────────────────────────────┼─────────┤
  │ Qwen3-1.7B-GGUF            │ 1.06 GB │                                      
  ├────────────────────────────┼─────────┤
  │ LFM2-1.2B-GGUF             │ 0.73 GB │                                      
  ├────────────────────────────┼─────────┤
  │ Llama-3.2-1B-Instruct-GGUF │ 0.83 GB │
  ├────────────────────────────┼─────────┤
  │ Phi-4-mini-instruct-GGUF   │ 2.49 GB │
  └────────────────────────────┴─────────┘

  五個模型同時串流辯論，總計約 5.5 GB，890M 可以承受。

  ---
  展前準備指令（Windows PowerShell）
                                                                                
  # 安裝 Lemonade Server（先從官網下載 MSI）
  # https://lemonade-server.ai/install_options.html#windows                     
              
  # 啟動 server                                                                 
  lemonade-server serve --max-loaded-models 9
                                                                                
  # 下載所有 demo 模型（一次跑完）
  lemonade-server pull Whisper-Large-v3-Turbo
  lemonade-server pull Qwen3-8B-Hybrid
  lemonade-server pull kokoro-v1                                                
  lemonade-server pull SD-Turbo
  lemonade-server pull Qwen3-0.6B-GGUF                                          
  lemonade-server pull Qwen3-1.7B-GGUF
  lemonade-server pull LFM2-1.2B-GGUF                                           
  lemonade-server pull Llama-3.2-1B-Instruct-GGUF
  lemonade-server pull Phi-4-mini-instruct-GGUF                                 
                                                                                
  # 安裝 Python 依賴
  pip install openai pyaudio websockets                                         
                                                                                
  ---
  核心話術（修訂版）                                                            
                    
  ┌─────────────────────┬─────────────────────────────────────────────────┐
  │       舊話術        │                    修訂話術                     │     
  ├─────────────────────┼─────────────────────────────────────────────────┤
  │ 「GPU 和 NPU 並行」 │ 「三個矽晶片各司其職：NPU 聽、CPU 說、iGPU 畫」 │     
  ├─────────────────────┼─────────────────────────────────────────────────┤
  │ 「需要獨顯」        │ 「不需要獨顯——這就是 Ryzen AI 的意義」          │     
  ├─────────────────────┼─────────────────────────────────────────────────┤
  │ 「雲端替代方案」    │ 「這台筆電，就是一座完整的 AI 工廠」            │     
  └─────────────────────┴─────────────────────────────────────────────────┘     
   
  ---                                                                           
  選配：Angel 語音主持層
                                                                                
  若要加上「Hello Angel」語音驅動整套 demo，架構已經就緒，到 Windows 機器 clone
  下來後，我可以直接幫你寫 orchestrator.py。 

