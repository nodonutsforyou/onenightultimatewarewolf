Feature: showing off behave

#  Scenario: run a simple Cop game
#     Given we start a simple cop game
#      When user 1 investigates card 1 of user 2
#      Then user 1 saw card 1 of user 2 last turn
#      When user 2 investigates card 2 of user 1
#      Then user 2 saw card 2 of user 1 last turn
#      When we play the game until it is turn of user 1
#      When user 1 arms himself and aims at enemy leader
#      When we play the game until it is turn of user 1
#      When user 1 shoots
#      Then enemy leader is wounded
#      When we play the game until it is turn of user 1
#      When user 1 arms himself and aims at enemy leader
#      When we play the game until it is turn of user 1
#      When user 1 shoots
#      Then user 1 team has won!
#
#  Scenario: check number of guns is correct (should be 3)
#     Given we start a simple cop game
#      When user 1 arms himself and aims at enemy leader
#      When user 2 arms himself and aims at enemy leader
#      When user 3 arms himself and aims at enemy leader
#      Then user 4 arms himself but there is no guns left
#
#  Scenario: check item TRUTH_SERUM
#     Given we start a cop game with user 1 having TRUTH_SERUM
#      When user 1 uses card item on user 2. Target opens card 1
#      Then everybody can see public card 1 of user 2
#
#  Scenario: check item FLASHBANG
#     Given we start a cop game with user 6 having FLASHBANG
#      When we play the game until it is turn of user 6
#      When user 6 arms himself and aims at enemy leader
#      When we play the game until it is turn of user 6
#      When user 6 uses item
#      When user 6 aims at enemy leader
#      Then everybody can not see public card 1 of user 6
#
#  Scenario: check item BLACKMAIL
#     Given we start a cop game with user non-leader having BLACKMAIL
#      When we play the game until it is turn of user non-leader
#      When user non-leader uses BLACKMAIL to gie victory to enemy leader
#      Then enemy leader is a winner

  Scenario: check item RESTRAINING_ORDER
     Given we start a cop game with user 2 having RESTRAINING_ORDER
      When user 1 arms himself and aims at enemy leader
      When user 2 uses RESTRAINING_ORDER on user 1
      Then user 1 can not target enemy leader
      When we play the game until it is turn of user 1
      When user 1 shoots
      Then user 3 is dead

#  Scenario: check item DEFIBRILLATOR
#     Given we start a cop game with user 1 having DEFIBRILLATOR
#      When user 1 arms himself and aims at enemy non-leader
#      When we play the game until it is turn of user 1
#      When user 1 shoots
#      Then user enemy non-leader is dead
#      When we play the game until it is turn of user 1
#      When user 1 uses item on user enemy non-leader
#      Then user enemy non-leader is not dead
#
#  Scenario: check item COFFEE
#     Given we start a cop game with user 1 having COFFEE
#      When user 1 uses item
#      When user 1 arms himself and aims at enemy leader
#      When user 1 shoots
#      Then enemy leader is wounded
#      When we play the game until it is turn of user 1