"""Exercise the installed wheel's actual console entry point outside this checkout."""
import hashlib, json, os, pathlib, shutil, sqlite3, subprocess, sys, tempfile

SOURCE=pathlib.Path(__file__).absolute().parent
PYTHON=pathlib.Path(sys.argv[1]).absolute()  # Do not resolve a venv symlink to its base interpreter.
COMMAND=PYTHON.parent / ("bom-rollup-ledger.exe" if os.name=="nt" else "bom-rollup-ledger")
CASES=0
def run(args, expected=0, data=True):
    global CASES
    p=subprocess.run([str(COMMAND), *map(str,args)],cwd=WORK,text=True,capture_output=True,timeout=30)
    assert p.returncode==expected, (args,p.returncode,p.stdout,p.stderr)
    CASES+=1
    if expected==2:
        assert not p.stdout and p.stderr, (args,p.stdout,p.stderr)
        return None
    return json.loads(p.stdout) if data else p.stdout

with tempfile.TemporaryDirectory(prefix="installed-command-") as tmp:
    WORK=pathlib.Path(tmp)
    assert not WORK.is_relative_to(SOURCE)
    env=subprocess.run([str(PYTHON),"-c","import bom_rollup_ledger; print(bom_rollup_ledger.__file__)"],cwd=WORK,text=True,capture_output=True,check=True)
    installed=pathlib.Path(env.stdout.strip()).absolute()
    assert not installed.is_relative_to(SOURCE), installed
    assert installed.read_bytes()==(SOURCE/"bom_rollup_ledger.py").read_bytes()
    run(["--help"],data=False)
    for name in ("example-bom.csv","example-costs.csv"): shutil.copyfile(SOURCE/name,WORK/name)
    args=["example-bom.csv","example-costs.csv","--root","R","--quantity","2"]
    r=run(args)
    assert r["leaves"][0]["quantity"]=="4.6" and r["total_material_cost"]=="11.5"
    (WORK/"example-costs.csv").write_text("part,unit_cost\n")
    r=run(args,1); assert r["total_material_cost"] is None and r["missing_prices"]==["L"]
    (WORK/"example-bom.csv").write_text("parent,component,quantity\nR,R,1\n")
    run(args,2)
    (WORK/"example-bom.csv").write_text("parent,component,quantity\nR,L,1,extra\n")
    run(args,2)
    (WORK/"example-bom.csv").write_bytes(b"x"*(2*1024*1024+1));run(args,2)
print(json.dumps({"installed_command":"bom-rollup-ledger","cases":CASES,"module_bytes_match_source":True,"outside_checkout":True,"python":subprocess.check_output([str(PYTHON),"--version"],text=True).strip()}))
