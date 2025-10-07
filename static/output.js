// Output Page JavaScript

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
    
    // 설정 복원
    const useHyphen = sessionStorage.getItem('useHyphen');
    if (useHyphen !== null) {
        document.getElementById('useHyphen').checked = useHyphen === 'true';
    }
    
    const addSpace = sessionStorage.getItem('addSpace');
    if (addSpace !== null) {
        document.getElementById('addSpace').checked = addSpace === 'true';
    }
    
    const showOriginal = sessionStorage.getItem('showOriginal');
    if (showOriginal !== null) {
        document.getElementById('showOriginal').checked = showOriginal === 'true';
    }
    
    const clarifyNn = sessionStorage.getItem('clarifyNn');
    if (clarifyNn !== null) {
        document.getElementById('clarifyNn').checked = clarifyNn === 'true';
    }
    
    const clarifyXts = sessionStorage.getItem('clarifyXts');
    if (clarifyXts !== null) {
        document.getElementById('clarifyXts').checked = clarifyXts === 'true';
    }
    
    updateOutput();
});

function goBack() {
    window.location.href = '/input';
}

// 한글 유니코드 분해
function decomposeHangul(char) {
    const code = char.charCodeAt(0);
    if (code < 0xAC00 || code > 0xD7A3) {
        return null;
    }
    const baseCode = 0xAC00;
    const choseongIndex = Math.floor((code - baseCode) / (21 * 28));
    const jungseongIndex = Math.floor(((code - baseCode) % (21 * 28)) / 28);
    const jongseongIndex = (code - baseCode) % 28;
    return { choseongIndex, jungseongIndex, jongseongIndex };
}

// 한글 유니코드 조합
function composeHangul(choseongIndex, jungseongIndex, jongseongIndex) {
    const baseCode = 0xAC00;
    return String.fromCharCode(baseCode + (choseongIndex * 21 * 28) + (jungseongIndex * 28) + jongseongIndex);
}

// 응(ㄴ) 세분화: ㄴ, ㅇ, ㅁ 받침을 다음 글자에 따라 변환
function clarifyNnFunc(char, nextChar) {
    const decomposed = decomposeHangul(char);
    if (!decomposed) return char;
    
    let { choseongIndex, jungseongIndex, jongseongIndex } = decomposed;
    
    // 종성이 ㄴ(4), ㅇ(21), ㅁ(16)인 경우만 처리
    if (jongseongIndex !== 4 && jongseongIndex !== 21 && jongseongIndex !== 16) {
        return char;
    }
    
    if (nextChar === ' ' || nextChar === '아' || nextChar === undefined) {
        // 공백이거나 문장 끝인 경우 ㅇ으로
        jongseongIndex = 21;
    } else {
        const nextDecomposed = decomposeHangul(nextChar);
        if (nextDecomposed) {
            const nextChoseong = nextDecomposed.choseongIndex;
            if (nextChoseong === 0 || nextChoseong === 15 || nextChoseong === 11) {
                // ㄱ, ㅋ, ㅇ → ㅇ으로
                jongseongIndex = 21;
            } else if (nextChoseong === 6 || nextChoseong === 7 || nextChoseong === 17) {
                // ㅁ, ㅂ, ㅍ → ㅁ으로
                jongseongIndex = 16;
            } else {
                // 그 외 → ㄴ으로
                jongseongIndex = 4;
            }
        }
    }
    
    return composeHangul(choseongIndex, jungseongIndex, jongseongIndex);
}

// 촉음(ㅅ) 세분화: ㅅ, ㄱ, ㄷ, ㅂ, ㄹ 받침을 다음 글자에 따라 변환
function clarifyXtsFunc(char, nextChar) {
    const decomposed = decomposeHangul(char);
    if (!decomposed) return char;
    
    let { choseongIndex, jungseongIndex, jongseongIndex } = decomposed;
    
    // 종성이 ㅅ(19), ㄱ(1), ㄷ(7), ㅂ(17), ㄹ(8)인 경우만 처리
    if (jongseongIndex !== 19 && jongseongIndex !== 1 && jongseongIndex !== 7 && 
        jongseongIndex !== 17 && jongseongIndex !== 8) {
        return char;
    }
    
    if (nextChar === ' ' || nextChar === undefined) {
        // 공백이거나 문장 끝인 경우 변환 안 함
        return char;
    }
    
    const nextDecomposed = decomposeHangul(nextChar);
    if (nextDecomposed) {
        const nextChoseong = nextDecomposed.choseongIndex;
        if (nextChoseong === 15) {
            // ㅋ → ㄱ으로
            jongseongIndex = 1;
        } else if (nextChoseong === 16) {
            // ㅌ → ㄷ으로
            jongseongIndex = 7;
        } else if (nextChoseong === 17) {
            // ㅍ → ㅂ로
            jongseongIndex = 17;
        } else if (nextChoseong === 5) {
            // ㄹ → ㄹ로
            jongseongIndex = 8;
        } else {
            // 그 외 → ㅅ으로
            jongseongIndex = 19;
        }
    }
    
    return composeHangul(choseongIndex, jungseongIndex, jongseongIndex);
}

// 단독 ㅅ, ㄴ을 앞 글자에 받침으로 추가
function attachJongseong(text, useHyphen, clarifyNn, clarifyXts) {
    if (text.length <= 1) return text;
    
    let result = '';
    const singleJamos = ['ㅅ', 'ㄴ'];
    
    for (let i = 0; i < text.length; i++) {
        const current = text[i];
        
        // ㅅ 또는 ㄴ이 단독으로 존재하고, 앞 글자가 있는 경우
        if (i > 0 && singleJamos.includes(current)) {
            let previousChar = text[i - 1];
            let previousIndex = i - 1;
            
            // 앞 글자가 공백인 경우 건너뛰기
            if (previousChar === ' ' && i > 1) {
                previousChar = text[i - 2];
                previousIndex = i - 2;
                result = result.slice(0, -1); // 공백 제거
            }
            
            // 장음 하이픈 예외 처리
            let isHyphen = previousChar === '-';
            if (isHyphen && previousIndex > 0) {
                previousChar = text[previousIndex - 1];
            }
            
            const decomposed = decomposeHangul(previousChar);
            if (decomposed) {
                let { choseongIndex, jungseongIndex, jongseongIndex } = decomposed;
                
                // 장음이면 초성 ㅇ으로
                if (isHyphen) {
                    choseongIndex = 11;
                }
                
                // ㅅ이면 19번 종성, ㄴ이면 4번 종성으로 설정
                if (current === 'ㅅ') {
                    jongseongIndex = 19;
                } else if (current === 'ㄴ') {
                    jongseongIndex = 4;
                }
                
                let newChar = composeHangul(choseongIndex, jungseongIndex, jongseongIndex);
                
                // 다음 글자와 비교해 응, 촉음 발음 세분화
                if (i !== text.length - 1) {
                    if (clarifyNn) {
                        newChar = clarifyNnFunc(newChar, text[i + 1]);
                    }
                    if (clarifyXts) {
                        newChar = clarifyXtsFunc(newChar, text[i + 1]);
                    }
                }
                
                // 결과에 추가 (이전 글자는 제거, 새 글자 추가)
                result = result.slice(0, -1) + newChar;
                continue;
            }
        }
        
        // 일반 문자는 그대로 추가
        result += current;
    }
    
    return result;
}

// 단어 내부의 응/촉음 세분화 처리
function processWordInternal(text, clarifyNnFlag, clarifyXtsFlag, isProperNoun) {
    if (text.length <= 1 || isProperNoun) return text;
    
    let result = '';
    for (let i = 0; i < text.length; i++) {
        let char = text[i];
        
        // 다음 글자가 있으면 세분화 적용
        if (i < text.length - 1) {
            if (clarifyNnFlag) {
                char = clarifyNnFunc(char, text[i + 1]);
            }
            if (clarifyXtsFlag) {
                char = clarifyXtsFunc(char, text[i + 1]);
            }
        } else if (clarifyNnFlag) {
            // 마지막 글자는 '아'로 처리 (문장 끝)
            char = clarifyNnFunc(char, '아');
        }
        
        result += char;
    }
    
    return result;
}

// 공백 추가 로직을 포함한 텍스트 생성
function getLineTextWithOptions(words, useHyphen, addSpace, clarifyNnFlag, clarifyXtsFlag) {
    if (words.length === 0) return '';
    
    let result = '';
    let previousWord = null;
    
    for (let i = 0; i < words.length; i++) {
        const word = words[i];
        const selected = word.alternative_pronunciations[word.selected_id];
        const isProperNoun = selected.pos2 === '固有名詞';
        
        // 기본 텍스트 가져오기
        let wordText = useHyphen ? selected.hangul_pron : selected.hangul_kana;
        
        // 단어 내부 세분화 처리 (고유명사 제외)
        if (!isProperNoun) {
            wordText = processWordInternal(wordText, clarifyNnFlag, clarifyXtsFlag, isProperNoun);
        }
        
        // 공백 추가 조건 확인
        let shouldAddSpace = false;
        if (previousWord && addSpace) {
            const pos1 = selected.pos1;
            const pos2 = selected.pos2;
            const pos3 = selected.pos3;
            const prevSelected = previousWord.alternative_pronunciations[previousWord.selected_id];
            const prevPos1 = prevSelected.pos1;
            const prevPos2 = prevSelected.pos2;
            
            // C# 코드의 공백 조건을 반대로 적용
            shouldAddSpace = !(
                pos1 === '助詞' || pos1 === '助動詞' || pos1 === '接尾辞' ||
                pos2 === '非自立' ||
                (prevPos1 !== '助詞' && pos2 === '非自立可能') ||
                (prevPos2 === '接続助詞' && pos1 === '動詞') ||  // 接続助詞 뒤의 動詞는 보조동사
                prevPos1 === '接頭辞' ||
                (prevPos2 === '数詞' && (pos2 === '数詞' || pos3 === '助数詞可能'))
            );
        }
        
        // 공백 추가 전에 이전 단어의 마지막 글자 세분화
        if (shouldAddSpace && result.length > 0 && wordText.length > 0) {
            // 공백이 추가될 경우, 이전 글자의 응 발음을 '아'(문장 끝)로 처리
            if (clarifyNnFlag) {
                const lastChar = result[result.length - 1];
                const clarifiedChar = clarifyNnFunc(lastChar, '아');
                result = result.slice(0, -1) + clarifiedChar;
            }
            result += ' ';
        } else if (previousWord && result.length > 0 && wordText.length > 0) {
            // 공백이 추가되지 않을 경우, 다음 글자와 비교해 세분화
            const lastChar = result[result.length - 1];
            const nextChar = wordText[0];
            
            let clarifiedChar = lastChar;
            if (clarifyNnFlag) {
                clarifiedChar = clarifyNnFunc(clarifiedChar, nextChar);
            }
            if (clarifyXtsFlag) {
                clarifiedChar = clarifyXtsFunc(clarifiedChar, nextChar);
            }
            result = result.slice(0, -1) + clarifiedChar;
        }
        
        result += wordText;
        previousWord = word;
    }
    
    // 라인의 첫 번째 문자가 공백이면 제거
    if (result.startsWith(' ')) {
        result = result.trimStart();
    }
    
    // 마지막으로 단독 ㅅ, ㄴ을 앞 글자에 받침으로 추가
    result = attachJongseong(result, useHyphen, clarifyNnFlag, clarifyXtsFlag);
    
    return result;
}


function updateOutput() {
    const panel = document.getElementById('outputPanel');
    const useHyphen = document.getElementById('useHyphen').checked;
    const addSpace = document.getElementById('addSpace').checked;
    const showOriginal = document.getElementById('showOriginal').checked;
    const clarifyNnFlag = document.getElementById('clarifyNn').checked;
    const clarifyXtsFlag = document.getElementById('clarifyXts').checked;
    
    panel.innerHTML = ''; // 초기화
    
    convertedData.lines.forEach(line => {
        const lineContainer = document.createElement('div');
        lineContainer.className = 'output-line-container';
        
        if (line.words.length === 0) {
            // 빈 줄
            lineContainer.innerHTML = '<br>';
        } else {
            // 원문 표시
            if (showOriginal) {
                const originalDiv = document.createElement('div');
                originalDiv.className = 'output-original';
                originalDiv.textContent = line.original_text;
                lineContainer.appendChild(originalDiv);
            }
            
            // 변환된 텍스트
            const convertedDiv = document.createElement('div');
            convertedDiv.className = 'output-converted';
            
            const lineText = getLineTextWithOptions(line.words, useHyphen, addSpace, clarifyNnFlag, clarifyXtsFlag);
            
            convertedDiv.textContent = lineText;
            lineContainer.appendChild(convertedDiv);
        }
        
        panel.appendChild(lineContainer);
    });
    
    // 세션에 저장
    sessionStorage.setItem('useHyphen', useHyphen);
    sessionStorage.setItem('addSpace', addSpace);
    sessionStorage.setItem('showOriginal', showOriginal);
    sessionStorage.setItem('clarifyNn', clarifyNnFlag);
    sessionStorage.setItem('clarifyXts', clarifyXtsFlag);
}

function copyToClipboard(event) {
    const panel = document.getElementById('outputPanel');
    const useHyphen = document.getElementById('useHyphen').checked;
    const addSpace = document.getElementById('addSpace').checked;
    const showOriginal = document.getElementById('showOriginal').checked;
    const clarifyNnFlag = document.getElementById('clarifyNn').checked;
    const clarifyXtsFlag = document.getElementById('clarifyXts').checked;
    
    // 복사할 텍스트 생성
    let result = [];
    
    convertedData.lines.forEach(line => {
        if (line.words.length === 0) {
            result.push('');
        } else {
            // 원문 추가
            if (showOriginal) {
                result.push(line.original_text);
            }
            
            // 변환된 텍스트 추가
            const lineText = getLineTextWithOptions(line.words, useHyphen, addSpace, clarifyNnFlag, clarifyXtsFlag);
            result.push(lineText);
        }
    });
    
    const text = result.join('\n');
    
    navigator.clipboard.writeText(text).then(() => {
        // 복사 성공 알림
        const button = event.target;
        const originalText = button.textContent;
        button.textContent = '✓ 복사됨!';
        button.style.background = '#4caf50';
        button.style.color = 'white';
        
        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '';
            button.style.color = '';
        }, 2000);
    }).catch(err => {
        console.error('복사 실패:', err);
        alert('복사에 실패했습니다.');
    });
}

