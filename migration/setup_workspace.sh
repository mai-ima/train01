#!/bin/bash
# リポジトリ形式(src/ scripts/ data/ net/ assets/) → 作業形式(フラット)へ展開する。冪等。
# 使い方: リポジトリ直下で  bash migration/setup_workspace.sh [展開先=/home/claude/station]
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
DST="${1:-/home/claude/station}"
echo "リポジトリ: $REPO → 作業: $DST"
mkdir -p "$DST/out" "$DST/net"
cp -n "$REPO"/src/*.py "$DST"/ 2>/dev/null || true
cp -n "$REPO"/scripts/*.sh "$DST"/ 2>/dev/null || true
cp -n "$REPO"/data/*.json "$DST"/ 2>/dev/null || true
cp -rn "$REPO"/net/. "$DST/net/" 2>/dev/null || true
[ -d "$REPO/assets/hdri" ] && mkdir -p "$DST/hdri" && cp -rn "$REPO"/assets/hdri/. "$DST/hdri/"
[ -d "$REPO/assets/textures" ] && mkdir -p "$DST/tex" && cp -rn "$REPO"/assets/textures/. "$DST/tex/"
[ -d "$REPO/assets/pbr_textures" ] && mkdir -p "$DST/pbr" && cp -rn "$REPO"/assets/pbr_textures/. "$DST/pbr/"
[ -d "$REPO/assets/candidates" ] && mkdir -p "$DST/cand" && cp -rn "$REPO"/assets/candidates/. "$DST/cand/"
[ -d "$REPO/viewer" ] && mkdir -p "$DST/viewer" && cp -rn "$REPO"/viewer/. "$DST/viewer/"
cp -n "$REPO"/README.md "$DST"/ 2>/dev/null || true
cp -n "$REPO"/docs/audit_rubric.md "$REPO"/docs/RECOVERY.md "$DST"/ 2>/dev/null || true
cp -rn "$REPO"/migration "$DST"/ 2>/dev/null || true
# CLAUDE.md は作業側が無ければコピー(上書きしない)
[ -f "$DST/CLAUDE.md" ] || cp "$REPO/CLAUDE.md" "$DST/CLAUDE.md"
# パス置換(/home/claude/station と /home/claude/train01 を現環境に合わせる)
if [ "$DST" != "/home/claude/station" ] || [ "$REPO" != "/home/claude/train01" ]; then
  echo "パス置換: /home/claude/station→$DST, /home/claude/train01→$REPO"
  grep -rlE "/home/claude/(station|train01)" "$DST" --include=*.py --include=*.sh 2>/dev/null | while read f; do
    sed -i "s#/home/claude/station#$DST#g; s#/home/claude/train01#$REPO#g" "$f"
  done
fi
# 依存確認
python3 - <<'P'
import importlib
for m in ("bpy","PIL","numpy"):
    try: importlib.import_module(m); print("OK ",m)
    except Exception as e: print("NG ",m,e,"→ pip install --break-system-packages",{"PIL":"pillow"}.get(m,m))
try:
    import bpy; print("Blender",bpy.app.version_string)
except Exception: pass
P
echo "完了。次: cd $DST && cat migration/HANDOFF.md ; python3 main.py --zone SH04 --parts none --cam ZA --w 400 --samples 4 --out smoke"
