from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
app = FastAPI()


# Task 1
@app.get("/")
def welcome():
    return {"message": "Welcome to City Public Library"}


# Task 2
books = [
    {"id": 1, "title": "The Alchemist", "author": "Paulo Coelho", "genre": "Fiction", "is_available": True},
    {"id": 2, "title": "Ikigai", "author": "Hector Garcia & Francesc Miralles", "genre": "Philosophy", "is_available": True},
    {"id": 3, "title": "White Nights", "author": "Fyodor Dostoevsky", "genre": "Fiction", "is_available": False},
    {"id": 4, "title": "Shelley: The Pursuit", "author": "Richard Holmes", "genre": "Biography", "is_available": False},
    {"id": 5, "title": "No Longer Human", "author": "Osamu Dazai", "genre": "Fiction", "is_available": True},
    {"id": 6, "title": "The World Is What It Is", "author": "Patrick French", "genre": "Biography", "is_available": True}
]

borrow_records = []
record_counter = 1
queue = []

def find_book(book_id):
    for book in books:
        if book["id"] == book_id:
            return book
    return None

def calculate_due_date(days, premium):
    if not premium and days > 30:
        return {"error": "Regular members cannot borrow more than 30 days"}
    if premium and days > 60:
        return {"error": "Premium members cannot borrow more than 60 days"}
    return f"Return by: Day {days}"


# Task 3
@app.get("/books")
def get_books():
    available_count = sum(1 for b in books if b["is_available"])
    return {
        "total": len(books),
        "available_count": available_count,
        "books": books
    }


# Task 16
@app.get("/books/search")
def search_books(keyword: str):
    keyword = keyword.lower()
    results = [
        b for b in books
        if keyword in b["title"].lower()
        or keyword in b["author"].lower()
    ]
    return {
        "keyword": keyword,
        "total_found": len(results),
        "results": results
    }


# Task 17
@app.get("/books/sort")
def sort_books(sort_by: str = "title", order: str = "asc"):
    allowed = ["title", "author", "genre"]
    if sort_by.lower() not in allowed:
        return {"error": "Invalid sort_by"}
    if order.lower() not in ["asc", "desc"]:
        return {"error": "Invalid order"}
    reverse = order.lower() == "desc"

    sorted_books = sorted(
        books,
        key=lambda b: b[sort_by.lower()].lower(),
        reverse=reverse
    )
    return {
        "sort_by": sort_by,
        "order": order,
        "books": sorted_books
    }


# Task 18
@app.get("/books/page")
def paginate_books(page: int = 1, limit: int = 3):
    total = len(books)
    total_pages = (total + limit - 1) // limit
    start = (page - 1) * limit
    end = start + limit
    return {
        "total": total,
        "total_pages": total_pages,
        "page": page,
        "limit": limit,
        "books": books[start:end]
    }


# Task 10
@app.get("/books/filter")
def filter_books(
    genre: Optional[str] = None,
    author: Optional[str] = None,
    is_available: Optional[bool] = None
):
    filtered = books
    if genre:
        filtered = [b for b in filtered if b["genre"].lower() == genre.lower()]
    if author:
        filtered = [b for b in filtered if author.lower() in b["author"].lower()]
    if is_available is not None:
        filtered = [b for b in filtered if b["is_available"] == is_available]
    return {
        "count": len(filtered),
        "books": filtered
    }


# Task 20
@app.get("/books/browse")
def browse_books(
    keyword: Optional[str] = None,
    sort_by: str = "title",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    results = books
    if keyword:
        keyword = keyword.lower()
        results = [
            b for b in results
            if keyword in b["title"].lower()
            or keyword in b["author"].lower()
        ]
    allowed = ["title", "author", "genre"]
    if sort_by.lower() not in allowed:
        return {"error": "Invalid sort_by"}
    if order.lower() not in ["asc", "desc"]:
        return {"error": "Invalid order"}
    reverse = order.lower() == "desc"
    results = sorted(
        results,
        key=lambda b: b[sort_by.lower()].lower(),
        reverse=reverse
    )
    total = len(results)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit
    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_results": total,
        "total_pages": total_pages,
        "books": results[start:end]
    }


# Task 5
@app.get("/books/summary")
def books_summary():
    total = len(books)
    available = sum(1 for b in books if b["is_available"])
    genres = {}
    for b in books:
        g = b["genre"]
        genres[g] = genres.get(g, 0) + 1
    return {
        "total_books": total,
        "available_books": available,
        "borrowed_books": total - available,
        "genre_breakdown": genres
    }


# Task 11
class NewBook(BaseModel):
    title: str = Field(..., min_length=2)
    author: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    is_available: bool = True

@app.post("/books", status_code=201)
def add_book(book: NewBook):
    for b in books:
        if b["title"].lower() == book.title.lower():
            return {"error": "Book already exists"}
    new_id = max(b["id"] for b in books) + 1
    new_book = {
        "id": new_id,
        "title": book.title,
        "author": book.author,
        "genre": book.genre,
        "is_available": book.is_available
    }
    books.append(new_book)
    return new_book


# Task 12
@app.put("/books/{book_id}")
def update_book(book_id: int, genre: Optional[str] = None, is_available: Optional[bool] = None):
    book = find_book(book_id)
    if not book:
        return {"error": "Book not found"}
    if genre:
        book["genre"] = genre
    if is_available is not None:
        book["is_available"] = is_available
    return book


# Task 13
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    book = find_book(book_id)
    if not book:
        return {"error": "Book not found"}
    books.remove(book)
    return {"message": f"Book '{book['title']}' deleted successfully"}


# Task 6
class BorrowRequest(BaseModel):
    member_name: str
    book_id: int
    borrow_days: int
    member_id: str
    is_premium: bool = False


# Task 8
@app.post("/borrow")
def borrow_book(request: BorrowRequest):
    global record_counter
    book = find_book(request.book_id)
    if not book:
        return {"error": "Book not found"}
    if not book["is_available"]:
        return {"error": "Book unavailable"}
    due = calculate_due_date(request.borrow_days, request.is_premium)
    if isinstance(due, dict):
        return due
    book["is_available"] = False
    record = {
        "record_id": record_counter,
        "member_name": request.member_name,
        "member_id": request.member_id,
        "is_premium": request.is_premium,
        "book_id": request.book_id,
        "borrow_days": request.borrow_days,
        "due_date": due
    }
    borrow_records.append(record)
    record_counter += 1
    return {"message": "Book borrowed", "record": record}


# Task 14
@app.post("/queue/add")
def add_to_queue(member_name: str, book_id: int):
    book = find_book(book_id)
    if not book:
        return {"error": "Book not found"}
    if book["is_available"]:
        return {"error": "Book is available"}
    entry = {"member_name": member_name, "book_id": book_id}
    queue.append(entry)
    return {"message": "Added to queue", "queue_entry": entry}

@app.get("/queue")
def get_queue():
    return {"total_waiting": len(queue), "queue": queue}


# Task 15
@app.post("/return/{book_id}")
def return_book(book_id: int):
    global record_counter
    book = find_book(book_id)
    if not book:
        return {"error": "Book not found"}
    book["is_available"] = True
    for person in queue:
        if person["book_id"] == book_id:
            queue.remove(person)
            record = {
                "record_id": record_counter,
                "member_name": person["member_name"],
                "member_id": "QUEUE",
                "is_premium": False,
                "book_id": book_id,
                "borrow_days": 15,
                "due_date": "Return by: Day 15"
            }
            borrow_records.append(record)
            record_counter += 1
            book["is_available"] = False
            return {"message": "Book returned and reassigned"}
    return {"message": "Book returned and available"}


# Task 4
@app.get("/borrow-records")
def get_borrow_records():
    return {"total": len(borrow_records), "records": borrow_records}


# Task 19
@app.get("/borrow-records/search")
def search_borrow_records(member_name: str):
    keyword = member_name.lower()
    results = [
        r for r in borrow_records
        if keyword in r["member_name"].lower()
    ]
    return {
        "member_name": member_name,
        "total_found": len(results),
        "records": results
    }

@app.get("/borrow-records/page")
def paginate_records(page: int = 1, limit: int = 3):
    total = len(borrow_records)
    total_pages = (total + limit - 1) // limit
    start = (page - 1) * limit
    end = start + limit
    return {
        "total": total,
        "total_pages": total_pages,
        "page": page,
        "limit": limit,
        "records": borrow_records[start:end]
    }


# Task 3
@app.get("/books/{book_id}")
def get_book(book_id: int):
    book = find_book(book_id)
    if book:
        return book
    return {"error": "Book not found"}