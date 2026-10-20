import unittest

from src.graph import build_graph

class TestGraph(unittest.TestCase):

    def setUp(self):
        """Подготовка тестовых данных."""

        self.dependencies = {
            "serde": ["serde_derive"],
            "serde_derive": ["syn", "quote"],
            "syn": [],
            "quote": []
        }

    def mock_get_dependencies(
        self,
        package_name,
        version,
        repository_url
    ):
        """Имитация получения зависимостей."""

        return self.dependencies.get(package_name, [])

    def test_depth_zero(self):
        """Проверка нулевой глубины."""

        graph = build_graph(
            "serde",
            "1.0.0",
            "https://crates.io",
            0,
            self.mock_get_dependencies
        )

        self.assertEqual(graph, {"serde": []})

    def test_depth_one(self):
        """Проверка глубины 1."""

        graph = build_graph(
            "serde",
            "1.0.0",
            "https://crates.io",
            1,
            self.mock_get_dependencies
        )

        self.assertEqual(
            graph,
            {
                "serde": ["serde_derive"],
                "serde_derive": []
            }
        )

    def test_depth_two(self):
        """Проверка глубины 2."""

        graph = build_graph(
            "serde",
            "1.0.0",
            "https://crates.io",
            2,
            self.mock_get_dependencies
        )

        self.assertEqual(
            graph,
            {
                "serde": ["serde_derive"],
                "serde_derive": ["syn", "quote"],
                "syn": [],
                "quote": []
            }
        )

    def test_invalid_depth(self):
        """Проверка отрицательной глубины."""

        with self.assertRaises(ValueError):
            build_graph(
                "serde",
                "1.0.0",
                "https://crates.io",
                -1,
                self.mock_get_dependencies
            )

if __name__ == "__main__":
    unittest.main()