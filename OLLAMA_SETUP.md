# Ollama Setup Guide - Free, Unlimited AI

## Why Ollama?
- ✅ **100% FREE** - No API keys, no subscriptions
- ✅ **UNLIMITED** - No quotas or rate limits
- ✅ **PRIVATE** - Runs on your computer, data never leaves
- ✅ **FAST** - No internet delays
- ✅ **AVAILABLE** - Works offline

## Installation (Windows)

### Method 1: Download Installer
1. Go to: https://ollama.com/download
2. Download Windows installer
3. Run and install

### Method 2: Using Winget
```powershell
winget install Ollama.Ollama
```

## Setup

### 1. Install a Model (Choose one)

**Llama 3.2 (Recommended - 2GB)**
```powershell
ollama pull llama3.2
```

**Other Options:**
```powershell
ollama pull mistral      # 4GB - Very good quality
ollama pull phi3         # 2.3GB - Fast and efficient
ollama pull gemma2:2b    # 1.6GB - Lightweight
ollama pull qwen2.5      # 4.7GB - Excellent for reasoning
```

### 2. Verify Installation
```powershell
ollama list
```

### 3. Test It
```powershell
ollama run llama3.2
```
Type a question, then `/bye` to exit.

## Running with Your Program

1. **Make sure Ollama is running** (it auto-starts on Windows)
2. **Run your dialogue program:**
   ```powershell
   python core/1223_interactive_dialogue_embedding.py
   ```
3. **Choose option 1** (Ollama)
4. **Start chatting!**

## Troubleshooting

### Error: "Cannot connect to Ollama"
```powershell
# Start Ollama service
ollama serve
```

### Check if Ollama is running
```powershell
curl http://localhost:11434
```
Should return: "Ollama is running"

### List available models
```powershell
ollama list
```

### Remove a model to save space
```powershell
ollama rm mistral
```

## Model Comparison

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| llama3.2 | 2GB | Fast | Good | General use, conversations |
| mistral | 4GB | Medium | Excellent | Quality responses |
| phi3 | 2.3GB | Very Fast | Good | Quick responses |
| gemma2:2b | 1.6GB | Very Fast | Decent | Low-resource systems |
| qwen2.5 | 4.7GB | Medium | Excellent | Reasoning, analysis |

## Advanced Usage

### Change model in the code
Edit `1223_interactive_dialogue_embedding.py`, line ~61:
```python
self.ollama_model = "mistral"  # Change from "llama3.2" to any installed model
```

### Update Ollama
```powershell
# Download latest version from ollama.com
# Or reinstall via winget
winget upgrade Ollama.Ollama
```

## Resources
- Official site: https://ollama.com
- Model library: https://ollama.com/library
- GitHub: https://github.com/ollama/ollama
