from behave import *
from tweezer.io.fio import newio

@given('we have behave installed')
def step(context):
    pass

@when('we run newio with 4')
def step(context):
    assert 4 == 4

@then('we get a result of 4')
def step(context):
    assert newio(4) == 4

