document.addEventListener('DOMContentLoaded', function () {
    const reportContainer = document.getElementById('report-container');
    
    
    const reportDataString = localStorage.getItem('reportData');
    const reportData = JSON.parse(reportDataString); // 바깥 상자를 열고
    
    // reportData가 여전히 문자열인지 확인하고, 그렇다면 한 번 더 엽니다.
    const finalReportData = (typeof reportData === 'string') ? JSON.parse(reportData) : reportData;
    debugger;
    if (!reportData) {
        reportContainer.innerHTML = '<p>분석 데이터가 없습니다. 랜딩 페이지에서 파일을 업로드해주세요.</p>';
        return;
    }

    // --- 데이터 렌더링 함수들 ---
    
    function renderChatSummary(summary) {
        debugger;
        if (!summary) {
        
            return '';
        }
        
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
        if (!userAnalysis) {
            return '';
        }
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
                    <canvas id="personality-radar-chart" style="max-width: 500px;"></canvas>
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

    // --- 차트 생성 함수들 ---

    // --- 차트 생성 함수들 ---

    function createSentimentCharts(userAnalysis) {
        // ✅ 방어 코드를 추가합니다.
        // userAnalysis가 없거나(null, undefined), 배열이 아니면
        // 아무것도 하지 않고 함수를 안전하게 종료합니다.
        if (!userAnalysis || !Array.isArray(userAnalysis)) {
            return;
        }

        userAnalysis.forEach(user => {
            // canvas 요소가 없을 수도 있으니 추가로 방어합니다.
            const canvas = document.getElementById(`sentiment-chart-${user.username}`);
            if (!canvas) return;

            const ctx = canvas.getContext('2d');
            const chartData = {
                labels: user.messages.map(msg => new Date(msg.sent_time)),
                datasets: [{
                    label: `${user.username}의 감정 변화`,
                    data: user.messages.map(msg => msg.sentiment),
                    borderColor: '#' + Math.floor(Math.random()*16777215).toString(16).padStart(6, '0'),
                    tension: 0.1
                }]
            };
            new Chart(ctx, {
                type: 'line',
                data: chartData,
                options: {
                    scales: {
                        x: { type: 'time', time: { unit: 'day' } },
                        y: { beginAtZero: false, suggestedMax: 1, suggestedMin: -1 }
                    }
                }
            });
        });
    }

    function createRadarChart(userAnalysis) {
        // ✅ 방어 코드를 추가합니다.
        // userAnalysis가 없거나, 배열이 아니거나, 내용이 없는 빈 배열이면
        // 아무것도 하지 않고 함수를 안전하게 종료합니다.
        if (!userAnalysis || !Array.isArray(userAnalysis) || userAnalysis.length === 0) {
            return;
        }

        const canvas = document.getElementById('personality-radar-chart');
        if (!canvas) return; // canvas 요소 방어

        const ctx = canvas.getContext('2d');
        const labels = userAnalysis[0]?.avg_indices.map(idx => idx.index) || [];
        const datasets = userAnalysis.map((user, index) => {
            const colors = ['rgba(46, 79, 33, 0.5)', 'rgba(196, 216, 192, 0.7)'];
            return {
                label: user.username,
                data: user.avg_indices.map(idx => idx.score),
                backgroundColor: colors[index % colors.length],
                borderColor: colors[index % colors.length].replace(/0\.\d+/, '1'),
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
    // --- 메인 렌더링 로직 ---
    reportContainer.innerHTML = `
        ${renderChatSummary(finalReportData.chatsummary)}
        ${renderUserAnalysis(finalReportData.user_analysis)}
        ${renderWarnings(finalReportData.warnings)}
    `;

    // 차트 생성
    createSentimentCharts(finalReportData.user_analysis);
    createRadarChart(finalReportData.user_analysis);
    debugger;
    // 사용 후 데이터 삭제 (새로고침 시 빈 페이지 표시)
    localStorage.removeItem('reportData');
});
