document.addEventListener('DOMContentLoaded', () => {
    
    // --- 공통 변수 및 함수 ---
    const toggleButtons = document.querySelectorAll('.toggle-btn');
    const prototypeContents = document.querySelectorAll('.prototype-content');
    const description = document.getElementById('prototype-description');

    const descriptions = {
        'app-prototype': 'NMgM 어플의 구조를 직접 경험해보세요! 앱에서는 실제 대화를 기반으로 한 관계 리포트를 동시에 받아볼 수 있습니다. AI가 당신의 말투와 감성을 이해하고, 더 따뜻하고 명확한 대화를 돕습니다.',
        'api-prototype': 'API 프로토타입은 AI가 실시간으로 대화를 이해하고 코칭하는 과정을 보여줍니다. 실제 앱에서는 키보드 API와 연동되어 작동하게 됩니다.'
    };
    
    // --- 프로토타입 탭 전환 기능 ---
    toggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.dataset.target;

            // 모든 버튼과 컨텐츠 비활성화 후, 선택된 것만 활성화
            toggleButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            description.textContent = descriptions[targetId];
            prototypeContents.forEach(content => {
                content.id === targetId ? content.classList.add('active') : content.classList.remove('active');
            });
            
            // 'API 프로토타입' 탭이 선택되면 애니메이션 시작
            if (targetId === 'api-prototype') {
                startApiAnimation();
            }
        });
    });

    // --- 1. NMGm 어플 프로토타입 스크립트 ---
    const btnStartDemo = document.getElementById('btn-start-demo');
    const btnAnalyzeChat = document.querySelector('.btn-analyze-chat');       // 채팅 리스트의 "상세 분석 보기"
    const btnBackToList = document.getElementById('btn-back-to-list');        // 개요에서 ← 리스트
    const appScreens = document.querySelectorAll('.app-screen');
    const snsFilterBtns = document.querySelectorAll('.sns-filter-btn');
    const chatLists = document.querySelectorAll('.app-chat-list');

    // 추가된 버튼들
    const btnDetailFromCard = document.querySelector('.app-btn-detail');      // 대시보드 카드의 "자세한 분석 보기" → 개요
    const btnGoDetail = document.getElementById('btn-go-detail');             // 개요 상단 버튼 → 상세
    const btnBackToOverview = document.getElementById('btn-back-to-overview');// 상세에서 ← 개요

    function switchScreen(targetScreenId) {
        appScreens.forEach(screen => {
            screen.id === targetScreenId ? screen.classList.add('active') : screen.classList.remove('active');
        });
        // 아이콘 재렌더 (헤더의 lucide 아이콘용)
        if (window.lucide?.createIcons) {
            window.lucide.createIcons();
        }
    }

    // 기본 전환
    if (btnStartDemo) btnStartDemo.addEventListener('click', () => switchScreen('app-screen-2'));

    // 대시보드 카드 → 개요(screen-3)
    if (btnDetailFromCard) btnDetailFromCard.addEventListener('click', () => switchScreen('app-screen-3'));

    // 채팅 리스트의 "상세 분석 보기" → 상세(screen-4) 로 변경
    if (btnAnalyzeChat) btnAnalyzeChat.addEventListener('click', (e) => {
        e.preventDefault();
        switchScreen('app-screen-4');
    });

    // 개요(screen-3) 상단 버튼 → 상세(screen-4)
    if (btnGoDetail) btnGoDetail.addEventListener('click', () => switchScreen('app-screen-4'));

    // 뒤로가기들
    if (btnBackToList) btnBackToList.addEventListener('click', () => switchScreen('app-screen-2'));       // 개요 → 리스트
    if (btnBackToOverview) btnBackToOverview.addEventListener('click', () => switchScreen('app-screen-3'));// 상세 → 개요

    // SNS 필터 유지
    snsFilterBtns.forEach(button => {
        button.addEventListener('click', () => {
            const platform = button.dataset.platform;
            snsFilterBtns.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            chatLists.forEach(list => {
                list.dataset.platform === platform ? list.classList.add('active') : list.classList.remove('active');
            });
        });
    });


    // --- 2. API 프로토타입 애니메이션 스크립트 (6턴) ---
    const sleep = (ms) => new Promise(r => setTimeout(r, ms));
    let isApiAnimating = false;

    // 추천 칩 클릭 시, 최근 사용자 버블에 텍스트 삽입
    function insertQuickReply(text) {
        const candidates = ['msg6', 'msg4', 'msg2']
            .map(id => document.getElementById(id)?.querySelector('.bubble'))
            .filter(Boolean);
        const target = candidates.find(el => el.parentElement.classList.contains('visible')) || candidates[0];
        if (!target) return;
        target.textContent = (target.textContent?.trim() ? target.textContent + ' ' : '') + text;
    }

    // 아이콘<i> 대신 logo.svg + strong 제목 + 설명 + 아래 칩
    function showAI({ title = '코칭', desc = '', recos = [] }) {
        const bar = document.getElementById('ai-bar');
        const logoUrl = bar.dataset.logo || '/static/images/logo.svg'; // fallback

        bar.innerHTML = `
            <img src="${logoUrl}" alt="NMgM" class="ai-logo">
            <div class="ai-content">
                <div class="ai-head">
                    <strong>${title}</strong>
                    <span class="ai-desc">${desc}</span>
                </div>
                <div class="ai-recos">
                    ${recos.map(t => `<button class="chip" type="button">${t}</button>`).join('')}
                </div>
            </div>
        `;
        bar.classList.add('visible');

        bar.querySelectorAll('.chip').forEach(btn => {
            btn.addEventListener('click', () => insertQuickReply(btn.textContent));
        });
    }


    async function startApiAnimation() {
        if (isApiAnimating) return;
        isApiAnimating = true;

        const el = {
            aiBar: document.getElementById('ai-bar'),
            m1: document.getElementById('msg1'),
            m2: document.getElementById('msg2'),
            m2b: document.getElementById('msg2').querySelector('.bubble'),
            m3: document.getElementById('msg3'),
            m4: document.getElementById('msg4'),
            m4b: document.getElementById('msg4').querySelector('.bubble'),
            m5: document.getElementById('msg5'),
            m6: document.getElementById('msg6'),
            m6b: document.getElementById('msg6').querySelector('.bubble'),
        };

        // 초기화
        [el.m1, el.m2, el.m3, el.m4, el.m5, el.m6].forEach(n => n.classList.remove('visible'));
        el.aiBar.classList.remove('visible');
        el.aiBar.innerHTML = '';
        el.m2b.textContent = '';
        el.m4b.textContent = '';
        el.m6b.textContent = '';
        await sleep(350);

        // T1: 상대방 1
        el.m1.classList.add('visible');
        await sleep(1000);

        // AI 힌트 1: 의도 파악
        showAI({
            title: '의도 파악',
            desc: '상대방 의도: <strong>약속 제안</strong> (긍정)',
            recos: ['좋지! 시간만 맞추자', '다음 주는 어때?']
        });
        await sleep(1200);

        // T2: 사용자 1 (거절 뉘앙스)
        el.m2.classList.add('visible');
        await type(el.m2b, '내일은 좀 어려울 것 같아');
        await sleep(800);

        // AI 힌트 2: 더 부드러운 제안
        showAI({
            title: '완곡 제안',
            desc: '직설 거절 대신 <em>대안</em>을 붙여보세요.',
            recos: [ '다음 주 수/목 어때?', '저녁 7시 괜찮아']
        });
        await sleep(1200);

        // T3: 상대방 2
        el.m3.classList.add('visible');
        await sleep(900);

        // AI 힌트 3: 구체화 유도
        showAI({
            title: '구체화',
            desc: '요일/시간을 먼저 제시하면 합의가 빨라져요.',
            recos: ['수요일 7시 가능', '목요일 8시는 어때?', '장소는 강남?']
        });
        await sleep(1000);

        // T4: 사용자 2 (구체 시간 제시)
        el.m4.classList.add('visible');
        await type(el.m4b, '수요일 7시는 괜찮아!');
        await sleep(800);

        // T5: 상대방 3 (확정 + 예약)
        el.m5.classList.add('visible');
        await sleep(800);

        // AI 힌트 4: 감사/확인 멘트 제안
        showAI({
            title: '마무리',
            desc: '감사/확인 멘트로 따뜻하게 마무리하세요.',
            recos: ['고마워!', '예약 고마워 🙏', '메뉴 미리 볼게 😉']
        });
        await sleep(900);

        // T6: 사용자 3 (감사 + follow-up)
        el.m6.classList.add('visible');
        await type(el.m6b, '고마워! 메뉴 미리 보고 갈게 😉');

        isApiAnimating = false;
    }

    // 타이핑 애니메이션
    function type(node, text) {
        return new Promise(res => {
            node.textContent = '';
            let i = 0;
            const it = setInterval(() => {
                if (i < text.length) { node.textContent += text[i++]; }
                else { clearInterval(it); res(); }
            }, 60);
        });
    }

    // 첫 로드 시 API 탭이 이미 활성화면 자동 실행
    const apiTab = document.getElementById('api-prototype');
    if (apiTab?.classList.contains('active')) {
        startApiAnimation();
    }

    // 헤더 등 기타 lucide 아이콘 렌더
    if (window.lucide?.createIcons) {
        window.lucide.createIcons();
    }
});
