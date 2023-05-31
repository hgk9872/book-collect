from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.models import mongodb
from app.models.book import BookModel
from app.book_scraper import NaverBookScraper

# 절대 경로 지정
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # book = BookModel(keyword="파이썬", publisher='BJpublic', price=12000, image='me.png') # 테스트용 data
    # print(await mongodb.engine.save(book))
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "프로젝트 책방"})


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str):
    # 1. 쿼리에서 검색어 추출
    keyword = q

    # 예외처리
    if not keyword:
        return templates.TemplateResponse(
            "index.html",
            {'request': request, 'title': '프로젝트 책방'},
        )

    if await mongodb.engine.find_one(BookModel, BookModel.keyword == keyword):
        books = await mongodb.engine.find(BookModel, BookModel.keyword == keyword)
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "title": "프로젝트 책방", "books": books})

    # 2. 데이터 수집
    # 인스턴스 생성
    naver_book_scaraper = NaverBookScraper()
    books = await naver_book_scaraper.search(keyword, 2)
    book_models = []
    for book in books:
        book_model = BookModel(
            keyword=keyword,
            publisher=book['publisher'],
            price=book['discount'],
            image=book['image'],
        )
        book_models.append(book_model)

    # 3. DB에 수집된 데이터를 저장
    await mongodb.engine.save_all(book_models)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "프로젝트 책방", "books": books})


# 이벤트 등록
@app.on_event("startup")
def on_app_start():
    mongodb.connect()


@app.on_event("shutdown")
async def on_app_shutdown():
    print("down")
    mongodb.close()
