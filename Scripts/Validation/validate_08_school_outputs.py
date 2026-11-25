import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import config,path,outdir
import pandas as pd, geopandas as gpd
def main():

    v=outdir("Vector"); t=outdir("Tables")
    for p in [v/"Schools_Priority_Assigned.gpkg",v/"School_Buffers.gpkg"]:
        g=gpd.read_file(p); print("PASS",p,"features",len(g))
    p=t/"Priority1_School_Buffer_Ranking.csv"; df=pd.read_csv(p); print("PASS",p,"rows",len(df))

if __name__=="__main__": main()
