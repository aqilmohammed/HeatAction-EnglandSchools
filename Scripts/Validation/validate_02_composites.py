import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import config,path,outdir
import rasterio
def main():

    d=outdir("Raster"); names=[config()["raster"]["baseline_output"],config()["raster"]["recent_output"]]
    opened=[]
    for n in names:
        with rasterio.open(d/n) as ds: opened.append((ds.crs,ds.transform,ds.width,ds.height)); print("PASS",n,ds.crs,ds.shape)
    if opened[0]!=opened[1]: print("FAIL: composite grids differ"); raise SystemExit(1)

if __name__=="__main__": main()
