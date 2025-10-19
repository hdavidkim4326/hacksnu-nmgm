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
    // 추천칩을 초안칸에 넣기
    function insertQuickReply(text) {
        const box = document.getElementById('compose-input');
        if (!box) return;
        const sep = box.textContent.trim() ? ' ' : '';
        box.textContent = box.textContent + sep + text;
        placeCaretAtEnd(box);
    }
    function placeCaretAtEnd(el) {
        el.focus();
        const range = document.createRange();
        range.selectNodeContents(el);
        range.collapse(false);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
    }

    // 코칭 바 그리기 (칩은 초안칸에 입력)
    function showAI({ title = '코칭', desc = '', recos = [] }) {
        const bar = document.getElementById('ai-bar');
        const logoUrl = bar.dataset.logo || '/static/images/logo.svg';
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

    // 초안 다루기
    function setDraft(text = '') {
        const box = document.getElementById('compose-input');
        box.textContent = text;
        placeCaretAtEnd(box);
    }
    function getDraft() {
        return document.getElementById('compose-input').textContent.trim();
    }
    function clearDraft() {
        document.getElementById('compose-input').textContent = '';
    }

    // 전송 대기(클릭 또는 타임아웃)
    function waitForSend(timeoutMs = 0) {
        return new Promise(resolve => {
            const btn = document.getElementById('btn-send');
            let done = false;

            const clickHandler = () => {
                if (done) return;
                done = true;
                btn.removeEventListener('click', clickHandler);
                resolve('clicked');
            };
            btn.addEventListener('click', clickHandler);

            if (timeoutMs > 0) {
                setTimeout(() => {
                    if (done) return;
                    done = true;
                    btn.removeEventListener('click', clickHandler);
                    resolve('timeout');
                }, timeoutMs);
            }
        });
    }

    // 특정 말풍선으로 초안 전송
    function sendDraftTo(bubbleEl) {
        const txt = getDraft();
        if (!txt) return false;
        bubbleEl.textContent = txt;
        bubbleEl.parentElement.classList.add('visible');
        clearDraft();
        return true;
    }

    // 타이핑 애니메이션(상대만 사용)
    function type(node, text, speed = 60) {
        return new Promise(res => {
            node.textContent = '';
            let i = 0;
            const it = setInterval(() => {
                if (i < text.length) node.textContent += text[i++];
                else { clearInterval(it); res(); }
            }, speed);
        });
    }

    async function startApiAnimation() {
        if (isApiAnimating) return;
        isApiAnimating = true;

        const T_APPEAR      = 600;  // 상대 말풍선 뜬 직후 텀
        const T_PRE_COACH   = 500;  // 코칭 전 숨 고르기
        const T_AFTER_COACH = 900;  // 코칭 노출 시간
        const AUTO_SEND     = 1400; // 사용자 미클릭시 자동 전송까지 대기(ms)
        const T_AFTER_SEND    = 800;
        const el = {
            aiBar: document.getElementById('ai-bar'),
            m1: document.getElementById('msg1'),
            m2: document.getElementById('msg2').querySelector('.bubble'),
            m3: document.getElementById('msg3'),
            m4: document.getElementById('msg4').querySelector('.bubble'),
            m5: document.getElementById('msg5'),
            m6: document.getElementById('msg6').querySelector('.bubble'),
        };

        // 초기화
        [ 'msg1','msg2','msg3','msg4','msg5','msg6' ]
            .forEach(id => document.getElementById(id).classList.remove('visible'));
        el.aiBar.classList.remove('visible');
        el.aiBar.innerHTML = '';
        clearDraft();
        await sleep(250);

        // ───────────────── ① 상대 → 초안 → 코칭 → (보내기) ─────────────────
        const INITIAL1 = '너가 보기와는 다르게 그런 것도 좋아하는구나ㅎㅎ';
        const COACHED1 = '넌 진짜 취미가 다양하다ㅎㅎ 어땠어?';

        // ───────────────── ① 상대 → 초안 → 코칭 → (교체 후 보내기) ─────────────────
        document.getElementById('msg1').classList.add('visible');  // 상대
        await sleep(T_APPEAR);

        // 1) 내 초안 타이핑
        await typeIntoDraft(INITIAL1, 70, { replace: true });
        await sleep(T_PRE_COACH);

        // 2) 코칭 노출 (칩에도 최종 문장 넣어줌)
        showAI({
            title: '말투 코칭',
            desc: '“보기와 다르게”는 평가처럼 들릴 수 있어요. <em>관심/칭찬</em> + <em>열린 질문</em>으로 바꿔볼까요?',
            recos: [
                COACHED1,  // ← 이 칩을 제일 앞에 둠 (클릭 시 초안에 들어감)
                '완전 반전매력이다 취미의 폭이 되게 넓네ㅎㅎ',
                '와 멋지다!'
            ]
        });

        // 3) 잠깐 멈칫한 뒤, 아직 사용자가 수정 안했다면 자동으로 교체
        await sleep(1000); // 코칭 뜬 뒤 짧은 텀
        if (getDraft() === INITIAL1) {
            await typeIntoDraft(COACHED1, 70, { replace: true });
        }
        
        await sleep(T_AFTER_COACH);

        // 클릭 or 자동전송
        await waitForSend(AUTO_SEND);
        sendDraftTo(el.m2);  // msg2(내 버블)에 반영
        await sleep(T_AFTER_SEND);
        // ───────────────── ② 상대 → 코칭 → (보내기) ─────────────────
        document.getElementById('msg3').classList.add('visible');
        await sleep(T_APPEAR);
        await sleep(T_PRE_COACH);

        showAI({
            title: '대화 확장',
            desc: '칭찬 뒤에 <em>열린 질문</em>을 붙이면 대화가 더 부드러워져요.',
            recos: [
                '반전 매력이네 ㅎㅎ',
                '뭐가 제일 재밌었어?',
                '다음엔 나도 만들어 줄 수 있어?'
            ]
        });
        await sleep(T_AFTER_COACH);

        await typeIntoDraft('완전 반전매력이네 ㅎㅎ 다음에 나도 만들어줘!', 70, {replace:true}); // 기본 추천을 초안에 채워둠(원하면 칩으로 덮어서 수정)
        await waitForSend(AUTO_SEND);
        sendDraftTo(el.m4);
        await sleep(T_AFTER_SEND);
        // ───────────────── ③ 상대 → 코칭 → (보내기) ─────────────────
        document.getElementById('msg5').classList.add('visible');
        await sleep(T_APPEAR);
        await sleep(T_PRE_COACH);

        showAI({
            title: '마무리 코칭',
            desc: '공감 + <em>열린질문</em>으로 따뜻하게 마무리해봐요.',
            recos: [
                
                '다음에 배우고 싶은 요리가 있어?',
                '기대된다 ㅎㅎ'
                
            ]
        });
        await sleep(T_AFTER_COACH);

        await typeIntoDraft('기대되네ㅎㅎ 다음에 배우고 싶은 요리있어?', 70, {replace:true});
        await waitForSend(AUTO_SEND);
        sendDraftTo(el.m6);

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
    // contenteditable에 타이핑 애니메이션
    async function typeIntoDraft(text, charDelay = 40, {replace=true} = {}){
        const el = document.getElementById('compose-input');
        if (!el) return;
        if (replace) el.textContent = '';
        el.focus();
        for (const ch of text){
            el.textContent += ch;
            placeCaretAtEnd(el);
            await sleep(charDelay);
        }
    }

});
