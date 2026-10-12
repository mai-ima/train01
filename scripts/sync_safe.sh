#!/bin/bash
# 作業ディレクトリ(フラット) → repo(機能別フォルダ)への「一方向・非破壊」同期(削除なし)。
# 使い方: bash scripts/sync_safe.sh [作業=/home/claude/station] [repo=このリポジトリ]
# 既存ファイルは repo 内の同名ファイルの場所へ上書き更新し、新規ファイルは src/misc/ または scripts/batch/ に置く。
S="${1:-/home/claude/station}"; R="${2:-$(cd "$(dirname "$0")/.." && pwd)}"
put() {   # put <拡張子> <repoの親(src|scripts)> <新規の置き場>
  for f in "$S"/*."$1"; do
    [ -f "$f" ] || continue
    b=$(basename "$f"); [ "$b" = "sync_repo.sh" ] && continue
    dst=$(find "$R/$2" -name "$b" -print -quit)
    [ -n "$dst" ] || { mkdir -p "$R/$2/$3"; dst="$R/$2/$3/$b"; }
    cmp -s "$f" "$dst" || cp "$f" "$dst"
  done
}
put py src misc
put sh scripts batch
rsync -a --exclude='__pycache__' --exclude='*.blend*' --exclude='*.png' "$S/net/" "$R/net/" 2>/dev/null || cp -ru "$S/net/." "$R/net/"
[ -d "$S/tex" ] && mkdir -p "$R/assets/textures" && cp -ru "$S/tex/." "$R/assets/textures/"
[ -d "$S/hdri" ] && mkdir -p "$R/assets/hdri" && cp -ru "$S/hdri/." "$R/assets/hdri/"
[ -f "$R/net/mktasklist.py" ] && (cd "$R" && python3 net/mktasklist.py >/dev/null) && echo "TASK_LIST.md を再生成"
[ -x "$R/scripts/size_guard.sh" ] && bash "$R/scripts/size_guard.sh" "$R"
echo "同期完了(削除なし): $S → $R"
