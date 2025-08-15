class Book:
    def __init__(self, title: str, author: str, isbn: str):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.is_borrowed = False

    def borrow_book(self):
        if not self.is_borrowed:
            self.is_borrowed = True
            return True
        raise Exception(f"{self.title} is already borrowed.")

    def return_book(self):
        if self.is_borrowed:
            self.is_borrowed = False
            return True
        raise Exception(f"{self.title} was not borrowed.")

    def display_info(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"
