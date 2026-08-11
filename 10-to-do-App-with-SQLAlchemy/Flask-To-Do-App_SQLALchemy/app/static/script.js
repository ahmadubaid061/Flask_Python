// show/hide add task form + overlay
const addForm = document.getElementById("addtask_form");
const overlay = document.querySelector(".overlay");

function toggleAddform() {
  const isOpen = addForm.classList.contains("show");
  if (isOpen) {
    addForm.classList.remove("show");
    overlay.classList.remove("show");
  } else {
    addForm.classList.add("show");
    overlay.classList.add("show");
  }
}

// prevent clicks inside the form from closing it via the overlay
addForm.addEventListener("click", function (e) {
  e.stopPropagation();
});

// disappearing flash messages
setTimeout(function () {
  const msg = document.getElementById("flash-message");
  if (msg) {
    msg.style.display = "none";
  }
}, 3000);
