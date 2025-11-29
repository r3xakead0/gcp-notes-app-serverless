# Generate Architecture Diagram in GCP using Python Diagrams

This document explains how to correctly install **Diagrams** and how to generate an architecture diagram using the `gcp_notes_architecture.py` script.

The diagram shows:
- Static frontend in Cloud Storage
- Serverless API in Cloud Functions
- Firestore database
- User accessing from a web browser

## 📦 1. Requirements

You need:
- Python 3.8+
- Updated pip
- Graphviz installed on your system

Install Graphviz depending on your OS:

### Ubuntu / Debian
```bash
sudo apt-get update
sudo apt-get install graphviz
```

### macOS (Homebrew)
```bash
brew install graphviz
```

### Windows
1. Download Graphviz from: https://graphviz.org/download/
2. Install it
3. Add the **bin/** folder to your PATH

## 🧪 2. Create a virtual environment (recommended)

```bash
python -m venv venv-diagrams
source venv-diagrams/bin/activate       # On Windows: venv-diagrams\Scripts\activate
pip install --upgrade pip
```

## 📥 3. Install required libraries

Install Graphviz and Jinja2:

```bash
pip install graphviz==0.20.1 jinja2==3.1.3
```

Now install Diagrams:

```bash
pip install diagrams==0.23.3
```

## ▶️ 4. Generate the diagram

Run:

```bash
python gcp_notes_architecture.py
```

This generates a file in the current directory:

```bash
gcp-notes-architecture.png
```

## 🎉 5. Result

You will obtain a visual diagram showing:
- User → Internet → Cloud Storage  
- Frontend → Cloud Function  
- Cloud Function → Firestore  

## 🛠️ 6. Deactivate the virtual environment (recommended)

Exit the virtual environment:

```bash
deactivate
```
