import sys, os, pytest

sys.path.append('..')
import submit

class TestCorrect:
    def setup_method(self, _):
        """Parse a real network file"""
        self.meta_data = submit.load_meta_data('_coursera2')

    def test_001(self):
        assert len(self.meta_data.problem_data) == 4

    def test_002(self):
        assert len(self.meta_data.model_data) == 1


class TestBroken:
    def test_001(self):
        with pytest.raises(SystemExit):
            submit.load_meta_data('_empty')

