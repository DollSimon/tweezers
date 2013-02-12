Feature: Implementation of the Extensible Worm Like Chain
    
    Scenario: Basic calculations

        Given an instance of the ExtensibleWormLikeChain class
        And that the persistence length is 50 nm
        And that the stretch modulus is 1200 pN 
        And that the temperature is 295 K
        And that the contour length of the DNA is 1000 nm
        When the instance is called like a function with a force value of 2
        Then you will obtain an extension of 1000 

    Scenario: call weired values

        Given a default instance of the ExtensibleWormLikeChain class
        When we call it with a force of "Rocket"
        Then we raise a ValueError
