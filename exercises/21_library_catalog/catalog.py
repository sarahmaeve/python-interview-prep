class Book:
    """A book identified by ISBN.

    Two books with the same ISBN are considered equal.
    Books are hashable (can be used in sets and as dict keys).

    Attributes:
        isbn (str): The unique ISBN identifier.
        title (str): The book's title.
        author (str): The book's author.
    """

    def __init__(self, isbn, title, author):
        pass

    def __eq__(self, other):
        pass

    def __hash__(self):
        pass

    def __repr__(self):
        pass


class Member:
    """A library member who can check out books.

    Attributes:
        member_id (str): Unique identifier.
        name (str): The member's name.

    Properties:
        checked_out (list[Book]): Books currently checked out (returns a copy).
    """

    def __init__(self, member_id, name):
        pass

    @property
    def checked_out(self):
        """Return a copy of the list of currently checked-out books."""
        pass

    def _checkout(self, book):
        """Internal: add a book to this member's checked-out list."""
        pass

    def _return(self, book):
        """Internal: remove a book from this member's checked-out list."""
        pass

    def __repr__(self):
        pass


class Library:
    """A library that manages books and member checkouts.

    Uses composition: a Library HAS books and members.

    Methods: add_book, register_member, checkout, return_book, available_books.
    Methods return copies of internal state where appropriate.
    """

    def __init__(self):
        pass

    def add_book(self, book):
        """Add a book to the library's collection.

        Raises ValueError if a book with the same ISBN already exists.
        """
        pass

    def register_member(self, member):
        """Register a new member.

        Raises ValueError if a member with the same ID already exists.
        """
        pass

    def checkout(self, member_id, isbn):
        """Check out a book to a member.

        Raises ValueError if the book is not available or member not found.
        Returns the Book that was checked out.
        """
        pass

    def return_book(self, member_id, isbn):
        """Return a book from a member.

        Raises ValueError if the member doesn't have this book.
        """
        pass

    def available_books(self):
        """Return a list of all books not currently checked out."""
        pass
