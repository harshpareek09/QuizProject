console.log("✅ Student JS Loaded");

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("studentloginbtn");
  const msg = document.getElementById("message");

  if (!btn) {
    console.error("❌ Student Login button not found");
    return;
  }

  btn.addEventListener("click", async () => {
    const email = document.getElementById("email").value.trim();
    const full_name = document.getElementById("studentName").value.trim();
    const course = document.getElementById("course").value.trim();

    if (!email || !full_name || !course) {
      msg.textContent = "❗ All fields are required.";
      msg.style.color = "red";
      return;
    }

    const loginData = {
      email: email,
      full_name: full_name,
      course: course
    };

    try {
      const response = await fetch("/student/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(loginData)
      });

      const result = await response.json();

      if (response.ok && result.status === "success") {
        msg.style.color = "lightgreen";
        msg.textContent = "✅ Login successful! Redirecting...";
        setTimeout(() => {
          // Redirect to quiz page (you can customize quiz_id)
          window.location.href = "/attempt_quiz.html?quiz_id=1";
        }, 1500);
      } else {
        msg.style.color = "red";
        msg.textContent = `❌ ${result.message || "Invalid credentials"}`;
      }
    } catch (err) {
      console.error("❌ Error in login:", err);
      msg.textContent = "⚠️ Server error. Please try again later.";
      msg.style.color = "red";
    }
  });
});
