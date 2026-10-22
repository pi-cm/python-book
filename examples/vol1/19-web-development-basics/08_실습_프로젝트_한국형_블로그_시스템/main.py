# [1권 Chapter 19: 웹 개발 기초 · 실습 프로젝트: 한국형 블로그 시스템 · manuscript/chapters/19-web-development-basics.md:810]
# main.py - 한국형 블로그 API
import sqlite3

from fastapi import Depends, FastAPI, HTTPException, Query, status

from database import 연결_얻기, 테이블_만들기
from models import Category, Post, PostIn, PostUpdate

app = FastAPI(title="한국형 블로그 API", version="1.0.0")
테이블_만들기()


def 행을_글로(행: sqlite3.Row) -> Post:
    태그들 = 행["tags"].split(",") if 행["tags"] else []
    return Post(**{**dict(행), "tags": 태그들})


def 글_찾기(post_id: int, db: sqlite3.Connection) -> sqlite3.Row:
    행 = db.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    if 행 is None:
        raise HTTPException(status_code=404, detail=f"{post_id}번 글이 없습니다")
    return 행


@app.get("/api/posts")
def 글_목록(
    category: Category | None = None,
    q: str | None = Query(default=None, min_length=1),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=50),
    db: sqlite3.Connection = Depends(연결_얻기),
) -> list[Post]:
    조건, 값들 = [], []
    if category:
        조건.append("category = ?")
        값들.append(category)
    if q:
        조건.append("(title LIKE ? OR content LIKE ?)")
        값들 += [f"%{q}%", f"%{q}%"]
    sql = "SELECT * FROM posts"
    if 조건:
        sql += " WHERE " + " AND ".join(조건)  # 조각은 모두 위에 고정된 문자열
    sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
    값들 += [size, (page - 1) * size]
    return [행을_글로(행) for 행 in db.execute(sql, 값들)]


@app.post("/api/posts", status_code=status.HTTP_201_CREATED)
def 글_쓰기(입력: PostIn, db: sqlite3.Connection = Depends(연결_얻기)) -> Post:
    커서 = db.execute(
        "INSERT INTO posts (title, content, author, category, tags)"
        " VALUES (?, ?, ?, ?, ?)",
        (입력.title, 입력.content, 입력.author, 입력.category, ",".join(입력.tags)),
    )
    db.commit()
    return 행을_글로(글_찾기(커서.lastrowid, db))


@app.get("/api/posts/{post_id}")
def 글_읽기(post_id: int, db: sqlite3.Connection = Depends(연결_얻기)) -> Post:
    글_찾기(post_id, db)
    db.execute("UPDATE posts SET views = views + 1 WHERE id = ?", (post_id,))
    db.commit()
    return 행을_글로(글_찾기(post_id, db))


@app.patch("/api/posts/{post_id}")
def 글_고치기(
    post_id: int, 입력: PostUpdate, db: sqlite3.Connection = Depends(연결_얻기)
) -> Post:
    글_찾기(post_id, db)
    태그 = ",".join(입력.tags) if 입력.tags is not None else None
    # COALESCE(새 값, 원래 값): 새 값이 NULL(None)이면 원래 값을 유지
    db.execute(
        """UPDATE posts SET title = COALESCE(?, title), content = COALESCE(?, content),
               category = COALESCE(?, category), tags = COALESCE(?, tags)
           WHERE id = ?""",
        (입력.title, 입력.content, 입력.category, 태그, post_id),
    )
    db.commit()
    return 행을_글로(글_찾기(post_id, db))


@app.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def 글_지우기(post_id: int, db: sqlite3.Connection = Depends(연결_얻기)) -> None:
    글_찾기(post_id, db)
    db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    db.commit()
