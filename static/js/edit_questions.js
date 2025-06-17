// 👇 Called when the page loads
window.onload = () => {
  loadQuestions();
};

const container = document.getElementById("questionContainer");

// ✅ 1. Fetch and show all questions
async function loadQuestions() {
  try {
    const res = await fetch(`/teacher/questions/${quizId}`);
    const data = await res.json();

    container.innerHTML = "";

    if (!data.success || data.questions.length === 0) {
      container.innerHTML = "<p>No questions found for this quiz.</p>";
      return;
    }

    data.questions.forEach((q) => {
      renderQuestionCard(q);
    });
  } catch (err) {
    console.error("Error loading questions:", err);
    container.innerHTML = "<p>Error loading questions.</p>";
  }
}

// ✅ 2. Render card for each question
function renderQuestionCard(q) {
  const card = document.createElement("div");
  card.className = "card";

  card.innerHTML = `
    <h3>Edit Question</h3>
    <div class="form-group">
      <label>Question Text</label>
      <input type="text" class="question-text" value="${q.question_text}">
    </div>
    <div class="form-group">
      <label>Option 1</label>
      <input type="text" class="option1" value="${q.option1}">
    </div>
    <div class="form-group">
      <label>Option 2</label>
      <input type="text" class="option2" value="${q.option2}">
    </div>
    <div class="form-group">
      <label>Option 3</label>
      <input type="text" class="option3" value="${q.option3}">
    </div>
    <div class="form-group">
      <label>Option 4</label>
      <input type="text" class="option4" value="${q.option4}">
    </div>
    <div class="form-group">
      <label>Correct Option (1 to 4)</label>
      <select class="correct-option">
        <option value="1" ${q.correct_option == 1 ? "selected" : ""}>1</option>
        <option value="2" ${q.correct_option == 2 ? "selected" : ""}>2</option>
        <option value="3" ${q.correct_option == 3 ? "selected" : ""}>3</option>
        <option value="4" ${q.correct_option == 4 ? "selected" : ""}>4</option>
      </select>
    </div>
    <div class="button-group">
      <button class="btn save"><i class="fas fa-save"></i> Save</button>
      <button class="btn delete"><i class="fas fa-trash"></i> Delete</button>
    </div>
  `;

  // 👉 Save button handler
  card.querySelector(".save").addEventListener("click", async () => {
    const payload = {
      question_text: card.querySelector(".question-text").value,
      option1: card.querySelector(".option1").value,
      option2: card.querySelector(".option2").value,
      option3: card.querySelector(".option3").value,
      option4: card.querySelector(".option4").value,
      correct_option: card.querySelector(".correct-option").value,
    };

    try {
      const res = await fetch(`/teacher/update-question/${q.question_id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const result = await res.json();
      alert(result.message);
    } catch (err) {
      alert("Error updating question");
    }
  });

  // 👉 Delete button handler
  card.querySelector(".delete").addEventListener("click", async () => {
    if (confirm("Are you sure you want to delete this question?")) {
      try {
        const res = await fetch(`/teacher/delete-question/${q.question_id}`, {
          method: "DELETE",
        });

        const result = await res.json();
        alert(result.message);
        if (result.success) loadQuestions(); // Reload
      } catch (err) {
        alert("Error deleting question");
      }
    }
  });

  container.appendChild(card);
}

// ✅ 3. Add new question form
function addNewQuestionForm() {
  const blank = {
    question_id: null,
    question_text: "",
    option1: "",
    option2: "",
    option3: "",
    option4: "",
    correct_option: 1,
  };
  renderAddQuestionCard(blank);
}

function renderAddQuestionCard(q) {
  const card = document.createElement("div");
  card.className = "card";

  card.innerHTML = `
    <h3>Add New Question</h3>
    <div class="form-group">
      <label>Question Text</label>
      <input type="text" class="question-text" value="${q.question_text}">
    </div>
    <div class="form-group">
      <label>Option 1</label>
      <input type="text" class="option1" value="${q.option1}">
    </div>
    <div class="form-group">
      <label>Option 2</label>
      <input type="text" class="option2" value="${q.option2}">
    </div>
    <div class="form-group">
      <label>Option 3</label>
      <input type="text" class="option3" value="${q.option3}">
    </div>
    <div class="form-group">
      <label>Option 4</label>
      <input type="text" class="option4" value="${q.option4}">
    </div>
    <div class="form-group">
      <label>Correct Option (1 to 4)</label>
      <select class="correct-option">
        <option value="1" selected>1</option>
        <option value="2">2</option>
        <option value="3">3</option>
        <option value="4">4</option>
      </select>
    </div>
    <div class="button-group">
      <button class="btn save"><i class="fas fa-plus-circle"></i> Add</button>
    </div>
  `;

  card.querySelector(".save").addEventListener("click", async () => {
    const payload = {
      quiz_id: quizId,
      question_text: card.querySelector(".question-text").value,
      option1: card.querySelector(".option1").value,
      option2: card.querySelector(".option2").value,
      option3: card.querySelector(".option3").value,
      option4: card.querySelector(".option4").value,
      correct_option: card.querySelector(".correct-option").value,
    };

    try {
      const res = await fetch(`/teacher/add-question`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const result = await res.json();
      alert(result.message);
      if (result.success) loadQuestions();
    } catch (err) {
      alert("Error adding question");
    }
  });

  container.appendChild(card);
}
