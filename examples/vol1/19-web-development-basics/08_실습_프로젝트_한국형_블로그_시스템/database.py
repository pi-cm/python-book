# [1권 Chapter 19: 웹 개발 기초 · 실습 프로젝트: 한국형 블로그 시스템 · manuscript/chapters/19-web-development-basics.md:732]
# database.py - sqlite3 연결 관리 (17장에서 배운 방식 그대로)
import os
import sqlite3
from collections.abc import Iterator
from pathlib import Path

DB_PATH = Path(os.environ.get("BLOG_DB", "blog.db"))


def 테이블_만들기() -> None:
    with sqlite3.connect(DB_PATH) as 연결:
        연결.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT NOT NULL,
                content    TEXT NOT NULL,
                author     TEXT NOT NULL,
                category   TEXT NOT NULL,
                tags       TEXT NOT NULL DEFAULT '',
                views      INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
        """)


def 연결_얻기() -> Iterator[sqlite3.Connection]:
    """요청 하나에 연결 하나: 응답이 끝나면 반드시 닫는다."""
    연결 = sqlite3.connect(DB_PATH, check_same_thread=False)
    연결.row_factory = sqlite3.Row  # 행을 열 이름으로 읽을 수 있게
    try:
        yield 연결
    finally:
        연결.close()
