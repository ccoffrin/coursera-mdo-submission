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


class TestCorrect:
    # tests problem selection
    def test_001(self):
        sys.stdin = StringIO.StringIO('1\n')
        submit.main([])

    # tests running a problem
    def test_003(self):
        sys.stdin = StringIO.StringIO('1\n')
        submit.main(['-override=./model/model.mzn'])

    # tests running a problem in record mode
    def test_004(self):
        sys.stdin = StringIO.StringIO('1\n')
        submit.main(['-override=./model/model.mzn', '-record_submission'])
    

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