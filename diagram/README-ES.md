# Generar Diagrama de Arquitectura en GCP usando Python Diagrams

ste documento explica cómo instalar correctamente Diagrams y cómo generar un diagrama de arquitectura usando el script `gcp_notes_architecture.py`.

El diagrama muestra:
- Frontend estático en Cloud Storage
- API Serverless en Cloud Functions
- Base de datos Firestore
- Usuario accediendo desde navegador

## 📦 1. Requisitos

Necesitas:
- Python 3.8+
- pip actualizado
- Graphviz instalado en tu sistema

Instalar Graphviz dependiendo de tu SO:

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
1. Descarga Graphviz desde: https://graphviz.org/download/
2. Instálalo
3. Agrega la carpeta bin/ al PATH

## 🧪 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv-diagrams
source venv-diagrams/bin/activate       # En Windows: venv-diagrams\Scripts\activate
pip install --upgrade pip
```

## 📥 3. Instalar librerías necesarias

Instala Graphviz y Jinja2:

```bash
pip install graphviz==0.20.1 jinja2==3.1.3
```

Ahora instala Diagrams:

```bash
pip install diagrams==0.23.3
```

## ▶️ 4. Generar el diagrama

Ejecuta:

```bash
python gcp_notes_architecture.py
```

Esto genera un archivo en la carpeta actual:

```bash
gcp-notes-architecture.png
```

## 🎉 5. Resultado

Obtendrás un diagrama visual que muestra:
- Usuario → Internet → Cloud Storage
- Frontend → Cloud Function
- Cloud Function → Firestore

## 🛠️ 6. Desactivar entorno virtual (recomendado)

Salir del entorno virtual:

```bash
deactivate
```
