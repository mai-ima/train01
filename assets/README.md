# assets/ — 画像・素材
**コードがテクスチャをファイル名で参照するため、フォルダ構成は変えない**(setup が `tex/` `pbr/` `cand/` `hdri/` に展開)。
| フォルダ | 内容 |
|---|---|
| `textures/` | 生成した画像すべて(看板・ポスター・駅名標・メニュー・時刻表・車両標記・ヘッドマーク・方向幕・紋章)。`kit/` は駅別キット画像。生成は `src/textures/` |
| `pbr_textures/` | PBR マテリアル(ambientCG の CC0 を使用)。色・法線・粗さ ほか |
| `hdri/` | 実写 HDRI(Poly Haven、CC0)。車両試験の照明・反射用。`README.txt` に取得元 |
| `candidates/` | 比較・候補の画像(ロゴ案・看板案など) |
| `misc/` | その他(初代紋章のアーカイブ `emblem_archive/` ほか) |
