# AI Dialogue Embedding Visualizer

**Real-time 3D visualization of conversations between users and AI**

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

Transform your AI conversations into beautiful 3D semantic space visualizations. Watch dialogue flow in real-time as sentences are embedded and plotted based on their semantic meaning.

---

## 1. Main Function and Principles

### Overview
This project visualizes AI-human dialogue by converting text into high-dimensional vectors (embeddings) and reducing them to 3D space for interactive visualization. Each sentence becomes a point in 3D space, where semantically similar sentences cluster together.

### Core Principles

#### **A. Sentence Embedding**
- Uses `SentenceTransformer` (all-MiniLM-L6-v2 model) to convert sentences into 768-dimensional vectors
- Each sentence is transformed into a mathematical representation capturing its semantic meaning
- Similar sentences produce similar vectors, different meanings produce distant vectors

#### **B. Dimensionality Reduction**
- **PCA (Principal Component Analysis)** reduces 768D vectors to 3D
- Preserves maximum variance while making data human-visualizable
- Fast computation (~1 second for hundreds of sentences)
- Maintains relative distances between semantically related sentences

#### **C. Real-time AI Conversation**
- **Ollama** provides local, unlimited AI responses
- No API keys or quotas needed
- Runs llama3.2 model on your computer
- Typical response time: 2-5 seconds after initial warm-up

#### **D. Live Visualization**
- **Plotly.js** renders interactive 3D scatter plots
- Color-coded: Blue (user) vs Green (AI)
- Auto-refreshing HTML updates every 3 seconds
- Trajectory lines show conversation flow

### Mathematical Flow
```
Text Sentence
    ↓
Sentence Transformer (768D embedding)
    ↓
PCA Reduction (3D projection)
    ↓
Plotly 3D Visualization
```

### Why This Matters
- **Understand conversation patterns**: See how topics evolve
- **Identify semantic clusters**: Related ideas group together
- **Track dialogue flow**: Visual trajectory through semantic space
- **Real-time feedback**: Watch your conversation unfold spatially

---

## 2. Usage

### Prerequisites

#### **System Requirements**
- Windows 10/11 (or macOS/Linux with minor adjustments)
- Python 3.8 or higher
- 8GB RAM minimum (16GB recommended)
- 5GB disk space for Ollama + models

#### **Software Dependencies**
1. **Python packages** (installed in virtual environment):
   ```
   sentence-transformers==3.3.1
   numpy==2.3.5
   torch==2.9.1+cpu
   plotly==6.5.0
   scikit-learn==1.8.0
   requests==2.32.5
   ```

2. **Ollama** (desktop application):
   - Download: https://ollama.com/download
   - Or install via: `winget install Ollama.Ollama`

### Installation

#### **Step 1: Install Ollama**
```powershell
# Method 1: Using winget
winget install Ollama.Ollama

# Method 2: Download from https://ollama.com/download
```

#### **Step 2: Pull AI Model**
```powershell
# Download llama3.2 (2GB)
ollama pull llama3.2

# Verify installation
ollama list
```

#### **Step 3: Set Up Python Environment**
```powershell
# Navigate to project directory
cd "prject file"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Verify packages (should already be installed)
pip list
```

### Running the Program

#### **Basic Usage**
```powershell
# Make sure you're in the project directory and venv is activated
python core/1223_fast_live_dialogue.py
```

#### **What Happens**
1. ⏳ **Loading phase** (~15 seconds):
   - Loads SentenceTransformer model (~5 sec)
   - Pre-warms Ollama (~10 sec)

2. 💬 **Chat interface**:
   ```
   💬 Your message: Hello, what is AI?
   ```

3. 🤖 **Ollama responds**:
   ```
   OLLAMA: Artificial Intelligence refers to...
   ```

4. 📊 **Graph opens** (after 3+ sentences):
   - Browser opens automatically
   - 3D scatter plot appears
   - Auto-refreshes every 3 seconds

5. 🔄 **Continue chatting**:
   - Keep typing messages
   - Watch points appear in real-time
   - Graph updates automatically

#### **Commands**
| Command | Action |
|---------|--------|
| Type message + Enter | Chat with AI |
| `quit` or `exit` | End session, save final graph |
| `save` | Save current state without quitting |
| `Ctrl+C` | Interrupt and save |

### Output

#### **Directory Structure**
```
output/
└── dia_20251223_105907/
    ├── dialogue_live.html      # Interactive 3D visualization
    └── dialogue_data.json      # Complete dialogue history
```

#### **dialogue_live.html**
- Open in any browser
- Rotate, zoom, pan the 3D graph
- Hover over points to see sentence text
- Auto-refreshes during conversation
- Stops refreshing after you quit

#### **dialogue_data.json**
```json
{
  "metadata": {
    "total_sentences": 12,
    "user_sentences": 6,
    "ollama_sentences": 6,
    "turns": 3
  },
  "dialogue": [
    {
      "index": 0,
      "text": "Hello, what is AI?",
      "speaker": "user",
      "timestamp": "2025-12-23T10:59:07.123456"
    },
    ...
  ]
}
```

### Example Session

```powershell
(.venv) PS> python core/1223_fast_live_dialogue.py

======================================================================
🚀 Fast Live-Updating Dialogue Visualizer
======================================================================
Loading embedding model (this takes ~5 seconds)...
✓ Model loaded!

Pre-warming Ollama (one-time 10-second delay)...
✓ Ollama ready! Future responses will be fast.

Output: output\dia_20251223_105907

======================================================================
Instructions:
  • Type your message and press Enter
  • Graph opens ONCE and auto-refreshes every 3 seconds
  • No manual browser refresh needed!
  • Type 'quit' or 'exit' to stop
  • Type 'save' to save without chatting
======================================================================

💬 Your message: What is machine learning?

======================================================================
[Turn 1] YOU: What is machine learning?
  Added 1 sentence(s) from user

[Ollama thinking...]

OLLAMA: Machine learning is a subset of artificial intelligence...
  Added 1 sentence(s) from ollama

======================================================================
Updating graph...
  Need at least 3 sentences to visualize

💬 Your message: How does it differ from traditional programming?

======================================================================
[Turn 2] YOU: How does it differ from traditional programming?
  Added 1 sentence(s) from user

[Ollama thinking...]

OLLAMA: Unlike traditional programming where explicit rules...
  Added 1 sentence(s) from ollama

======================================================================
Updating graph...
✓ Graph opened in browser: output\dia_20251223_105907\dialogue_live.html
  Graph auto-refreshes every 3 seconds - no manual refresh needed!

💬 Your message: quit

👋 Goodbye!
   Saving final state...
   ✓ Final visualization saved (no auto-refresh)
   Final data saved to: output\dia_20251223_105907

📊 Session Summary:
   Turns: 2
   Total sentences: 4
   You: 2 | Ollama: 2
   Output: output\dia_20251223_105907
```

---

## 3. Code Structure

### Architecture Overview

```
1223_fast_live_dialogue.py
│
├── Imports & Configuration
│   ├── sentence_transformers (embedding)
│   ├── sklearn.decomposition.PCA (dimensionality reduction)
│   ├── requests (Ollama API communication)
│   └── plotly (visualization)
│
├── Class: FastDialogueVisualizer
│   │
│   ├── __init__()
│   │   ├── Initialize output directory
│   │   ├── Configure Ollama connection
│   │   ├── Load SentenceTransformer model
│   │   └── Pre-warm Ollama model
│   │
│   ├── Data Management
│   │   ├── split_sentences() - Regex sentence splitter
│   │   ├── add_message() - Incremental embedding
│   │   └── save_data() - JSON export
│   │
│   ├── AI Communication
│   │   ├── get_ai_response_streaming() - Ollama API calls
│   │   └── _prewarm_ollama() - Initial model loading
│   │
│   ├── Visualization
│   │   ├── reduce_to_3d() - PCA transformation
│   │   └── create_interactive_plot() - HTML generation
│   │
│   └── Conversation Flow
│       └── chat_turn() - Complete turn handler
│
└── Function: main()
    ├── Check Ollama availability
    ├── Initialize visualizer
    ├── Interactive loop
    └── Cleanup & summary
```

### Key Components

#### **1. FastDialogueVisualizer Class**

**Purpose**: Encapsulates all functionality for dialogue embedding and visualization

**Attributes**:
- `output_dir`: Timestamped directory for session files
- `ollama_url`: Ollama API endpoint (localhost:11434)
- `ollama_model`: Model name (llama3.2:latest)
- `model`: SentenceTransformer instance
- `sentences`: List of all dialogue sentences
- `speakers`: List of speaker labels (user/ollama)
- `timestamps`: ISO format timestamps
- `embeddings`: NumPy array of 768D vectors
- `browser_opened`: Flag to open browser only once
- `turn_count`: Conversation turn counter

#### **2. Core Methods**

##### `__init__(ollama_model, output_dir)`
- Creates timestamped output directory
- Loads SentenceTransformer model (all-MiniLM-L6-v2)
- Pre-warms Ollama by sending test query
- Initializes tracking variables

##### `split_sentences(text)`
- Uses regex to split text on sentence boundaries
- Pattern: `(?<=[.!?])\s+`
- Returns list of cleaned sentence strings

##### `add_message(text, speaker)`
- Splits text into sentences
- Embeds new sentences using SentenceTransformer
- Appends to embeddings array (incremental, not full re-embedding)
- Stores metadata (speaker, timestamp)

##### `get_ai_response_streaming(prompt)`
- Sends HTTP POST to Ollama API
- Endpoint: `http://localhost:11434/api/generate`
- Payload: `{model, prompt, stream: false}`
- 60-second timeout for response
- Returns response text or error message

##### `reduce_to_3d()`
- Applies PCA to embeddings array
- Reduces from 768D → 3D
- Returns NumPy array of 3D coordinates
- Fast computation (~1 second)

##### `create_interactive_plot(is_final=False)`
- Converts 3D coordinates to Plotly format
- Embeds data directly in HTML (no external JSON)
- Generates HTML with Plotly.js
- Conditional auto-refresh script based on `is_final` flag
- Color mapping: user=#3498db, ollama=#2ecc71

##### `save_data()`
- Exports dialogue to JSON format
- Includes metadata (counts, turns)
- Each sentence with index, text, speaker, timestamp

##### `chat_turn(user_message)`
- Complete conversation cycle:
  1. Print user message
  2. Add to embeddings
  3. Call Ollama API
  4. Add response to embeddings
  5. Update visualization
  6. Save data

#### **3. Main Function**

**Flow**:
1. Check Ollama connectivity
2. Initialize `FastDialogueVisualizer`
3. Display instructions
4. Enter interactive loop:
   - Get user input
   - Handle commands (quit/save)
   - Execute chat turn
   - Handle errors
5. Print session summary

### Data Flow Diagram

```
User Input
    ↓
split_sentences()
    ↓
add_message() → SentenceTransformer.encode()
    ↓                     ↓
    ↓               embeddings array
    ↓                     ↓
get_ai_response() ← Ollama API
    ↓
AI Response
    ↓
split_sentences()
    ↓
add_message() → SentenceTransformer.encode()
    ↓                     ↓
    ↓               embeddings array
    ↓                     ↓
reduce_to_3d() ← PCA transformation
    ↓
3D coordinates
    ↓
create_interactive_plot() → HTML file
    ↓
Browser auto-refresh
```

### HTML Structure

The generated HTML contains:

```html
<!DOCTYPE html>
<html>
<head>
    <!-- Plotly CDN -->
    <!-- CSS styling (dark theme) -->
</head>
<body>
    <!-- Status indicator (Live/Stopped, sentence count) -->
    <div class="info">🟢 Live | 📊 Sentences: 12</div>
    
    <!-- Plot container -->
    <div id="plot"></div>
    
    <script>
        // Embedded JSON data
        const plotData = {...};
        
        // Plotly traces (line + points)
        const lineTrace = {...};
        const pointTrace = {...};
        
        // Layout (dark theme, 3D scene)
        const layout = {...};
        
        // Create plot
        Plotly.newPlot('plot', [lineTrace, pointTrace], layout);
        
        // Auto-refresh (if not final)
        setTimeout(() => location.reload(), 3000);
    </script>
</body>
</html>
```

---

## 4. Development Process

### Phase 1: Initial Concept (1222_embedding3D.py)
**Goal**: Basic embedding and visualization from JSON file

**Features**:
- Load dialogue from JSON file
- Generate embeddings with SentenceTransformer
- Reduce with UMAP/t-SNE/PCA
- Create static Plotly visualizations
- Nearest neighbor analysis

**Limitations**:
- Not real-time (process existing files)
- Requires manual file input
- No AI conversation generation
- Static output only

### Phase 2: Gemini Integration (1222-1_embedding3D.py)
**Goal**: Add AI-generated dialogue capability

**Additions**:
- `generate_dialogue_samples()` function
- Gemini API integration
- Category-based prompt templates
- Automated sample generation

**Challenges**:
- API quota limitations (1,500 requests/day)
- Rate limiting issues
- Dependency on internet connectivity
- Cost concerns for heavy usage

### Phase 3: Multi-Backend Support (1223_interactive_dialogue_embedding.py)
**Goal**: Solve quota issues with alternative AI backends

**Innovations**:
- Support for 3 backends: Ollama, Gemini, HuggingFace
- Backend selection at startup
- Graceful error handling
- Ollama as recommended option

**Improvements**:
- No API quotas with Ollama
- Local processing (privacy)
- Unlimited conversations
- Offline capability

**Remaining Issues**:
- Slow response times (30+ seconds first load)
- Graph refresh caused flashing
- Separate JSON file loading issues
- Manual browser refresh required

### Phase 4: Optimization (1223_fast_live_dialogue.py) ✅ CURRENT
**Goal**: Fast, smooth, production-ready experience

**Optimizations**:
1. **Speed Improvements**:
   - Pre-warm Ollama on startup (one-time delay)
   - Incremental embedding (only new sentences)
   - PCA instead of UMAP (instant vs 10+ seconds)
   - Reduced first response time to 2-5 seconds

2. **UX Enhancements**:
   - Embedded data in HTML (no file loading)
   - Auto-refresh with page reload (simple, reliable)
   - Smart refresh control (`is_final` flag)
   - Live status indicator
   - Dark theme

3. **Reliability**:
   - Better error messages
   - Connection checks before starting
   - Graceful degradation
   - Session summaries

### Key Technical Decisions

| Decision | Rationale |
|----------|-----------|
| **Ollama over Gemini** | Unlimited, free, local, private |
| **PCA over UMAP** | 100x faster, good enough for visualization |
| **Incremental embedding** | Don't re-embed all sentences every turn |
| **Embedded HTML data** | Avoids CORS and file loading issues |
| **Page reload over AJAX** | Simpler, more reliable, good enough at 3-second intervals |
| **Pre-warming** | 10-second startup delay beats 30-second first response |
| **Dark theme** | Easier on eyes for long sessions |

### Evolution Summary

```
1222_embedding3D.py (Static file processing)
        ↓
1222-1_embedding3D.py (Add Gemini)
        ↓
1223_interactive_dialogue_embedding.py (Multi-backend + interactivity)
        ↓
1223_fast_live_dialogue.py (Optimized + smooth UX)
```

---

## 5. Resources

### Documentation

#### **Official Documentation**
- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/docs/README.md)
- [SentenceTransformers Docs](https://www.sbert.net/)
- [Plotly Python Graphing Library](https://plotly.com/python/)
- [scikit-learn PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html)

#### **Model Information**
- [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) - SentenceTransformer model
- [Llama 3.2](https://ollama.com/library/llama3.2) - Ollama model

### Key Concepts

#### **Natural Language Processing**
- [Understanding Word Embeddings](https://towardsdatascience.com/introduction-to-word-embeddings-4cf857b12edc)
- [Sentence Embeddings Explained](https://www.sbert.net/examples/applications/computing-embeddings/README.html)
- [Semantic Similarity](https://en.wikipedia.org/wiki/Semantic_similarity)

#### **Dimensionality Reduction**
- [PCA Tutorial](https://builtin.com/data-science/step-step-explanation-principal-component-analysis)
- [t-SNE vs UMAP vs PCA](https://towardsdatascience.com/tsne-vs-umap-global-structure-4d8045acba17)

#### **Large Language Models**
- [Llama Model Family](https://ai.meta.com/llama/)
- [Local LLMs with Ollama](https://ollama.com/blog)

### Dependencies

#### **Python Packages**

| Package | Version | Purpose |
|---------|---------|---------|
| sentence-transformers | 3.3.1 | Text → embeddings |
| numpy | 2.3.5 | Array operations |
| torch | 2.9.1+cpu | Neural network backend |
| plotly | 6.5.0 | Interactive visualization |
| scikit-learn | 1.8.0 | PCA transformation |
| requests | 2.32.5 | HTTP communication |

#### **External Software**
- **Ollama 0.13.5**: Local LLM runtime
- **llama3.2**: 2GB language model

### Installation Commands

```powershell
# Install Ollama
winget install Ollama.Ollama

# Pull AI model
ollama pull llama3.2

# Verify Python packages (should be pre-installed in venv)
pip install sentence-transformers numpy torch plotly scikit-learn requests
```

### Project Files

```
AI-dialogue-project/
├── core/
│   ├── 1222_embedding3D.py              # Original static version
│   ├── 1222-1_embedding3D.py            # Gemini integration
│   ├── 1223_interactive_dialogue_embedding.py  # Multi-backend
│   └── 1223_fast_live_dialogue.py       # Optimized (CURRENT)
├── data/
│   ├── database.json                    # Sample dialogue data
│   └── test.json                        # Test data
├── output/
│   └── dia_YYYYMMDD_HHMMSS/            # Session outputs
│       ├── dialogue_live.html
│       └── dialogue_data.json
├── record/
│   └── chat_record/
│       ├── 1216_chat.md
│       └── 1223_chat.md                # This session's record
├── OLLAMA_SETUP.md                      # Ollama installation guide
├── README.md                            # This file
└── requirements_full.txt                # Python dependencies
```

### Related Projects & Inspiration
- [BERTopic](https://github.com/MaartenGr/BERTopic) - Topic modeling with transformers
- [LangChain](https://python.langchain.com/) - LLM application framework
- [Embeddings Projector](https://projector.tensorflow.org/) - Google's embedding visualizer

### Further Reading
- **Research Paper**: [Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks](https://arxiv.org/abs/1908.10084)
- **Blog**: [Visualizing High-Dimensional Data](https://colah.github.io/posts/2014-10-Visualizing-MNIST/)
- **Tutorial**: [Building Chatbots with Local LLMs](https://ollama.com/blog/building-chatbots)

### Community & Support
- **Ollama Discord**: https://discord.gg/ollama
- **SentenceTransformers GitHub Issues**: https://github.com/UKPLab/sentence-transformers/issues
- **Plotly Community Forum**: https://community.plotly.com/

### Troubleshooting Resources
- [Ollama FAQ](https://github.com/ollama/ollama/blob/main/docs/faq.md)
- [Common CORS Issues](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS/Errors)
- [Python Virtual Environment Guide](https://docs.python.org/3/library/venv.html)

---

## License

MIT License - Feel free to use and modify for your projects.

## Author

Created as part of Computer Programming coursework (114-1 semester).

## Acknowledgments

- **Ollama Team** for making local LLMs accessible
- **SentenceTransformers** for excellent embedding models
- **Plotly** for interactive visualization tools
- **Meta AI** for the Llama model family

---

**Last Updated**: December 23, 2025  
**Version**: 1.0  
**Status**: Production-ready ✅
