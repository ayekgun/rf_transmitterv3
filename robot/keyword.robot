*** Keywords ***
Transmitter
    [Arguments]       ${type}     ${no_test}
    SetConfigDynamic        ${TransmitterName}
    Run Keyword If   '${type}' == 'T818'     Transmitter ReDirect      ${type}     ${no_test}
    ...    ELSE IF   '${type}' == 'T623'    Transmitter ReDirect      ${type}     ${no_test}
    ...    ELSE       Transmitter Direct      ${type}     ${no_test}
    # ClearVariable

Transmitter Sleep Mode
    [Arguments]       ${type}     ${no_test}
    Run Keyword If   '${type}' == 'T818'     Transmitter ReDirect Sleep Mode      ${type}     ${no_test}
    ...    ELSE IF   '${type}' == 'T623'    Transmitter ReDirect Sleep Mode      ${type}     ${no_test}
    ...    ELSE       Transmitter Direct Sleep Mode      ${type}     ${no_test}

Transmitter ReDirect
    [Arguments]             ${type}   ${no_test}
    SetVariableTestCase     ${type}   ${no_test}
    SendMessageQueue        normal
    RunAMQTransmitter     3
    Check Queue Transmitter      CheckQueueTransmitterReDirect

Transmitter ReDirect Sleep Mode
    [Arguments]             ${type}   ${no_test}
    SetVariableTestCase     ${type}   ${no_test}
    FOR    ${i}    IN RANGE    10
        SendMessageQueue        sleepmode
        Exit For Loop If    ${i} == 10
    END
    RunAMQTransmitter     10
    Check Queue Transmitter     CheckQueueTransmitterReDirectSleepMode

Transmitter Direct
    [Arguments]             ${type}   ${no_test}
    @{listrespon}=   GetTestResponeDummy
    FOR     ${item}   IN       @{listrespon}
        ${sleep}=   Preparation Data and Dummy     ${type}   ${no_test}    ${item}
        Run Proccess Send Queue       normal
        ${status}=    CheckFlowToTelco
        Check Result Parameter in Telco     ${sleep}
        ${newretry_status}=    CheckFlowNewRetryMechanisme
        ${newreroute_status}=    CheckFlowNewRerouteMechanisme
        Run Keyword If   '${newretry_status}' == 'False'   Check Queue Submit Result    1
        Run Keyword If   '${newretry_status}' == 'True'   Check Retry Transmitter
        Run Keyword If   '${newreroute_status}' == 'True'   Check Reroute Transmitter
        
    END

Transmitter Direct Sleep Mode
    [Arguments]             ${type}   ${no_test}
    # @{listrespon}=   GetTestResponeDummy
    # FOR     ${item}   IN       @{listrespon}
    ${sleep}=   Preparation Data and Dummy Sleep     ${type}   ${no_test}    1
    FOR    ${i}    IN RANGE    10
        Run Proccess Send Queue        sleepmode
        Exit For Loop If    ${i} == 10
    END
    Run Proccess Consume Queue SubmitResult      10
    Check Queue Transmitter     CheckQueueTransmitterReDirectSleepMode
    #      Check Result Parameter in Telco     ${sleep}
    # Check Queue Submit Result

Transmitter Smart Break
    [Arguments]       ${type}     ${no_test}      ${message}
    Run Keyword If   '${type}' == 'T818'     Transmitter ReDirect Smart Break      ${type}     ${no_test}   ${message}
    ...    ELSE IF   '${type}' == 'T623'    Transmitter ReDirect Smart Break      ${type}     ${no_test}    ${message}
    ...    ELSE       Transmitter Direct Smart Break      ${type}     ${no_test}    ${message}

Transmitter ReDirect Smart Break
    [Arguments]       ${type}     ${no_test}    ${message}
    Preparation Data For Smart Break     ${type}   ${no_test}
    Send Topic Smart Break    ${message}      false
    Check Consumer Transmitter Smart Break    ${message}

Transmitter Direct Smart Break
    [Arguments]       ${type}     ${no_test}    ${message}
    Preparation Data For Smart Break     ${type}   ${no_test}
    Send Topic Smart Break    ${message}      true
    Check Consumer Transmitter Smart Break    ${message}

Send Topic Smart Break
    [Arguments]       ${break}       ${direct}
    Run Keyword If    '${direct}' == 'true'       SetTopicSmartBreake      ${break}       ${direct}
    ...     ELSE      SetTopicSmartBreake      ${break}       ${direct}

Preparation Data and Dummy
    [Arguments]             ${type}   ${no_test}     ${item}
    SetVariableTestCase     ${type}   ${no_test}
    ${sleep}=   ChangeDummyRespone      ${item}
    [return]     ${sleep.json()['sleep']}

Preparation Data and Dummy Sleep
    [Arguments]             ${type}   ${no_test}     ${item}
    SetVariableTestCase     ${type}   ${no_test}
    ${sleep}=   ChangeDummyResponeSleepMode
    [return]     ${sleep.json()['sleep']}

Preparation Data For Smart Break
    [Arguments]             ${type}   ${no_test}
    SetVariableTestCase     ${type}   ${no_test}

Run Proccess Consume Queue SubmitResult
    [Arguments]             ${sleep}
    # Sleep    ${sleep}
    RunAmqSubmitResultHandler         ${sleep}

Run Proccess Send Queue
    [Arguments]       ${type}
    SendMessageQueue      ${type}

Check Result Parameter in Telco
    [Arguments]             ${sleep}
    Sleep    ${sleep}
    SetSenderidsParameterForCheck
    ${status}=    CheckFlowToTelco
    Run Keyword If   '${status}' == 'valid'    Check Result Telco

Check Queue Transmitter
    [Arguments]           ${subkeyword}
    @{list}=    GetKeywordFromDB     ${subkeyword}
    set suite variable    @{list}
    FOR    ${item}    IN       @{list}
       log   ${item}
       Check Data Table Transaction    ${item}
    END

Check Result Telco
    @{list}=    GetKeywordFromDB    CheckResultTelco
    set suite variable    @{list}
    # ${File}=    Get File   ${CheckResultTelco}
    # @{list}=    Split to lines   ${File}
    FOR    ${item}    IN       @{list}
       log   ${item}
       Check Data Table Transaction    ${item}
    END

Check Data Queue Submit Result
    @{list}=    GetKeywordFromDB     CheckQueueSubmitResult
    set suite variable    @{list}
    # ${File}=    Get File   ${CheckQueueSubmitResult}
    # @{list}=    Split to lines   ${File}
    FOR    ${item}    IN       @{list}
       log   ${item}
       Check Data Table Transaction    ${item}
    END


Reload Application
    ${File}=    Get File   ${CheckQueueSubmitResult}
    @{list}=    Split to lines   ${File}
    FOR    ${item}    IN       @{list}
       log   ${item}
       Check Data Table Transaction    ${item}
    END

Check Queue Submit Result
    [Arguments]    ${sleep}
    RunAmqSubmitResultHandler         ${sleep}
    Check Data Queue Submit Result

Check Retry Transmitter
    Check Data Table Transaction    SetVariableRetryTransmitterMongoDB
    Check Data Table Transaction    CheckJsonRetryTransmitterMongoDB
    Check Data Table Transaction    CheckJsonRetryTransmitterMongoDB_created_at
    Check Data Table Transaction    CheckJsonRetryTransmitterMongoDB_next_schedule

Check Reroute Transmitter
    Check Data Table Transaction    CheckDataTempForReroute

Check Data Table Transaction
    [Arguments]     ${DataCheck}
    ${respone}=  Run Keyword    ${DataCheck}
    Run Keyword And Continue On Failure                Should Be Equal   ${respone['status']}   OK
    # Log     ${respone['message']}

Check Consumer Transmitter Smart Break
    [Arguments]     ${message}
    ${respone}=  Run Keyword      CheckConsumerQueue    ${message}
    Should Be Equal   ${respone['status']}   OK
    # Log     ${respone['message']}
#batas
