document.addEventListener('DOMContentLoaded', function () {
    const reportContainer = document.getElementById('report-container');
    const reportData = JSON.parse(localStorage.getItem('reportData'));

    if (!reportData) {
        reportContainer.innerHTML = '<p>분석 데이터가 없습니다. 랜딩 페이지에서 파일을 업로드해주세요.</p>';
        return;
    }

    // --- 데이터 렌더링 함수들 ---

    function renderChatSummary(summary) {
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

    function createSentimentCharts(userAnalysis) {
        userAnalysis.forEach(user => {
            const ctx = document.getElementById(`sentiment-chart-${user.username}`).getContext('2d');
            const chartData = {
                labels: user.messages.map(msg => new Date(msg.sent_time)),
                datasets: [{
                    label: `${user.username}의 감정 변화`,
                    data: user.messages.map(msg => msg.sentiment),
                    borderColor: '#' + Math.floor(Math.random()*16777215).toString(16),
                    tension: 0.1
                }]
            };
            new Chart(ctx, {
                type: 'line',
                data: chartData,
                options: {
                    scales: {
                        x: { type: 'time', time: { unit: 'day' } },
                        y: { beginAtZero: true, suggestedMax: 1, suggestedMin: -1 }
                    }
                }
            });
        });
    }

    function createRadarChart(userAnalysis) {
        const ctx = document.getElementById('personality-radar-chart').getContext('2d');
        const labels = userAnalysis[0]?.avg_indices.map(idx => idx.index) || [];
        const datasets = userAnalysis.map((user, index) => {
             const colors = ['rgba(46, 79, 33, 0.5)', 'rgba(196, 216, 192, 0.7)'];
            return {
                label: user.username,
                data: user.avg_indices.map(idx => idx.score),
                backgroundColor: colors[index % colors.length],
                borderColor: colors[index % colors.length].replace('0.5', '1').replace('0.7', '1'),
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
        ${renderChatSummary(reportData.chat_summary)}
        ${renderUserAnalysis(reportData.user_analysis)}
        ${renderWarnings(reportData.warnings)}
    `;

    // 차트 생성
    createSentimentCharts(reportData.user_analysis);
    createRadarChart(reportData.user_analysis);

    // 사용 후 데이터 삭제 (새로고침 시 빈 페이지 표시)
    localStorage.removeItem('reportData');
});
