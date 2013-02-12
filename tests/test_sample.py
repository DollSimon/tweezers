import sure

def func(x):
    return x + 1


def test_answer():
    assert func(4) == 5
    (4).should.be.within(2, 7)

