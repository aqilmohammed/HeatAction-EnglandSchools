import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

"""Calculate recent median minus baseline median in degrees Celsius."""
import numpy as np
import rasterio
from common import config,outdir

def main():
    c=config(); r=c["raster"]; d=outdir("Raster")
    with rasterio.open(d/r["baseline_output"]) as b, rasterio.open(d/r["recent_output"]) as n:
        if (b.crs,b.transform,b.width,b.height)!=(n.crs,n.transform,n.width,n.height):
            raise ValueError("Composite rasters must have identical grids.")
        x=b.read(1).astype("float32"); y=n.read(1).astype("float32")
        valid=(b.read_masks(1)>0)&(n.read_masks(1)>0)
        if b.nodata is not None: valid &= x!=b.nodata
        if n.nodata is not None: valid &= y!=n.nodata
        valid &= np.isfinite(x)&np.isfinite(y)
        z=np.where(valid,y-x,r["nodata"]).astype("float32")
        profile=b.profile.copy()
    profile.update(dtype="float32",count=1,nodata=r["nodata"],compress="deflate")
    with rasterio.open(d/r["difference_output"],"w",**profile) as ds: ds.write(z,1)
    print("Created recent-minus-baseline LST difference:",d/r["difference_output"])
if __name__=="__main__": main()
