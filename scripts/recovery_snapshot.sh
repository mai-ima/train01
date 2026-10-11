#!/bin/bash
# 圧縮直後に1回実行: 回復に必要な情報を一括表示(CLAUDE.md末尾・状態ファイル・直近ユーザー指示・git・実行中ジョブ・直近出力)
echo "=== CLAUDE.md 末尾60行 ==="; tail -60 /home/claude/train01/CLAUDE.md
echo; echo "=== session_state.md 末尾50行 ==="; tail -50 /home/claude/station/net/session_state.md
echo; echo "=== 直近のユーザー発言(会話ログ) ==="
J=$(ls -t /root/.claude/projects/-home-claude*/*.jsonl | head -1)
python3 - "$J" <<'PY'
import sys,json
import re
rows=[]
for l in open(sys.argv[1],errors='ignore'):
    try:d=json.loads(l)
    except: continue
    m=d.get('message') or {}
    if m.get('role')!='user': continue
    c=m.get('content')
    if isinstance(c,list): c=' '.join(x.get('text','') for x in c if isinstance(x,dict) and x.get('type')=='text')
    if not isinstance(c,str): continue
    c=re.sub(r'<system-reminder>.*?</system-reminder>','',c,flags=re.S).strip()
    if not c or c.startswith('This session is being continued'): continue
    rows.append((d.get('timestamp','')[:19],c[:260]))
for t,c in rows[-15:]: print(t,c.replace('\n',' '))
PY
echo; echo "=== git ==="; git -C /home/claude/train01 status --short | head -20; git -C /home/claude/train01 log --oneline | head -3
echo; echo "=== 実行中ジョブ(blender/python3) ==="; pgrep -ax python3 | head; pgrep -ax blender | head
echo; echo "=== 最近更新されたファイル ==="; ls -t /home/claude/station/out | head -8; ls -t /home/claude/station/net | head -8
echo; echo "次: TaskList を確認 → 一言「回復完了」を SendUserMessage"
