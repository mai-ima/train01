"""【S-Q7】静かな失敗の検出: ビルド/レンダのログを走査し、failed / Traceback / Error を報告する(既知の無害な行は除外)。
使い方: python3 healthscan.py out/e3b/*.log      終了コード: 0=問題なし / 1=問題あり。
背景: 例外を握りつぶして print だけで続行する箇所(stock failed / concourse failed 等)があり、停車車両が全駅で置かれない状態に長期間気付けなかったため。"""
import re, sys, glob
BAD = re.compile(r"(Traceback|[A-Za-z_ ]+ failed|Error:|error with argument|NameError|AttributeError|KeyError|TypeError|ValueError)")
OK = re.compile(r"CUEW initialization failed|use_nodes|DeprecationWarning")
def scan(path):
    out = []
    for n, l in enumerate(open(path, errors="ignore"), 1):
        if BAD.search(l) and not OK.search(l):
            out.append((n, l.strip()[:160]))
    return out
files = sorted({f for a in sys.argv[1:] for f in glob.glob(a)})
bad = 0
for f in files:
    r = scan(f)
    if r:
        bad += 1
        print(f"NG {f}")
        for n, l in r[:5]:
            print(f"   {n}: {l}")
print(f"健全性: {len(files)}ログ中 問題あり {bad}")
sys.exit(1 if bad else 0)
