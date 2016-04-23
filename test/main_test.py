import sys, os, pytest

sys.path.append('.')
import submit

import StringIO


# Mocking curl
#
# import urllib2
# def mock_response(req):
#     if req.get_full_url() == submit.submitt_url:
#         resp = urllib2.addinfourl(StringIO('mock file'), 'mock message', req.get_full_url())
#         resp.code = 200
#         resp.msg = 'OK'
#         return resp

# class MyHTTPHandler(urllib2.HTTPHandler):
#     def http_open(self, req):
#         print 'mock opener'
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
        login, password = submit.login_prompt('')
        assert(login == 'username')
        assert(password == 'token')

    # def test_002(self):
    #     sys.stdin = StringIO.StringIO('username\ntoken\n')
    #     submit.login_prompt('_empty')


class TestProblemSubmission:
    # tests problem selection
    def test_001(self):
        sys.stdin = StringIO.StringIO('1\n')
        submit.main(['-metadata=./test/_coursera', '-credentials=./test/_credentials'])

    # tests running a problem
    def test_002(self):
        sys.stdin = StringIO.StringIO('1\n')
        submit.main(['-override=./test/model/model.mzn', '-metadata=./test/_coursera', '-credentials=./test/_credentials'])

    # tests running a problem in record mode
    def test_003(self):
        sys.stdin = StringIO.StringIO('1\n')
        submit.main(['-override=./test/model/model.mzn', '-record_submission', '-metadata=./test/_coursera', '-credentials=./test/_credentials'])


class TestModelSubmission:
    def setup_method(self, _):
        '''Parse a real network file'''
        self.metadata = submit.load_metadata('./test/_coursera2')
        self.login, self.token = submit.login_prompt('./test/_credentials2')

    def test_001(self):
        sys.stdin = StringIO.StringIO('4\n')
        results = submit.submit(self.metadata, self.login, self.token, './test/model/model.mzn', True)
        for k,v in results.iteritems():
            assert(v['code'] == 201) #submission worked

    #model file not found
    def test_002(self):
        sys.stdin = StringIO.StringIO('4\n')
        results = submit.submit(self.metadata, self.login, self.token)
        assert(len(results) == 0)


class TestBrokenSubmission:
    def setup_method(self, _):
        self.metadata = submit.load_metadata('./test/_coursera3')
        self.login, self.token = submit.login_prompt('./test/_credentials2')

    # should throw incorrect problem parts
    def test_001(self):
        sys.stdin = StringIO.StringIO('1\n')
        results = submit.submit(self.metadata, self.login, self.token, './test/model/model.mzn', False)
        for k,v in results.iteritems():
            assert(v['code'] == 400) #submission broken

    # should throw incorrect login details
    def test_002(self):
        sys.stdin = StringIO.StringIO('1\n')
        login, token = submit.login_prompt('./test/_credentials')
        results = submit.submit(self.metadata, login, token, './test/model/model.mzn', False)
        for k,v in results.iteritems():
            assert(v['code'] == 400) #submission broken


class TestPartsPrompt:
    def test_001(self):
        sys.stdin = StringIO.StringIO('0.1\n1\n')
        submit.main(['-metadata=./test/_coursera', '-credentials=./test/_credentials'])

    def test_002(self):
        sys.stdin = StringIO.StringIO('100\n1\n')
        submit.main(['-metadata=./test/_coursera', '-credentials=./test/_credentials'])

    def test_003(self):
        sys.stdin = StringIO.StringIO('-1\n1\n')
        submit.main(['-metadata=./test/_coursera', '-credentials=./test/_credentials'])


class TestUtilFunctions:
    def test_001(self):
        sol = submit.last_solution('obj=2;\n'+submit.mzn_solution+'\nobj=1;\n'+submit.mzn_solution+'\n==========\n')
        assert(sol == ('\nobj=1;\n'+submit.mzn_solution+'\n==========\n'))

    def test_002(self):
        sol = submit.last_solution('no solution')
        assert(sol == ('no solution'))

    # def test_002(self):
    #     sys.stdin = StringIO.StringIO('username\ntoken\n')
    #     submit.login_prompt('_empty')


