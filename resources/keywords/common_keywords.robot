*** Settings ***
Documentation    Keyword bootstrap lifecycle suite dan test setup/teardown untuk drpulltelkomsel v2.0.0.
Library          MockTelkomselV2Library
Library          MongoDrPullLibrary
Library          ActiveMqDrPullLibrary
Library          MySqlDrPullLibrary
Library          DrPullAppLibrary
Library          SutLogLibrary
Resource         ../variables/drpull_variables.robot


*** Keywords ***
Inisialisasi Lingkungan Pengujian Drpull
    [Documentation]    Suite Setup: menyalakan mock server, menghubungkan ke Mongo/AMQ/MySQL, backup konfigurasi, arahkan endpoint ke mock, dan mulai SUT.
    Mock Telkomsel Mulai Server    port=${MOCK_PORT}    secret=${DEFAULT_CLIENT_SECRET}
    Mongo Hubungkan Ke Database Dr Pull
    Activemq Hubungkan Ke Broker
    Mysql Hubungkan Ke Database Apps Config
    Mysql Backup Konfigurasi Dr Pull
    Mysql Update Lookup Value    mongo_host    192.168.181.63
    Mysql Update Lookup Value    mongo_port    27017
    Mysql Update Lookup Value    mongo_user    jnsCore
    Mysql Update Lookup Value    mongo_password    jnsCore123
    Mysql Update Lookup Value    mongo_db    jnsCore
    Mysql Update Lookup Value    mongo_collection    dr_pull_telkomsel
    Mysql Update Lookup Value    activemq_host    tcp://192.168.181.51:61616
    Mysql Update Lookup Value    activemq_user    admin
    Mysql Update Lookup Value    activemq_password    admin
    Mysql Update Lookup Value    activemq_queuedr    jns.dr.drrealhandler
    Mysql Update Lookup Value    activemq_dbexecutor    jns.db.deliveryreport
    Mysql Update Lookup Value    sweep_interval_seconds    2
    Mysql Set Konfigurasi Provider Status Url    ${MOCK_STATUS_URL}
    Mysql Set Konfigurasi Dr Pull Secret Dan Json    client_secret=${DEFAULT_CLIENT_SECRET}    client_secrets_json=${DEFAULT_CLIENT_SECRETS_JSON}
    Mock Telkomsel Set Secret    ${DEFAULT_CLIENT_SECRET}
    Drpull App Mulai Service
    Log    Suite bootstrap selesai. Seluruh dependency dan SUT siap.

Hentikan Lingkungan Pengujian Drpull
    [Documentation]    Suite Teardown: hentikan SUT, restore MySQL original, putuskan seluruh koneksi dan hentikan mock.
    Drpull App Hentikan Service
    Mysql Restore Konfigurasi Dr Pull
    Mysql Putuskan Dari Database Apps Config
    Activemq Putuskan Dari Broker
    Mongo Putuskan Dari Database Dr Pull
    Mock Telkomsel Hentikan Server
    Log    Suite teardown selesai. Seluruh resource telah dipulihkan.

Persiapkan Konteks Pengujian
    [Documentation]    Test Setup: reset state mock, drain pesan ActiveMQ, dan siapkan variabel konteks transaksi.
    Mock Telkomsel Reset Perekam Request
    Mock Telkomsel Set Secret    ${DEFAULT_CLIENT_SECRET}
    Mock Telkomsel Set Secret Map    ${DEFAULT_CLIENT_SECRETS_JSON}
    Activemq Reset Penampung Pesan
    Set Test Variable    ${CURRENT_TRXID}    ${EMPTY}

Bersihkan Konteks Pengujian
    [Documentation]    Test Teardown: bersihkan dokumen uji pada MongoDB dan pulihkan state mock serta konfigurasi MySQL.
    ${status}=    Get Variable Value    ${TEST STATUS}
    IF    '${CURRENT_TRXID}' != '${EMPTY}' and '${status}' == 'PASS'
        Mongo Bersihkan Dokumen Uji    ${CURRENT_TRXID}
    END
    Mysql Set Konfigurasi Provider Status Url    ${MOCK_STATUS_URL}
    Mysql Set Konfigurasi Dr Pull Secret Dan Json    client_secret=${DEFAULT_CLIENT_SECRET}    client_secrets_json=${DEFAULT_CLIENT_SECRETS_JSON}
    Mysql Update Lookup Value    activemq_dbexecutor    jns.db.deliveryreport
    Mock Telkomsel Reset Perekam Request
    Mock Telkomsel Set Secret    ${DEFAULT_CLIENT_SECRET}
    Mock Telkomsel Set Secret Map    ${DEFAULT_CLIENT_SECRETS_JSON}
    Mock Telkomsel Set Virtual Clock Delta    ${None}
