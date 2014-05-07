from behave import *
import sure

from tweezer.geom import Point


@given('I create a Point with coordinates 1, 2, and 3')
def step_impl(context):
    p = Point(1, 2, 3)
    context.point = p
    (p.x).should.be(1)
    (p.y).should.be(2)
    (p.z).should.be(3)


@when('I try to display it')
def step_impl(context):
    pass


@then('I will see a 3D image of the point')
def step_impl(context):
    pass

