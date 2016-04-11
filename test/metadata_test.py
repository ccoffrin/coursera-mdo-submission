import sys, os, pytest

sys.path.append('..')
import submit

class TestCorrect:
    def setup_method(self, _):
        """Parse a real network file"""
        self.meta_data = submit.load_meta_data()
        #self.case = mpdata.io.parse_mp_case_file(os.path.dirname(os.path.realpath(__file__))+'/data/correct/MP_5_1/case4gs.m')

    def test_001(self):
        assert len(self.meta_data.problem_data) == 4

    def test_002(self):
        assert len(self.meta_data.model_data) == 1


class TestBroken:
    def test_001(self):
        with pytest.raises(SystemExit):
            submit.load_meta_data('_empty')

