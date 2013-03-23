from nose.tools import *
import tweezer
import sure

class TestRackoon:
    """
    TestRackoon covers:
    ===================

    * user can build a new house
    """

    def test_is_4_a_number(self):
        
        (4).shouldnot.equal(5) 
        (4).should.equal(4) 

    def test_5_is_new(self):
        [].should.be.empty

    def test_6_is_new(self):
        [4, 3, 2].should.be.empty
        

        
        
        


