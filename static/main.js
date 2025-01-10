document.addEventListener('DOMContentLoaded', () => {
    const loginButton = document.getElementById('login-button'); // 로그인 버튼
    const loginPopup = document.getElementById('login-popup');   // 팝업 창
    const closePopup = document.getElementById('close-popup');   // 닫기 버튼
    const popupOverlay = document.querySelector('.popup-overlay'); // 팝업 배경

    // 팝업 열기
    if (loginButton) {
        loginButton.addEventListener('click', () => {
            loginPopup.style.display = 'flex'; // 팝업 표시
        });
    }

    // 팝업 닫기 버튼
    if (closePopup) {
        closePopup.addEventListener('click', () => {
            loginPopup.style.display = 'none'; // 팝업 숨김
        });
    }

    // 팝업 외부 클릭 시 닫기
    if (popupOverlay) {
        popupOverlay.addEventListener('click', () => {
            loginPopup.style.display = 'none'; // 팝업 숨김
        });
    }

    // 로그인 버튼 클릭 시 홈으로 이동
    const loginSubmitButton = document.querySelector('.login-button'); // 로그인 제출 버튼
    if (loginSubmitButton) {
        loginSubmitButton.addEventListener('click', (event) => {
            event.preventDefault(); // 폼 제출 방지
            window.location.href = '/home'; // home.html로 이동
        });
    }

    // 프롬프트 입력 후 제출 버튼 클릭 시 고정된 URL로 이동
    const promptSubmitButton = document.getElementById('submit-button'); // 프롬프트 제출 버튼
    const promptInput = document.getElementById('prompt-input');         // 입력 필드

    if (promptSubmitButton && promptInput) {
        promptSubmitButton.addEventListener('click', (event) => {
            event.preventDefault(); // 기본 동작 방지 (폼 제출 방지)
            window.location.href = 'http://127.0.0.1:8000/main_home_pli';
        });
    }
});