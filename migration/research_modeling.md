# モデリング調査(S-M1・最優先 / 2026-10-12 Claude Code)

ユーザー指示: Blender 公式・「綺麗で素早く高品質に作る方法」・AI を使った超高品質モデリングを調べ、サイトの中身まで読み、**AI 関連(使い方)と「どれをどう直すか」**を報告する。
読めた範囲・読めなかった範囲を区別して書く(未読は推測しない)。

## 1. 読んだソースと要点(本文を取得して確認したもの)
| # | ソース | 読めた範囲 | 要点 |
|---|---|---|---|
| 1 | [LL3M 論文(arXiv 2508.08228 html)](https://arxiv.org/html/2508.08228v1) | 要約取得(全体構成・手法・評価) | LLM が **Blender の Python を書いて**3D を作るマルチエージェント。Planner(分解)→ Retrieval(**Blender 4.4 公式ドキュメント1,729ファイルを RAG**)→ Coding(bpy 生成・実行、エラーは RAG で解決)→ Critic(**5視点レンダを VLM が批評**)→ Verification(修正の適用確認)→ User(追加指示の局所編集)。RAG 有りで複雑操作の種類が約5倍、実行エラー約26%減。弱点は **VLM の空間認識**(部品の接続切れ・位置ずれを見逃す)。初期生成約4分・自動改善約6分。 |
| 2 | [GIGAZINE: LL3M](https://www.gigazine.net/gsc_news/en/20250818-ll3m) | 全文 | 上と同内容の一般向け解説。生成コードは変数が明確で後から調整可能、親子関係・インスタンスでシーン階層を作る。 |
| 3 | [blender-llm-addin(GitHub)](https://github.com/mac999/blender-llm-addin) | 全文 | Blender 内パネルからプロンプト→bpy 生成→**失敗コードは自動で修正・再試行**。例は格子/正弦波など単純形状のみ。数量・配置・色・サイズを**具体的に**指示する。 |
| 4 | [BlenderMCP 解説(vagon ほか検索結果)](https://vagon.io/blog/how-to-use-blender-mcp-with-anthropic-claude-ai) | 検索結果の要約のみ(本文は未取得) | Claude と Blender を MCP で接続(uvx blender-mcp、アドオン、localhost:9876)。シーン情報の取得・作成/編集・マテリアル・任意の Python 実行。Poly Haven(HDRI/モデル)と Hyper3D Rodin 連携あり。**具体的で詳細なプロンプトが良い**。 |
| 5 | [AI 3D ゲームアセット生成ツール比較(wavespeed)](https://wavespeed.ai/blog/3d-model-access/best-ai-tools-for-3d-game-assets/) | 全文 | Meshy / Tripo / Rodin / Sloyd / Hunyuan3D 2.1 / TRELLIS の比較。**共通の限界: エッジフロー・ピボット・階層・命名・UV/コリジョンは保証されず、手作業の整理(リトポ)が必要**。推奨手順: 同一ブリーフ(寸法・三角形予算・UV・PBR・パーツ構成)→ Blender で三角形数・非多様体・法線・UV を検査 → エンジンで検証 → 生成条件(シード等)を記録。Hunyuan3D は商用は法務確認、TRELLIS は MIT だが 24GB 以上の GPU。 |
| 6 | [Hunyuan3D 2.1 ドキュメント(検索結果)](https://docsearch.algolia.com/mcp/docs/repo/tencent-hunyuan/hunyuan3d-2.1) | 検索結果の要約のみ | 公式 README の VRAM: 形状10GB・テクスチャ21GB・両方29GB(A100 で検証)。**当環境(CPU のみ)では実行不可**。 |
| 7 | Blender 公式マニュアル: [Sampling](https://docs.blender.org/manual/en/4.1/render/cycles/render_settings/sampling.html)・[Performance](https://docs.blender.org/manual/en/4.1/render/cycles/render_settings/performance.html)・[Reducing Noise](https://docs.blender.org/manual/de/5.3/render/cycles/optimizations/reducing_noise.html) | 本文を取得(ページの大半はナビ。本文のみ抜粋して確認) | ノイズ閾値 0.1〜0.001。**デノイズ入力は少なくとも Albedo を使う**(None は細部がぼやける)。OpenImageDenoise の Prefilter: None=最速で細部保持(入力がノイズ無し前提)/Fast=ぼやけやすい/**Accurate=高ディテール(遅い)**。Persistent Data=再レンダ/アニメを速くする(メモリを使う)。Threads は他作業があるなら論理コアより少なく。**バウンスは拡散<グロッシー<ガラスの順に必要、色成分は 0.8 以下**、ファイアフライは**間接のみクランプ(例 4)**、**室内の昼光には Light Portal**。 |
| 8 | [Bevel Modifier(公式マニュアル各版)](https://docs.blender.org/manual/de/4.0/modeling/modifiers/generate/bevel.html) | 検索結果の要約 | Limit Method=Angle で鋭いエッジだけ面取り、Clamp Overlap、**Harden Normals** で面取り部だけ滑らかに陰影(Auto Smooth は 4.1 で廃止=版依存)。 |
| 9 | [Polycount: Bevel modifier 助言](https://polycount.com/discussion/comment/2703566) | **取得失敗(403)** — 検索結果の抜粋のみ | Bevel Modifier を土台にして幅を後から調整、サブディビより mid-poly+法線調整が有効な場面が多い。 |
| 10 | [devtalk: Fast mesh IO](https://devtalk.blender.org/t/fast-mesh-io-for-addon-development/19962) | 全文 | **numpy 配列を foreach_set / foreach_get に渡す**。add() で領域確保→属性ごとに一括設定。100万三角形で約1.25秒。後段の内部処理が支配的になりやすい。 |
| 11 | [Blender Artists: ops と data](https://blenderartists.org/t/creating-mesh-from-python-performances-issues-ops-vs-data/1342226) | 全文 | **bpy.ops で作ると極端に遅い(9分)→ bpy.data.meshes.new + from_pydata で13秒**。基本は operator を使わない。例外は bmesh.ops。 |
| 12 | 実車参照: [113系(Wikipedia)](https://en.wikipedia.org/wiki/113_series)、[DT21 台車(weblio 検索結果)](https://www.weblio.jp/content/DT21) | 全文/要約 | 113系: 長 20,000mm・幅 2,900mm・片側3扉・MT54(120kW)・座席ピッチ 1,490mm(2000番台)・座席幅 965mm。DT21: 軸距 2,100mm・車輪径 860mm・ウィングばね式。**高さ・床面高さ・前面形状・屋根上機器・窓割は記載なし(未確認)**。 |
| 13 | [asahi-net: 111・113・115系](https://www.asahi-net.or.jp/~eg6f-tkhs/tetu/jr113_115.htm) | 取得したが文字化け(Shift_JIS)で**大半が読めず** | 寸法は未確認。再取得時は文字コードを指定する必要あり。 |

**未読/限界(正直に)**: Blender 公式マニュアルは取得ページの大半がナビゲーションで、本文は抜粋でしか確認できていない。Geometry Nodes・Hard Surface の公式チュートリアル本文、BlenderMCP の GitHub 本体、Rodin/Tripo の公式ドキュメントは未読。

## 2. AI を使ったモデリング(使い方の整理)
- **A. LLM に bpy コードを書かせる**(LL3M 型): すでに本プロジェクトの方式(私が Python でモデルを書く)。足りないのは LL3M の「①公式ドキュメント検索(RAG)②複数視点レンダの自動批評③修正の検証」。→ ②③は strict-auditor(独立監査)と imgcheck で一部実現済み。①は不要(bpy 5.2 の API は都度確認)。
- **B. Blender に MCP で接続**(BlenderMCP): 対話的な調整向き。本環境はヘッドレスの一括生成なので得られる利点は小さい。
- **C. 画像/テキスト→メッシュ生成**(Meshy/Tripo/Rodin/Hunyuan3D/TRELLIS): 試作・小物向き。**車両のように寸法・台車・ドア可動・室内が必要なものは、リトポ/リグ/UV を手作業する必要があり、このプロジェクトの要件(リグ・軌道グラフ)と相性が悪い**。GPU が必要(Hunyuan3D 29GB、TRELLIS 24GB 以上)で当環境では動かせない。
- **D. AI 生成の「画像」(広告・方向幕・看板・テクスチャ)**: 品質向上に最も効く可能性が高い。ただし当環境に画像生成モデルは無く、ユーザー提供が必要(docs/REQUESTS_TO_USER.md に記載)。

## 3. 「どれをどう直すか」(実施・計画)
| 項目 | 現状の問題 | 直し方 | 状況 |
|---|---|---|---|
| レンダ設定 | サンプル/デノイズが弱い | `--hq`: 1600px以上・128spl・適応閾値0.008・**Albedo+Normal デノイズ・Prefilter Accurate**(公式の推奨) | **実施済み** |
| 複数カメラ撮影の速度 | 構築2〜3分を毎回やり直し | 1回の構築で複数カメラ(`MULTICAM="@A;@E;@ZA"`)+**Persistent Data** | **実施済み** |
| 人物の表示/非表示 | 別々に撮り直し | `PEOPLE_BOTH=1` で1回の構築から両方撮影 | **実施済み** |
| 環境光 | 手続き型の空で反射が乏しい | 実写 HDRI(Poly Haven CC0)を車両試験の既定に | **実施済み** |
| 人物 | 球と円柱のマネキン | ロフト(`Acc.tube`)で胴・四肢を滑らかに、身長1.5〜1.7m | 実施済み(まだ実写比で大差) |
| ハードサーフェス | 箱の直角エッジで「模型」に見える | 面取り(`Acc` の bevel)を広く使う+**Bevel(Angle)+Harden Normals** 相当を出力メッシュに適用 | 計画(F5) |
| 構築速度 | bpy.ops 使用箇所・巨大メッシュの Python ループ | プロファイル(cProfile)でボトルネックを特定し、numpy+`foreach_set`化、`bpy.ops` 排除 | **計測中**(/tmp/prof_sh04.out) |
| 検証の決定論化 | VLM(監査員)は部品の接続切れを見逃す(論文の弱点) | 寸法・接触・浮きを数値で検査する `vehcheck.py`(車両の全部品のバウンディングと仕様値の照合) | 計画 |
| 室内の昼光 | 室内灯のみ | 窓に Light Portal | 計画(効果小) |
| 実車準拠 | 形式は架空の汎用 | 実車の寸法・窓割・前面・台車を調べた**参照仕様表**に合わせる | 進行中(F5・資料が不足、REQUESTS 参照) |

## 4. 率直な結論
現在の「プリミティブの組み合わせ」方式の天井は、独立監査で外観約55点・車内約45点でした。公式推奨のレンダ設定や HDRI で**見た目の質は上がる(照明軸 62→70)が、モデリング・質感・人物の差は埋まらない**。95点には、高精細な外部モデル/テクスチャ、または手作業の仕上げが必要と考えます(docs/REQUESTS_TO_USER.md B-1 でご判断をお願いしています)。
