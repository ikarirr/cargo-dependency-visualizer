import unittest

from src.reverse_dependencies import get_reverse_dependencies

class TestReverseDependencies(unittest.TestCase):

    def test_direct_dependencies(self):
        """Проверка прямых обратных зависимостей."""

        graph = {
            "A": ["B"],
            "B": [],
            "C": ["B"]
        }

        result = get_reverse_dependencies(graph, "B")

        self.assertEqual(result, ["A", "C"])

    def test_transitive_dependencies(self):
        """Проверка транзитивных обратных зависимостей."""

        graph = {
            "A": ["B"],
            "B": ["C"],
            "C": []
        }

        result = get_reverse_dependencies(graph, "C")

        self.assertEqual(result, ["A", "B"])

    def test_no_dependencies(self):
        """Проверка пакета без обратных зависимостей."""

        graph = {
            "A": ["B"],
            "B": []
        }

        result = get_reverse_dependencies(graph, "A")

        self.assertEqual(result, [])

    def test_cyclic_dependencies(self):
        """Проверка циклических зависимостей."""

        graph = {
            "A": ["B"],
            "B": ["C"],
            "C": ["A"]
        }

        result = get_reverse_dependencies(graph, "A")

        self.assertEqual(result, ["B", "C"])

    def test_unknown_package(self):
        """Проверка отсутствующего пакета."""

        graph = {
            "A": ["B"],
            "B": []
        }

        with self.assertRaises(ValueError):
            get_reverse_dependencies(graph, "X")

if __name__ == "__main__":
    unittest.main()