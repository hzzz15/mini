// 모든 circle 요소 선택
const circles = document.querySelectorAll('.circle');

// 클릭 이벤트 추가
circles.forEach(circle => {
    circle.addEventListener('click', () => {
        circle.classList.toggle('active'); // active 클래스 토글
        console.log('Circle clicked!'); // 클릭 확인용 로그
    });
});
