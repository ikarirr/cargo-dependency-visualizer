import tempfile
import unittest
from pathlib import Path
from xml.sax.saxutils import escape

from src.main import load_config

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.config = {
            "package_name": "serde",
            "repository_url": "https://github.com/rust-lang/crates.io-index",
            "test_mode": "true",
            "package_version": "1.0.0",
            "output_mode": "ascii",
            "max_depth": "3"
        }

    def create_config(self, parameters):
        """Создание временного XML-файла для проверки."""

        content = "<config>\n"

        for key, value in parameters.items():
            content += f"<{key}>{escape(value)}</{key}>\n"

        content += "</config>"

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".xml",
            encoding="utf-8",
            delete=False
        ) as file:
            file.write(content)
            return Path(file.name)

    def check_config(self, parameters):
        """Загрузка тестовой конфигурации."""

        path = self.create_config(parameters)

        try:
            return load_config(path)
        finally:
            path.unlink()

    def test_valid_config(self):
        """Проверка правильной конфигурации."""

        result = self.check_config(self.config)

        self.assertEqual(result["package_name"], "serde")
        self.assertEqual(result["max_depth"], 3)
        self.assertTrue(result["test_mode"])

    def test_empty_package(self):
        """Проверка пустого названия пакета."""

        self.config["package_name"] = ""

        with self.assertRaises(ValueError):
            self.check_config(self.config)

    def test_invalid_url(self):
        """Проверка неправильного URL."""

        self.config["repository_url"] = "wrong_url"

        with self.assertRaises(ValueError):
            self.check_config(self.config)

    def test_invalid_test_mode(self):
        """Проверка режима тестирования."""

        self.config["test_mode"] = "hello"

        with self.assertRaises(ValueError):
            self.check_config(self.config)

    def test_empty_version(self):
        """Проверка пустой версии пакета."""

        self.config["package_version"] = ""

        with self.assertRaises(ValueError):
            self.check_config(self.config)

    def test_invalid_output_mode(self):
        """Проверка неправильного режима вывода."""

        self.config["output_mode"] = "wrong"

        with self.assertRaises(ValueError):
            self.check_config(self.config)

    def test_invalid_depth(self):
        """Проверка неправильной глубины."""

        self.config["max_depth"] = "abc"

        with self.assertRaises(ValueError):
            self.check_config(self.config)

    def test_negative_depth(self):
        """Проверка отрицательной глубины."""

        self.config["max_depth"] = "-5"

        with self.assertRaises(ValueError):
            self.check_config(self.config)

    def test_missing_parameter(self):
        """Проверка отсутствующего параметра."""

        del self.config["package_name"]

        with self.assertRaises(ValueError):
            self.check_config(self.config)

if __name__ == "__main__":
    unittest.main()