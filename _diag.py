import sys, tempfile, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import complexity_budget_gate as cbg

TMP = tempfile.mkdtemp()

def w(n, t):
    p = os.path.join(TMP, n)
    with open(p, "w", encoding="utf-8") as f:
        f.write(t)
    return p

NL = chr(10)
BR = ("def g(x):" + NL
      + "    if x > 0:" + NL
      + "        if x > 10:" + NL
      + "            return 2" + NL
      + "        return 1" + NL
      + "    for i in range(x):" + NL
      + "        if i:" + NL
      + "            x += 1" + NL
      + "    return x and x or 0" + NL)
print("branchy:", cbg.file_complexities(w("br.py", BR)))

big = "def big(x):" + NL + "    y = x" + NL
try:
    print("big:", cbg.file_complexities(w("big.py", big)))
except Exception as e:
    print("big ERR:", type(e).__name__, str(e)[:120])

dn = ("def long_cond(a, b, c, d):" + NL
      + "    return a and b and c and d and a or b or c or d" + NL)
print("dense:", cbg.file_complexities(w("d.py", dn)))
