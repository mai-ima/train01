#!/bin/bash
# 作業ディレクトリ → repo への「一方向・非破壊」同期(削除なし)。 使い方: bash scripts/sync_safe.sh [作業=/home/claude/station] [repo=このリポジトリ]
S="${1:-/home/claude/station}"; R="${2:-$(cd "$(dirname "$0")/.." && pwd)}"
cp -u "$S"/*.py "$R/src/" 2>/dev/null
for f in "$S"/*.sh; do b=$(basename "$f"); [ "$b" = "sync_repo.sh" ] || cp -u "$f" "$R/scripts/"; done
rsync -a --exclude='__pycache__' --exclude='*.blend*' --exclude='*.png' "$S/net/" "$R/net/" 2>/dev/null || cp -ru "$S/net/." "$R/net/"
[ -d "$S/tex" ] && mkdir -p "$R/assets/textures" && cp -ru "$S/tex/." "$R/assets/textures/"
echo "同期完了(削除なし): $S → $R"
