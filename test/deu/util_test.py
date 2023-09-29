import unittest

from click.testing import CliRunner

from deu.util import deu


class UtilTestSuite(unittest.TestCase):
    def test_util_cred_add(self):
        runner = CliRunner()
        result = runner.invoke(deu, ['cred', 'list'])




if __name__ == '__main__':
    unittest.main()