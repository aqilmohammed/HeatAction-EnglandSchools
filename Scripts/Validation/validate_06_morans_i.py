import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import outdir
import rasterio, numpy as np
def main():
    d=outdir("Raster")
    for n in ["Local_MoransI.tif","Local_MoransI_Cluster.tif"]:
        with rasterio.open(d/n) as ds:
            a=ds.read(1); valid=(a!=ds.nodata) if ds.nodata is not None else np.isfinite(a)
            vals,counts=np.unique(a[valid],return_counts=True)
            print("PASS",n,"valid",int(valid.sum()),"values",dict(zip(vals.tolist(),counts.tolist())))
            if n.endswith("Cluster.tif") and not set(vals.tolist()).issubset({0,1,2,3,4}):
                print("FAIL: unexpected cluster codes"); raise SystemExit(1)
if __name__=="__main__": main()
