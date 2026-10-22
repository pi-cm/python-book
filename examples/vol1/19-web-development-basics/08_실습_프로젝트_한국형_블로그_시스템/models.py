# [1권 Chapter 19: 웹 개발 기초 · 실습 프로젝트: 한국형 블로그 시스템 · manuscript/chapters/19-web-development-basics.md:772]
# models.py - 요청과 응답의 모양 (8장의 Pydantic)
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["일상", "여행", "맛집", "개발"]


class PostIn(BaseModel):
    """글을 쓸 때 클라이언트가 보내는 값"""
    title: str = Field(min_length=2, max_length=100)
    content: str = Field(min_length=10)
    author: str = Field(min_length=2, max_length=20)
    category: Category = "일상"
    tags: list[str] = Field(default_factory=list, max_length=5)


class PostUpdate(BaseModel):
    """PATCH용: 보낸 값만 바꾸고, 빠진 값(None)은 그대로 둔다"""
    title: str | None = Field(default=None, min_length=2, max_length=100)
    content: str | None = Field(default=None, min_length=10)
    category: Category | None = None
    tags: list[str] | None = Field(default=None, max_length=5)


class Post(PostIn):
    """서버가 돌려주는 글: 입력값 + 서버가 정하는 값"""
    id: int
    views: int
    created_at: datetime
