#!/usr/bin/env python3
"""
Fast Live-Updating Dialogue Embedding Visualizer
================================================
Real-time 3D visualization with auto-refresh and optimized speed.

Features:
  - Auto-refreshing 3D graph (no manual refresh needed)
  - Faster embedding with batching
  - Streaming responses from Ollama
  - PCA for instant dimensionality reduction
  - Color-coded dialogue flow

Usage:
    python core/1223_fast_live_dialogue.py
"""

import os
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

import json
import re
import threading
import time
from pathlib import Path
from datetime import datetime
import numpy as np
import requests

from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA, IncrementalPCA
import plotly.graph_objects as go


class FastDialogueVisualizer:
    def __init__(self, ollama_model='llama3.2:latest', output_dir='output'):
        """Initialize with optimizations for speed."""
        # Output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(output_dir) / f"dia_{timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.html_file = self.output_dir / "dialogue_live.html"
        
        # Ollama settings
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_model = ollama_model
        
        # Load embedding model (lightweight and fast)
        print("Loading embedding model (this takes ~5 seconds)...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ Model loaded!")
        
        # Dialogue storage
        self.sentences = []
        self.speakers = []
        self.timestamps = []
        self.embeddings = None
        
        # Tracking
        self.browser_opened = False
        self.turn_count = 0
        self._reduction_method = 'PCA'
        
        # Pre-warm Ollama (load model into memory)
        print("\nPre-warming Ollama (one-time 10-second delay)...")
        self._prewarm_ollama()
        print("✓ Ollama ready! Future responses will be fast.\n")
    
    def _prewarm_ollama(self):
        """Pre-load Ollama model into memory for faster responses."""
        try:
            requests.post(
                self.ollama_url,
                json={
                    "model": self.ollama_model,
                    "prompt": "Hi",
                    "stream": False
                },
                timeout=30
            )
        except:
            pass  # Ignore errors, just trying to warm up
    
    def split_sentences(self, text):
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
        """Add message and update embeddings incrementally."""
        sentences = self.split_sentences(text)
        
        if not sentences:
            return
        
        # Add to storage
        for sent in sentences:
            self.sentences.append(sent)
            self.speakers.append(speaker)
            self.timestamps.append(datetime.now().isoformat())
        
        # Embed new sentences only (incremental update)
        new_embeddings = self.model.encode(sentences, show_progress_bar=False)
        
        if self.embeddings is None:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])
        
        print(f"  Added {len(sentences)} sentence(s) from {speaker}")
    
    def get_ai_response_streaming(self, prompt):
        """Get response from Ollama with streaming for better UX."""
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False  # Faster for short responses
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()['response'].strip()
            else:
                return "[Error: Unable to get response]"
                
        except requests.exceptions.Timeout:
            return "[Error: Response timed out - Ollama might be processing]"
        except Exception as e:
            return f"[Error: {str(e)[:50]}]"
    
    def reduce_to_3d(self):
        """Reduce embeddings to 3D using a method chosen based on dataset size.

        Method selection rationale:
        - n < 3: cannot reduce to 3D, return None
        - n < 50: PCA is fast and stable for small datasets
        - n >= 50: IncrementalPCA allows efficient updates without
          refitting from scratch each time the dataset grows
        """
        if self.embeddings is None or len(self.embeddings) < 3:
            return None

        n_samples = len(self.embeddings)

        if n_samples < 50:
            pca = PCA(n_components=3, random_state=42)
            coords_3d = pca.fit_transform(self.embeddings)
            self._reduction_method = 'PCA'
        else:
            ipca = IncrementalPCA(n_components=3, batch_size=max(10, n_samples // 5))
            coords_3d = ipca.fit_transform(self.embeddings)
            self._reduction_method = 'IncrementalPCA'

        return coords_3d
    
    def create_interactive_plot(self, is_final=False):
        """Create smooth auto-updating HTML visualization - embedded data version.
        
        Args:
            is_final: If True, disables auto-refresh (conversation ended)
        """
        coords_3d = self.reduce_to_3d()
        
        if coords_3d is None:
            print("  Need at least 3 sentences to visualize")
            return None
        
        # Color mapping
        color_map = {'user': '#3498db', 'ollama': '#2ecc71'}
        colors = [color_map.get(s, '#95a5a6') for s in self.speakers]
        
        # Prepare data directly in HTML (no separate JSON file)
        plot_data = {
            "x": coords_3d[:, 0].tolist(),
            "y": coords_3d[:, 1].tolist(),
            "z": coords_3d[:, 2].tolist(),
            "colors": colors,
            "texts": [f"{i}" for i in range(len(self.sentences))],
            "hovertexts": [
                f"<b>{spk.upper()}</b><br>{txt[:80]}{'...' if len(txt) > 80 else ''}"
                for txt, spk in zip(self.sentences, self.speakers)
            ],
            "count": len(self.sentences)
        }
        
        # Embed data directly in HTML
        data_json = json.dumps(plot_data)
        
        # Auto-refresh script (only if not final)
        auto_refresh_script = "" if is_final else """
        // Auto-reload page every 3 seconds to get updated data
        setTimeout(function() {
            location.reload();
        }, 3000);"""
        
        # Status indicator
        status_text = "🔴 Stopped" if is_final else "🟢 Live"
        refresh_text = "No refresh" if is_final else "Auto-refresh: 3s"
        
        # Create HTML with embedded data
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Live Dialogue Embedding</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ 
            margin: 0; 
            padding: 0; 
            background: #1a1a1a; 
            color: white; 
            font-family: Arial, sans-serif;
            overflow: hidden;
        }}
        #plot {{ 
            width: 100vw; 
            height: 100vh; 
        }}
        .info {{ 
            position: fixed; 
            top: 10px; 
            right: 10px; 
            background: rgba(0,0,0,0.8); 
            padding: 15px; 
            border-radius: 8px; 
            font-size: 13px;
            z-index: 1000;
            border: 1px solid #444;
        }}
        .status {{
            color: #2ecc71;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="info">
        <div class="status">{status_text}</div>
        <div>📊 Sentences: <span id="count">{len(self.sentences)}</span></div>
        <div>🔄 {refresh_text}</div>
        <div style="margin-top:10px; font-size:11px; color:#888;">
            Blue=You | Green=Ollama
        </div>
    </div>
    <div id="plot"></div>
    
    <script>
        // Data embedded directly (updated each time HTML is saved)
        const plotData = {data_json};
        
        console.log('Loading plot with', plotData.count, 'points');
        
        // Create traces
        const lineTrace = {{
            type: 'scatter3d',
            mode: 'lines',
            x: plotData.x,
            y: plotData.y,
            z: plotData.z,
            line: {{ color: 'rgba(255,255,255,0.2)', width: 2 }},
            hoverinfo: 'skip',
            showlegend: false
        }};
        
        const pointTrace = {{
            type: 'scatter3d',
            mode: 'markers+text',
            x: plotData.x,
            y: plotData.y,
            z: plotData.z,
            marker: {{
                size: 10,
                color: plotData.colors,
                line: {{ color: 'white', width: 1 }}
            }},
            text: plotData.texts,
            textposition: 'top center',
            textfont: {{ size: 8, color: 'gray' }},
            hovertext: plotData.hovertexts,
            hoverinfo: 'text'
        }};
        
        const layout = {{
            paper_bgcolor: '#1a1a1a',
            plot_bgcolor: '#1a1a1a',
            title: {{
                text: 'Live Dialogue Flow in 3D Semantic Space ({self._reduction_method})',
                font: {{ color: 'white', size: 18 }}
            }},
            scene: {{
                xaxis: {{ title: 'Dim 1', gridcolor: '#333', color: 'white' }},
                yaxis: {{ title: 'Dim 2', gridcolor: '#333', color: 'white' }},
                zaxis: {{ title: 'Dim 3', gridcolor: '#333', color: 'white' }},
                bgcolor: '#0d0d0d',
                camera: {{ eye: {{ x: 1.3, y: 1.3, z: 1.3 }} }}
            }},
            margin: {{ l: 0, r: 0, t: 50, b: 0 }},
            showlegend: false
        }};
        
        // Create the plot
        Plotly.newPlot('plot', [lineTrace, pointTrace], layout, {{responsive: true}});
        {auto_refresh_script}
    </script>
</body>
</html>"""
        
        # Save HTML
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return self.html_file
    
    def save_data(self):
        """Save dialogue data to JSON."""
        data = {
            "metadata": {
                "total_sentences": len(self.sentences),
                "user_sentences": self.speakers.count('user'),
                "ollama_sentences": self.speakers.count('ollama'),
                "turns": self.turn_count
            },
            "dialogue": [
                {"index": i, "text": txt, "speaker": spk, "timestamp": ts}
                for i, (txt, spk, ts) in enumerate(zip(self.sentences, self.speakers, self.timestamps))
            ]
        }
        
        json_file = self.output_dir / "dialogue_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def chat_turn(self, user_message):
        """One complete chat turn."""
        self.turn_count += 1
        
        print(f"\n{'='*70}")
        print(f"[Turn {self.turn_count}] YOU: {user_message}")
        
        # Add user message
        self.add_message(user_message, speaker='user')
        
        # Get AI response
        print(f"\n[Ollama thinking...]")
        ai_response = self.get_ai_response_streaming(user_message)
        print(f"\nOLLAMA: {ai_response}")
        
        # Add AI response
        self.add_message(ai_response, speaker='ollama')
        
        # Update visualization
        print(f"\n{'='*70}")
        print("Updating graph...")
        output_file = self.create_interactive_plot()
        
        if output_file:
            # Check if JSON was created
            json_file = self.output_dir / "dialogue_coords.json"
            if json_file.exists():
                print(f"✓ Data file created: {json_file}")
            
            # Open browser only once
            if not self.browser_opened:
                import webbrowser
                webbrowser.open(str(output_file.absolute()))
                self.browser_opened = True
                print(f"✓ Graph opened in browser: {output_file}")
                print("  Graph auto-refreshes every 2 seconds - no manual refresh needed!")
                print("  If you see a black screen, check browser console (F12) for errors")
            else:
                print(f"✓ Graph updated: {output_file}")
                print("  (Graph will auto-update in browser within 2 seconds)")
        else:
            print("  (Waiting for at least 3 sentences to create graph)")
        
        # Save data
        self.save_data()
        
        return ai_response


def main():
    """Main interactive loop."""
    print("\n" + "="*70)
    print("🚀 Fast Live-Updating Dialogue Visualizer")
    print("="*70)
    
    # Check Ollama
    try:
        r = requests.get("http://localhost:11434", timeout=2)
        if r.status_code != 200:
            print("\n⚠️  Ollama not responding. Make sure it's running:")
            print("   Run: ollama serve")
            return
    except:
        print("\n⚠️  Cannot connect to Ollama. Make sure it's installed and running.")
        print("   Download: https://ollama.com/download")
        print("   Then run: ollama pull llama3.2")
        return
    
    # Initialize
    viz = FastDialogueVisualizer()
    
    print(f"\nOutput: {viz.output_dir}")
    print("\n" + "="*70)
    print("Instructions:")
    print("  • Type your message and press Enter")
    print("  • Graph opens ONCE and auto-refreshes every 2 seconds")
    print("  • No manual browser refresh needed!")
    print("  • Type 'quit' or 'exit' to stop")
    print("  • Type 'save' to save without chatting")
    print("="*70)
    
    while True:
        try:
            user_input = input(f"\n💬 Your message: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                print(f"   Saving final state...")
                viz.save_data()
                if len(viz.sentences) >= 3:
                    viz.create_interactive_plot(is_final=True)
                    print(f"   ✓ Final visualization saved (no auto-refresh)")
                print(f"   Final data saved to: {viz.output_dir}")
                break
            
            if user_input.lower() == 'save':
                viz.save_data()
                if len(viz.sentences) >= 3:
                    viz.create_interactive_plot(is_final=False)
                print("✓ Saved current state")
                continue
            
            # Chat
            viz.chat_turn(user_input)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Saving final state...")
            viz.save_data()
            if len(viz.sentences) >= 3:
                viz.create_interactive_plot(is_final=True)
                print("✓ Final visualization saved (no auto-refresh)")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n📊 Session Summary:")
    print(f"   Turns: {viz.turn_count}")
    print(f"   Total sentences: {len(viz.sentences)}")
    print(f"   You: {viz.speakers.count('user')} | Ollama: {viz.speakers.count('ollama')}")
    print(f"   Output: {viz.output_dir}")


if __name__ == "__main__":
    main()
