*** Settings ***
Library           TrafficGenLibrary.py
Suite Setup       Connect To Traffic Generator    %{TRAFFICGEN_BASE_URL}    %{TRAFFICGEN_USER=}    %{TRAFFICGEN_PASS=}    verify_tls=%{TRAFFICGEN_VERIFY_TLS=True}
Suite Teardown    Disconnect From Traffic Generator

*** Test Cases ***
Appliance Reports Its Version
    ${info}=    Get System Info
    Should Not Be Empty    ${info}[version]

Ports Are Numbered From One
    ${ports}=    Get Ports
    Should Be Equal As Integers    ${ports}[0][PortNo]    1

Line Rate Can Be Read
    ${rate}=    Get Line Rate    1
    Should Not Be Empty    ${rate}

MAC Counters Can Be Read
    ${mac}=    Get Mac Counters    1
    Should Not Be Empty    ${mac}[tx]
    Should Not Be Empty    ${mac}[rx]
