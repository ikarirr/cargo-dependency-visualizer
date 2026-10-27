import unittest

from src.dependencies import get_dependencies


class TestDependencies(unittest.TestCase):

    def test_valid_dependencies(self):
        """Проверка успешного получения зависимостей."""

        result = get_dependencies(
            "serde",
            "1.0.0",
            "https://crates.io"
        )

        self.assertIsInstance(result, list)

        self.assertIn("serde_derive", result)


if __name__ == "__main__":
    unittest.main()
