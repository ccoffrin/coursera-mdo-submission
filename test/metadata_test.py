import sys, os, pytest

sys.path.append('.')
import submit

class TestCorrect:
    def setup_method(self, _):
        self.meta_data = submit.load_metadata('./test/_coursera2')

    def test_001(self):
        assert len(self.meta_data.problem_data) == 3

    def test_002(self):
        assert len(self.meta_data.model_data) == 1


class TestBroken:
    # file not found
    def test_001(self):
        with pytest.raises(SystemExit):
            submit.load_metadata('./test/_missing')

    # bad meta data format
    def test_002(self):
        with pytest.raises(SystemExit):
            submit.load_metadata('./test/_empty')

