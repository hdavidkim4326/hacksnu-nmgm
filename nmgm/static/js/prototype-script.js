document.addEventListener('DOMContentLoaded', () => {

    const toggleButtons = document.querySelectorAll('.toggle-btn');
    const prototypeContents = document.querySelectorAll('.prototype-content');
    const description = document.getElementById('prototype-description');

    const descriptions = {
        'app-prototype': 'NMgM 어플의 구조를 직접 경험해보세요! 앱에서는 실제 대화를 기반으로 한 관계 리포트를 동시에 받아볼 수 있습니다. AI가 당신의 말투와 감성을 이해하고, 더 따뜻하고 명확한 대화를 돕습니다.',
        'api-prototype': 'API 프로토타입은 AI가 실시간으로 대화를 이해하고 코칭하는 과정을 보여줍니다. 실제 앱에서는 키보드 API와 연동되어 작동하게 됩니다.'
    };
    
    // --- 토글 기능 ---
    toggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.dataset.target;

            toggleButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            description.textContent = descriptions[targetId];

            prototypeContents.forEach(content => {
                content.id === targetId ? content.classList.add('active') : content.classList.remove('active');
            });
            
            if (targetId === 'api-prototype') {
                startApiAnimation();
            }
        });
    });

    // --- 1. NMGm 어플 프로토타입 기능 ---
    const btnStartDemo = document.getElementById('btn-start-demo');
    const btnAnalyzeChat = document.querySelector('.btn-analyze-chat');
    const appScreens = document.querySelectorAll('.app-screen');
    const snsFilterBtns = document.querySelectorAll('.sns-filter-btn');
    const chatLists = document.querySelectorAll('.app-chat-list');

    function switchScreen(targetScreenId) {
        appScreens.forEach(screen => {
            screen.id === targetScreenId ? screen.classList.add('active') : screen.classList.remove('active');
        });
    }

    if (btnStartDemo) {
        btnStartDemo.addEventListener('click', () => switchScreen('app-screen-2'));
    }
    if (btnAnalyzeChat) {
        btnAnalyzeChat.addEventListener('click', () => switchScreen('app-screen-3'));
    }
    
    // SNS 필터 탭 기능
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


    // --- 2. API 프로토타입 기능 ---
    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    let isApiAnimating = false;

    async function startApiAnimation() {
        if (isApiAnimating) return;
        isApiAnimating = true;

        const elements = {
            msg1: document.getElementById('msg1'),
            analysis1: document.getElementById('analysis1'),
            msg2Bubble: document.getElementById('msg2').querySelector('.bubble'),
            msg2Container: document.getElementById('msg2'),
            analysis2: document.getElementById('analysis2'),
        };

        Object.values(elements).forEach(el => el.classList.remove('visible'));
        elements.msg2Bubble.textContent = '';

        await sleep(1000);
        elements.msg1.classList.add('visible');

        await sleep(1500);
        elements.analysis1.classList.add('visible');

        await sleep(1500);
        elements.msg2Container.classList.add('visible');
        await typeMessage(elements.msg2Bubble, "내일은 좀 그런데");

        await sleep(1000);
        elements.analysis2.classList.add('visible');
        
        isApiAnimating = false;
    }

    function typeMessage(element, text) {
        return new Promise(resolve => {
            let index = 0;
            element.textContent = '';
            const interval = setInterval(() => {
                if (index < text.length) {
                    element.textContent += text.charAt(index);
                    index++;
                } else {
                    clearInterval(interval);
                    resolve();
                }
            }, 100);
        });
    }
});