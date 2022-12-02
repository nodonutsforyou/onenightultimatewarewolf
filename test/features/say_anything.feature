Feature: showing off behave

  Scenario: run a simple opinion game
     Given we start a simple opinion game
      When user 1 picks any question
      When everybody sends some answers
      Then user 1 can see answers list
      When user 1 votes for answer 2
      When user 2 votes for answer 2
      When user 2 votes for answer 2
      When all other users except 1 2 vote for answer 3
      When all other users except 1 2 vote for answer 4
      Then user 2 gets score 3