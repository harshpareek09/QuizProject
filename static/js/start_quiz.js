console.log("📘 start_quiz.js loaded");

document.addEventListener("DOMContentLoaded", async () => {
  const quizArea = document.getElementById("questionArea");
  const loader = document.getElementById("loader");
  const submitBtn = document.getElementById("submitQuizBtn");

  if (!quiz_id || !student_email) {
    quizArea.innerHTML = "<p style='color: red;'>❌ Invalid quiz access.</p>";
    return;
  }

  // 🚨 Cheating Detection
  async function handleViolation(reason) {
    console.warn("🚨 Cheating detected:", reason);
    try {
      await fetch("/student/violation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ student_email, quiz_id, reason })
      });

      await fetch("/student/final-submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ student_email, quiz_id })
      });

      alert("🚨 Cheating Detected: " + reason + "\nQuiz auto-submitted with 0 marks.");
      window.location.href = `/student/view-result/${quiz_id}?email=${student_email}`;

    } catch (err) {
      console.error("❌ Violation submission failed:", err);
    }
  }

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) handleViolation("Tab switch detected");
  });

  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey && ["c", "v"].includes(e.key.toLowerCase())) || e.key === "PrintScreen") {
      handleViolation("Copy/Paste or Screenshot attempt");
    }
    if ((e.ctrlKey && e.shiftKey && e.key.toLowerCase() === "i") || e.key === "F12") {
      handleViolation("Dev tools opened");
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth < 600 || window.innerHeight < 400) {
      handleViolation("Floating window or screen resized");
    }
  });

  if ("Notification" in window && Notification.permission === "denied") {
    handleViolation("Notifications blocked");
  }

  // ✅ Load Quiz Questions
  try {
    const res = await fetch(`/student/quiz/${quiz_id}`);
    const data = await res.json();
    loader.remove();

    if (!data.success) {
      quizArea.innerHTML = `<p style='color: red;'>❌ ${data.message}</p>`;
      return;
    }

    data.questions.forEach((q, i) => {
      const box = document.createElement("div");
      box.className = "question-box";

      const h4 = document.createElement("h4");
      h4.textContent = `Q${i + 1}. ${q.question_text}`;
      box.appendChild(h4);

      for (let opt = 1; opt <= 4; opt++) {
        const div = document.createElement("div");
        div.className = "option";

        const radio = document.createElement("input");
        radio.type = "radio";
        radio.name = `question_${q.question_id}`;
        radio.value = opt;

        const label = document.createElement("label");
        label.textContent = q[`option${opt}`];

        div.appendChild(radio);
        div.appendChild(label);
        box.appendChild(div);
      }

      quizArea.appendChild(box);
    });
  } catch (err) {
    console.error("❌ Error loading questions:", err);
    quizArea.innerHTML = `<p style='color: red;'>⚠️ Failed to load quiz.</p>`;
  }

  // ✅ Submit Quiz
  submitBtn.addEventListener("click", async () => {
    const answers = [];
    document.querySelectorAll(".question-box").forEach((box) => {
      const questionId = box.querySelector("input").name.split("_")[1];
      const selected = box.querySelector("input:checked");
      if (selected) {
        answers.push({ question_id: parseInt(questionId), selected_option: parseInt(selected.value) });
      }
    });

    if (answers.length === 0 || answers.length !== document.querySelectorAll(".question-box").length) {
      alert("❗ Please answer all questions before submitting.");
      return;
    }

    try {
      for (let ans of answers) {
        await fetch("/student/submit-response", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            student_email,
            quiz_id,
            question_id: ans.question_id,
            selected_option: ans.selected_option
          })
        });
      }

      const res = await fetch("/student/final-submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ student_email, quiz_id })
      });

      const result = await res.json();
      if (result.success) {
        alert(`✅ Quiz submitted!\nScore: ${result.score}`);
        window.location.href = `/student/view-result/${quiz_id}?email=${student_email}`;
      } else {
        alert("❌ Failed to submit quiz.");
      }
    } catch (err) {
      console.error("❌ Submission failed:", err);
      alert("⚠️ Error occurred during submission.");
    }
  });
});
