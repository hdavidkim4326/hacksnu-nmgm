// nmgm/static/nmgm/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    
    // SNS 필터 버튼 상호작용
    const snsFilter = document.querySelector('.sns-filter');
    const filterButtons = document.querySelectorAll('.filter-btn');

    if (snsFilter) {
        snsFilter.addEventListener('click', (event) => {
            const clickedButton = event.target.closest('.filter-btn');

            if (!clickedButton) return;

            // 모든 버튼에서 active 클래스 제거
            filterButtons.forEach(button => {
                button.classList.remove('active');
            });

            // 클릭된 버튼에 active 클래스 추가
            clickedButton.classList.add('active');

            // TODO: 실제 기능 구현 시, 선택된 플랫폼(kakao, instagram 등)에 따라
            // 채팅방 리스트를 비동기(AJAX/Fetch)로 불러오는 로직을 추가할 수 있습니다.
            const platform = clickedButton.textContent;
            console.log(platform + ' 필터 선택됨');
        });
    }

    // 동기화 버튼 상호작용 (예시)
    const syncButton = document.querySelector('.btn-sync');
    if (syncButton) {
        syncButton.addEventListener('click', () => {
            // 아이콘에 애니메이션 클래스 추가
            const icon = syncButton.querySelector('svg');
            icon.style.transition = 'transform 0.5s ease';
            icon.style.transform = 'rotate(360deg)';

            // 애니메이션이 끝나면 원상태로 복구
            setTimeout(() => {
                icon.style.transform = 'rotate(0deg)';
            }, 500);

            // TODO: 채팅 리스트를 새로고침하는 API 호출 로직 추가
            console.log('동기화 버튼 클릭됨');
        });
    }

});

// 팝업 애니메이션 적용 