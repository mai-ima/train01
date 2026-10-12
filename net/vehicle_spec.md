# 車両仕様表(自動生成: spec_table.py ← vehtypes.TYPES)

実在車両のデザイン(窓割・前面・台車・屋根機器・塗色)を参考にしつつ、社名・標章は使わない。機関車は公開諸元ベース。

| 形式 | 名称 | 全長m | 幅m | 前面 | 窓 | 窓扉割(右) | 窓扉割(左) | 扉 | 外板 | 下塗色 | 上塗色 | 屋根 | 屋根上機器 | 台車 | 床下 | 室内 | 座席 | 室内灯 | 前面表示 | 側面表示 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| jnr_dc | 通勤形(平妻・4扉) | 20.0 | 2.8 | flat | single | w1 D w3 D w3 D w3 D w1 |  | two | weld | t_sky | t_sky | round | ['pant', 'garland', 'tvent'] | ('dt', 2.1, 0.43) | boxes | long | t_moq_g | tube | sabo | sabo |
| jnr_sub | 近郊形(湘南顔・3扉) | 20.0 | 2.9 | vee | sash2 | w2 D w3 D w3 D w2 |  | louver | louver | t_green | t_orange | round | ['pant', 'pant2', 'torpedo'] | ('dt', 2.1, 0.43) | skirt | mix | t_moq_b | tube | sabo | roll |
| jnr_exp | 急行形(2扉デッキ・大窓) | 19.1 | 2.9 | slope | wide | D s w8 D |  | deck | rivets | t_verm | t_cream | round | ['pant', 'bigvent', 'duct'] | ('air', 2.2, 0.43) | boxes | box | t_moq_r | tube | holder | sabo |
| jnr_ltd | 特急形(ボンネット・リクライニング) | 19.4 | 2.95 | bonnet | wide | D s w9 D |  | plug | flute | t_cream | t_cream | round | ['pant', 'acpod', 'aerial'] | ('air', 2.3, 0.43) | skirtfull | recline | t_moq_y | strip | holder | roll |
| jnr_ac | 交流形(波板・碍子) | 20.0 | 2.8 | slope | single | w2 D w4 D w4 D w2 |  | slide1 | corrug | t_ivory | t_ivory | flat | ['pant', 'insul', 'hvcable', 'tvent'] | ('dt', 2.2, 0.43) | xfmr | mix | t_moq_o | globe | roll | roll |
| ke | 私鉄形(丸い3枚窓・転換クロス) | 18.0 | 2.7 | round | arch | w1 D w3 D w3 D w1 |  | fold | plank | t_maroon | t_maroon | round | ['pant_sa', 'pods', 'signbox'] | ('pedestal', 2.0, 0.4) | skirt | cross | t_moq_b | globe | sabo | roll |
| km | 地下鉄(ステンレス・4扉・貫通扉) | 18.0 | 2.8 | subfront | subway | w1 D w2 D w2 D w2 D w1 |  | two2 | ribs | t_steel | t_steel | flat | ['ac_box', 'ac_box2', 'aerial'] | ('dt', 2.1, 0.43) | skirtfull | subway | t_moq_r | strip | roll | roll |
| kiha_std | 国鉄一般形気動車(2扉・ラジエーター) | 21.3 | 2.94 | gate | pair | w2 D w8 D w2 |  | hing | lap | t_orange | t_cream | round | ['radiator', 'exhaust', 'garland'] | ('dt', 2.1, 0.43) | engine | box | t_moq_g | globe | sabo | sabo |
| kiha_exp | 国鉄急行形気動車(2扉デッキ・大窓) | 20.3 | 2.9 | round | wide | D s w9 D |  | deck | beads | t_cream | t_cream | round | ['radiator', 'exhaust', 'bigvent'] | ('air', 2.3, 0.43) | engine | box | t_moq_r | tube | holder | sabo |
| kiha_hyb | 国鉄ハイブリッド汎用気動車(3扉・パンタ付) | 20.0 | 2.95 | flat | ribbon | w1 D w3 D w3 D w1 |  | modern | smooth | t_steel | t_steel | flat | ['pant', 'hybrid', 'aerial'] | ('dt', 2.1, 0.43) | skirtfull | mix | t_moq_b | strip | roll | roll |
| kiha_ltd | 国鉄特急ハイブリッド気動車(展望前面) | 19.8 | 2.95 | slope | ribbon | D s w9 D |  | modern | smooth | t_ivory | t_ivory | round | ['pant', 'hybrid', 'acpod'] | ('air', 2.3, 0.43) | skirtfull | recline | t_moq_o | strip | roll | roll |
| kiha_sr | 山麓鉄道キハ200(丸形・片引き1扉) | 16.0 | 2.65 | slope | bus | w2 D w4 w1 |  | bus | plank | t_green | t_ivory | round | ['radiator', 'exhaust', 'pods'] | ('pedestal', 1.9, 0.4) | engine | long | t_wood | globe | sabo | sabo |
| kiha_hr | 臨港線小型気動車(バス型・中央扉) | 12.5 | 2.5 | flat | bus | w2 D w2 |  | bus | weld | t_navy | t_warn | round | ['radiator', 'exhaust'] | ('dt', 1.8, 0.36) | engine | long | t_moq_y | globe | sabo | sabo |
| sl_b | 国鉄寝台客車 B寝台(開放式・2段) | 21.0 | 2.9 | flat | wide | D w15 D | D w11 D | deck | beads | t_navy | t_navy | round | ['torpedo', 'duct'] | ('dt', 2.4, 0.43) | sleeper | bunk | t_moq_b | tube | holder | sabo |
| sl_a | 国鉄寝台客車 A寝台(個室・廊下側窓) | 21.0 | 2.9 | flat | sash2 | D w16 D | D w8 D | deck | lap | t_navy | t_navy | round | ['bigvent', 'duct'] | ('air', 2.5, 0.43) | sleeper | compart | t_moq_r | globe | holder | sabo |
| sl_din | 国鉄食堂車(厨房・大窓・煙突) | 21.0 | 2.9 | flat | arch | D s w7 D | D s w7 D | deck | smooth | t_navy | t_navy | round | ['acpod', 'kvent'] | ('air', 2.5, 0.43) | sleeper | dining | t_moq_r | strip | holder | sabo |
| sl_gen | 国鉄電源荷物車(発電機・ルーバー) | 21.0 | 2.9 | flat | pair | D s s s s s s s s s s s s s s s s s s D |  | deck | weld | t_navy | t_navy | round | ['gensetvent', 'exhaust'] | ('dt', 2.4, 0.43) | gen | genset | t_moq_k | globe | holder | sabo |
| tram_o | 大湊市電 600形(両運転台・2扉・丸屋根) | 12.6 | 2.45 | round | single | w3 D w3 D w3 |  | bus | beads | t_green | t_cream | round | ['pant_sa', 'pods'] | ('dt', 1.6, 0.33) | boxes | long | t_wood | globe | sabo | sabo |
| lx_obs | 周遊列車「結」展望スイート(パノラマ前面・発電機) | 21.0 | 2.95 |  | grand | D w7 D | D w5 D |  |  |  |  |  | ['hybrid', 'acpod'] |  | gen | lux_obs |  |  |  |  |
| lx_ste | 周遊列車「結」スイート(1両3室・廊下側は小窓) | 21.0 | 2.95 |  | square | D w16 D | D w9 D |  |  |  |  |  | ['hybrid', 'aerial'] |  |  | lux_ste |  |  |  |  |
| lx_lng | 周遊列車「結」ラウンジ「結の間」(床まで大窓・唯一の乗降口) | 21.0 | 2.95 |  | arch | w4 D w4 | w4 D w4 |  |  |  |  |  | ['acpod', 'aerial'] |  |  | lux_lng |  | strip |  |  |
| lx_din | 周遊列車「結」ダイニング「穂波膳」(大窓・ライブキッチン) | 21.0 | 2.95 |  | grand | D w8 D | D w5 D |  |  |  |  |  | ['acpod', 'kvent'] |  |  | lux_din |  |  |  |  |
| lx_grn | 周遊列車「結」特別スイート(メゾネット・檜風呂) | 21.0 | 2.95 |  | square | D w10 D | D w4 D |  |  |  |  |  | ['hybrid', 'acpod'] |  |  | lux_grn |  |  |  |  |

## 差別化チェック(窓扉割・扉・外板・前面が全て同じ形式の組)
なし
