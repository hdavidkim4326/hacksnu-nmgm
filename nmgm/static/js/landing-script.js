document.addEventListener('DOMContentLoaded', () => {

    // ===================================================================
    // 1. 공통 UI 기능 (모든 페이지에서 재사용 가능)
    // ===================================================================

    // 1-1. 스크롤 시 헤더에 그림자 효과 추가
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

    // 1-2. 네비게이션 부드러운 스크롤
    const navLinks = document.querySelectorAll('.main-nav a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const offset = target.getBoundingClientRect().top + window.pageYOffset - (header ? header.offsetHeight : 0);
                window.scrollTo({
                    top: offset,
                    behavior: 'smooth'
                });
            }
        });
    });

    // 1-3. 섹션 페이드인 애니메이션
    const sections = document.querySelectorAll('.fade-in-section');
    if (sections.length > 0) {
        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        sections.forEach(section => observer.observe(section));
    }


    // ===================================================================
    // 2. 랜딩 페이지 기능 (파일 업로드, 기술 소개 탭)
    // ===================================================================

    const dropZone = document.querySelector('.file-drop-zone');
    const fileInput = document.getElementById('chat-file-input');
    const startAnalysisBtn = document.getElementById('start-analysis-btn');

    // 파일 업로드 관련 기능은 해당 요소들이 있을 때만 실행
    if (dropZone && fileInput && startAnalysisBtn) {
        let selectedFile = null;

        function handleFileSelect(file) {
            if (!file) return;
            selectedFile = file;
            dropZone.querySelector('p').textContent = `선택된 파일: ${file.name}`;
            dropZone.style.borderColor = 'var(--primary-light)';
            startAnalysisBtn.disabled = false;
        }

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

        fileInput.addEventListener('change', e => {
            if (e.target.files.length > 0) handleFileSelect(e.target.files[0]);
        });
        
        // 파일 업로드 및 리포트 페이지로 이동
        startAnalysisBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            if (!selectedFile) {
                alert('분석할 파일을 선택해주세요.');
                return;
            }

            startAnalysisBtn.textContent = 'AI 분석 중...';
            startAnalysisBtn.disabled = true;

            const formData = new FormData();
            formData.append('file', selectedFile);

            try {
                // --- ✨ 여기가 핵심 수정 부분입니다 ---

                // ① CSV 파일 업로드 요청 후, 서버가 분석한 JSON 결과를 바로 받습니다.
                const response = await fetch('/import_data/', { // Django urls.py에 설정된 URL
                    method: 'POST',
                    body: formData,
                });

                // 서버에서 에러가 발생하면, 에러 메시지를 포함하여 예외를 발생시킵니다.
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || '서버에서 리포트를 생성하는데 실패했습니다.');
                }

                // ② 응답으로 받은 JSON 데이터를 reportData 변수에 저장합니다.
                const reportData = await response.json();

                // ③ 받은 데이터를 브라우저 임시 저장소(localStorage)에 저장합니다.
                localStorage.setItem('reportData', JSON.stringify(reportData));

                // ④ 데이터 저장이 끝나면, URL 파라미터 없이 깔끔하게 리포트 페이지로 이동합니다.
                window.location.href = startAnalysisBtn.dataset.reportUrl;

            } catch (error) {
                console.error('Error:', error);
                // 사용자에게 더 친절한 에러 메시지를 보여줍니다.
                alert(`분석 중 오류가 발생했습니다: ${error.message}`);
                startAnalysisBtn.textContent = 'AI 분석 시작하기 →';
                startAnalysisBtn.disabled = false;
            }
        });
    }

    // 기술 소개 탭 기능은 해당 요소들이 있을 때만 실행
    const techMenuItems = document.querySelectorAll('.tech-menu-item');
    if (techMenuItems.length > 0) {
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
    }


    // ===================================================================
    // 3. 리포트 페이지 기능 (데이터 로딩, 렌더링, 차트 생성)
    // ===================================================================
    
    const reportContainer = document.getElementById('report-container');

    // reportContainer가 있는 페이지에서만 아래 코드 실행
    if (reportContainer) {
        // 페이지 로드 시 즉시 실행되는 async 함수
        // landing-script.js 의 (async function loadReport() { ... }) 부분을 교체하세요.

        (async function loadReport() {
            try {
                // ① localStorage에서 'reportData'를 가져옵니다.
                const storedData = localStorage.getItem('reportData');

                if (!storedData) {
                    throw new Error('분석 데이터가 없습니다. 랜딩 페이지에서 파일을 먼저 업로드해주세요.');
                }

                // ② 가져온 데이터를 JSON 객체로 변환합니다.
                const reportData = JSON.parse(storedData);
                
                // 로딩 메시지를 실제 리포트로 교체합니다.
                reportContainer.innerHTML = `
                    ${renderChatSummary(reportData.chat_summary)}
                    ${renderUserAnalysis(reportData.user_analysis)}
                    ${renderWarnings(reportData.warnings)}
                `;

                // 차트를 생성합니다.
                createSentimentCharts(reportData.user_analysis);
                createRadarChart(reportData.user_analysis);

                // (중요) 사용한 데이터는 localStorage에서 삭제하여,
                // 새로고침 시 빈 페이지가 보이도록 합니다.
                localStorage.removeItem('reportData');

            } catch (error) {
                console.error(error);
                reportContainer.innerHTML = `<p class="error-message">⚠️ 분석 데이터를 불러오는 데 실패했습니다. <br>${error.message}</p>`;
            }
        })();
    }

    // --- 리포트 페이지용 렌더링 및 차트 함수들 ---

    function renderChatSummary(summary) {
        if (!summary) return '';
        const threadsHtml = summary.threads.map(thread => `
            <div class="thread-item">
                <div class="thread-item-topic">${thread.topic_summary}</div>
                <div class="thread-item-type">${thread.chat_type}</div>
                <div class="thread-item-count">${thread.num_messages} messages</div>
            </div>
        `).join('');

        return `
            <section class="report-section">
                <h2 class="section-title">대화 요약</h2>
                <p class="section-subtitle">${new Date(summary.start_time).toLocaleString()} ~ ${new Date(summary.end_time).toLocaleString()}</p>
                <div class="summary-grid">
                    <div class="summary-text">
                        <h4>AI 요약</h4>
                        <p>${summary.summary}</p>
                    </div>
                    <div class="summary-threads">
                        <h4>주요 대화 주제</h4>
                        ${threadsHtml}
                    </div>
                </div>
            </section>
        `;
    }

    function renderUserAnalysis(userAnalysis) {
        if (!userAnalysis) return '';
        const userCardsHtml = userAnalysis.map(user => `
            <div class="user-card">
                <h4>${user.username}</h4>
                <p class="personality">${user.personality}</p>
                <p>${user.description}</p>
                <div class="user-stats">
                    <div class="stat-item">
                        <div class="label">응답 시간(중앙값)</div>
                        <div class="value">${user.median_response_time.toFixed(1)}분</div>
                    </div>
                    <div class="stat-item">
                        <div class="label">대화 시작률</div>
                        <div class="value">${(user.initiative_rate * 100).toFixed(0)}%</div>
                    </div>
                </div>
                <h5>감정 시계열 분석</h5>
                <canvas id="sentiment-chart-${user.username}"></canvas>
            </div>
        `).join('');

        return `
            <section class="report-section">
                <h2 class="section-title">참여자 분석</h2>
                <div class="user-analysis-container">${userCardsHtml}</div>
                <div class="radar-chart-container">
                    <canvas id="personality-radar-chart" style="max-width: 500px; margin: auto;"></canvas>
                </div>
            </section>
        `;
    }

    function renderWarnings(warnings) {
        if (!warnings || warnings.length === 0) return '';
        const warningsRowsHtml = warnings.map(warn => `
            <tr>
                <td><strong>${warn.sent_by}</strong>: "${warn.message}"</td>
                <td><span class="warning-type">${warn.warning_type}</span></td>
                <td>${warn.detail}</td>
                <td><span class="action-plan">${warn.action_plan}</span></td>
            </tr>
        `).join('');

        return `
            <section class="report-section">
                <h2 class="section-title">오해 위험 구간 분석 (Top 3)</h2>
                <table class="warnings-table">
                    <thead>
                        <tr><th>메시지 내용</th><th>오해 종류</th><th>설명</th><th>개선 방안</th></tr>
                    </thead>
                    <tbody>${warningsRowsHtml}</tbody>
                </table>
            </section>
        `;
    }

    function createSentimentCharts(userAnalysis) {
        if (!userAnalysis) return;
        userAnalysis.forEach(user => {
            const ctx = document.getElementById(`sentiment-chart-${user.username}`)?.getContext('2d');
            if (!ctx) return;
            
            const chartData = {
                labels: user.messages.map(msg => new Date(msg.sent_time)),
                datasets: [{
                    label: `${user.username}의 감정 변화`,
                    data: user.messages.map(msg => msg.sentiment),
                    borderColor: '#' + Math.floor(Math.random()*16777215).toString(16).padStart(6, '0'),
                    tension: 0.1,
                    fill: false
                }]
            };
            new Chart(ctx, {
                type: 'line',
                data: chartData,
                options: {
                    scales: {
                        x: { type: 'time', time: { unit: 'day', tooltipFormat: 'yyyy-MM-dd HH:mm' } },
                        y: { beginAtZero: false, suggestedMax: 1, suggestedMin: -1 }
                    }
                }
            });
        });
    }

    function createRadarChart(userAnalysis) {
        if (!userAnalysis || userAnalysis.length === 0) return;
        const ctx = document.getElementById('personality-radar-chart')?.getContext('2d');
        if (!ctx) return;

        const labels = userAnalysis[0]?.avg_indices.map(idx => idx.index) || [];
        const datasets = userAnalysis.map((user, index) => {
            const colors = ['rgba(46, 79, 33, 0.5)', 'rgba(196, 216, 192, 0.7)', 'rgba(100, 150, 200, 0.6)'];
            return {
                label: user.username,
                data: user.avg_indices.map(idx => idx.score),
                backgroundColor: colors[index % colors.length],
                borderColor: colors[index % colors.length].replace(/0\.\d+/, '1'),
                borderWidth: 2
            }
        });
        new Chart(ctx, {
            type: 'radar',
            data: { labels, datasets },
            options: {
                elements: { line: { borderWidth: 3 } },
                scales: { r: { suggestedMin: 0, suggestedMax: 1 } }
            }
        });
    }

});