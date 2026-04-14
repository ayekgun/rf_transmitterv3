*** Settings ***
Resource          resource.robot


*** Test Cases ***
TC001-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-001]

TC002-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-002]

TC003-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-003]

TC004-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-004]

TC005-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-005]

TC006-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-006]

TC007-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-007]

TC008-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-008]

TC009-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-009]

TC010-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-010]

TC011-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-011]

TC012-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-012]

TC013-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-013]

TC014-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-014]

TC015-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-015]

TC016-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-016]

TC017-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-017]

TC018-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-018]

TC019-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-019]

TC020-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-020]

TC021-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-021]

TC022-Put Queue Transmitter 623
    [Tags]   Transmnitter 623
    Transmitter      T623     [TRANSJNS-022]

TC023-Put 10 Queue Transmitter 623 For CHeck Sleep Mode
    [Tags]   Testing Sleepmode
    Transmitter Sleep Mode      T623     [TRANSJNS-001]

TC024-Testing Smart Break Transmitter
    [Tags]   Testing Smart Break
    Transmitter Smart Break      T623     [TRANSJNS-001]    break
    Transmitter Smart Break      T623     [TRANSJNS-001]    unbreak
