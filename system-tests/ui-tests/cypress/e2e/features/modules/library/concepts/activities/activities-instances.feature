@REQ_ID:1070683
Feature: Library - Activities Instances

    As a user, I want to manage every Activity Instances in the Concepts Library
    Background: User must be logged in
        Given The user is logged in

    Scenario: User must be able to navigate to the Activities Instances page
        Given The '/library' page is opened
        When The 'Activities' submenu is clicked in the 'Concepts' section
        And The 'Activity Instances' tab is selected
        Then The current URL is '/library/activities/activity-instances'

    Scenario: User must be able to see the columns list on the main page as below
        Given The '/library/activities/activity-instances' page is opened
        Then A table is visible with following options
            | options                                                         |
            | Add activity instance                                           |
            | Filters                                                         |
            | Columns                                                         |
            | Export                                                          |
            | Show version history                                            |
            | Add select boxes to table to allow selection of rows for export |
            | search-field                                                    |
            
        And A table is visible with following headers
            | headers                       |
            | Library                       |
            | Activity instance class       |
            | Activity                      |
            | Activity Instance             |
            | Definition                    |
            | NCI Concept ID                |
            | NCI Concept Name              |
            | Research Lab                  |
            | Molecular Weight              |
            | Topic code                    |
            | ADaM parameter code           |
            | Required for activity         |
            | Default selected for activity |
            | Data sharing                  |
            | Legacy usage                  |
            | Modified                      |
            | Modified by                   |
            | Status                        |
            | Version                       |

    Scenario: User must be able to select visibility of columns in the table 
        Given The '/library/activities/activity-instances' page is opened
        When The first column is selected from Select Columns option for table with actions
        Then The table contain only selected column and actions column

    Scenario: User must be able to add a new Activity Instance
        Given The '/library/activities/activity-instances' page is opened
        When The Add Activity Instance button is clicked
        And The activity instance data is filled in and saved
        And The newly added Activity Instance item is added in the table by default

    Scenario: User must not be able to continue Step 1 of new activity instance without mandatory fields of 'Activity' selection
        Given The '/library/activities/activity-instances' page is opened
        When The Add Activity Instance button is clicked
        And Activity selection is not made
        Then The user is not able to continue
        And The message is displayed as 'This field is required' in the Activity field
        When Activity selected but Activity group does not select
        Then The user is not able to continue
        And The pop up displays 'You need to choose at least one Activity Grouping'

    Scenario: User must not be able to continue Step 2 of new activity Instance without mandatory fields of 'Activity instance class'
        Given The '/library/activities/activity-instances' page is opened
        When The Add Activity Instance button is clicked
        And The Activity instance class does not select any data
        Then The user is not able to continue
        And The message is displayed as 'This field is required' in the class field

    Scenario: User must not be able to save the fom of new activity instance without mandatory fields of 'Activity instance name', 'Sentence case name', 'Definition' and 'Topic code'
        Given The '/library/activities/activity-instances' page is opened
        When The Add Activity Instance button is clicked
        And The Activity instance name, Sentence case name, Definition and Topic code fields are not filled with data
        Then The message of "This field is required" displayed in all the above mandatory fields
        And The form is not closed

    Scenario: System must default value for 'Sentence case name' to lower case value of 'Activity instance name'
        Given The '/library/activities/activity-instances' page is opened
        When The user is editing an activity instance
        And The user enters a value for Activity instance name
        Then The field for Sentence case name will be defaulted to the lower case value of the Activity instance name

    Scenario: System must ensure value of 'Sentence case name' independent of case is identical to the value of 'Activity instance name'
        Given The '/library/activities/activity-instances' page is opened
        When The user is editing an activity instance
        And The user define a value for Sentence case name and it is not identical to the value of Activity instance name
        Then The user is not able to save
        And The message is displayed as 'Sentence case name value must be identical to name value' in the Sentence case name field

    Scenario: User must be able to add a new version for the approved Activity Instance
        Given The '/library/activities/activity-instances' page is opened
        And The test Activity Instance item exists with a status as Final
        When The 'New version' option is clicked from the three dot menu list
        Then The activity instance has status 'Draft' and version '1.1'

    Scenario: User must be able to inactivate the approved version of the Activity Instance
        Given The '/library/activities/activity-instances' page is opened
        And The test Activity Instance item exists with a status as Final
        When The 'Inactivate' option is clicked from the three dot menu list
        Then The activity instance has status 'Retired' and version '1.0'

    Scenario: User must be able to reactivate the inactivated version of the Activity Instance
        Given The '/library/activities/activity-instances' page is opened
        And The test Activity Instance item exists with a status as Retired
        When The 'Reactivate' option is clicked from the three dot menu list
        Then The activity instance has status 'Final' and version '1.0'

    Scenario: User must be able to edit the drafted version of the Activity Instance
        Given The '/library/activities/activity-instances' page is opened
        And The test Activity Instance item exists with a status as Draft
        When The 'Edit' option is clicked from the three dot menu list
        Then The activity instance is edited
        And The activity instance has status 'Draft' and version '0.2'

    Scenario: User must be able to edit and approve new version of Activity Instance
        Given The '/library/activities/activity-instances' page is opened
        And The test Activity Instance item exists with a status as Final
        When The 'New version' option is clicked from the three dot menu list
        Then The activity instance has status 'Draft' and version '1.1'
        When The 'Edit' option is clicked from the three dot menu list
        And The activity instance is edited
        Then The activity instance has status 'Draft' and version '1.2'
        When The 'Approve' option is clicked from the three dot menu list
        Then The activity instance has status 'Final' and version '2.0'

    Scenario: User must be able to Approve the drafted version of the Activity Instance
        Given The '/library/activities/activity-instances' page is opened
        And The test Activity Instance item exists with a status as Draft
        When The 'Approve' option is clicked from the three dot menu list
        Then The activity instance has status 'Final' and version '1.0'

    Scenario: User must be able to Delete the intial created version of the activity Instance
        Given The '/library/activities/activity-instances' page is opened
        And The test Activity Instance item exists with a status as Draft
        When The 'Delete' option is clicked from the three dot menu list
        Then The activity instance is no longer available

    Scenario: User must be able to Cancel creation of the activity instance
        Given The '/library/activities/activity-instances' page is opened
        And The activity instance form is filled with data
        When Fullscreen wizard is closed by clicking cancel button
        And Cancelation is confirmed by clicking continue
        Then The form is no longer available
        And The activity instance is not created

    Scenario: User must be able to Cancel edition of the activity instance
        Given The '/library/activities/activity-instances' page is opened
        And The test Activity Instance item exists with a status as Draft
        When The 'Edit' option is clicked from the three dot menu list
        When The activity instance edition form is filled with data
        And Fullscreen wizard is closed by clicking cancel button
        And Cancelation is confirmed by clicking continue
        Then The form is no longer available
        And The activity instance is not edited

    Scenario: User must only have access to aprove, edit, delete, history actions for Drafted version of the activity instance
        Given The '/library/activities/activity-instances' page is opened
        And The test Activity Instance item exists with a status as Draft
        Then The item actions button is clicked
        Then Only actions that should be avaiable for the Draft item are displayed

    Scenario: User must only have access to new version, inactivate, history actions for Final version of the activity instance
        Given The '/library/activities/activity-instances' page is opened
        And The test Activity Instance item exists with a status as Final
        Then The item actions button is clicked
        Then Only actions that should be avaiable for the Final item are displayed

    Scenario: User must only have access to reactivate, history actions for Retired version of the activity instance
        Given The '/library/activities/activity-instances' page is opened
        And The test Activity Instance item exists with a status as Retired
        Then The item actions button is clicked
        Then Only actions that should be avaiable for the Retired item are displayed

    Scenario: User must be able to search created activity instance
        Given The '/library/activities/activity-instances' page is opened
        When First activity instance for search test is created
        And Second activity instance for search test is created
        Then One activity instance is found after performing full name search
        And More than one item is found after performing partial name search 

    Scenario: User must be able to search not existing group and table will correctly filtered
        Given The '/library/activities/activity-instances' page is opened
        When The not existing item is searched for
        Then The item is not found and table is correctly filtered

    Scenario: User must be able to combine search and filters to narrow table results
        Given The '/library/activities/activity-instances' page is opened
        When The user filters table by status 'Final'
        And The existing item in status Draft is searched for
        And The item is not found and table is correctly filtered
        And The user changes status filter value to 'Draft'
        Then More than one item is found after performing partial name search

    Scenario Outline: User must be able to filter the table by text fields
        Given The '/library/activities/activity-instances' page is opened
        When The user filters field '<name>'
        Then The table is filtered correctly

        Examples:
        | name                          |
        | Activity                      |
        | Activity Instance             |
        | Topic code                    |
        | Legacy usage                  |
        | Status                        |