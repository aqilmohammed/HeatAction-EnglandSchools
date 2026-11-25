import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import config,path,outdir
import rasterio, numpy as np
def main():

    c=config(); folder=path(c["paths"]["landsat_dir"])
    fs=sorted(folder.rglob("lst_*_scene*.tif"))
    if not fs: print("FAIL: no scene LST files found"); raise SystemExit(1)
    grids=set()
    for f in fs:
        with rasterio.open(f) as ds:
            a=ds.read(1,masked=True).compressed()
            print(("PASS" if a.size else "FAIL"),f,"valid",a.size,"CRS",ds.crs,"shape",ds.shape)
            grids.add((str(ds.crs),ds.transform.a,ds.transform.e))
            if not a.size: raise SystemExit(1)
    if len(grids)>1: print("WARN: scene rasters use different grids; align before compositing.")

if __name__=="__main__": main()
