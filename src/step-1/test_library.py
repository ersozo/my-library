import pytest
from library     import Book


def test_book_create():
    book = Book("1984", "George Orwell", "1234567890")
    assert book.title == "1984"
    assert book.author == "George Orwell"
    assert book.isbn == "1234567890"


def test_book_borrow():
    book = Book("1984", "George Orwell", "1234567890")
    assert book.borrow_book() == True
    assert book.is_borrowed == True

    with pytest.raises(Exception):
        book.borrow_book()


def test_book_return():
    book = Book("1984", "George Orwell", "1234567890")
    book.borrow_book()
    assert book.return_book() == True
    assert book.is_borrowed == False

    with pytest.raises(Exception):
        book.return_book()
