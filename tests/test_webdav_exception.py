import unittest
from webdav_api_client.webdav_exception import WebDavException


class TestWebDavException(unittest.TestCase):
    """
    This class contains unit tests for the `WebDavException` class.
    """
    def test_code_and_text(self):
        """
        Tests that the `code` and `text` arguments are correctly assigned to the
        `WebDavException` instance.
        """
        code = 404
        text = "Not Found"
        exception = WebDavException(code, text)
        self.assertEqual(exception.code, code)
        self.assertEqual(str(exception), f"Error {code}: {text}")


if __name__ == '__main__':
    unittest.main()
