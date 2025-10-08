// Edit Page JavaScript

let convertedData = null;

// 페이지 로드 시 데이터 로드
window.addEventListener('DOMContentLoaded', function() {
    const dataStr = sessionStorage.getItem('convertedData');
    if (!dataStr) {
        alert('변환된 데이터가 없습니다.');
        window.location.href = '/input';
        return;
    }
    
    convertedData = JSON.parse(dataStr);
    renderEditPanel();
    updateBorderVisibility();
});

function goBack() {
    window.location.href = '/input';
}

function renderEditPanel() {
    const panel = document.getElementById('editPanel');
    panel.innerHTML = '';
    
    convertedData.lines.forEach((line, lineIndex) => {
        const lineDiv = document.createElement('div');
        lineDiv.className = 'edit-line';
        
        if (line.words.length === 0) {
            // 빈 줄
            lineDiv.innerHTML = '<br>';
        } else {
            line.words.forEach((word, wordIndex) => {
                const wordGroup = createWordGroup(word, lineIndex, wordIndex);
                lineDiv.appendChild(wordGroup);
            });
        }
        
        panel.appendChild(lineDiv);
    });
    
    updateDisplay();
    updateBorderVisibility();
}

function createWordGroup(word, lineIndex, wordIndex) {
    const group = document.createElement('div');
    group.className = 'word-group';
    group.dataset.lineIndex = lineIndex;
    group.dataset.wordIndex = wordIndex;
    
    const alternatives = word.alternative_pronunciations || [];
    
    // alternative_pronunciations가 비어있으면 기본값 생성
    if (alternatives.length === 0) {
        alternatives.push({
            hangul_pron: word.surface,
            hangul_kana: word.surface,
            hiragana_pron: word.surface,
            katakana_pron: word.surface,
            pos1: '',
            pos2: '',
            pos3: ''
        });
        word.selected_id = 0;
    }
    
    const selected = alternatives[word.selected_id] || alternatives[0];
    
    // 원문
    const originalDiv = document.createElement('div');
    originalDiv.className = 'word-original';
    originalDiv.textContent = word.surface;
    group.appendChild(originalDiv);
    
    // 한글 발음
    const hangulDiv = document.createElement('div');
    hangulDiv.className = 'word-pronunciation';
    hangulDiv.dataset.pron = selected.hangul_pron || word.surface;
    hangulDiv.dataset.kana = selected.hangul_kana || word.surface;
    hangulDiv.textContent = selected.hangul_pron || word.surface; // 기본값은 하이픈 사용
    group.appendChild(hangulDiv);
    
    // 여러 발음이 있으면 클릭 가능하게
    if (alternatives.length > 1) {
        group.classList.add('clickable');
        
        // 발음 개수 뱃지
        const badge = document.createElement('div');
        badge.className = 'word-count-badge';
        badge.textContent = alternatives.length;
        group.appendChild(badge);
        
        // 클릭 이벤트
        group.addEventListener('click', function(e) {
            e.stopPropagation();
            showSelectionMenu(group, word, lineIndex, wordIndex);
        });
    }
    
    return group;
}

function showSelectionMenu(group, word, lineIndex, wordIndex) {
    // 기존 메뉴 제거
    document.querySelectorAll('.selection-menu').forEach(menu => menu.remove());
    
    // 모든 word-group의 z-index 초기화
    document.querySelectorAll('.word-group').forEach(g => {
        g.style.zIndex = '';
    });
    
    // 현재 그룹의 z-index를 최상위로
    group.style.zIndex = '1000';
    
    const menu = document.createElement('div');
    menu.className = 'selection-menu show';
    
    word.alternative_pronunciations.forEach((alt, altIndex) => {
        const item = document.createElement('div');
        item.className = 'selection-item';
        if (altIndex === word.selected_id) {
            item.classList.add('selected');
        }
        
        const pronDiv = document.createElement('div');
        pronDiv.className = 'selection-pron';
        pronDiv.textContent = `${alt.hangul_pron} / ${alt.hangul_kana}`;
        item.appendChild(pronDiv);
        
        const infoDiv = document.createElement('div');
        infoDiv.className = 'selection-info';
        infoDiv.textContent = `${alt.hiragana_pron} (${alt.pos1})`;
        item.appendChild(infoDiv);
        
        item.addEventListener('click', function(e) {
            e.stopPropagation();
            selectPronunciation(lineIndex, wordIndex, altIndex);
            menu.remove();
            // z-index 초기화
            group.style.zIndex = '';
        });
        
        menu.appendChild(item);
    });
    
    group.appendChild(menu);
    
    // 메뉴 외부 클릭 시 닫기
    setTimeout(() => {
        document.addEventListener('click', function closeMenu() {
            menu.remove();
            // z-index 초기화
            group.style.zIndex = '';
            document.removeEventListener('click', closeMenu);
        });
    }, 0);
}

function selectPronunciation(lineIndex, wordIndex, selectedId) {
    // 데이터 업데이트
    convertedData.lines[lineIndex].words[wordIndex].selected_id = selectedId;
    
    // 세션에 저장
    sessionStorage.setItem('convertedData', JSON.stringify(convertedData));
    
    // 화면 업데이트
    renderEditPanel();
}



function updateDisplay() {
    const useHyphen = document.getElementById('useHyphen').checked;
    
    document.querySelectorAll('.word-group').forEach(group => {
        const hangulDiv = group.querySelector('.word-pronunciation');
        // 하이픈 사용 여부에 따라 pron 또는 kana 표시
        hangulDiv.textContent = useHyphen ? hangulDiv.dataset.pron : hangulDiv.dataset.kana;
    });
}

function updateBorderVisibility() {
    // 여러 발음이 있을 때만 테두리 표시 (고정)
    document.querySelectorAll('.word-group').forEach(group => {
        // clickable 클래스가 있으면 (여러 발음) 테두리 표시
        if (group.classList.contains('clickable')) {
            group.style.border = '2px solid #2196F3';
            group.style.cursor = 'pointer';
        } else {
            group.style.border = '1px solid #e0e0e0';
            group.style.cursor = 'default';
        }
    });
}

function generateOutput() {
    // 현재 표시 설정을 세션에 저장
    const useHyphen = document.getElementById('useHyphen').checked;
    sessionStorage.setItem('useHyphen', useHyphen);
    
    // 출력 페이지로 이동
    window.location.href = '/output';
}
