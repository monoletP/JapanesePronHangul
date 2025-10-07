#!/usr/bin/env python3
"""
일본어 가나(히라가나, 가타카나)를 한글로 변환하는 헬퍼 모듈
C# RomajiConverter.Core의 KanaHelper.cs를 Python으로 포팅
"""


def to_hiragana(text):
    """
    가타카나를 히라가나로 변환
    
    Args:
        text: 변환할 문자열
    
    Returns:
        히라가나로 변환된 문자열
    """
    result = []
    for ch in text:
        code = ord(ch)
        # 가타카나 범위 (U+30A0 ~ U+30FA)
        if 0x30A0 <= code <= 0x30FA:
            # 히라가나로 변환 (0x60 빼기)
            result.append(chr(code - 0x60))
        else:
            result.append(ch)
    return ''.join(result)


def to_katakana(text):
    """
    히라가나를 가타카나로 변환
    
    Args:
        text: 변환할 문자열
    
    Returns:
        가타카나로 변환된 문자열
    """
    result = []
    for ch in text:
        code = ord(ch)
        # 히라가나 범위 (U+3040 ~ U+309F)
        if 0x3040 <= code <= 0x309F:
            # 가타카나로 변환 (0x60 더하기)
            result.append(chr(code + 0x60))
        else:
            result.append(ch)
    return ''.join(result)


# 기본 가나 → 한글 변환 사전
KANA_DICT = {
    # 히라가나
    "あ": "아", "い": "이", "う": "우", "え": "에", "お": "오",
    "か": "카", "き": "키", "く": "쿠", "け": "케", "こ": "코",
    "さ": "사", "し": "시", "す": "스", "せ": "세", "そ": "소",
    "た": "타", "ち": "치", "つ": "츠", "て": "테", "と": "토",
    "な": "나", "に": "니", "ぬ": "누", "ね": "네", "の": "노",
    "は": "하", "ひ": "히", "ふ": "후", "へ": "헤", "ほ": "호",
    "ま": "마", "み": "미", "む": "무", "め": "메", "も": "모",
    "や": "야", "ゆ": "유", "よ": "요",
    "ら": "라", "り": "리", "る": "루", "れ": "레", "ろ": "로",
    "わ": "와", "を": "오",
    "が": "가", "ぎ": "기", "ぐ": "구", "げ": "게", "ご": "고",
    "ざ": "자", "じ": "지", "ず": "즈", "ぜ": "제", "ぞ": "조",
    "だ": "다", "ぢ": "지", "づ": "즈", "で": "데", "ど": "도",
    "ば": "바", "び": "비", "ぶ": "부", "べ": "베", "ぼ": "보",
    "ぱ": "파", "ぴ": "피", "ぷ": "푸", "ぺ": "페", "ぽ": "포",
    
    # 가타카나
    "ア": "아", "イ": "이", "ウ": "우", "エ": "에", "オ": "오",
    "カ": "카", "キ": "키", "ク": "쿠", "ケ": "케", "コ": "코",
    "サ": "사", "シ": "시", "ス": "스", "セ": "세", "ソ": "소",
    "タ": "타", "チ": "치", "ツ": "츠", "テ": "테", "ト": "토",
    "ナ": "나", "ニ": "니", "ヌ": "누", "ネ": "네", "ノ": "노",
    "ハ": "하", "ヒ": "히", "フ": "후", "ヘ": "헤", "ホ": "호",
    "マ": "마", "ミ": "미", "ム": "무", "メ": "메", "モ": "모",
    "ヤ": "야", "ユ": "유", "ヨ": "요",
    "ラ": "라", "リ": "리", "ル": "루", "レ": "레", "ロ": "로",
    "ワ": "와", "ヲ": "오",
    "ガ": "가", "ギ": "기", "グ": "구", "ゲ": "게", "ゴ": "고",
    "ザ": "자", "ジ": "지", "ズ": "즈", "ゼ": "제", "ゾ": "조",
    "ダ": "다", "ヂ": "지", "ヅ": "즈", "デ": "데", "ド": "도",
    "バ": "바", "ビ": "비", "ブ": "부", "ベ": "베", "ボ": "보",
    "パ": "파", "ピ": "피", "プ": "푸", "ペ": "페", "ポ": "포",
    
    # 소가나
    "ぁ": "아", "ぃ": "이", "ぅ": "우", "ぇ": "에", "ぉ": "오",
    "ゃ": "야", "ゅ": "유", "ょ": "요", "ゎ": "와",
    "ァ": "아", "ィ": "이", "ゥ": "우", "ェ": "에", "ォ": "오",
    "ャ": "야", "ュ": "유", "ョ": "요", "ヮ": "와",
}

# 확장 가나 → 한글 변환 사전 (요음 등)
EXTENDED_KANA_DICT = {
    # 히라가나 요음
    "きゃ": "캬", "きゅ": "큐", "きょ": "쿄",
    "しゃ": "샤", "しゅ": "슈", "しょ": "쇼",
    "ちゃ": "챠", "ちゅ": "츄", "ちょ": "쵸",
    "にゃ": "냐", "にゅ": "뉴", "にょ": "뇨",
    "ひゃ": "햐", "ひゅ": "휴", "ひょ": "효",
    "みゃ": "먀", "みゅ": "뮤", "みょ": "묘",
    "りゃ": "랴", "りゅ": "류", "りょ": "료",
    "ぎゃ": "갸", "ぎゅ": "규", "ぎょ": "교",
    "じゃ": "자", "じゅ": "주", "じょ": "조",
    "ぢゃ": "자", "ぢゅ": "주", "ぢょ": "조",
    "びゃ": "뱌", "びゅ": "뷰", "びょ": "뵤",
    "ぴゃ": "퍄", "ぴゅ": "퓨", "ぴょ": "표",
    
    # 가타카나 요음
    "キャ": "캬", "キュ": "큐", "キョ": "쿄",
    "シャ": "샤", "シュ": "슈", "ショ": "쇼",
    "チャ": "챠", "チュ": "츄", "チョ": "쵸",
    "ニャ": "냐", "ニュ": "뉴", "ニョ": "뇨",
    "ヒャ": "햐", "ヒュ": "휴", "ヒョ": "효",
    "ミャ": "먀", "ミュ": "뮤", "ミョ": "묘",
    "リャ": "랴", "リュ": "류", "リョ": "료",
    "ギャ": "갸", "ギュ": "규", "ギョ": "교",
    "ジャ": "자", "ジュ": "주", "ジョ": "조",
    "ヂャ": "자", "ヂュ": "주", "ヂョ": "조",
    "ビャ": "뱌", "ビュ": "뷰", "ビョ": "뵤",
    "ピャ": "퍄", "ピュ": "퓨", "ピョ": "표",
    
    # 그 외 언어들
    "イェ": "예",
    "ウィ": "위", "ウェ": "웨", "ウォ": "워",
    "ヴァ": "바", "ヴィ": "비", "ヴ": "부", "ヴェ": "베", "ヴォ": "보",
    "ヴュ": "뷰",
    "クァ": "콰", "クィ": "퀴", "クェ": "퀘", "クォ": "쿼",
    "グァ": "과",
    "シェ": "셰",
    "ジェ": "제",
    "チェ": "체",
    "ツァ": "차", "ツィ": "치", "ツェ": "체", "ツォ": "초",
    "ティ": "티", "トゥ": "투",
    "テュ": "튜",
    "ディ": "디", "ドゥ": "두",
    "デュ": "듀",
    "ファ": "파", "フィ": "피", "フェ": "페", "フォ": "포",
    "フュ": "퓨",
}


def add_jongseong(char, jongseong_index):
    """
    한글 문자에 종성(받침)을 추가
    
    Args:
        char: 한글 문자
        jongseong_index: 종성 인덱스 (0~27)
    
    Returns:
        받침이 추가된 한글 문자
    """
    if not (0xAC00 <= ord(char) <= 0xD7A3):
        return char
    
    unicode_index = ord(char) - 0xAC00
    choseong = unicode_index // (21 * 28)
    jungseong = (unicode_index // 28) % 21
    
    new_char = 0xAC00 + (choseong * 21 * 28) + (jungseong * 28) + jongseong_index
    return chr(new_char)


def kana_to_hangul(text, use_hyphen=True):
    """
    가나를 한글로 변환
    C# KanaHelper.KatakanaToRomaji의 한글 버전
    
    Args:
        text: 변환할 가나 문자열
        use_hyphen: 장음을 하이픈(-)으로 표시할지 여부
    
    Returns:
        한글로 변환된 문자열
    """
    result = []
    i = 0
    
    while i < len(text):
        # 2글자 확장 가나 체크
        if i < len(text) - 1:
            two_char = text[i:i+2]
            if two_char in EXTENDED_KANA_DICT:
                result.append(EXTENDED_KANA_DICT[two_char])
                i += 2
                continue
        
        # 1글자 가나 체크
        char = text[i]
        if char in KANA_DICT:
            result.append(KANA_DICT[char])
        elif char == "ー":
            # 장음 처리
            result.append("-")
        else:
            # 변환 불가능한 문자는 그대로 유지
            result.append(char)
        
        i += 1
    
    # 촉음(っ, ッ)과 ん(ン) 처리
    i = 0
    while i < len(result):
        current = result[i]
        
        # 촉음 처리
        if current in ['っ', 'ッ']:
            if i == 0 or len(result) <= 1:
                result[i] = 'ㅅ'  # 기본값
            else:
                # 이전 문자에 ㅅ 받침 추가
                prev_char = result[i - 1]
                if 0xAC00 <= ord(prev_char) <= 0xD7A3:
                    result[i - 1] = add_jongseong(prev_char, 19)  # ㅅ
                    result.pop(i)
                    i -= 1
                else:
                    result[i] = 'ㅅ'
        
        # ん(ン) 처리
        elif current in ['ん', 'ン']:
            if i == 0 or len(result) <= 1:
                result[i] = 'ㄴ'  # 기본값
            else:
                # 이전 문자에 ㄴ 받침 추가
                prev_char = result[i - 1]
                if 0xAC00 <= ord(prev_char) <= 0xD7A3:
                    result[i - 1] = add_jongseong(prev_char, 4)  # ㄴ
                    result.pop(i)
                    i -= 1
                else:
                    result[i] = 'ㄴ'
        
        i += 1
    
    result_str = ''.join(result)
    
    # 하이픈을 장음으로 변환
    if not use_hyphen:
        result_str = convert_hyphen_to_longsound(result_str)
    
    return result_str


def is_hangul_without_jongseong(char):
    """
    한글이 종성(받침) 없이 초성+중성만 있는지 확인
    
    Args:
        char: 확인할 문자
    
    Returns:
        받침이 없으면 True, 아니면 False
    """
    if not (0xAC00 <= ord(char) <= 0xD7A3):
        return False
    
    unicode_index = ord(char) - 0xAC00
    jongseong_index = unicode_index % 28
    
    return jongseong_index == 0


def is_longsound(prev_char, current_char):
    """
    이전 한글 문자와 현재 한글 문자가 같은 중성을 가지면서
    현재 한글 문자가 초성이 'ㅇ'인지 확인 (장음 판정)
    
    Args:
        prev_char: 이전 문자
        current_char: 현재 문자
    
    Returns:
        장음이면 True, 아니면 False
    """
    if not (0xAC00 <= ord(prev_char) <= 0xD7A3 and 0xAC00 <= ord(current_char) <= 0xD7A3):
        return False
    
    prev_index = ord(prev_char) - 0xAC00
    curr_index = ord(current_char) - 0xAC00
    
    prev_jungseong = (prev_index % (21 * 28)) // 28
    curr_jungseong = (curr_index % (21 * 28)) // 28
    curr_choseong = curr_index // (21 * 28)
    
    # 초성 'ㅇ' 인덱스는 11
    is_ieung = (curr_choseong == 11)
    
    # 예외 중성 쌍
    special_jungseong_pairs = [
        (8, 13),   # ㅗ → ㅜ
        (6, 0),    # ㅑ → ㅏ
        (7, 4),    # ㅕ → ㅓ
        (12, 8),   # ㅛ → ㅗ
        (12, 13),  # ㅛ → ㅜ
        (17, 13),  # ㅠ → ㅜ
    ]
    
    is_special_pair = (prev_jungseong, curr_jungseong) in special_jungseong_pairs
    
    return is_ieung and (prev_jungseong == curr_jungseong or is_special_pair)


def get_longsound_char(prev_char):
    """
    이전 한글 문자와 중성이 같으면서 초성이 'ㅇ'인 글자를 반환 (장음 표현)
    
    Args:
        prev_char: 이전 한글 문자
    
    Returns:
        장음 표현 문자
    """
    if not (0xAC00 <= ord(prev_char) <= 0xD7A3):
        return prev_char
    
    prev_index = ord(prev_char) - 0xAC00
    prev_jungseong = (prev_index % (21 * 28)) // 28
    
    # 초성 'ㅇ' 인덱스는 11
    ieung_choseong = 11
    
    new_char = 0xAC00 + (ieung_choseong * 21 * 28) + (prev_jungseong * 28)
    return chr(new_char)


def convert_longsound_to_hyphen(text):
    """
    장음을 하이픈(-)으로 변환
    
    Args:
        text: 변환할 문자열
    
    Returns:
        하이픈으로 변환된 문자열
    """
    result = []
    result.append(text[0])  # 첫 번째 문자 추가
    
    for i in range(1, len(text)):
        prev_char = text[i - 1]
        curr_char = text[i]
        
        # 동어반복 예외 처리
        is_repetition = False
        if i > 1 and i < len(text) - 1:
            if text[i - 2] == curr_char and prev_char == text[i + 1]:
                is_repetition = True
        
        if is_longsound(prev_char, curr_char) and not is_repetition:
            result.append("-")
        else:
            result.append(curr_char)
    
    return ''.join(result)


def convert_hyphen_to_longsound(text):
    """
    하이픈(-)을 장음으로 변환
    
    Args:
        text: 변환할 문자열
    
    Returns:
        장음으로 변환된 문자열
    """
    result = []
    
    for i in range(len(text)):
        if text[i] == '-':
            if i > 0:
                result.append(get_longsound_char(text[i - 1]))
            else:
                result.append('-')
        else:
            result.append(text[i])
    
    return ''.join(result)


if __name__ == '__main__':
    # 테스트
    test_cases = [
        "こえ",      # 목소리 (koe)
        "せい",      # 소리 (sei)
        "こんにちは", # 안녕하세요
        "ありがとう", # 감사합니다
        "きょう",    # 오늘
        "がっこう",  # 학교
        "せんせい",  # 선생님
    ]
    
    print("가나 → 한글 변환 테스트\n")
    for test in test_cases:
        hyphen_ver = kana_to_hangul(test, use_hyphen=True)
        longsound_ver = kana_to_hangul(test, use_hyphen=False)
        print(f"{test:10} → {hyphen_ver:10} (하이픈) / {longsound_ver:10} (장음)")
