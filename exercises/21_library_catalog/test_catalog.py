import unittest
from catalog import Book, Member, Library


class TestBook(unittest.TestCase):

    def test_books_with_same_isbn_are_equal(self):
        """Two Book instances with the same ISBN should be equal."""
        # TODO: create two books with the same ISBN but different titles
        # assert they are equal
        self.fail("not implemented")

    def test_books_are_hashable(self):
        """Books should work in sets and as dict keys."""
        # TODO: create books, add to a set, verify deduplication by ISBN
        self.fail("not implemented")

    def test_repr_contains_isbn_and_title(self):
        """repr(book) should contain the ISBN and title."""
        # TODO
        self.fail("not implemented")


class TestMember(unittest.TestCase):

    def test_checked_out_returns_copy(self):
        """Modifying the returned list should not affect the member's state."""
        # TODO: get checked_out, modify it, verify member is unchanged
        self.fail("not implemented")


class TestLibrary(unittest.TestCase):

    def test_checkout_and_return(self):
        """Check out a book, verify it's unavailable, return it, verify it's available."""
        # TODO
        self.fail("not implemented")

    def test_checkout_unavailable_raises(self):
        """Checking out an already-checked-out book should raise ValueError."""
        # TODO
        self.fail("not implemented")

    def test_available_books_excludes_checked_out(self):
        """available_books should not include books that are checked out."""
        # TODO
        self.fail("not implemented")

    def test_duplicate_isbn_raises(self):
        """Adding a book with a duplicate ISBN should raise ValueError."""
        # TODO
        self.fail("not implemented")


if __name__ == "__main__":
    unittest.main()
