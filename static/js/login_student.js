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

    const pathParts = window.location.pathname.split('/');
    const quiz_id = pathParts[pathParts.length - 1];

    if (!email || !full_name || !course) {
      msg.textContent = "❗ All fields are required.";
      msg.style.color = "red";
      return;
    }

    const loginData = {
      email: email,
      full_name: full_name,
      course: course,
      quiz_id: quiz_id
    };

    try {
      const response = await fetch("/student/login-quiz", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(loginData)
      });

      const result = await response.json();

      if (response.ok && result.status === "success") {
        msg.style.color = "lightgreen";

        if (result.already_attempted && result.redirect_url) {
          msg.textContent = "ℹ️ You have already attempted this quiz. Redirecting to result...";
          setTimeout(() => {
            window.location.href = result.redirect_url;
          }, 1500);
        } else {
          msg.textContent = "✅ Login successful! Redirecting to quiz...";
          setTimeout(() => {
            window.location.href = `/student/start-quiz/${quiz_id}?email=${encodeURIComponent(email)}`;
          }, 1500);
        }

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
