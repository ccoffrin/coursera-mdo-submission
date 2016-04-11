import sys, os, pytest

sys.path.append('..')
import submit

import StringIO


# Mocking curl
#
# import urllib2
# def mock_response(req):
#     if req.get_full_url() == submit.submitt_url:
#         resp = urllib2.addinfourl(StringIO("mock file"), "mock message", req.get_full_url())
#         resp.code = 200
#         resp.msg = "OK"
#         return resp

# class MyHTTPHandler(urllib2.HTTPHandler):
#     def http_open(self, req):
#         print "mock opener"
#         return mock_response(req)

# my_opener = urllib2.build_opener(MyHTTPHandler)
# urllib2.install_opener(my_opener)

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


class TestProblemSubmission:
    # tests problem selection
    def test_001(self):
        sys.stdin = StringIO.StringIO('1\n')
        submit.main([])

    # tests running a problem
    def test_002(self):
        sys.stdin = StringIO.StringIO('1\n')
        submit.main(['-override=./model/model.mzn'])

    # tests running a problem in record mode
    def test_003(self):
        sys.stdin = StringIO.StringIO('1\n')
        submit.main(['-override=./model/model.mzn', '-record_submission'])


class TestModelSubmission:
    def setup_method(self, _):
        """Parse a real network file"""
        self.metadata = submit.load_metadata('_coursera2')
        self.login, self.token = submit.login_prompt('_credentials2')

    def test_001(self):
        sys.stdin = StringIO.StringIO('4\n')
        submit.submit(self.metadata, self.login, self.token, './model/model.mzn', True)


class TestBrokenSubmission:
    def setup_method(self, _):
        self.metadata = submit.load_metadata('_coursera3')
        self.login, self.token = submit.login_prompt('_credentials2')

    # should throw incorrect problem parts
    def test_001(self):
        sys.stdin = StringIO.StringIO('1\n')
        submit.submit(self.metadata, self.login, self.token, './model/model.mzn', False)

    # should throw incorrect login details
    def test_002(self):
        sys.stdin = StringIO.StringIO('1\n')
        login, token = submit.login_prompt()
        submit.submit(self.metadata, login, token, './model/model.mzn', False)


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

