Feature: Creating basic geometric elements
  In order to visualise the a dual trap tweezer
  As a user and developer
  I want to be able to create basic geometric elements and to display them

Scenario: create and display a Point
  Given I create a Point with coordinates 1, 2, and 3
  When I try to display it 
  Then I will see a 3D image of the point 




