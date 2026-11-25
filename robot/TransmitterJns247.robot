*** Settings ***
Resource          resource.robot


*** Test Cases ***
TC001-sender id on DB, No key match
    [Tags]   Transmnitter 247    NoRetry Param
    Transmitter      T247     [TRANSJNS-001]

TC002-sender id on DB, No key match
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-002]

TC003-sender id on json , key match
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-003]

TC004-sender id on DB , Senderids
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-004]

TC005-sender id on DB , witout Param senderids
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-005]

TC006-sender id on DB , Format Senderids Json BAD
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-006]

TC007-sender id on json ,But Expired
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-007]

TC008-sender id on json , No expired
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-008]

TC009-sender id on DB No key match And Expired
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-009]

TC010-sender id on DB, Set without parameter Senderid
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-010]

TC011-sender id on DB, No key match with originMQ Name
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-011]

TC012-sender id on json , key match with originMQ Name tsel 818
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-012]

TC013-sender id on json , key match with originMQ Name tsel 623
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-013]

TC014-sender id on json , key match with originMQ Name Channel lain 247
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-014]

TC015-sender id on json ,But Expired with originMQ Name
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-015]

TC016-sender id on json , No expired with originMQ Name
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-016]

TC017-sender id on DB , witout Param senderids with originMQ Name
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-017]

TC018-1 key match username kosong
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-018]

TC019-1 key match Pass Kosong
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-019]

TC020-1 key match user Pass Kosong
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-020]

TC021-1 key match Sender Kosong
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-021]

TC022-1 key sendrids user Pass Kosong & in queue user Pass Kosong
    [Tags]   Transmnitter 247
    Transmitter      T247     [TRANSJNS-022]

TC023-Put 10 Queue Transmitter 247 For CHeck Sleep Mode
    [Tags]   Testing Sleepmode
    Transmitter Sleep Mode      T247     [TRANSJNS-001]

TC024-Testing Smart Break Transmitter
    [Tags]   Testing Smart Break
    Transmitter Smart Break      T247     [TRANSJNS-001]    break
    Transmitter Smart Break      T247     [TRANSJNS-001]    unbreak

TC025- Test Retry Transmitter = 1
    [Tags]   Transmnitter 247    Retry1    HTTP
    Transmitter      T247     [TRANSJNS-025]

TC026- Test Retry Transmitter = 2
    [Tags]   Transmnitter 247    Retry2    HTTP
    Transmitter      T247     [TRANSJNS-026]

TC027- Test Retry Transmitter = 3
    [Tags]   Transmnitter 247    Retry3    HTTP
    Transmitter      T247     [TRANSJNS-027]

TC028- Test Dual Site Deduplication Single DB
    [Tags]   Transmitter 247    DualSite    Deduplication
    Transmitter Dual Site Deduplication      T247     [TRANSJNS-025]
TC029- Test Boundary SMS 1999 Chars
    [Tags]   Transmitter 247    Boundary    SMS1999
    Transmitter Single Respon      T247     [TRANSJNS-029]    177

TC030- Test Boundary SMS 2000 Chars Max Limit
    [Tags]   Transmitter 247    Boundary    SMS2000
    Transmitter Single Respon      T247     [TRANSJNS-030]    177

TC031- Test Boundary SMS 2001 Chars Over Limit
    [Tags]   Transmitter 247    Boundary    SMS2001
    Transmitter Single Respon      T247     [TRANSJNS-031]    177

TC032- Test HTTP Socket Timeout 15s SUT To Vendor
    [Tags]   Transmitter 247    Timeout    SocketTimeout
    Transmitter Single Respon      T247     [TRANSJNS-032]    185

TC033- Test Valid MSISDN Telkomsel Prefix Halo 62811
    [Tags]   Transmitter 247    MSISDN    Halo62811    Positive
    Transmitter Single Respon      T247     [TRANSJNS-033]    177

TC034- Test Invalid MSISDN Non-Telkomsel Prefix 62818
    [Tags]   Transmitter 247    MSISDN    NonTsel    HTTP400    Negative
    Transmitter Single Respon      T247     [TRANSJNS-034]    178

TC035- Test Malformed MSISDN Without Country Code 0812
    [Tags]   Transmitter 247    MSISDN    Malformed    HTTP400    Negative
    Transmitter Single Respon      T247     [TRANSJNS-035]    178

TC036- Test Register DR Pull Pending To ActiveMQ MongoDB Queue
    [Tags]   Transmitter 247    DRPull    ActiveMQ    Positive
    Transmitter Single Respon DRPull      T247     [TRANSJNS-036]    177
