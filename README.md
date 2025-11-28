# Sistema de Notas - Guía Completa con Cloud Functions, Firestore y Cloud Storage

Este proyecto implementa un sistema simple para registrar notas utilizando servicios serverless de Google Cloud: Firestore, Cloud Functions y un frontend estático alojado en Cloud Storage.

---

## 🧱 Arquitectura General

**1. Base de datos NoSQL:**\
Firestore en modo nativo, colección `notes`.

**2. Backend serverless:**\
Cloud Functions (Python) exponiendo un mini-API REST: 
- `POST /notes` - crear nota
- `GET /notes` - listar notas
- `GET /notes/{id}` - obtener detalle de nota
- `PUT /notes/{id}` - actualizar nota
- `DELETE /notes/{id}` - eliminar nota

**3. Frontend:**\
Página web (HTML/CSS/JS) alojada como sitio estático en Cloud Storage.

---

## 🔧 Paso 0: Prerrequisitos

``` bash
gcloud auth login
gcloud config set project <PROJECT_ID>
```

---

## 🎯 Paso 1: Variables de entorno

``` bash
export PROJECT_ID="<PROJECT_ID>"
export REGION="us-central1"
export BUCKET_NAME="${PROJECT_ID}-notas-web"
export FUNCTION_NAME="notes_api"
```

---

## 📦 Paso 2: Habilitar APIs

``` bash
gcloud services enable \
  firestore.googleapis.com \
  cloudfunctions.googleapis.com \
  storage.googleapis.com
```

---

## 🗄️ Paso 3: Crear Firestore (Modo Nativo)

``` bash
gcloud firestore databases create \
  --location=$REGION \
  --type=firestore-native
```

---

## 🧠 Paso 4: Código del Backend (Cloud Function)

En Cloud Shell

``` bash
mkdir notes-backend
cd notes-backend
```

Crea el archivo `main.py`

``` python
import json
import datetime
from google.cloud import firestore

db = firestore.Client()
NOTES_COLLECTION = "notes"

def _get_cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

def _note_to_dict(doc):
    data = doc.to_dict()
    data["id"] = doc.id
    return data

def notes_api(request):
    # CORS
    if request.method == "OPTIONS":
        return ("", 204, _get_cors_headers())

    headers = _get_cors_headers()
    method = request.method

    path = request.path or "/"
    segments = [seg for seg in path.split("/") if seg]

    is_collection = False
    note_id = None

    if len(segments) == 0:
        is_collection = True              # "/"
    elif len(segments) == 1 and segments[0] == "notes":
        is_collection = True              # "/notes"
    elif len(segments) == 2 and segments[0] == "notes":
        note_id = segments[1]             # "/notes/{id}"
    else:
        return (json.dumps({"error": "Not found"}), 404, headers)

    try:
        # GET lista o detalle
        if method == "GET":
            if is_collection:
                docs = (
                    db.collection(NOTES_COLLECTION)
                    .order_by("created_at", direction=firestore.Query.DESCENDING)
                    .stream()
                )
                notes = [_note_to_dict(d) for d in docs]
                return (json.dumps(notes), 200, headers)
            else:
                doc = db.collection(NOTES_COLLECTION).document(note_id).get()
                if not doc.exists:
                    return (json.dumps({"error": "Note not found"}), 404, headers)
                return (json.dumps(_note_to_dict(doc)), 200, headers)

        # POST crear
        if method == "POST" and is_collection:
            payload = request.get_json(silent=True)
            if not payload or "title" not in payload:
                return (json.dumps({"error": "Invalid JSON"}), 400, headers)

            now = datetime.datetime.utcnow().isoformat() + "Z"

            doc_ref = db.collection(NOTES_COLLECTION).document()
            doc_ref.set({
                "title": payload["title"],
                "detail": payload.get("detail", ""),
                "created_at": now,
                "updated_at": now
            })

            return (json.dumps(_note_to_dict(doc_ref.get())), 201, headers)

        # PUT actualizar
        if method in ("PUT", "PATCH") and note_id:
            payload = request.get_json(silent=True)
            if not payload:
                return (json.dumps({"error": "Invalid JSON"}), 400, headers)

            doc_ref = db.collection(NOTES_COLLECTION).document(note_id)
            if not doc_ref.get().exists:
                return (json.dumps({"error": "Note not found"}), 404, headers)

            updates = {
                "updated_at": datetime.datetime.utcnow().isoformat() + "Z"
            }
            if "title" in payload:
                updates["title"] = payload["title"]
            if "detail" in payload:
                updates["detail"] = payload["detail"]

            doc_ref.update(updates)
            return (json.dumps(_note_to_dict(doc_ref.get())), 200, headers)

        # DELETE eliminar
        if method == "DELETE" and note_id:
            doc_ref = db.collection(NOTES_COLLECTION).document(note_id)
            if not doc_ref.get().exists:
                return (json.dumps({"error": "Note not found"}), 404, headers)
            doc_ref.delete()
            return (json.dumps({"message": "Note deleted"}), 200, headers)

        return (json.dumps({"error": "Method not allowed"}), 405, headers)

    except Exception as e:
        return (json.dumps({"error": str(e)}), 500, headers)
``` 

> Incluye funcionalidad: crear, listar, editar, eliminar notas + CORS.

Crea el archivo `requirements.txt`

``` text
google-cloud-firestore==2.16.0
```

---

## ☁️ Paso 5: Desplegar Cloud Function

``` bash
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=notes_api \
  --trigger-http \
  --allow-unauthenticated
```

Obtener y guardar la URL:

``` bash
export FUNCTION_URL="$(gcloud functions describe $FUNCTION_NAME \
  --region=$REGION \
  --format='value(serviceConfig.uri)')"

echo "FUNCTION_URL = $FUNCTION_URL"
```

Obtener y guardar el service account que usa la función:

``` bash
export SA_EMAIL="$(gcloud functions describe $FUNCTION_NAME \
  --gen2 \
  --region=$REGION \
  --format='value(serviceConfig.serviceAccountEmail)')"

echo "SA_EMAIL = $SA_EMAIL"
``` 

Dar permisos de Firestore a ese service account

``` bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/datastore.user"
``` 

---

## 🧪 Paso 6: Probar la API

### Crear nota

``` bash
curl -X POST "$FUNCTION_URL/notes" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Primera nota",
    "detail": "Hola Firestore"
  }'
```

### Listar notas

``` bash
curl "$FUNCTION_URL/notes"
```

### Obtener nota

``` bash
curl "$FUNCTION_URL/notes/{id}"
```

### Editar nota

``` bash
curl -X PUT "$FUNCTION_URL/notes/kISGMWGfsazN6CIfxqV2" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Primera nota",
    "detail": "Hola Firestore + Cloud Functions"
  }'
```

### Eliminar nota

``` bash
curl -X DELETE "$FUNCTION_URL/notes/{id}" \
  -H "Content-Type: application/json"
```

---

## 🧠 Paso 7: Código del Frontend (HTML + CSS + JS en Cloud Storage)

En Cloud Shell

``` bash
mkdir notes-frontend
cd notes-frontend
```

Crea el archivo `index.html`

``` html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>Notas - Demo GCP</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <h1>📒 Mis Notas</h1>

  <section class="form-section">
    <h2 id="form-title">Crear nota</h2>
    <form id="note-form">
      <!-- Campo oculto para el ID al editar -->
      <input type="hidden" id="note-id" />

      <label for="note-title">
        Título:
        <input type="text" id="note-title" required />
      </label>

      <label for="note-detail">
        Detalle:
        <textarea id="note-detail" rows="4"></textarea>
      </label>

      <div class="buttons">
        <button type="submit" id="save-btn">Guardar</button>
        <button type="button" id="cancel-btn">Cancelar</button>
      </div>
    </form>
  </section>

  <section class="list-section">
    <h2>Listado de notas</h2>
    <table id="notes-table">
      <thead>
        <tr>
          <th>Título</th>
          <th>Creada</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody id="notes-tbody">
        <!-- Filas dinámicas -->
      </tbody>
    </table>
  </section>

  <footer>
    <small>Sistema de notas con Firestore + Cloud Functions + Cloud Storage</small>
  </footer>

  <script src="app.js"></script>
</body>
</html>
``` 

Crea el archivo `styles.css`

``` css
/* Layout general */
body {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  background: #f9fafb;
  color: #0f172a;
}

h1 {
  text-align: center;
  margin-bottom: 20px;
}

/* Secciones */
section {
  background: #ffffff;
  padding: 15px 20px;
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.1);
}

.form-section h2,
.list-section h2 {
  margin-top: 0;
}

/* Formulario */
label {
  display: block;
  margin-bottom: 10px;
  font-size: 0.95rem;
}

input[type="text"],
textarea {
  width: 100%;
  padding: 8px;
  margin-top: 4px;
  border-radius: 4px;
  border: 1px solid #cbd5e1;
  box-sizing: border-box;
  font-size: 0.95rem;
}

textarea {
  resize: vertical;
}

.buttons {
  margin-top: 10px;
}

/* Botones */
button {
  padding: 8px 14px;
  margin-right: 8px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
}

#save-btn {
  background-color: #2563eb;
  color: white;
}

#save-btn:hover {
  background-color: #1d4ed8;
}

#cancel-btn {
  background-color: #e5e7eb;
}

#cancel-btn:hover {
  background-color: #d1d5db;
}

/* Tabla */
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  font-size: 0.9rem;
}

th,
td {
  border-bottom: 1px solid #e5e7eb;
  padding: 8px;
  text-align: left;
}

th {
  background-color: #f1f5f9;
  font-weight: 600;
}

tr:nth-child(even) {
  background-color: #f9fafb;
}

/* Botones de acción */
.action-btn {
  margin-right: 6px;
  padding: 4px 10px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 0.8rem;
}

.edit-btn {
  background-color: #22c55e;
  color: #fff;
}

.edit-btn:hover {
  background-color: #16a34a;
}

.delete-btn {
  background-color: #ef4444;
  color: #fff;
}

.delete-btn:hover {
  background-color: #dc2626;
}

/* Footer */
footer {
  text-align: center;
  color: #6b7280;
  font-size: 0.8rem;
  margin-top: 10px;
}

/* Responsive */
@media (max-width: 600px) {
  body {
    padding: 10px;
  }

  table,
  thead,
  tbody,
  th,
  td,
  tr {
    display: block;
  }

  thead {
    display: none;
  }

  tr {
    margin-bottom: 10px;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 8px;
    background: #ffffff;
  }

  td {
    border: none;
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
  }

  td::before {
    content: attr(data-label);
    font-weight: 600;
    margin-right: 8px;
    color: #6b7280;
  }
}
``` 

Crea el archivo `app.js`

> 👉 Cambia API_BASE_URL por la URL real de tu Cloud Function.

``` javascript
// URL base de la Cloud Function
const API_BASE_URL = "https://notes-api-cinsoje5sq-uc.a.run.app";

const form = document.getElementById("note-form");
const noteIdInput = document.getElementById("note-id");
const titleInput = document.getElementById("note-title");
const detailInput = document.getElementById("note-detail");
const cancelBtn = document.getElementById("cancel-btn");
const formTitle = document.getElementById("form-title");
const notesTbody = document.getElementById("notes-tbody");

async function fetchNotes() {
  const res = await fetch(`${API_BASE_URL}/notes`);
  if (!res.ok) {
    console.error("Error fetching notes", res.status);
    return;
  }
  const notes = await res.json();
  renderNotes(notes);
}

function renderNotes(notes) {
  notesTbody.innerHTML = "";
  notes.forEach((note) => {
    const tr = document.createElement("tr");

    const tdTitle = document.createElement("td");
    tdTitle.textContent = note.title;

    const tdCreated = document.createElement("td");
    tdCreated.textContent = note.created_at
      ? new Date(note.created_at).toLocaleString()
      : "";

    const tdActions = document.createElement("td");

    const editBtn = document.createElement("button");
    editBtn.textContent = "Editar";
    editBtn.className = "action-btn edit-btn";
    editBtn.onclick = () => loadNoteForEdit(note);

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "Eliminar";
    deleteBtn.className = "action-btn delete-btn";
    deleteBtn.onclick = () => deleteNote(note.id);

    tdActions.appendChild(editBtn);
    tdActions.appendChild(deleteBtn);

    tr.appendChild(tdTitle);
    tr.appendChild(tdCreated);
    tr.appendChild(tdActions);

    notesTbody.appendChild(tr);
  });
}

function resetForm() {
  noteIdInput.value = "";
  titleInput.value = "";
  detailInput.value = "";
  formTitle.textContent = "Crear nota";
}

function loadNoteForEdit(note) {
  noteIdInput.value = note.id;
  titleInput.value = note.title;
  detailInput.value = note.detail || "";
  formTitle.textContent = "Editar nota";
}

async function saveNote(event) {
  event.preventDefault();

  const id = noteIdInput.value.trim();
  const payload = {
    title: titleInput.value.trim(),
    detail: detailInput.value.trim(),
  };

  if (!payload.title) {
    alert("El título es obligatorio");
    return;
  }

  let url = `${API_BASE_URL}/notes`;
  let method = "POST";

  if (id) {
    url = `${API_BASE_URL}/notes/${id}`;
    method = "PUT";
  }

  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    console.error("Error saving note:", error);
    alert("Error guardando la nota");
    return;
  }

  resetForm();
  fetchNotes();
}

async function deleteNote(id) {
  if (!confirm("¿Eliminar esta nota?")) return;

  const res = await fetch(`${API_BASE_URL}/notes/${id}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    console.error("Error deleting note");
    alert("Error eliminando la nota");
    return;
  }

  fetchNotes();
}

form.addEventListener("submit", saveNote);
cancelBtn.addEventListener("click", resetForm);

fetchNotes();
``` 

---

## 🌐 Paso 8: Crear el sitio web con Cloud Storage

Crear bucket:

``` bash
gsutil mb -l $REGION gs://$BUCKET_NAME
```

Configurar sitio estático:

``` bash
gsutil web set -m index.html -e index.html gs://$BUCKET_NAME
```

Permitir acceso público:

``` bash
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
```

---

## 📤 Paso 9: Subir el frontend

``` bash
gsutil cp index.html styles.css app.js gs://$BUCKET_NAME
```

---

## 🌍 Paso 10: URL del sitio

    http://storage.googleapis.com/<BUCKET_NAME>/index.html

---

## 🧹 Paso 11: Limpieza (opcional)

``` bash
gcloud functions delete $FUNCTION_NAME --region=$REGION --quiet
gsutil rm -r gs://$BUCKET_NAME
```
