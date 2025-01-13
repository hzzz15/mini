document.getElementById("login-button").addEventListener("click", () => {
    const popup = document.getElementById("login-popup");
    popup.style.display = "flex";
});

document.getElementById("popup-overlay").addEventListener("click", () => {
    const popup = document.getElementById("login-popup");
    popup.style.display = "none";
});

document.getElementById("login-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({ username, password }),
        });

        if (response.ok) {
            window.location.href = "/home?username=" + username;
        } else {
            const errorMessage = await response.json();
            alert(errorMessage.message);
        }
    } catch (error) {
        console.error("로그인 요청 중 오류:", error);
        alert("로그인 요청 중 문제가 발생했습니다.");
    }
});
