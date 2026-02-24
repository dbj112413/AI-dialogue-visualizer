#!/usr/bin/env python3
"""
Interactive AI Dialogue Embedding Visualizer
=============================================
Real-time 3D visualization of dialogue between user and Gemini AI.

Usage:
    python core/1223_interactive_dialogue_embedding.py

Features:
    - Chat with Gemini AI interactively
    - Each message is split into sentences and embedded
    - Real-time 3D visualization updates after each exchange
    - Color-coded: User (blue) vs Gemini (red)
    - Interactive Plotly graph shows dialogue flow in semantic space
"""

import os
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

import json
import re
from pathlib import Path
import numpy as np
import torch
from datetime import datetime

from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import requests  # For Ollama API

# Import Gemini (optional)
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Import UMAP if available
try:
    import umap
    UMAP_AVAILABLE = True
except ImportError:
    UMAP_AVAILABLE = False

# Use PCA as primary method (faster and more stable for small datasets)
REDUCER = "pca"


class DialogueEmbeddingVisualizer:
    def __init__(self, ai_backend='ollama', api_key_path=None, model_name='all-MiniLM-L6-v2', output_dir='output'):
        """Initialize the dialogue visualizer.
        
        Args:
            ai_backend: 'ollama' (local, free), 'gemini' (needs API key), or 'huggingface' (free tier)
            api_key_path: Path to API key file (only for Gemini/HuggingFace)
            model_name: SentenceTransformer model for embeddings
            output_dir: Output directory for results
        """
        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(output_dir) / f"dia_{timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup AI backend
        self.ai_backend = ai_backend.lower()
        
        if self.ai_backend == 'ollama':
            # Ollama - completely free, runs locally
            self.ollama_url = "http://localhost:11434/api/generate"
            self.ollama_model = "llama3.2"  # or "mistral", "phi3", etc.
            print(f"Using Ollama (local) with model: {self.ollama_model}")
            print("  → Unlimited, free, private - no API key needed!")
            
        elif self.ai_backend == 'gemini':
            # Gemini - requires API key
            if not GEMINI_AVAILABLE:
                raise ImportError("google-genai not installed. Run: pip install google-genai")
            if not api_key_path:
                raise ValueError("API key path required for Gemini")
            api_key = Path(api_key_path).read_text(encoding='utf-8').strip()
            print(f"Using Gemini API (key: {api_key[:20]}...{api_key[-10:]})")
            self.client = genai.Client(api_key=api_key)
            
        elif self.ai_backend == 'huggingface':
            # HuggingFace - free tier with limits
            if not api_key_path:
                raise ValueError("API key path required for HuggingFace")
            self.hf_token = Path(api_key_path).read_text(encoding='utf-8').strip()
            self.hf_model = "mistralai/Mistral-7B-Instruct-v0.2"
            print(f"Using HuggingFace Inference API (30k requests/month free)")
        
        else:
            raise ValueError(f"Unknown backend: {ai_backend}. Use 'ollama', 'gemini', or 'huggingface'")
        
        # Track if browser was already opened
        self.browser_opened = False
        
        # Load sentence transformer
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading model '{model_name}' on {device}...")
        self.model = SentenceTransformer(model_name, device=device)
        
        # Storage for dialogue history
        self.sentences = []  # All sentences
        self.speakers = []   # 'user' or 'gemini'
        self.timestamps = [] # When each sentence was added
        self.embeddings = None
        
        print(f"✓ Visualizer ready! Reducer: {REDUCER}")
    
    def split_into_sentences(self, text):
        """Split text into sentences with improved handling of complex inputs.

        Handles mathematical expressions (e.g. '1+1=2'), abbreviations,
        multi-line text, and inputs that lack standard sentence terminators.
        """
        text = text.strip()
        if not text:
            return []

        # Split on newlines first to handle multi-line responses
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        all_sentences = []
        for line in lines:
            # Split on sentence-ending punctuation followed by a space and an
            # uppercase letter or digit, which avoids breaking on abbreviations
            # like "Dr." or decimal numbers like "3.14".
            parts = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', line)
            for part in parts:
                part = part.strip()
                if part:
                    all_sentences.append(part)

        # If no split happened, return the whole text as one sentence
        if not all_sentences:
            all_sentences = [text]

        return all_sentences
    
    def add_message(self, text, speaker):
        """Add a message to the dialogue and update embeddings."""
        sentences = self.split_into_sentences(text)
        timestamp = datetime.now().isoformat()
        
        for sentence in sentences:
            self.sentences.append(sentence)
            self.speakers.append(speaker)
            self.timestamps.append(timestamp)
        
        # Re-compute embeddings for all sentences
        print(f"  Embedding {len(sentences)} new sentences from {speaker}...")
        self.embeddings = self.model.encode(
            self.sentences,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        print(f"  Total sentences: {len(self.sentences)}")
    
    def reduce_to_3d(self):
        """Reduce embeddings to 3D using PCA or UMAP."""
        if self.embeddings is None or len(self.embeddings) < 3:
            return None
        
        # Need at least 3 points for 3D
        n_samples = len(self.embeddings)
        
        if REDUCER == "pca":
            # PCA is fast and works well for all sample sizes
            reducer = PCA(n_components=3, random_state=42)
        elif REDUCER == "umap":
            # Adjust n_neighbors based on sample size
            n_neighbors = min(15, max(2, n_samples - 1))
            reducer = umap.UMAP(
                n_components=3,
                n_neighbors=n_neighbors,
                min_dist=0.1,
                random_state=42
            )
        else:
            # t-SNE fallback
            perplexity = min(30, max(5, n_samples - 1))
            reducer = TSNE(
                n_components=3,
                perplexity=perplexity,
                random_state=42
            )
        
        coords_3d = reducer.fit_transform(self.embeddings)
        return coords_3d
    
    def visualize(self, coords_3d=None):
        """Create interactive 3D visualization."""
        if coords_3d is None:
            coords_3d = self.reduce_to_3d()
        
        if coords_3d is None:
            print("  Not enough data to visualize yet (need at least 3 sentences)")
            return
        
        # Color mapping: user = blue, AI = red/orange/green based on backend
        color_map = {
            'user': '#3498db',      # Blue
            'ollama': '#2ecc71',    # Green
            'gemini': '#e74c3c',    # Red
            'huggingface': '#f39c12' # Orange
        }
        colors = [color_map.get(s, '#95a5a6') for s in self.speakers]
        
        # Create hover text
        hover_texts = [
            f"<b>{speaker.upper()}</b><br>{text[:80]}{'...' if len(text) > 80 else ''}<br><i>{ts}</i>"
            for text, speaker, ts in zip(self.sentences, self.speakers, self.timestamps)
        ]
        
        # Create 3D scatter plot
        fig = go.Figure(data=[go.Scatter3d(
            x=coords_3d[:, 0],
            y=coords_3d[:, 1],
            z=coords_3d[:, 2],
            mode='markers+text',
            marker=dict(
                size=8,
                color=colors,
                line=dict(color='white', width=0.5)
            ),
            text=[f"{i}" for i in range(len(self.sentences))],
            textposition="top center",
            textfont=dict(size=8, color='gray'),
            hovertext=hover_texts,
            hoverinfo='text'
        )])
        
        # Add trajectory lines connecting sentences in order
        fig.add_trace(go.Scatter3d(
            x=coords_3d[:, 0],
            y=coords_3d[:, 1],
            z=coords_3d[:, 2],
            mode='lines',
            line=dict(color='lightgray', width=2),
            hoverinfo='skip',
            showlegend=False
        ))
        
        fig.update_layout(
            title=dict(
                text=f"Dialogue Flow in 3D Semantic Space ({REDUCER.upper()})<br>"
                     f"<span style='font-size:12px'>Blue=User | Green=Ollama | Red=Gemini | Total: {len(self.sentences)} sentences</span>",
                x=0.5,
                xanchor='center'
            ),
            scene=dict(
                xaxis_title='Dim 1',
                yaxis_title='Dim 2',
                zaxis_title='Dim 3',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            width=1200,
            height=800,
            showlegend=False
        )
        
        # Save HTML
        output_file = self.output_dir / "dialogue_3d_interactive.html"
        fig.write_html(str(output_file))
        print(f"\n✓ Saved visualization: {output_file}")
        
        # Open in browser only the first time
        if not self.browser_opened:
            import webbrowser
            webbrowser.open(str(output_file.absolute()))
            self.browser_opened = True
            print("✓ Opened in browser (graph will auto-refresh on file updates)")
        else:
            print("✓ Graph updated (refresh your browser to see changes)")
        
        # Also save data
        self.save_data()
        
        return output_file
    
    def save_data(self):
        """Save dialogue data to JSON."""
        data = {
            "metadata": {
                "total_sentences": len(self.sentences),
                "user_sentences": self.speakers.count('user'),
                "ai_sentences": len(self.sentences) - self.speakers.count('user'),
                "ai_backend": self.ai_backend,
                "model": "all-MiniLM-L6-v2",
                "reducer": REDUCER
            },
            "dialogue": [
                {
                    "index": i,
                    "text": text,
                    "speaker": speaker,
                    "timestamp": ts
                }
                for i, (text, speaker, ts) in enumerate(zip(self.sentences, self.speakers, self.timestamps))
            ]
        }
        
        output_file = self.output_dir / "dialogue_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved data: {output_file}")
    
    def chat_with_ai(self, user_message):
        """Send user message to AI and get response."""
        print(f"\n{'='*60}")
        print(f"YOU: {user_message}")
        
        # Add user message
        self.add_message(user_message, speaker='user')
        
        try:
            print(f"\n[Waiting for {self.ai_backend.upper()} response...]")
            
            if self.ai_backend == 'ollama':
                # Ollama local API
                print("   (First response may take 10-30 seconds to load the model...)")
                response = requests.post(
                    self.ollama_url,
                    json={
                        "model": self.ollama_model,
                        "prompt": user_message,
                        "stream": False
                    },
                    timeout=60  # Increased timeout for first load
                )
                response.raise_for_status()
                ai_text = response.json()['response'].strip()
                
            elif self.ai_backend == 'gemini':
                # Gemini API
                response = self.client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=user_message
                )
                ai_text = response.text.strip()
                
            elif self.ai_backend == 'huggingface':
                # HuggingFace Inference API
                api_url = f"https://api-inference.huggingface.co/models/{self.hf_model}"
                headers = {"Authorization": f"Bearer {self.hf_token}"}
                response = requests.post(
                    api_url,
                    headers=headers,
                    json={"inputs": user_message},
                    timeout=30
                )
                response.raise_for_status()
                ai_text = response.json()[0]['generated_text'].strip()
            
            print(f"\n{self.ai_backend.upper()}: {ai_text}")
            
            # Add AI response
            self.add_message(ai_text, speaker=self.ai_backend)
            
        except requests.exceptions.ConnectionError:
            print(f"\n⚠️ Cannot connect to {self.ai_backend}.")
            if self.ai_backend == 'ollama':
                print("   Make sure Ollama is running: ollama serve")
                print("   And the model is installed: ollama pull llama3.2")
            ai_text = "[Connection error - response not generated]"
            self.add_message(ai_text, speaker=self.ai_backend)
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                print(f"\n⚠️ API quota exceeded. Your message was still embedded.")
            else:
                print(f"\n⚠️ Error: {error_msg[:200]}")
            
            ai_text = "[API unavailable - response not generated]"
            self.add_message(ai_text, speaker=self.ai_backend)
        
        # Update visualization
        print(f"\n{'='*60}")
        print("Updating 3D visualization...")
        output_file = self.visualize()
        
        return ai_text, output_file


def main():
    """Main interactive loop."""
    print("\n" + "="*60)
    print("Interactive Dialogue Embedding Visualizer")
    print("="*60)
    
    # Configuration - Choose AI backend
    print("\nAvailable AI backends:")
    print("  1. Ollama (FREE, UNLIMITED, local) - RECOMMENDED")
    print("  2. Gemini (needs API key, has quotas)")
    print("  3. HuggingFace (free tier, 30k/month)")
    
    choice = input("\nChoose backend (1/2/3) [default=1]: ").strip() or "1"
    
    if choice == "1":
        ai_backend = "ollama"
        api_key_path = None
    elif choice == "2":
        ai_backend = "gemini"
        api_key_path = r"C:\Users\C\OneDrive\Desktop\計算機程式設計\code\114-1\AI-dialogue-project\GeminiAPI.txt"
    elif choice == "3":
        ai_backend = "huggingface"
        api_key_path = input("Enter path to HuggingFace token file: ").strip()
    else:
        print("Invalid choice, using Ollama")
        ai_backend = "ollama"
        api_key_path = None
    
    output_dir = "output"
    
    # Initialize visualizer
    viz = DialogueEmbeddingVisualizer(
        ai_backend=ai_backend,
        api_key_path=api_key_path,
        output_dir=output_dir
    )
    
    print(f"\nOutput will be saved to: {viz.output_dir}")
    
    print("\nInstructions:")
    print(f"  - Type your message and press Enter to chat with {ai_backend.upper()}")
    print("  - The 3D graph opens ONCE in your browser on the first turn")
    print("  - After each turn, the graph file updates - just REFRESH your browser to see updates")
    print("  - Type 'quit' or 'exit' to stop")
    print("  - Type 'save' to save current state without chatting")
    
    if ai_backend == 'ollama':
        print("\n✓ Using Ollama - completely free and unlimited!")
        print("  Make sure Ollama is running in background")
    
    print("\n" + "="*60)
    
    turn = 0
    last_output_file = None
    
    while True:
        try:
            # Get user input
            user_input = input(f"\n[Turn {turn + 1}] Your message: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye! Final visualization saved.")
                if last_output_file:
                    print(f"   {last_output_file}")
                break
            
            if user_input.lower() == 'save':
                print("\nSaving current state...")
                viz.save_data()
                if len(viz.sentences) >= 3:
                    last_output_file = viz.visualize()
                continue
            
            # Chat with AI
            ai_response, output_file = viz.chat_with_ai(user_input)
            last_output_file = output_file
            turn += 1
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Saving final state...")
            if len(viz.sentences) >= 3:
                viz.visualize()
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\nTotal dialogue:")
    print(f"  - Turns: {turn}")
    print(f"  - Sentences: {len(viz.sentences)}")
    print(f"  - User: {viz.speakers.count('user')}")
    print(f"  - AI: {len(viz.sentences) - viz.speakers.count('user')}")
    print(f"\nOutput directory: {viz.output_dir}")


if __name__ == "__main__":
    main()
