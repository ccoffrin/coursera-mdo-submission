import sys, os, pytest

sys.path.append('..')
import submit

import StringIO

class TestCorrect:
    # tests problem selection
    def test_001(self):
        sys.stdin = StringIO.StringIO('1\n')
        submit.main([])

    # tests model selection
    def test_002(self):
        sys.stdin = StringIO.StringIO('5\n')
        submit.main([])

#    # tests model selection
#    def test_003(self):
#        sys.stdin = StringIO.StringIO('\n\n')
#        submit.main([])


class TestLogin:
    def test_001(self):
        sys.stdin = StringIO.StringIO('username\ntoken\n')
        submit.login_prompt('')

    # def test_002(self):
    #     sys.stdin = StringIO.StringIO('username\ntoken\n')
    #     submit.login_prompt('_empty')


class TestPartsPrompt:
    def test_001(self):
        sys.stdin = StringIO.StringIO('0.1\n1\n')
        submit.main([])

    def test_002(self):
        sys.stdin = StringIO.StringIO('100\n1\n')
        submit.main([])

    def test_003(self):
        sys.stdin = StringIO.StringIO('-1\n1\n')
        submit.main([])



# class TestBroken:
#     def test_001(self):
#         with pytest.raises(SystemExit):
#             submit.load_meta_data('_broken')