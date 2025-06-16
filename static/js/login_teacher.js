console.log("✅ Teacher JS Loaded");

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("teacherloginbtn");
  const msg = document.getElementById("message");
  const card = document.getElementById("loginCard");

  if (!btn) {
    console.error("❌ Teacher Login button not found");
    return;
  }

  btn.addEventListener("click", async () => {
    const teacherId = document.getElementById("teacherId").value.trim();
    const full_name = document.getElementById("teacherName").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!teacherId || !full_name || !password) {
      msg.textContent = "❗ All fields are required!";
      msg.style.color = "red";
      return;
    }

    const loginData = {
      teacher_id: teacherId,
      full_name: full_name,
      password: password,
    };

    try {
      const response = await fetch("/teacher/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(loginData)
      });

      const result = await response.json();

      if (response.ok && result.success) {
        card.style.opacity = 0;

        setTimeout(() => {
          card.innerHTML = `
            <h2 style="color: lightgreen;">✅ Login Successful</h2>
            <p style="margin-top: 15px; font-size: 16px;">Welcome, ${full_name}!</p>
          `;
          card.style.transition = "opacity 0.8s ease";
          card.style.opacity = 1;

          // Optionally redirect after 1.5s
          setTimeout(() => {
            window.location.href = "/teacher-dashboard";
          }, 1500);
        }, 500);
      } else {
        msg.textContent = result.message || "❌ Invalid login details!";
        msg.style.color = "red";
      }
    } catch (error) {
      console.error("❌ Error during login:", error);
      msg.textContent = "⚠️ Server error. Please try again.";
      msg.style.color = "red";
    }
  });
});
