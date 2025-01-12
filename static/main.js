// 로그인 버튼 클릭 시 팝업 표시
document.getElementById("login-button").addEventListener("click", () => {
    const popup = document.getElementById("login-popup");
    popup.style.display = "flex";
});

// 팝업 배경 클릭 시 팝업 닫기
document.getElementById("popup-overlay").addEventListener("click", () => {
    const popup = document.getElementById("login-popup");
    popup.style.display = "none";
});

// 로그인 폼 제출 처리
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
            window.location.href = "/home?username=" + username; // 홈으로 이동
        } else {
            const errorMessage = await response.json();
            alert(errorMessage.message);
        }
    } catch (error) {
        console.error("로그인 요청 중 오류:", error);
        alert("로그인 요청 중 문제가 발생했습니다.");
    }
});
