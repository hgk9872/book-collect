# 하나의 도큐먼트 -> model
from odmantic import Model


class BookModel(Model):
    keyword: str
    publisher: str
    price: int
    image: str

    class Config:
        collection = "books"

# db fastapi-pj -> collection -> document { ~~ }
