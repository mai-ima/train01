#!/bin/bash
# 【S-Q7】リポジトリ肥大のガード: コミット前に実行。.git が 900MB を超える/20MB超のファイル/1MB超のPNG(作業画像)があれば警告。
R="${1:-/home/user/train01}"; cd "$R" || exit 1
g=$(du -sm .git | cut -f1); echo ".git = ${g}MB (GitHub 推奨上限 ~1GB)"; [ "$g" -gt 900 ] && echo "警告: 上限に近い。作業画像は JPEG(q85)のみコミットし、新規の大きなバイナリを控える"
git status --short | awk '{print $NF}' | while read f; do [ -f "$f" ] || continue; s=$(du -k "$f" | cut -f1)
  [ "$s" -gt 20480 ] && echo "警告: ${s}KB $f (20MB超)"
  case "$f" in renders/work/*.png) [ "$s" -gt 1024 ] && echo "警告: 作業画像は JPEG で(PNG ${s}KB: $f)";; esac; done
exit 0
