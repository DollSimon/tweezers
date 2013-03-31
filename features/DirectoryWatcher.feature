Feature: Directory watcher
  In order to analyse the experimental data automatically
  As a manual user or as a robot
  I want a way to watch directories for newly saved files and perform actions accordingly.

  @wip
  Scenario: Detect changes in data directory
    Given a data directory is watched by the Directory Watcher
    When a file is added or changed or deleted
    Then the directory watcher notifies us about the change
    And detects which file class has changed
  
  
  
