import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import config,path,outdir
import geopandas as gpd
def main():

    p=outdir("Vector")/"Priority_Areas.gpkg"; g=gpd.read_file(p)
    missing={"PRIORITY","HH_PCT"}-set(g.columns)
    print("PASS" if not missing else "FAIL","features",len(g),"priority counts",g["PRIORITY"].value_counts(dropna=False).to_dict())
    if missing: raise SystemExit(1)

if __name__=="__main__": main()
