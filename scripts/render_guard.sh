#!/bin/bash
# レンダ撮影スクリプトの二重起動ガード(stock_cfg.json を奪い合って構成が乱れるのを防ぐ)。
# 使い方: スクリプト冒頭で `source /home/user/train01/scripts/render_guard.sh` する。
# 別の main.py が動いている間は起動せず、終了コード 3 で止める(待つ場合は先に Monitor で終了を確認する)。
if pgrep -f "[p]ython3 main.py" > /dev/null; then
  echo "別のレンダ(main.py)が実行中のため起動しません。終了を待ってから再実行してください。" >&2
  exit 3
fi
