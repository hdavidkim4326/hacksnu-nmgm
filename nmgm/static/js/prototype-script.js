document.addEventListener('DOMContentLoaded', () => {

    // 1. 스크롤 시 헤더에 그림자 효과 추가
    const header = document.querySelector('.main-header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 10) header.classList.add('scrolled');
            else header.classList.remove('scrolled');
        });
    }

    // 2. 네비게이션 부드러운 스크롤
    const navLinks = document.querySelectorAll('.main-nav a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const offset = target.getBoundingClientRect().top + window.pageYOffset - header.offsetHeight;
                window.scrollTo({ top: offset, behavior: 'smooth' });
            }
        });
    });

    // 3. 파일 드래그 & 드롭
    const dropZone = document.querySelector('.file-drop-zone');
    const fileInput = document.getElementById('chat-file-input');
    const startAnalysisBtn = document.getElementById('start-analysis-btn');
    let selectedFile = null;

    function handleFileSelect(file) {
        if (!file) return;
        selectedFile = file;
        dropZone.querySelector('p').textContent = `선택된 파일: ${file.name}`;
        dropZone.style.borderColor = 'var(--primary-light)';
        startAnalysisBtn.disabled = false;
    }

    if (dropZone) {
        dropZone.addEventListener('dragover', e => {
            e.preventDefault();
            dropZone.style.backgroundColor = 'rgba(255,255,255,0.1)';
        });
        dropZone.addEventListener('dragleave', () => {
            dropZone.style.backgroundColor = 'transparent';
        });
        dropZone.addEventListener('drop', e => {
            e.preventDefault();
            dropZone.style.backgroundColor = 'transparent';
            if (e.dataTransfer.files.length > 0) {
                handleFileSelect(e.dataTransfer.files[0]);
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', e => {
            if (e.target.files.length > 0) handleFileSelect(e.target.files[0]);
        });
    }

    // 4. 파일 업로드 및 분석 요청
    if (startAnalysisBtn) {
        startAnalysisBtn.addEventListener('click', async () => {
            if (!selectedFile) {
                alert('분석할 파일을 선택해주세요.');
                return;
            }

            startAnalysisBtn.textContent = '분석 중...';
            startAnalysisBtn.disabled = true;

            const formData = new FormData();
            formData.append('file', selectedFile);

            try {
                // ① CSV 파일 업로드
                const uploadResponse = await fetch('/import_data/', {
                    method: 'POST',
                    body: formData,
                });
                if (!uploadResponse.ok) throw new Error('업로드 실패');

                // ② 리포트 생성 요청
                const reportResponse = await fetch(`/generate_chatroom_report/?filepath=${selectedFile.name}`);
                if (!reportResponse.ok) throw new Error('리포트 생성 실패');

                const reportData = await reportResponse.json();

                // ③ 데이터 저장 후 리포트 페이지로 이동
                localStorage.setItem('reportData', JSON.stringify(reportData));
                window.location.href = startAnalysisBtn.dataset.reportUrl;

            } catch (error) {
                console.error('Error:', error);
                alert('분석 중 오류가 발생했습니다.');
            } finally {
                startAnalysisBtn.textContent = 'AI 분석 시작하기 →';
                startAnalysisBtn.disabled = false;
            }
        });
    }

    // 5. 섹션 페이드인 애니메이션
    const sections = document.querySelectorAll('.fade-in-section');
    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                obs.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    sections.forEach(section => observer.observe(section));

    // 6. 기술 소개 탭
    const techMenuItems = document.querySelectorAll('.tech-menu-item');
    const techContents = document.querySelectorAll('.tech-content');
    techMenuItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabId = item.getAttribute('data-tab');
            techMenuItems.forEach(menu => menu.classList.remove('active'));
            techContents.forEach(content => content.classList.remove('active'));
            item.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });
});
