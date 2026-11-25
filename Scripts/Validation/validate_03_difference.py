import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import config,path,outdir
import rasterio, numpy as np
def main():

    p=outdir("Raster")/config()["raster"]["difference_output"]
    with rasterio.open(p) as ds:
        a=ds.read(1,masked=True).compressed()
        if not a.size: print("FAIL: no valid pixels"); raise SystemExit(1)
        print("PASS",p,"valid",a.size,"min",a.min(),"max",a.max(),"mean",a.mean())
        print("Positive %",100*(a>0).mean(),"negative %",100*(a<0).mean(),"zero %",100*(a==0).mean())

if __name__=="__main__": main()
