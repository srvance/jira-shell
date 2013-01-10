Feature: List critial information about a specific issue
         In order that I can view critical information about an issue
         As a user
         I want a command to list critical data for a specific issue

    Scenario: A user lists critical data for a specific issue
        Given I have the following issues in the release
        | key  | title | status | type |
        | NG-1 | Foo1  | 1      | 1    |
        | NG-2 | Bar2  | 2      | 72   |
        | NG-3 | Baz3  | 3      | 78   |
        When I enter the command "stat NG-2"
        Then I see critical data for the specific issue
        | key  | title | status | type |
        | NG-2 | Bar2  | 2      | 72   |

    Scenario: A user enters only the numeric portion of an issue id
        Given I have the following issues in the release
        | key  | title | status | type |
        | NG-1 | Foo1  | 1      | 1    |
        | NG-2 | Bar2  | 2      | 72   |
        | NG-3 | Baz3  | 3      | 78   |
        When I enter the command "stat 2"
        Then I see critical data for the specific issue
        | key  | title | status | type |
        | NG-2 | Bar2  | 2      | 72   |