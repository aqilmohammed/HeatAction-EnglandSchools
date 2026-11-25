import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import config,path,outdir
import rasterio
def main():

    p=outdir("Raster")/"LST_Moran_Input.tif"
    with rasterio.open(p) as ds:
        a=ds.read(1,masked=True).compressed()
        print("PASS" if a.size else "FAIL",p,"valid",a.size,"shape",ds.shape,"CRS",ds.crs)
        if not a.size: raise SystemExit(1)

if __name__=="__main__": main()
