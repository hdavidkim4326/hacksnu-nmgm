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
            // landing.html 페이지 내에서만 스크롤 이동
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

    // 3. 파일 드래그 앤 드롭 및 API 호출
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
    
    if(dropZone){
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
        });
        dropZone.addEventListener('dragleave', () => {
            dropZone.style.backgroundColor = 'transparent';
        });
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.style.backgroundColor = 'transparent';
            if (e.dataTransfer.files.length > 0) {
                handleFileSelect(e.dataTransfer.files[0]);
            }
        });
    }


    if(fileInput){
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
    }
    
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
                // --- 목업 데이터 (실제 API 연결 시 이 부분 삭제) ---
                await new Promise(resolve => setTimeout(resolve, 2000)); // 2초 딜레이
                const mockResponse = {
                  "chat_summary" : { "summary" : "제주도 여행 계획을 세우다 갈등이 발생했지만, 이후 관계 회복을 위해 노력하는 대화입니다.", "start_time": "2025-10-08T10:00:00Z", "end_time": "2025-10-14T23:59:59Z", "threads" : [ { "topic_summary" : "제주도 여행 계획", "chat_type" : "계획/정보공유", "num_messages" : 50 }, { "topic_summary" : "일상적인 감정 공유", "chat_type" : "감정공유", "num_messages" : 30 } ] },
                  "user_analysis" : [ { "username" : "현지", "personality" : "표현형 (Expressive)", "description" : "자신의 감정을 솔직하게 표현하며, 관계에서 적극적인 소통과 공감을 중요하게 생각합니다.", "avg_indices" : [ {"index" : "직설", "score" : 0.8}, {"index" : "감정", "score" : 0.7}, {"index" : "지배", "score" : 0.6}, {"index": "친화", "score": 0.9}, {"index": "논리", "score": 0.4} ], "median_response_time" : 1.5, "initiative_rate": 0.78, "messages" : [ {"sent_time" : "2025-10-10T14:42:00Z", "sentiment" : -0.8}, {"sent_time" : "2025-10-11T18:00:00Z", "sentiment" : 0.2}, {"sent_time" : "2025-10-12T11:20:00Z", "sentiment" : 0.9} ] }, { "username" : "민석", "personality" : "조화형 (Harmonizer)", "description" : "상대방의 감정에 공감하고 위로하려 하며, 갈등을 피하고 원만하게 해결하려는 노력을 보입니다.", "avg_indices" : [ {"index" : "직설", "score" : 0.3}, {"index" : "감정", "score" : 0.8}, {"index" : "지배", "score" : 0.2}, {"index": "친화", "score": 0.8}, {"index": "논리", "score": 0.6} ], "median_response_time" : 4.0, "initiative_rate": 0.22, "messages" : [ {"sent_time" : "2025-10-11T13:49:00Z", "sentiment" : -0.2}, {"sent_time" : "2025-10-12T09:00:00Z", "sentiment" : 0.5}, {"sent_time" : "2025-10-13T23:39:00Z", "sentiment" : 0.3} ] } ],
                  "warnings" : [ { "message" : "나만 표현하고 나만 맞추고", "sent_by" : "현지", "warning_type" : "감정해석차이", "detail" : "혼자인 것 같아 서운하다는 의미지만, 상대는 비난으로 들을 수 있습니다.", "action_plan" : "'나만' 대신 '나는 ~라고 느껴'와 같이 자신의 감정 중심으로 표현해보세요." }, { "message" : "요즘 일도 많고", "sent_by" : "민석", "warning_type" : "의미불일치", "detail" : "민석님은 회사 업무를 얘기한 거지만 현지님은 둘 사이의 일로 인해 민석님의 말이 줄었다고 받아들일 수 있습니다.", "action_plan" : "주어를 명확히 하여('회사 일이 많아서') 오해의 소지를 줄여보세요."} ]
                };
                const data = mockResponse;
                // --- 여기까지 목업 데이터 ---

                localStorage.setItem('reportData', JSON.stringify(data));
                window.open(startAnalysisBtn.dataset.reportUrl, '_blank');

            } catch (error) {
                console.error('Error:', error);
                alert('분석 중 오류가 발생했습니다. 다시 시도해주세요.');
            } finally {
                startAnalysisBtn.textContent = 'AI 분석 시작하기 →';
                startAnalysisBtn.disabled = false;
            }
        });
    }

    // 4. 스크롤에 따른 섹션 나타나는 애니메이션
    const sections = document.querySelectorAll('.fade-in-section');
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    sections.forEach(section => {
        observer.observe(section);
    });
    
    // 5. 기술 소개 탭 기능
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
