async function loadQuizzes() {
  const container = document.getElementById("quizContainer");
  const template = document.getElementById("quizCardTemplate");

  try {
    const res = await fetch(`/teacher/quizzes/${teacherId}`);
    const data = await res.json();

    if (
      !data.success ||
      !Array.isArray(data.quizzes) ||
      data.quizzes.length === 0
    ) {
      container.innerHTML =
        "<p style='font-weight: bold;'>No quizzes created yet.</p>";
      return;
    }

    container.innerHTML = "";

    data.quizzes.forEach((quiz) => {
      const clone = template.content.cloneNode(true);

      clone.querySelector(".quiz-title").textContent = quiz.title;
      clone.querySelector(".quiz-id").textContent = quiz.quiz_id;
      clone.querySelector(".quiz-date").textContent = new Date(
        quiz.created_at
      ).toLocaleDateString();

      // Edit button
      clone.querySelector(".edit-btn").addEventListener("click", () => {
        window.location.href = `/edit-quiz/${quiz.quiz_id}`;
      });

      // DELETE API + reload
      clone.querySelector(".delete-btn").addEventListener("click", async () => {
        const confirmDelete = confirm(
          `Are you sure you want to delete Quiz ID: ${quiz.quiz_id}?`
        );
        if (!confirmDelete) return;

        try {
          const res = await fetch(`/teacher/delete-quiz/${quiz.quiz_id}`, {
            method: "DELETE",
          });

          const result = await res.json();
          if (result.success) {
            alert("Quiz deleted successfully!");
            loadQuizzes(); // Refresh cards
          } else {
            alert("Failed to delete: " + result.message);
          }
        } catch (err) {
          console.error("Error deleting:", err);
          alert("Server error while deleting quiz.");
        }
      });

      // View Result
      clone.querySelector(".result-btn").addEventListener("click", () => {
        window.location.href = `/view-result/${quiz.quiz_id}`;
      });

      container.appendChild(clone);
    });
  } catch (error) {
    console.error("Failed to load quizzes:", error);
    container.innerHTML = "<p style='color: red;'>Error loading quizzes.</p>";
  }
}

window.onload = loadQuizzes;
