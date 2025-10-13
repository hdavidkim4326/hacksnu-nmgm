document.addEventListener('DOMContentLoaded', () => {

    // 1. 스크롤 시 헤더에 그림자 효과 추가
    const header = document.querySelector('.main-header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 10) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    // 2. 네비게이션 링크 클릭 시 부드럽게 스크롤
    const navLinks = document.querySelectorAll('.main-nav a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const headerOffset = header.offsetHeight;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // 3. 파일 드래그 앤 드롭 존 (시각적 효과)
    const dropZone = document.querySelector('.file-drop-zone');
    if (dropZone) {
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                console.log('File dropped:', files[0].name);
                alert(`${files[0].name} 파일이 선택되었습니다. (실제 업로드 기능 구현 필요)`);
            }
        });
    }

    // 4. 스크롤에 따른 섹션 나타나는 애니메이션
    const sections = document.querySelectorAll('.fade-in-section');
    const observerOptions = {
        root: null, // 뷰포트를 기준으로
        rootMargin: '0px',
        threshold: 0.1 // 섹션이 10% 보이면 실행
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target); // 애니메이션은 한 번만 실행
            }
        });
    }, observerOptions);

    sections.forEach(section => {
        observer.observe(section);
    });
});


// 5. 기술 소개 탭 기능
const techMenuItems = document.querySelectorAll('.tech-menu-item');
const techContents = document.querySelectorAll('.tech-content');

techMenuItems.forEach(item => {
    item.addEventListener('click', () => {
        const tabId = item.getAttribute('data-tab');

        // 모든 메뉴와 컨텐츠에서 active 클래스 제거
        techMenuItems.forEach(menu => menu.classList.remove('active'));
        techContents.forEach(content => content.classList.remove('active'));

        // 클릭한 메뉴와 해당 컨텐츠에 active 클래스 추가
        item.classList.add('active');
        document.getElementById(tabId).classList.add('active');
    });
});