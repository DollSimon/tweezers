from tweezer.core.polymer import ExtensibleWormLikeChain


def test_default_values():
    wlc = ExtensibleWormLikeChain(1000)

    assert wlc.L == 1000
    assert wlc.P == 50
    assert wlc.S == 1200
    assert wlc.T == 295


def test_changing_start_values():
    wlc = ExtensibleWormLikeChain(1000, 40, 600, 300)

    assert wlc.L == 1000
    assert wlc.P == 40
    assert wlc.S == 600
    assert wlc.T == 300


def test_type_of_parameter():
    wlc = ExtensibleWormLikeChain(1000)

    assert type(wlc.L) == float
    assert type(wlc.P) == float
    assert type(wlc.S) == float
    assert type(wlc.T) == float


def test_extension_with_zero_force():
    wlc = ExtensibleWormLikeChain(1000)

    assert wlc.extension(0.000001) == 0
