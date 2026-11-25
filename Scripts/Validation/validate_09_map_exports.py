import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import config,path,outdir

def main():

    d=outdir("Maps")
    for n in ["Local_MoransI_Cluster_Map.png","Local_MoransI_Cluster_Map.pdf"]:
        p=d/n; print("PASS" if p.exists() and p.stat().st_size else "FAIL",p)
        if not p.exists() or not p.stat().st_size: raise SystemExit(1)

if __name__=="__main__": main()
