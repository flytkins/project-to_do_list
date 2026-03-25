const API_URL = ""; // Relative to same origin (nginx proxy handles /tasks)

const taskForm = document.getElementById("taskForm");
const taskList = document.getElementById("taskList");
const searchInput = document.getElementById("searchInput");

let allTasks = [];
let asc = true;
let searchQuery = "";

// Sorting
function toggleSort() {
  asc = !asc;
  renderTasks();
}

// Filtering
function filterTasks() {
  if (!searchQuery) return allTasks;
  return allTasks.filter(task =>
    task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (task.description && task.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );
}

// Render tasks: filter, sort, then build HTML
function renderTasks() {
  let filtered = filterTasks();
  filtered.sort((a, b) => {
    return asc
      ? a.title.localeCompare(b.title)
      : b.title.localeCompare(a.title);
  });

  taskList.innerHTML = "";
  filtered.forEach(task => {
    const li = document.createElement("li");
    const completed = task.status === "completed";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = completed;
    checkbox.addEventListener("change", () => toggleStatus(task.id, checkbox.checked));

    const titleSpan = document.createElement("span");
    titleSpan.className = "task-title";
    if (completed) titleSpan.classList.add("completed");
    titleSpan.textContent = task.title;

    const editBtn = document.createElement("button");
    editBtn.textContent = "✏️";
    editBtn.addEventListener("click", () => editTask(task.id, task.title));

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "❌";
    deleteBtn.addEventListener("click", () => deleteTask(task.id));

    li.appendChild(checkbox);
    li.appendChild(titleSpan);
    li.appendChild(editBtn);
    li.appendChild(deleteBtn);
    taskList.appendChild(li);
  });
}

// Fetch all tasks from server
async function loadTasks() {
  const response = await fetch(`${API_URL}/tasks`);
  allTasks = await response.json();
  renderTasks();
}

// Create new task
async function createTask(title) {
  await fetch(`${API_URL}/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, status: "pending" })
  });
  loadTasks();
}

// Delete task
async function deleteTask(id) {
  await fetch(`${API_URL}/tasks/${id}`, { method: "DELETE" });
  loadTasks();
}

// Toggle completion status
async function toggleStatus(id, isCompleted) {
  const newStatus = isCompleted ? "completed" : "pending";
  await fetch(`${API_URL}/tasks/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status: newStatus })
  });
  loadTasks();
}

// Edit task title
async function editTask(id, oldTitle) {
  const newTitle = prompt("Введите новое название:", oldTitle);
  if (newTitle && newTitle.trim()) {
    await fetch(`${API_URL}/tasks/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: newTitle.trim() })
    });
    loadTasks();
  }
}

// Form submit handler
taskForm.addEventListener("submit", function (e) {
  e.preventDefault();
  const title = document.getElementById("title").value;
  createTask(title);
  taskForm.reset();
});

// Search input handler
searchInput.addEventListener("input", (e) => {
  searchQuery = e.target.value;
  renderTasks();
});

// Initial load
loadTasks();