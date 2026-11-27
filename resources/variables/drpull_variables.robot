*** Variables ***
${MOCK_HOST}                        %{MOCK_HOST=192.168.181.51}
${MOCK_PORT}                        %{MOCK_PORT=8095}
${MOCK_STATUS_URL}                  http://${MOCK_HOST}:${MOCK_PORT}/bank/v2/transaction-status
${DEFAULT_CLIENT_SECRET}            7s5tLvM1
${INTEG_APPSID}                     INTEG_APP_035
${INTEG_SID}                        INTEG_SID_035
${INTEG_SECRET_UNIQUE}              SECRET_TC035_UNIQUE
${DEFAULT_CLIENT_SECRETS_JSON}      {"INTEG_APP_035:INTEG_SID_035":"SECRET_TC035_UNIQUE","QueueUID:QueueSenderID":"7s5tLvM1","tselxyz:jatismatahari":"7s5tLvM1","cp_sample:sender_sample":"7s5tLvM1","cp_sample":"7s5tLvM1","app_tier2_only":"secret_tier_dua","prio_app:prio_sid":"SECRET_KEY_A_EXACT","prio_app":"SECRET_KEY_B_APP"}
${DEFAULT_APPSID}                   cp_sample
${DEFAULT_SID}                      sender_sample
