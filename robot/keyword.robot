*** Keywords ***
Transmitter
    [Arguments]       ${type}     ${no_test}
    Log To Console    ================================================================================
    Log To Console    [Transmitter] Starting test: type=${type}, test=${no_test}
    Log To Console    ================================================================================
    SetSiteMode             ${SiteMode}
    SetConfigDynamic        ${TransmitterName}
    Run Keyword If   '${type}' == 'T818'     Transmitter ReDirect      ${type}     ${no_test}
    ...    ELSE IF   '${type}' == 'T623'    Transmitter ReDirect      ${type}     ${no_test}
    ...    ELSE       Transmitter Direct      ${type}     ${no_test}
    Log To Console    [Transmitter] Test completed: type=${type}, test=${no_test}
    Log To Console    ================================================================================
    # ClearVariable

Transmitter Sleep Mode
    [Arguments]       ${type}     ${no_test}
    SetConfigDynamic        ${TransmitterName}
    Run Keyword If   '${type}' == 'T818'     Transmitter ReDirect Sleep Mode      ${type}     ${no_test}
    ...    ELSE IF   '${type}' == 'T623'    Transmitter ReDirect Sleep Mode      ${type}     ${no_test}
    ...    ELSE       Transmitter Direct Sleep Mode      ${type}     ${no_test}

Transmitter ReDirect
    [Arguments]             ${type}   ${no_test}
    Log To Console    [Transmitter ReDirect] Starting: type=${type}, test=${no_test}
    SetVariableTestCase     ${type}   ${no_test}
    Log To Console    [Transmitter ReDirect] Sending message to queue...
    SendMessageQueue        normal
    Log To Console    [Transmitter ReDirect] Running AMQ Transmitter...
    RunAMQTransmitter     3
    Log To Console    [Transmitter ReDirect] Checking queue transmitter...
    Check Queue Transmitter      CheckQueueTransmitterReDirect
    Log To Console    [Transmitter ReDirect] Completed

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
    Log To Console    [Transmitter Direct] Starting: type=${type}, test=${no_test}
    @{listrespon}=   GetTestResponeDummy
    ${list_length}=    Get Length    ${listrespon}
    Log To Console    [Transmitter Direct] Found ${list_length} dummy responses to process
    ${counter}=    Set Variable    0
    FOR     ${item}   IN       @{listrespon}
        ${counter}=    Evaluate    ${counter} + 1
        Log To Console    [Transmitter Direct] Processing dummy response ${counter}/${list_length}: item=${item}
        Sleep    2
        ${sleep}=   Preparation Data and Dummy     ${type}   ${no_test}    ${item}
        Log To Console    [Transmitter Direct] Sleep time: ${sleep}
        Run Proccess Send Queue       normal
        ${status}=    CheckFlowToTelco
        Log To Console    [Transmitter Direct] Flow status: ${status}
        Check Result Parameter in Telco     ${sleep}
        ${newretry_status}=    CheckFlowNewRetryMechanisme
        ${newreroute_status}=    CheckFlowNewRerouteMechanisme
        Run Keyword If   '${newretry_status}' == 'False'   Check Queue Submit Result    1
        Run Keyword If   '${newretry_status}' == 'True'   Check Retry Transmitter
        Run Keyword If   '${newreroute_status}' == 'True'   Check Reroute Transmitter
        Log To Console    [Transmitter Direct] Completed processing item ${counter}
    END
    Log To Console    [Transmitter Direct] All items processed

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
    SetConfigDynamic        ${TransmitterName}
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
    Log To Console    [Preparation Data and Dummy] Preparing: type=${type}, test=${no_test}, item=${item}
    SetVariableTestCase     ${type}   ${no_test}
    ${sleep}=   ChangeDummyRespone      ${item}
    Log To Console    [Preparation Data and Dummy] Sleep time: ${sleep.json()['sleep']}
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
    Log To Console    [Run Proccess Consume Queue SubmitResult] Starting: sleep=${sleep}
    # Sleep    ${sleep}
    RunAmqSubmitResultHandler         ${sleep}
    Log To Console    [Run Proccess Consume Queue SubmitResult] Completed

Run Proccess Send Queue
    [Arguments]       ${type}
    Log To Console    [Run Proccess Send Queue] Sending message: type=${type}
    SendMessageQueue      ${type}
    Log To Console    [Run Proccess Send Queue] Message sent

Check Result Parameter in Telco
    [Arguments]             ${sleep}
    Log To Console    [Check Result Parameter in Telco] Starting validation (sleep=${sleep})
    Sleep    ${sleep}
    SetSenderidsParameterForCheck
    ${status}=    CheckFlowToTelco
    Log To Console    [Check Result Parameter in Telco] Flow status: ${status}
    Run Keyword If   '${status}' == 'valid'    Check Result Telco
    Log To Console    [Check Result Parameter in Telco] Validation completed

Check Queue Transmitter
    [Arguments]           ${subkeyword}
    Log To Console    [Check Queue Transmitter] Starting: subkeyword=${subkeyword}
    @{list}=    GetKeywordFromDB     ${subkeyword}
    set suite variable    @{list}
    ${list_length}=    Get Length    ${list}
    Log To Console    [Check Queue Transmitter] Found ${list_length} checks to perform
    ${counter}=    Set Variable    0
    FOR    ${item}    IN       @{list}
       ${counter}=    Evaluate    ${counter} + 1
       Log To Console    [Check Queue Transmitter] Running check ${counter}/${list_length}: ${item}
       log   ${item}
       Check Data Table Transaction    ${item}
    END
    Log To Console    [Check Queue Transmitter] All checks completed

Check Result Telco
    Log To Console    [Check Result Telco] Starting validation
    @{list}=    GetKeywordFromDB    CheckResultTelco
    set suite variable    @{list}
    ${list_length}=    Get Length    ${list}
    Log To Console    [Check Result Telco] Found ${list_length} checks to perform
    # ${File}=    Get File   ${CheckResultTelco}
    # @{list}=    Split to lines   ${File}
    ${counter}=    Set Variable    0
    FOR    ${item}    IN       @{list}
       ${counter}=    Evaluate    ${counter} + 1
       Log To Console    [Check Result Telco] Running check ${counter}/${list_length}: ${item}
       log   ${item}
       Check Data Table Transaction    ${item}
    END
    Log To Console    [Check Result Telco] All checks completed

Check Data Queue Submit Result
    Log To Console    [Check Data Queue Submit Result] Starting validation
    @{list}=    GetKeywordFromDB     CheckQueueSubmitResult
    set suite variable    @{list}
    ${list_length}=    Get Length    ${list}
    Log To Console    [Check Data Queue Submit Result] Found ${list_length} checks to perform
    # ${File}=    Get File   ${CheckQueueSubmitResult}
    # @{list}=    Split to lines   ${File}
    ${counter}=    Set Variable    0
    FOR    ${item}    IN       @{list}
       ${counter}=    Evaluate    ${counter} + 1
       Log To Console    [Check Data Queue Submit Result] Running check ${counter}/${list_length}: ${item}
       log   ${item}
       Check Data Table Transaction    ${item}
    END
    Log To Console    [Check Data Queue Submit Result] All checks completed


Reload Application
    ${File}=    Get File   ${CheckQueueSubmitResult}
    @{list}=    Split to lines   ${File}
    FOR    ${item}    IN       @{list}
       log   ${item}
       Check Data Table Transaction    ${item}
    END

Check Queue Submit Result
    [Arguments]    ${sleep}
    Log To Console    [Check Queue Submit Result] Starting: sleep=${sleep}
    RunAmqSubmitResultHandler         ${sleep}
    Check Data Queue Submit Result
    Log To Console    [Check Queue Submit Result] Completed

Check Retry Transmitter
    Log To Console    [Check Retry Transmitter] Starting retry validation
    Check Data Table Transaction    SetVariableRetryTransmitterMongoDB
    Check Data Table Transaction    CheckJsonRetryTransmitterMongoDB
    Check Data Table Transaction    CheckJsonRetryTransmitterMongoDB_created_at
    Check Data Table Transaction    CheckJsonRetryTransmitterMongoDB_next_schedule
    Log To Console    [Check Retry Transmitter] Retry validation completed

Check Reroute Transmitter
    Log To Console    [Check Reroute Transmitter] Starting reroute validation
    Check Data Table Transaction    CheckDataTempForReroute
    Check Data Table Transaction    CheckDataQueeueForReroute
    Log To Console    [Check Reroute Transmitter] Reroute validation completed

Check Data Table Transaction
    [Arguments]     ${DataCheck}
    Log To Console    [Check Data Table Transaction] Running: ${DataCheck}
    ${respone}=  Run Keyword    ${DataCheck}
    ${status}=    Set Variable    ${respone['status']}
    Run Keyword And Continue On Failure                Should Be Equal   ${status}   OK
    Run Keyword If    '${status}' == 'OK'    Log To Console    [Check Data Table Transaction] ✓ ${DataCheck}: ${status} - ${respone['message']}
    ...    ELSE    Log To Console    [Check Data Table Transaction] ✗ ${DataCheck}: ${status} - ${respone['message']}
    # Log     ${respone['message']}

Check Consumer Transmitter Smart Break
    [Arguments]     ${message}
    ${respone}=  Run Keyword      CheckConsumerQueue    ${message}
    Should Be Equal   ${respone['status']}   OK
    # Log     ${respone['message']}

Transmitter Dual Site Deduplication
    [Arguments]             ${type}   ${no_test}
    Log To Console    ================================================================================
    Log To Console    [Transmitter Dual Site Deduplication] Starting: type=${type}, test=${no_test}
    Log To Console    ================================================================================
    SetSiteMode             ${SiteMode}
    SetConfigDynamic        ${TransmitterName}
    ${is_single}=           IsSingleSiteMode
    Run Keyword If    ${is_single}    Log To Console    [Transmitter Dual Site Deduplication] NOTICE: Running in single-site / legacy mode. Skipping dual-site injection and deduplication check.
    Return From Keyword If    ${is_single}
    SetVariableTestCase     ${type}   ${no_test}
    ${sleep}=   ChangeDummyRespone      181
    Log To Console    [Transmitter Dual Site Deduplication] Set dummy HTTP 502 (id=181) to trigger retry
    Log To Console    [Transmitter Dual Site Deduplication] Sending queue to BOTH PROD (.51) and DRC (.58)...
    SendMessageQueueDualSite    dual_site
    Log To Console    [Transmitter Dual Site Deduplication] Waiting 5s for both transmitters to process...
    Sleep    5
    Log To Console    [Transmitter Dual Site Deduplication] Verifying deduplication in MongoDB retry_transmitter...
    Check Dual Site Deduplication
    Log To Console    [Transmitter Dual Site Deduplication] Completed successfully
    Log To Console    ================================================================================

Check Dual Site Deduplication
    Check Data Table Transaction    CheckDualSiteDeduplicationMongoDB
#batas

Transmitter Single Respon
    [Arguments]       ${type}     ${no_test}    ${dummy_id}
    Log To Console    ================================================================================
    Log To Console    [Transmitter Single Respon] Starting: type=${type}, test=${no_test}, dummy_id=${dummy_id}
    Log To Console    ================================================================================
    SetSiteMode             ${SiteMode}
    SetConfigDynamic        ${TransmitterName}
    ${sleep}=   Preparation Data and Dummy     ${type}   ${no_test}    ${dummy_id}
    Log To Console    [Transmitter Single Respon] Sleep time: ${sleep}
    Run Proccess Send Queue       normal
    ${status}=    CheckFlowToTelco
    Log To Console    [Transmitter Single Respon] Flow status: ${status}
    Check Result Parameter in Telco     ${sleep}
    Check Queue Submit Result    1
    Log To Console    [Transmitter Single Respon] Completed test: type=${type}, test=${no_test}
    Log To Console    ================================================================================


Check Queue DR Pull Registration
    Log To Console    [Check Queue DR Pull Registration] Starting DR Pull registration validation
    Check Data Table Transaction    SetVariableQueueDrPullRegistration
    Check Data Table Transaction    CheckDrPullCollectionAndType
    Check Data Table Transaction    CheckDrPullDocumentsStatusPending
    Check Data Table Transaction    CheckDrPullDocumentsIdentifiers
    Check Data Table Transaction    CheckDrPullNextPullSchedule
    Check Data Table Transaction    CheckDrPullSutLogTrace
    Log To Console    [Check Queue DR Pull Registration] DR Pull registration validation completed

Transmitter Single Respon DRPull
    [Arguments]       ${type}     ${no_test}    ${dummy_id}
    Log To Console    ================================================================================
    Log To Console    [Transmitter Single Respon DRPull] Starting: type=${type}, test=${no_test}, dummy_id=${dummy_id}
    Log To Console    ================================================================================
    SetSiteMode             ${SiteMode}
    SetConfigDynamic        ${TransmitterName}
    ${sleep}=   Preparation Data and Dummy     ${type}   ${no_test}    ${dummy_id}
    Log To Console    [Transmitter Single Respon DRPull] Sleep time: ${sleep}
    Run Proccess Send Queue       normal
    ${status}=    CheckFlowToTelco
    Log To Console    [Transmitter Single Respon DRPull] Flow status: ${status}
    Check Result Parameter in Telco     ${sleep}
    Check Queue Submit Result    1
    Check Queue DR Pull Registration
    Log To Console    [Transmitter Single Respon DRPull] Completed test: type=${type}, test=${no_test}
    Log To Console    ================================================================================
