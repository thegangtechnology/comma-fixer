import itertools
from io import StringIO

from comma_fixer.fixer import create_chunks


class TestChunking:
    test_string = (
        "a\nb\nc\nd\ne\nf\ng\nh\ni\nj\nk\nl\nm\nn\no\np\nq\nr\ns\nt\nu\nv\nw\nx\ny\nz"
    )

    def test_chunk(self):
        res = create_chunks(StringIO(self.test_string), 1, False)
        exp = self.test_string.split("\n")
        for res_val, exp_val in zip(res, exp):
            assert res_val.read() == exp_val

    def test_chunk_size_2(self):
        res = create_chunks(StringIO(self.test_string), 2, False)
        exp = itertools.batched(self.test_string.split("\n"), n=2)
        for res_val, exp_val in zip(res, exp):
            assert res_val.read() == "\n".join(exp_val)

    def test_chunk_size_3(self):
        res = create_chunks(StringIO(self.test_string), 3, False)
        exp = itertools.batched(self.test_string.split("\n"), n=3)
        for res_val, exp_val in zip(res, exp):
            assert res_val.read() == "\n".join(exp_val)

    def test_chunk_size_4(self):
        res = create_chunks(StringIO(self.test_string), 4, False)
        exp = itertools.batched(self.test_string.split("\n"), n=4)
        for res_val, exp_val in zip(res, exp):
            assert res_val.read() == "\n".join(exp_val)

    def test_chunk_size_26(self):
        res = create_chunks(StringIO(self.test_string), 26, False)
        exp = itertools.batched(self.test_string.split("\n"), n=26)
        for res_val, exp_val in zip(res, exp):
            assert res_val.read() == "\n".join(exp_val)

    def test_chunk_size_larger_than_stream(self):
        res = create_chunks(StringIO(self.test_string), 30, False)
        exp = itertools.batched(self.test_string.split("\n"), n=30)
        for res_val, exp_val in zip(res, exp):
            assert res_val.read() == "\n".join(exp_val)
