from behave import *
import sure

from tweezer.core.polymer import ExtensibleWormLikeChain

# Scenario: Basic calculations
@given(u'an instance of the ExtensibleWormLikeChain class')
def impl(context):
    context.xwlc = ExtensibleWormLikeChain(contour_length = 1000)

@given(u'that the persistence length is 50 nm')
def impl(context):
    (context.xwlc.P).should.be(50)

@given(u'that the stretch modulus is 1200 pN')
def impl(context):
    (context.xwlc.S).should.be(1200)

@given(u'that the temperature is 295 K')
def impl(context):
    (context.xwlc.T).should.be(295)

@given(u'that the contour length of the DNA is 1000 nm')
def impl(context):
    (context.xwlc.L).should.be(1000)

@when(u'the instance is called like a function with a force value of 2')
def impl(context):
    context.extension = context.xwlc(2)

@then(u'you will obtain an extension of 1000')
def impl(context):
    print(context.extension)
    context.extension.should.be(10000)
    assert False

# Scenario: call weired values
@given(u'a default instance of the ExtensibleWormLikeChain class')
def impl(context):
    context.xwlc = ExtensibleWormLikeChain(contour_length = 1000)

@when(u'we call it with a force of "Rocket"')
def impl(context):
    context.force = "Rocket"

@then(u'we raise a ValueError')
def impl(context):
    xwlc = ExtensibleWormLikeChain(contour_length = 1000)
    xwlc.when.called_with(context.force).should.throw(ValueError)
