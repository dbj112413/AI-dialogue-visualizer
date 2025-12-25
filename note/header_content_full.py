#!/usr/bin/env python3
"""
AI Dialogue Embedding and 3D Visualization
==========================================

Generates sentence embeddings from text data and visualizes them in 3D space
using dimensionality reduction techniques (PCA, t-SNE, UMAP).

Features:
  - Sentence embeddings using SentenceTransformer models
  - Dimensionality reduction: PCA, t-SNE, UMAP
  - 3D coordinate export (JSON, CSV, NPY formats)
  - Interactive 3D visualization with Plotly
  - Static 3D plots with Matplotlib
  - Nearest neighbor analysis
  - Cluster detection (optional)

Prerequisites:
  - Python 3.8+
  - Virtual environment with required packages

Setup (First Time):
  # Windows PowerShell
  cd "C:\Users\C\OneDrive\Desktop\計算機程式設計\code\114-1\AI-dialogue-project"
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt

Activation (Every Session):
  # Navigate to project folder
  cd "C:\Users\C\OneDrive\Desktop\計算機程式設計\code\114-1\AI-dialogue-project"
  
  # Activate virtual environment
  .\.venv\Scripts\Activate.ps1
  
  # Verify (should show project .venv path)
  python -c "import sys; print(sys.executable)"

Usage:
  # Basic usage (UMAP reduction with plot)
  python core/1222_embedding3D.py --in_file data/lyrics.json --out_dir output --method umap --plot
  
  # Using t-SNE
  python core/1222_embedding3D.py --in_file data/dialogues.csv --out_dir results --method tsne --perplexity 50
  
  # Using PCA (fastest)
  python core/1222_embedding3D.py --in_file data/texts.json --out_dir output --method pca
  
  # Full options
  python core/1222_embedding3D.py \
    --in_file data/input.json \
    --out_dir output \
    --model all-MiniLM-L6-v2 \
    --method umap \
    --batch_size 32 \
    --top_k 10 \
    --plot \
    --overwrite

Arguments:
  --in_file       Input file (JSON/CSV/TXT)
  --out_dir       Output directory for results
  --model         SentenceTransformer model (default: all-MiniLM-L6-v2)
  --method        Reduction method: pca/tsne/umap (default: umap)
  --batch_size    Encoding batch size (default: 32)
  --top_k         Number of nearest neighbors (default: 5)
  --plot          Generate 3D plots (static + interactive)
  --overwrite     Overwrite existing embeddings
  --perplexity    t-SNE perplexity (default: 30)
  --n_neighbors   UMAP n_neighbors (default: 15)

Output Files:
  output/
    ├── embeddings.npy              # Original high-dimensional embeddings
    ├── coords_3d.npy               # 3D coordinates (NumPy array)
    ├── coords_3d.json              # 3D coordinates (JSON format)
    ├── coords_3d.csv               # 3D coordinates (CSV format)
    ├── neighbors.json              # Nearest neighbors for each item
    ├── metadata.json               # Original data with indices
    ├── metadata.csv                # Original data (CSV format)
    ├── plot_3d_static.png          # Static 3D plot (if --plot)
    └── plot_3d_interactive.html    # Interactive 3D plot (if --plot)

Examples:
  # Example 1: Quick visualization of lyrics
  python core/1222_embedding3D.py --in_file data/lyrics.json --out_dir output/lyrics --method umap --plot
  
  # Example 2: Analyze dialogue similarities
  python core/1222_embedding3D.py --in_file data/dialogues.csv --out_dir output/dialogue --method tsne --top_k 10
  
  # Example 3: Fast PCA for large datasets
  python core/1222_embedding3D.py --in_file data/large.json --out_dir output/large --method pca --batch_size 64

Input Format:
  JSON:
    [
      {"text": "First sentence", "category": "optional"},
      {"text": "Second sentence", "category": "optional"}
    ]
  
  CSV:
    text,category
    "First sentence",category1
    "Second sentence",category2

Author: Your Name
Course: 計算機程式設計 Final Project 2024
Date: 2024-12-22
"""