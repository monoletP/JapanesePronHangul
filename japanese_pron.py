#!/usr/bin/env python3
"""
일본어 문장의 모든 단어에 대해 품사 정보와 가능한 모든 발음들을 JSON으로 추출
"""

import MeCab
import json
import sys
from typing import List, Dict, Any
from hangul_helper import kana_to_hangul


class JapanesePronunciationExtractor:
    def __init__(self, dict_path=None, nbest=10):
        """
        MeCab 초기화
        
        Args:
            dict_path: UniDic 사전 경로 (None이면 기본 사전 사용)
            nbest: N-best 결과 개수 (여러 발음 가능성을 얻기 위해)
        """
        self.nbest = nbest
        
        # lattice-level=1 옵션으로 lattice 정보 활성화
        lattice_option = '--lattice-level=1'
        
        if dict_path:
            self.tagger = MeCab.Tagger(f'-d {dict_path} {lattice_option}')
        else:
            # UniDic 사용 시도
            try:
                self.tagger = MeCab.Tagger(f'-d /usr/lib/x86_64-linux-gnu/mecab/dic/unidic {lattice_option}')
            except:
                # 기본 사전 사용
                self.tagger = MeCab.Tagger(lattice_option)
    
    def get_all_replace_nodes(self, node, length):
        """
        GetAllReplaceNode 함수의 파이썬 구현 (C# 원본 그대로)
        같은 길이를 가진 모든 대체 가능한 노드들을 재귀적으로 수집
        
        Args:
            node: MeCab 노드
            length: 대상 길이
            
        Returns:
            같은 길이를 가진 모든 노드 리스트
        """
        result = []
        visited = set()
        max_depth = 100  # 무한 루프 방지
        
        def collect_nodes(current_node, depth=0):
            """재귀적으로 BNext와 ENext를 탐색"""
            if current_node is None or depth > max_depth:
                return
            
            # 노드의 feature를 키로 사용하여 중복 체크 (같은 발음은 같은 feature)
            if current_node.surface:
                node_key = (current_node.surface, current_node.feature)
                if node_key in visited:
                    return
                
                # 같은 길이의 노드만 수집
                if current_node.length == length:
                    visited.add(node_key)
                    result.append(current_node)
                    
                    # BNext와 ENext로 재귀적 탐색 (C# 코드와 동일)
                    if hasattr(current_node, 'bnext') and current_node.bnext:
                        collect_nodes(current_node.bnext, depth + 1)
                    if hasattr(current_node, 'enext') and current_node.enext:
                        collect_nodes(current_node.enext, depth + 1)
        
        collect_nodes(node)
        return result
    
    def extract_pronunciations(self, text: str) -> List[Dict[str, Any]]:
        """
        입력 텍스트의 각 단어에 대한 품사와 발음 정보 추출
        
        Args:
            text: 분석할 일본어 텍스트
            
        Returns:
            단어 정보 리스트
        """
        # 기본 파싱 (1-best)
        self.tagger.parse('')  # 버그 방지
        node = self.tagger.parseToNode(text)
        
        results = []
        
        while node:
            # BOS(Begin of Sentence)와 EOS(End of Sentence) 노드는 건너뛰기
            if node.surface:
                features = node.feature.split(',')
                
                # UniDic 형식: 品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用型,活用形,語彙素読み,語彙素,書字形出現形,発音形出現形,書字形基本形,発音形基本形,語種
                pos1 = features[0] if len(features) > 0 else ""
                pos2 = features[1] if len(features) > 1 else ""
                pos3 = features[2] if len(features) > 2 else ""
                
                # 발음 정보 추출
                pron = ""
                kana = ""
                
                if len(features) >= 18:
                    # UniDic 형식
                    pron = features[9] if features[9] != '*' else features[0]  # 発音形出現形 (장음 하이픈)
                    kana = features[17] if features[17] != '*' else pron  # 読みがな (장음 모음 반복)
                    
                    # C# GetKana 로직: 助詞는 kana도 pron 사용 (は→わ)
                    pos1 = features[0] if len(features) > 0 else ""
                    if pos1 == "助詞":
                        kana = pron
                else:
                    # 기본 사전 형식 또는 features가 부족한 경우
                    if len(features) >= 10:
                        pron = features[9] if features[9] != '*' else features[0]
                    elif len(features) >= 8:
                        pron = features[7] if features[7] != '*' else node.surface
                    else:
                        pron = node.surface
                    kana = pron
                
                word_info = {
                    "surface": node.surface,  # 원문
                    "selected_id": 0,  # 기본 선택 (0-based 인덱스)
                    "alternative_pronunciations": []  # 대체 발음들
                }
                
                # 대체 발음 수집 (C# GetReplaceData와 동일한 방식)
                seen_prons = {}  # {pron: (kana, node)} 딕셔너리
                
                # Lattice에서 같은 길이의 모든 노드 수집
                try:
                    alt_nodes = self.get_all_replace_nodes(node, node.length)
                    
                    # 발음별로 중복 제거
                    for alt_node in alt_nodes:
                        alt_features = alt_node.feature.split(',')
                        
                        # 발음과 표기 추출
                        if len(alt_features) >= 18:
                            # UniDic 형식
                            alt_pron = alt_features[9] if alt_features[9] != '*' else alt_node.surface  # 発音形出現形
                            alt_kana = alt_features[17] if alt_features[17] != '*' else alt_pron  # 読みがな
                            
                            # C# GetKana 로직: 助詞는 kana도 pron 사용
                            alt_pos1 = alt_features[0] if len(alt_features) > 0 else ""
                            if alt_pos1 == "助詞":
                                alt_kana = alt_pron
                        elif len(alt_features) >= 10:
                            # UniDic이지만 features가 부족한 경우
                            alt_pron = alt_features[9] if alt_features[9] != '*' else alt_node.surface
                            alt_kana = alt_pron
                        elif len(alt_features) >= 8:
                            # 기본 사전
                            alt_pron = alt_features[7] if alt_features[7] != '*' else alt_node.surface
                            alt_kana = alt_pron
                        else:
                            alt_pron = alt_node.surface
                            alt_kana = alt_node.surface
                        if alt_pron not in seen_prons:
                            seen_prons[alt_pron] = (alt_kana, alt_node)
                except Exception as e:
                    # lattice 접근 실패 시 기본 발음만
                    seen_prons[pron] = (kana, node)
                
                # 한자 여부 체크
                has_kanji = any('\u4e00' <= c <= '\u9fff' for c in node.surface)
                
                # 히라가나/카타카나 여부 체크
                is_kana = all(
                    ('\u3040' <= c <= '\u309f') or  # 히라가나
                    ('\u30a0' <= c <= '\u30ff')     # 카타카나
                    for c in node.surface
                )
                
                # 모든 발음을 alternative_pronunciations에 추가 (중복 제거, 한자가 아닌 것 제외)
                added_prons = set()  # (hiragana_pron, katakana_pron) 튜플로 중복 체크
                for alt_pron, (alt_kana, alt_node) in seen_prons.items():
                    # 한자가 그대로 있으면 제외
                    if alt_pron == node.surface and any('\u4e00' <= c <= '\u9fff' for c in alt_pron):
                        continue
                    
                    # 품사 정보 추출
                    alt_features = alt_node.feature.split(',')
                    alt_pos1 = alt_features[0] if len(alt_features) > 0 else ""
                    
                    # alt_kana는 이미 seen_prons에서 가져온 값 (UniDic의 kana 필드)
                    # pron: 장음 하이픈 (サイコー), kana: 장음 모음 반복 (サイコウ)
                    
                    # 히라가나/카타카나로 정규화 (UniDic이 혼합해서 반환할 수 있음)
                    from hangul_helper import to_hiragana, to_katakana
                    alt_hiragana_pron = to_hiragana(alt_pron)
                    alt_katakana_pron = to_katakana(alt_pron)
                    alt_hiragana_kana = to_hiragana(alt_kana)
                    alt_katakana_kana = to_katakana(alt_kana)
                    
                    # 중복 체크
                    pron_key = (alt_hiragana_pron, alt_pron)
                    if pron_key in added_prons:
                        continue
                    added_prons.add(pron_key)
                    
                    # 대체 노드의 품사 정보 추출
                    alt_node_features = alt_node.feature.split(',')
                    alt_pos1 = alt_node_features[0] if len(alt_node_features) > 0 else ""
                    alt_pos2 = alt_node_features[1] if len(alt_node_features) > 1 else ""
                    alt_pos3 = alt_node_features[2] if len(alt_node_features) > 2 else ""
                    
                    # pron은 하이픈 사용, kana는 모음 반복으로 표시
                    alt_hangul_pron = kana_to_hangul(alt_pron, use_hyphen=True)
                    alt_hangul_kana = kana_to_hangul(alt_kana, use_hyphen=False)
                    word_info["alternative_pronunciations"].append({
                        "hiragana_pron": alt_hiragana_pron,
                        "hiragana_kana": alt_hiragana_kana,
                        "katakana_pron": alt_pron,
                        "katakana_kana": alt_katakana_kana,
                        "hangul_pron": alt_hangul_pron,
                        "hangul_kana": alt_hangul_kana,
                        "pos1": alt_pos1,
                        "pos2": alt_pos2,
                        "pos3": alt_pos3
                    })
                    
                    # 히라가나/카타카나/특수문자는 첫 번째 발음만 추가 (한자만 여러 발음 제공)
                    if not has_kanji:
                        break
                
                results.append(word_info)
            
            node = node.next
        
        return results
    
    def analyze_sentence(self, text: str) -> Dict[str, Any]:
        """
        문장 전체를 분석하여 JSON 형식으로 반환
        
        Args:
            text: 분석할 일본어 텍스트
            
        Returns:
            분석 결과 딕셔너리
        """
        words = self.extract_pronunciations(text)
        
        return {
            "original_text": text,
            "word_count": len(words),
            "words": words
        }


def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법: python japanese_pron.py <일본어 텍스트>")
        print("예시: python japanese_pron.py '日本語の文章'")
        sys.exit(1)
    
    text = sys.argv[1]
    
    # 사전 경로 지정 (필요시)
    dict_path = None
    if len(sys.argv) > 2:
        dict_path = sys.argv[2]
    
    extractor = JapanesePronunciationExtractor(dict_path)
    result = extractor.analyze_sentence(text)
    
    # JSON 출력
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
