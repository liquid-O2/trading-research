import os, resource, subprocess, sys, json, time
W = "/workspace/implementation/reports/research-work/P15-16A/_work_r3"
env = dict(os.environ, PYTHONPATH="src")
started = time.time()
with open(f"{W}/produce.log", "wb") as log:
    rc = subprocess.call(
        ["/workspace/implementation/.venv/bin/python", "tools/produce_p15_16a.py"],
        cwd="/workspace/implementation", env=env, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
    )
ru = resource.getrusage(resource.RUSAGE_CHILDREN)
open(f"{W}/produce.rss.json", "w").write(json.dumps({
    "exit_code": rc,
    "ru_maxrss_kb": ru.ru_maxrss,
    "ru_maxrss_gb": round(ru.ru_maxrss / 1048576, 3),
    "wall_seconds": round(time.time() - started, 1),
}, indent=2) + "\n")
print("produce exit", rc, "peak child RSS GB", round(ru.ru_maxrss / 1048576, 3))
