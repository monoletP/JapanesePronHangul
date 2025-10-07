#!/usr/bin/env python3
"""
FastAPI 웹 애플리케이션 - 일본어 가사 한글 변환기
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
import json

from japanese_pron import JapanesePronunciationExtractor

app = FastAPI(title="일본어 가사 한글 변환기")

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# MeCab 초기화 (전역으로 한 번만)
extractor = JapanesePronunciationExtractor()


class ConvertRequest(BaseModel):
    """변환 요청 모델"""
    text: str
    detail_mode: bool = False


class UpdateSelectionRequest(BaseModel):
    """선택 업데이트 요청 모델"""
    line_index: int
    word_index: int
    selected_id: int


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("main.html", {"request": request})


@app.get("/input", response_class=HTMLResponse)
async def input_page(request: Request):
    """입력 페이지"""
    return templates.TemplateResponse("input.html", {"request": request})


@app.get("/edit", response_class=HTMLResponse)
async def edit_page(request: Request):
    """편집 페이지 (상세 모드)"""
    return templates.TemplateResponse("edit.html", {"request": request})


@app.get("/output", response_class=HTMLResponse)
async def output_page(request: Request):
    """출력 페이지"""
    return templates.TemplateResponse("output.html", {"request": request})


@app.post("/api/convert")
async def convert_text(request: ConvertRequest):
    """
    일본어 텍스트를 한글로 변환
    여러 줄 입력을 받아서 각 줄마다 분석
    """
    lines = request.text.strip().split('\n')
    result = []
    
    for line_text in lines:
        if not line_text.strip():
            # 빈 줄은 빈 단어 리스트로
            result.append({
                "original_text": line_text,
                "word_count": 0,
                "words": []
            })
        else:
            # 각 줄을 분석
            line_result = extractor.analyze_sentence(line_text.strip())
            result.append(line_result)
    
    return JSONResponse(content={
        "lines": result,
        "detail_mode": request.detail_mode
    })


@app.post("/api/update_selection")
async def update_selection(request: UpdateSelectionRequest):
    """
    특정 단어의 선택된 발음 업데이트
    (세션 관리가 필요하면 추가 구현 필요)
    """
    return JSONResponse(content={
        "success": True,
        "line_index": request.line_index,
        "word_index": request.word_index,
        "selected_id": request.selected_id
    })


@app.get("/api/health")
async def health_check():
    """헬스 체크"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
