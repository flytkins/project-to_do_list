const API_URL = "";

const taskForm = document.getElementById("taskForm");
const taskList = document.getElementById("taskList");

let asc = true;

function toggleSort() {
    asc = !asc;
    loadTasks();
}

async function loadTasks() {
  const response = await fetch(`${API_URL}/tasks`);
  const tasks = await response.json();

  tasks.sort((a, b) => {
    return asc
        ? a.title.localeCompare(b.title)
        : b.title.localeCompare(a.title);
  });

  taskList.innerHTML = "";

  tasks.forEach(task => {
    const li = document.createElement("li");
    li.innerHTML = `
      ${task.title}
      <button onclick="deleteTask(${task.id})">❌</button>
    `;
    taskList.appendChild(li);
  });
}

async function createTask(title) {
  await fetch(`${API_URL}/tasks`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ title })
  });

  loadTasks();
}

async function deleteTask(id) {
  await fetch(`${API_URL}/tasks/${id}`, {
    method: "DELETE"
  });

  loadTasks();
}

taskForm.addEventListener("submit", function (e) {
  e.preventDefault();
  const title = document.getElementById("title").value;
  createTask(title);
  taskForm.reset();
});

loadTasks();