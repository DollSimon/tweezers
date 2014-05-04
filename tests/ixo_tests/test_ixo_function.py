#!/usr/bin/env python
#-*- coding: utf-8 -*-

import inspect

import pytest
import sure

from tweezer.ixo.functions import build_argument_signature


def my_func(a, x=4, y=5):
    return x + y


@pytest.mark.wip
def test_argument_signature():
    A = inspect.getargspec(my_func)

    args = build_argument_signature(A)

    my_func(*args).should.equal(9)
