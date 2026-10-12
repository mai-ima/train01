# 引き継ぎ書(HANDOFF) — 2026-10-12 作成(S-MG1)

## 1. プロジェクト概要
- **何か**: 昭和・国鉄(JNR)時代の**架空路線網**を Blender(`bpy` 5.2 LTS、ヘッドレス、Cycles CPU)で丸ごと生成するPythonスクリプト群。42駅・9路線・7社。基準駅=穂波野(M06・国鉄本社)、中央駅=国都中央(M01)。駅舎・ホーム・町・車両基地・車両(室内まで)・線路網(橋/トンネル/地下/高架)・路線図ページ・360°パノラマ。
- **すべて架空**: 実在の社名・標章は使わない(国鉄/JNRの名称は維持)。機関車は実物写真を参照できず**公開諸元ベース**(納品時に必ず伝える)。実車デザインは参考可。商用ゲームからの抽出は不可。
- **成果物の置き場**: 作業 `/home/claude/station`(フラット配置)、GitHub `github.com/mai-ima/train01`(整理配置: src/ scripts/ net/ data/ docs/ assets/ renders/ viewer/ migration/ .claude/)。`.blend` は含めない(27MB以下に分割して納品)。
- **ユーザー**: 日本語話者。要求は非常に厳格(品質=実写と見分けがつかない水準、差別化、監査の点数化)。「止まるな」を繰り返し強調している。

## 2. 構造(どこに何があるか)
- `main.py`: 入口。`--zone <駅ID>`(単駅)、`--world`(全駅+線路)、`--parts a,b,c`(core,station,depot,props,train,veg,hq,life,vtest…)、`--cam`、`--w`、`--samples`、`--out`、`--people on|off|cars|station`、`--stock`、`--interf`、`--no-render`。環境変数 `MULTICAM="x,y,z,tx,ty,tz,lens;..."` で1回のビルドから複数視点を撮影(出力 `out/<out>_<n>.png`)。
- 駅ビルダー: `kit.py`(穂波野基準)、`kit2.py`(駅別デザイン DESIGN)、`kit3.py`(特殊駅 M01・BUILD登録)、`kit4.py`(線路網・軌道グラフ・local_tracks)、`kit5.py`(駅間架線・分岐器)、`kit6.py`(他社線8駅)、`kit7.py`(地下/構造物)、`kit8.py`。町:`kit_town.py`, `houses.py`。部屋:`rooms.py`。小物:`props.py`。
- 車両: `vehtypes.py`(中核。TYPES仕様、前面形状 flat/vee/bonnet/round/subfront/gate、室内 `_interior/_sleep_inside/_lux_inside`、人物 `_rider`)、`trainkit.py`(Veh・材質 vpaint/moquette/carpet_lux)、`train.py/train2.py/steam*.py/diesel2.py`。
- データ: `net/network.py`(駅・路線の正)、`net/details.py`(線数・配線)、`net/services.py`(運行系統・種別 SVC/KIND_RANK)、`net/facilities.py`、`net/track_graph.json`(軌道グラフ)、`net/status.json`(状態表)、`net/taxonomy.md`(タスク記号)、`net/audit_rubric.md`(監査点数基準)。
- 路線図: `net/mkmap.py` → `net/routemap_v245.html`。Artifact公開先 `Ae51R2sD6GyV81wgfMWG5A`(v2.4.5)。**`patch_v245.py` は再実行禁止**。
- 検査: `imgcheck.py`(黒/単色/白飛び検出)、`sheet.py`(コンタクトシート)、`interf.py`(線路干渉)、`doorcheck.py`、`floatcheck.py`、`stockcheck.py`、`net/orient_graph.py`(向き)、`comp_check.py`。

## 3. 現状(正直に)
- 完了: 95 / 進行中: 10 / 未着手: 79(tasks.json 参照。全184件)。
- **車両の監査はすべて不合格**: 車内 第3回(最高52点: cross 52, lx_lng 51…)、外観 第1回(43〜47点)。人物はマネキン調、座席は箱形、窓に厚み/反射なし、台車/床下が似通う、vtest環境(砂地・短い線路)は試験用。
- 地下鉄/路面電車/モノレール/K03 の構造監査(Z-A)は0/6不合格 → 素材刷新(Z-A7)→意匠差別化(Z-A8)→3回目監査(Z-A9)の途中で、路線図v2.4.5(S-R6/R7)と車両F3へ割り込み。
- 穂波野・試作ゾーン・画像も新基準(総合95/全軸90)では不合格扱い。**「おおむね良い」は不合格**。
- 直近の実装(未再監査): 車内天井高修正(窓上帯を中空化、天井=zt-0.06)、`--people`、人物関節球/耳、ロングシートのバケット化、頭当て/肘掛け、形式別床材、寝台はしご/読書灯、lux肘掛け椅子、前面付帯物(連結器/ホース/ステップ/渡り板)、屋根煤、kiha_exp/ltd/sr/std の塗色差別化(`out/fe1_*` は撮影済・fe1_sheet0.png 未確認)。

## 3b. 最新更新(2026-10-12 20:20・セッション終了時点)
- 【S-MG1】完了・push済。ユーザー指示(19:51)により本セッションは終了、以後は Claude Code で続行。
- 直近の車両作業: vpaint の雨筋汚れ係数を 0.55→0.38 に下げ(fg1 で淡色車体の灰色化が緩和、形式の色差が見えやすくなった)。bg1 で台車/車輪の接地は正常と確認(fe1 の『浮き』は見かけ)。車両の骨格差別化・前面形状・人物・座席は未達で、監査は依然すべて不合格。
- 未実施: F3c続き(骨格・前面)、F3d2、再監査 X13 以降すべて。

## 4. 現在地と次の一手
1. 【S-MG1】移行パッケージを完成 → コミット/push(この作業)。
2. F3c(外観差別化): fe1_sheet0.png を目視(前面ディテール・塗色)。似たペア(jnr_exp/kiha_exp/km/kiha_ltd, jnr_dc/jnr_sub, ke/kiha_sr/kiha_std, jnr_ac/kiha_hyb, jnr_ltd/kiha_ltd)の骨格(断面・屋根・台車・窓割・ドア)を形式別に別設計 → 汚れの因果(雨筋・台車油)→ 外観再監査(前回点数を伏せる)。
3. F3d2(内装): 人物の質の向上(服・体型・ポーズ)、座席形状、窓の厚み/反射、照明の色温度、経年 → 車内第4回監査(X13)。
4. 周遊列車「結」(F4/N6/P7/X12)、F3f(客車/機関車/寝台特急「ほなみ」)、ヘッドマーク/方向幕(P6、未装着)、画像監査 X11。
5. 構造 Z-A7〜A9 → B6(駅内部)→ K2/K6 → 新車庫 D4–D9 → …(TASKS.md「実行順」と net/session_state.md)。
6. 最後: X9 最終超超超高レベル監査 → Z-G1 修正ループ → 納品(G1/G3: 全景レンダ、.blendゾーン別27MB以下、パノラマビューア、路線図、元データ)。

## 5. 作業サイクル(1タスクの回し方)
1. tasks.json で対象を決め in_progress に。 2. 実装(該当 .py)。 3. レンダ(1本ずつ・Monitorで待機)。 4. `imgcheck.py` → `sheet.py` でコンタクトシート → Read で目視(3視点以上)。 5. 完了したら tasks.json/ session_state.md 更新。 6. グループ完了時に strict-auditor で監査(点数)。 7. `bash scripts/sync_repo.sh` 相当でコミット/push(日本語本文+トレーラー2行)。

## 6. 既知の落とし穴(詳細は CONTEXT.md)
- 室内が真っ黒 → ライトが中実ジオメトリ内にある。窓上帯は中空に。
- カメラは車内に置くこと(車体の外だと壁に遮られる)。
- フォアグラウンドで10分超待つとタイムアウト(exit 143)。Monitor/別コマンドで待つ。`sync_repo.sh` は nohup でバックグラウンド。
- `sync_repo.sh` は train01 を .git と CLAUDE.md 以外ぜんぶ消して再コピーする(migration/ と .claude/ もコピー対象に追加済み)。
- 2コアなので並列レンダ禁止。並列Agentは監査のみ。
- WebFetch は検索結果に出たURL/ユーザーが提示したURLしか取得できない(先に WebSearch)。
- SVG の `hidden` プロパティは効かない(setAttribute('hidden'))。

## 7. 未検証・限界
- この移行パッケージは Claude Code 実環境でまだ動かしていない(setup_workspace.sh はこの環境で構文確認のみ)。初回で差分が出たら本節に追記すること。
- 旧セッションの bpy 以外の依存(PIL, numpy, Playwright など)は setup_workspace.sh が確認するが、移行先に無ければ `pip install --break-system-packages` が必要。

## 8. Claude Code 初回実走の結果(2026-10-12・移行先環境)
- setup_workspace.sh は成功。bpy は未導入だったため `pip install --break-system-packages bpy==5.2.2`(Python 3.13)で導入でき、`import bpy` は 5.2.2 LTS。
- 煙テスト `python3 main.py --zone SH04 --parts none --cam ZA --w 400 --samples 4 --out smoke` は成功(約2分27秒、4コア)。警告: CUEW 初期化失敗(CPUレンダでは無害)、World.use_nodes の非推奨警告。
- 未検証: Playwright(路線図の検査用)の有無。

## 9. 全ファイル確認で見つかった不整合(2026-10-12・Claude Code 側)
- **点数基準の置き場**: 点数化・厳格化(95/90、未確認=0)は元々 `net/audit_rubric.md` にだけあり、`docs/audit_rubric.md`(strict-auditor が参照)には無かった → docs 側へ追記して一致させた(`net/` 側は残置)。
- **`scripts/sync_repo.sh` は使用禁止**: repo を .git と CLAUDE.md 以外すべて削除して再コピーする上、パスが /home/claude/train01 固定・`dotclaude/` を前提にしており、この環境(repo=/home/user/train01)では repo を破壊しうる。コミットは通常の `git add/commit/push` で行う。必要なら作業側→repo の一方向コピーだけを行う安全版を別途作る。
- **`net/vehicle_spec.md` は古い**(自動生成: spec_table.py。例: kiha_std の前面は現行 gate だが表は vee)。F3c の変更後に `net/mkspec.py` 等で再生成する。
- `scripts/continue_check.sh` と `recovery_snapshot.sh` は /home/claude/station・/home/claude/train01 固定(setup が sed で置換するのは展開先のコピーのみ。repo 側の scripts/ は元のまま)。
- 会話ログ jsonl の探索パスは /root/.claude/projects/-home-claude*/ 固定。ここでは該当なし(旧ログは migration/transcripts/ のみ)。
- **重大バグ修正(2026-10-12)**: `zone_stock._place_auto` が未定義の `_len` / `_nose2` を呼んで全駅で停車車両の配置に失敗していた(前任セッション末の編集で混入。ゾーン構築ログに "stock failed … name '_len' is not defined")。`_len`(車両全長)と `_nose2`(連結間隔=0)を定義して解消。**駅ゾーンの旧レンダ(renders/ 以下)は車両なし/旧車両のため撮り直しが必要(E3)**。

## 10. リポジトリ構成の整理(2026-10-12・【S-G8】)
- `src/` は機能別(`core/ honamino/ stations/ vehicles/ textures/ checks/ export/`)、`scripts/` は運用(直下)と一括系(`batch/`)、`renders/work/` は用途別(`vehicles/ interiors/ stations/ structures/ misc/`)、路線図キャプチャは `renders/routemap/`。履歴は `git mv` で保持。
- **作業はこれまでどおりフラットな作業ディレクトリ**(`bash migration/setup_workspace.sh` が `src/**/*.py` と `scripts/**/*.sh` をフラットに展開)。作業側の変更は `bash scripts/sync_safe.sh` で repo の機能別構成へ書き戻す(同名ファイルは元の場所へ、新規は `src/misc/`・`scripts/batch/`)。
- 文書の入口は `docs/README.md`。**`net/` の .md(taxonomy / session_state / research_tour など)は CLAUDE.md や hook から参照されるため動かしていない**。以前の記述にある `src/xxx.py`・`scripts/xxx.sh` は、それぞれ機能別/batch 配下に移動している(ファイル名で検索)。

## 11. Claude Code セッションの到達点(2026-10-12 夜時点)と次の一手
- 完了(最優先): S-G8 リポジトリ整理 / S-T1 新タスク一覧(docs/TASK_LIST.md) / S-M1 モデリング調査(migration/research_modeling.md) / S-Q7 根本原因(docs/ROOT_CAUSES.md)。ほか R9 路線図再出力(artifact Version 6)・X14 超超超厳格基準・V4 人物ON/OFF両撮り・W3 速度(草の散布BVH化で構築10倍速・--hq/--draft・Persistent Data)・B6a 駅舎の改札/券売機・Q8 絶対パス一元化・F5a 実車参照表(net/vehicle_reference.md)。
- 重大バグ修正: 停車車両の配置(zone_stock の _len/_nose2)。**旧レンダの駅には車両がない**ため全駅を撮り直し中(E3a: scripts/e3_batch.sh、出力 out/e3b/、`--draft`)。
- 車両・車内の独立監査は2回とも全件不合格(外観約55・車内約45)。**手続き型の天井**。ユーザー判断待ち: docs/REQUESTS_TO_USER.md B-1。
- 次: E3a の確認と healthscan → G1a/G1b(納品の先行完成)→ F5b〜e → 群監査。待機は短い呼び出し+Monitor、長い同期待機をしない(CLAUDE.md の運用ルール)。
