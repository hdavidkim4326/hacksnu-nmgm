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

        // 이전 코칭 바 초기화 후 갱신
        bar.classList.remove('visible');
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
        // 등장
        requestAnimationFrame(() => bar.classList.add('visible'));

        // 추천 칩 클릭 → 마지막 내 버블에 텍스트 삽입
        bar.querySelectorAll('.chip').forEach(btn => {
            btn.addEventListener('click', () => insertQuickReply(btn.textContent));
        });
    }

    async function startApiAnimation() {
        if (isApiAnimating) return;
        isApiAnimating = true;

        // 타이밍 상수 (필요시 숫자만 조절)
        const T_APPEAR      = 900;  // 말풍선이 뜬 직후 텀
        const T_AFTER_TYPE  = 600;  // 내가 타이핑 끝난 뒤 텀
        const T_AFTER_COACH = 1100;  // 코칭 바가 떠 있는 시간
        const T_PRE_COACH   = 300;  // (추가) 상대 말 → 코칭 전 잠깐 대기
        const T_PRE_REPLY   = 600;  // (추가) 코칭 → 내 말 전 잠깐 대기
        const TYPE_SPEED    = 60;   // 문자당 ms

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
        await sleep(250);

        // ── T1: 상대 (그대로) ───────────────────────────────
        el.m1.classList.add('visible');
        await sleep(T_APPEAR);

        // ── T2: 내 말 → 1번 코칭 (그대로) ───────────────────
        el.m2.classList.add('visible');
        await type(el.m2b, '너가 보기와는 다르게 그런 것도 좋아하는구나ㅎㅎ', TYPE_SPEED);
        await sleep(T_AFTER_TYPE);

        showAI({
            title: '말투 코칭',
            desc: '“보기와 다르게”는 평가처럼 들릴 수 있어요. <em>관심/칭찬</em> 중심으로 바꿔볼까요?',
            recos: [
                '완전 반전매력이다 취미의 폭이 되게 넓네ㅎㅎ',
                '넌 진짜 취미가 다양하다ㅎㅎ',
                '와 멋지다!'
            ]
        });
        await sleep(T_AFTER_COACH);

        // ── T3: 상대 → (추가 대기) → 2번 코칭 → (추가 대기) → 내 T4 ──
        el.m3.classList.add('visible');
        await sleep(T_APPEAR);
        await sleep(T_PRE_COACH); // ★ 추가: 코칭 전에 잠깐 대기

        showAI({
            title: '대화 확장',
            desc: '<em>칭찬 + 제안</em>을 붙이면 자연스러운 대화 확장이 가능해요.',
            recos: [
                '반전 매력이다',
                '뭐가 제일 재밌었어?',
                '다음엔 나도 만들어 줄 수 있어?'
            ]
        });
        await sleep(T_AFTER_COACH);
        await sleep(T_PRE_REPLY); // ★ 추가: 코칭 후 내 말 전 잠깐 대기

        el.m4.classList.add('visible');
        await type(el.m4b, '완전 반전매력이네 ㅎㅎ 다음에 나도 만들어줘!', TYPE_SPEED);
        await sleep(T_AFTER_TYPE);

        // ── T5: 상대 → (추가 대기) → 3번 코칭 → (추가 대기) → 내 T6 ──
        el.m5.classList.add('visible');
        await sleep(T_APPEAR);
        await sleep(T_PRE_COACH); // ★ 추가

        showAI({
            title: '관계 심화',
            desc: ' <em>공간 +열린질문</em>을 통하면 관계를 심화할 수 있어요',
            recos: [
                '다음에 배우고 싶은 요리가 있어?',
                '기대된다 ㅎㅎ'        
            ]
        });
        await sleep(T_AFTER_COACH);
        await sleep(T_PRE_REPLY); // ★ 추가

        el.m6.classList.add('visible');
        await type(el.m6b, '기대되네 ㅎㅎ 다음에 배우고 싶은 요리 있어?', TYPE_SPEED);

        isApiAnimating = false;
    }


    function type(node, text, charDelay = 60) {
        return new Promise(res => {
            node.textContent = '';
            let i = 0;
            const it = setInterval(() => {
                if (i < text.length) { node.textContent += text[i++]; }
                else { clearInterval(it); res(); }
            }, charDelay);
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
