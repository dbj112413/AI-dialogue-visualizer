#!/usr/bin/env python3
r"""
AI Dialogue Embedding and 3D Visualization
==========================================
Generate sentence embeddings and visualize in 3D using PCA/t-SNE/UMAP.

 QUICK START:
  # Activate virtual environment (REQUIRED EVERY TIME)
  cd "C:\Users\C\OneDrive\Desktop\計算機程式設計\code\114-1\AI-dialogue-project"
  .\.venv\Scripts\Activate.ps1
  
  # Run script
  python core/1222_embedding3D.py --in_file data/database.json --out_dir output --method umap --plot
  
  # Open html
  start output/filename.html 

 Features:
  - SentenceTransformer embeddings (768D → 3D)
  - Dimensionality reduction: PCA, t-SNE, UMAP
  - Interactive 3D plots (Plotly)
  - Nearest neighbor analysis
  - Export: JSON, CSV, NumPy

 Usage:
  python core/1222_embedding3D.py --in_file INPUT --out_dir OUTPUT --method [pca|tsne|umap] --plot

 Full documentation: See README.md
"""


import os
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import time
import platform
import torch

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors

# Dimensionality reduction
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# Dialogue Gemini
from google import genai

# Optional: UMAP (install with: pip install umap-learn)
try:
    import umap
    UMAP_AVAILABLE = True
except ImportError:
    UMAP_AVAILABLE = False
    print("UMAP not available. Install with: pip install umap-learn")

# Optional: Plotting (install with: pip install matplotlib plotly)
try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


def load_items(in_path: Path):
    """Load items from JSON, CSV, or plain text."""
    if not in_path.exists():
        raise FileNotFoundError(f"Input not found: {in_path}")
    
    if in_path.suffix.lower() == '.json':
        data = json.loads(in_path.read_text(encoding='utf-8'))
        items = []
        for it in data:
            if isinstance(it, dict) and 'text' in it:
                items.append(it)
            elif isinstance(it, str):
                items.append({'text': it})
        return items
    
    elif in_path.suffix.lower() in ('.csv', '.tsv'):
        df = pd.read_csv(in_path)
        return df.to_dict('records')
    
    else:
        # Plain text
        txt = in_path.read_text(encoding='utf-8')
        lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
        return [{'text': ln} for ln in lines]


def reduce_dimensions(embeddings, method='pca', n_components=3, **kwargs):
    """
    Reduce embeddings to n_components dimensions.
    
    Args:
        embeddings: (n_samples, n_features) array
        method: 'pca', 'tsne', or 'umap'
        n_components: target dimensions (typically 3)
        **kwargs: method-specific parameters
    
    Returns:
        reduced: (n_samples, n_components) array
    """
    print(f"\nReducing {embeddings.shape[1]}D → {n_components}D using {method.upper()}...")
    start = time.time()
    
    if method.lower() == 'pca':
        reducer = PCA(n_components=n_components, random_state=42)
        reduced = reducer.fit_transform(embeddings)
        explained = reducer.explained_variance_ratio_
        print(f"  Explained variance: {explained.sum():.1%} ({explained})")
    
    elif method.lower() == 'tsne':
        perplexity = kwargs.get('perplexity', min(30, embeddings.shape[0] - 1))
        reducer = TSNE(
            n_components=n_components,
            perplexity=perplexity,
            random_state=42,
            n_iter=1000
        )
        reduced = reducer.fit_transform(embeddings)
        print(f"  Perplexity: {perplexity}")
    
    elif method.lower() == 'umap':
        if not UMAP_AVAILABLE:
            raise ImportError("UMAP not installed. Use: pip install umap-learn")
        n_neighbors = kwargs.get('n_neighbors', min(15, embeddings.shape[0] - 1))
        min_dist = kwargs.get('min_dist', 0.1)
        reducer = umap.UMAP(
            n_components=n_components,
            n_neighbors=n_neighbors,
            min_dist=min_dist,
            random_state=42
        )
        reduced = reducer.fit_transform(embeddings)
        print(f"  n_neighbors: {n_neighbors}, min_dist: {min_dist}")
    
    else:
        raise ValueError(f"Unknown method: {method}. Use 'pca', 'tsne', or 'umap'")
    
    elapsed = time.time() - start
    print(f"  Reduction completed in {elapsed:.1f}s")
    return reduced


def save_3d_coords(coords_3d, texts, out_dir: Path, metadata=None):
    """
    Save 3D coordinates in multiple formats.
    
    Outputs:
        - coords_3d.npy: NumPy array (n, 3)
        - coords_3d.json: JSON with text + coordinates
        - coords_3d.csv: CSV for easy inspection
    """
    # NumPy format
    np.save(out_dir / "coords_3d.npy", coords_3d)
    
    # JSON format (for web visualization)
    points = []
    for i, (x, y, z) in enumerate(coords_3d):
        point = {
            'id': i,
            'text': texts[i],
            'x': float(x),
            'y': float(y),
            'z': float(z)
        }
        if metadata and i < len(metadata):
            point.update(metadata[i])
        points.append(point)
    
    (out_dir / "coords_3d.json").write_text(
        json.dumps(points, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    
    # CSV format (for spreadsheets)
    df = pd.DataFrame({
        'id': range(len(texts)),
        'text': texts,
        'x': coords_3d[:, 0],
        'y': coords_3d[:, 1],
        'z': coords_3d[:, 2]
    })
    if metadata:
        meta_df = pd.DataFrame(metadata)
        df = pd.concat([df, meta_df.drop(columns=['text'], errors='ignore')], axis=1)
    
    df.to_csv(out_dir / "coords_3d.csv", index=False)
    
    print(f"\nSaved 3D coordinates to:")
    print(f"  - {out_dir / 'coords_3d.npy'}")
    print(f"  - {out_dir / 'coords_3d.json'}")
    print(f"  - {out_dir / 'coords_3d.csv'}")


def plot_3d_matplotlib(coords_3d, texts, out_dir: Path):
    """Create static 3D plot with matplotlib."""
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available, skipping static plot")
        return
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Scatter plot
    scatter = ax.scatter(
        coords_3d[:, 0],
        coords_3d[:, 1],
        coords_3d[:, 2],
        c=range(len(texts)),
        cmap='viridis',
        s=100,
        alpha=0.6
    )
    
    # Add labels for first few points
    for i in range(min(10, len(texts))):
        ax.text(
            coords_3d[i, 0],
            coords_3d[i, 1],
            coords_3d[i, 2],
            f"  {i}",
            fontsize=8
        )
    
    ax.set_xlabel('Dimension 1')
    ax.set_ylabel('Dimension 2')
    ax.set_zlabel('Dimension 3')
    ax.set_title('3D Embedding Visualization')
    
    plt.colorbar(scatter, label='Line Index')
    
    out_file = out_dir / "plot_3d_static.png"
    plt.savefig(out_file, dpi=150, bbox_inches='tight')
    print(f"\nSaved static 3D plot to: {out_file}")
    plt.close()


def plot_3d_interactive(coords_3d, texts, out_dir: Path):
    """Create interactive 3D plot with plotly."""
    if not PLOTLY_AVAILABLE:
        print("Plotly not available, skipping interactive plot")
        return
    
    # Create hover text (truncate long texts)
    hover_texts = [
        f"<b>Line {i}</b><br>{text[:50]}{'...' if len(text) > 50 else ''}"
        for i, text in enumerate(texts)
    ]
    
    # Convert range to list for Plotly 6.x compatibility
    colors = list(range(len(texts)))
    
    fig = go.Figure(data=[go.Scatter3d(
        x=coords_3d[:, 0],
        y=coords_3d[:, 1],
        z=coords_3d[:, 2],
        mode='markers+text',
        marker=dict(
            size=8,
            color=colors,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Line Index")
        ),
        text=[str(i) for i in range(len(texts))],
        textposition="top center",
        textfont=dict(size=8),
        hovertext=hover_texts,
        hoverinfo='text'
    )])
    
    fig.update_layout(
        title='Interactive 3D Embedding Visualization',
        scene=dict(
            xaxis_title='Dimension 1',
            yaxis_title='Dimension 2',
            zaxis_title='Dimension 3'
        ),
        width=1000,
        height=800
    )
    
    out_file = out_dir / "plot_3d_interactive.html"
    fig.write_html(str(out_file))
    print(f"\nSaved interactive 3D plot to: {out_file}")
    print(f"  Open in browser to interact (rotate, zoom, hover)")


def generate_dialogue_samples(num_samples=50, topic="general conversation"):
    """Generate dialogue samples using Gemini."""
    
    # 1. Load Gemini API key from file (FIXED: Use raw string)
    GEMINI_KEY = Path(r"C:\Users\C\OneDrive\Desktop\計算機程式設計\code\114-1\GeminiAPI.txt").read_text().strip()
    # OR use forward slashes (works on Windows too):
    # GEMINI_KEY = Path("C:/Users/C/OneDrive/Desktop/計算機程式設計/code/114-1/GeminiAPI.txt").read_text().strip()
    
    client = genai.Client(api_key=GEMINI_KEY)
    
    samples = []
    
    # 2. Define 5 different prompt templates
    prompts = [
        "Who are you. (1 sentence):",
        "What's conscious. (1 sentence):",  # Fixed typo: concious → conscious
        "How do you learn languages. (1 sentence):",
        "Explain your database. (1 sentence):",
        "Do you understand your own limitation. (1 sentence):",
    ]
    
    # 3. Loop to generate samples
    for i in range(num_samples):
        # Rotate through prompts (prompt 1, 2, 3, 4, 5, 1, 2, ...)
        prompt = prompts[i % len(prompts)]
        
        # 4. Send to Gemini API
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )
        
        # 5. FIXED: Extract category properly
        # Extract the topic from the prompt (e.g., "Who are you" → "identity")
        category_map = {
            "Who are you": "identity",
            "What's conscious": "philosophy",
            "How do you learn": "learning",
            "Explain your database": "technical",
            "Do you understand": "self-awareness"
        }
        
        # Find matching category
        category = "general"  # default
        for key, value in category_map.items():
            if key in prompt:
                category = value
                break
        
        # Store response with metadata
        samples.append({
            "text": response.text.strip(),  # AI's response
            "category": category,  # FIXED: Actual category value
            "generated_by": "gemini-2.0-flash",
            "prompt_type": prompt.split("(")[0].strip(),  # Extract prompt text
            "prompt_full": prompt  # Store full prompt for reference
        })
        
        print(f"Generated {i+1}/{num_samples}: {response.text[:50]}...")
    
    return samples


def main():
    p = argparse.ArgumentParser(description="Embedding with 3D visualization")
    
    # Original arguments
    p.add_argument('--in_file', required=True, help="Input lyrics file")
    p.add_argument('--out_dir', required=True, help="Output directory")
    p.add_argument('--model', default='all-MiniLM-L6-v2', help="Sentence-Transformers model")
    p.add_argument('--batch_size', type=int, default=32, help="Encoding batch size")
    p.add_argument('--overwrite', action='store_true', help="Overwrite existing embeddings")
    p.add_argument('--top_k', type=int, default=5, help="Top-k neighbors")
    
    # New arguments for 3D
    p.add_argument('--method', default='umap', choices=['pca', 'tsne', 'umap'],
                   help="Dimensionality reduction method")
    p.add_argument('--plot', action='store_true', help="Generate 3D plots")
    p.add_argument('--perplexity', type=int, default=30, help="t-SNE perplexity")
    p.add_argument('--n_neighbors', type=int, default=15, help="UMAP n_neighbors")
    
    args = p.parse_args()
    
    in_path = Path(args.in_file)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    items = load_items(in_path)
    texts = [it['text'] for it in items]
    n = len(texts)
    print(f"Loaded {n} lines from {in_path}")
    
    # Setup device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Load model
    print(f"Loading model: {args.model}")
    model = SentenceTransformer(args.model, device=device)
    
    # Generate embeddings
    emb_path = out_dir / "embeddings.npy"
    if emb_path.exists() and not args.overwrite:
        print(f"Loading existing embeddings from {emb_path}")
        embeddings = np.load(str(emb_path))
    else:
        print("Generating embeddings...")
        embeddings = model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            batch_size=args.batch_size
        )
        np.save(str(emb_path), embeddings)
        print(f"Saved embeddings: {embeddings.shape}")
    
    # Dimensionality reduction to 3D
    coords_3d = reduce_dimensions(
        embeddings,
        method=args.method,
        n_components=3,
        perplexity=args.perplexity,
        n_neighbors=args.n_neighbors
    )
    
    # Save 3D coordinates
    save_3d_coords(coords_3d, texts, out_dir, metadata=items)
    
    # Save original metadata
    metadata = [{'embed_index': i, **it} for i, it in enumerate(items)]
    (out_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    pd.DataFrame(metadata).to_csv(out_dir / "metadata.csv", index=False)
    
    # Compute neighbors
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    embeddings_normed = embeddings / norms
    
    k = min(args.top_k + 1, n)
    nn = NearestNeighbors(n_neighbors=k, metric='cosine').fit(embeddings_normed)
    distances, indices = nn.kneighbors(embeddings_normed)
    sims = 1.0 - distances
    
    neighbors = []
    for i in range(n):
        row = []
        for idx, sim in zip(indices[i], sims[i]):
            if idx != i:
                row.append({"index": int(idx), "similarity": float(sim)})
            if len(row) >= args.top_k:
                break
        neighbors.append(row)
    
    (out_dir / "neighbors.json").write_text(
        json.dumps(neighbors, indent=2),
        encoding='utf-8'
    )
    
    # Generate plots if requested
    if args.plot:
        print("\nGenerating 3D plots...")
        plot_3d_matplotlib(coords_3d, texts, out_dir)
        plot_3d_interactive(coords_3d, texts, out_dir)
    
    # Print sample
    print("\n" + "="*60)
    print("Sample 3D coordinates (first 5 lines):")
    print("="*60)
    for i in range(min(5, n)):
        print(f"[{i}] {texts[i][:60]}...")
        print(f"    384D embedding: [{embeddings[i, :3]}, ..., {embeddings[i, -1]}]")
        print(f"    3D coords: x={coords_3d[i, 0]:.3f}, y={coords_3d[i, 1]:.3f}, z={coords_3d[i, 2]:.3f}")
        print(f"    Nearest neighbors:")
        for nb in neighbors[i][:3]:
            print(f"      → ({nb['similarity']:.3f}) [{nb['index']}] {texts[nb['index']][:50]}...")
        print()
    
    print("="*60)
    print("✅ Processing complete!")
    print(f"Output directory: {out_dir}")
    print("="*60)


if __name__ == "__main__":
    main()