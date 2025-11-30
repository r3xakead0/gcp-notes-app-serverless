/* ---------------------------------------------------------------------
 * Author: Afu Tse
 * GitHub Repo: https://github.com/r3xakead0/gcp-notes-app-serverless
 * Description: JavaScript for a frontend notes application
 * -------------------------------------------------------------------*/

// Base URL of the Cloud Function
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
    editBtn.textContent = "Edit";
    editBtn.className = "action-btn edit-btn";
    editBtn.onclick = () => loadNoteForEdit(note);

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "Delete";
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
  formTitle.textContent = "Create note";
}

function loadNoteForEdit(note) {
  noteIdInput.value = note.id;
  titleInput.value = note.title;
  detailInput.value = note.detail || "";
  formTitle.textContent = "Edit note";
}

async function saveNote(event) {
  event.preventDefault();

  const id = noteIdInput.value.trim();
  const payload = {
    title: titleInput.value.trim(),
    detail: detailInput.value.trim(),
  };

  if (!payload.title) {
    alert("Title is required");
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
    alert("Error saving the note");
    return;
  }

  resetForm();
  fetchNotes();
}

async function deleteNote(id) {
  if (!confirm("Delete this note?")) return;

  const res = await fetch(`${API_BASE_URL}/notes/${id}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    console.error("Error deleting note");
    alert("Error deleting the note");
    return;
  }

  fetchNotes();
}

form.addEventListener("submit", saveNote);
cancelBtn.addEventListener("click", resetForm);

fetchNotes();
