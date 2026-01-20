/* ---------- Loader ---------- */
function showLoader() {
  const loader = document.getElementById("loader");
  if (loader) loader.style.display = "flex";
}

/* ---------- Drag & Drop ---------- */
const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const fileNameText = document.getElementById("file-name");

function dragOver(e) {
  e.preventDefault();
  dropZone.classList.add("drag-over");
}

function dragLeave(e) {
  dropZone.classList.remove("drag-over");
}

function dropFile(e) {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  const file = e.dataTransfer.files[0];
  if (!file) return;

  const dataTransfer = new DataTransfer();
  dataTransfer.items.add(file);
  fileInput.files = dataTransfer.files;

  updateFileName();
}

function updateFileName() {
  if (fileInput.files.length > 0) {
    fileNameText.innerText = fileInput.files[0].name;
  } else {
    fileNameText.innerText = "Drag & Drop or Click to Upload Image";
  }
}

/* ---------- Theme toggle ---------- */
function toggleTheme() {
  const body = document.body;
  const toggle = document.querySelector(".theme-toggle");
  body.classList.toggle("light");
  toggle.innerText = body.classList.contains("light") ? "☀️" : "🌙";
}

/* ---------- DOM ---------- */
document.addEventListener("DOMContentLoaded", () => {
  dropZone.addEventListener("dragover", dragOver);
  dropZone.addEventListener("dragleave", dragLeave);
  dropZone.addEventListener("drop", dropFile);
  fileInput.addEventListener("change", updateFileName);
});
