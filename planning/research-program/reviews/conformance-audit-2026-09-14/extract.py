import sys, fitz
path=sys.argv[1]; rng=sys.argv[2]
a,_,b=rng.partition('-'); a=int(a); b=int(b or a)
d=fitz.open(path)
for i in range(a-1, min(b, d.page_count)):
    print(f"===== p.{i+1} =====")
    print(d[i].get_text())
