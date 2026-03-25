import math
import unittest
from shapes import Shape, Rectangle, Square, Circle


class TestRectangle(unittest.TestCase):

    def test_rectangle_area(self):
        r = Rectangle(5, 10)
        self.assertEqual(r.area(), 50)

    def test_rectangle_str(self):
        r = Rectangle(3, 4)
        self.assertEqual(str(r), "Rectangle: area=12")

    def test_rectangle_attributes(self):
        r = Rectangle(7, 3)
        self.assertEqual(r.width, 7)
        self.assertEqual(r.height, 3)


class TestSquare(unittest.TestCase):

    def test_square_area(self):
        s = Square(5)
        self.assertEqual(s.area(), 25)

    def test_square_resize(self):
        s = Square(4)
        s.resize(10)
        self.assertEqual(s.area(), 100)

    def test_square_str_after_resize(self):
        s = Square(3)
        s.resize(6)
        self.assertEqual(str(s), "Square: area=36")


class TestCircle(unittest.TestCase):

    def test_circle_area(self):
        c = Circle(5)
        self.assertAlmostEqual(c.area(), math.pi * 25)

    def test_circle_area_unit(self):
        c = Circle(1)
        self.assertAlmostEqual(c.area(), math.pi)

    def test_circle_str(self):
        c = Circle(1)
        expected = f"Circle: area={math.pi}"
        self.assertEqual(str(c), expected)


class TestShapeBase(unittest.TestCase):

    def test_base_shape_raises(self):
        s = Shape("Generic")
        with self.assertRaises(NotImplementedError):
            s.area()


if __name__ == "__main__":
    unittest.main()
