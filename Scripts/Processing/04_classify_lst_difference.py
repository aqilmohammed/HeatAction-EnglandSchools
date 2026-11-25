import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

"""Create a configurable equal-frequency classification of valid LST differences."""
import numpy as np
import rasterio
from common import config,outdir

def main():
    c=config(); classes=int(c["classification"]["classes"]); r=c["raster"]; d=outdir("Raster")
    srcpath=d/r["difference_output"]
    with rasterio.open(srcpath) as src:
        a=src.read(1).astype("float32"); valid=src.read_masks(1)>0
        if src.nodata is not None: valid &= a!=src.nodata
        valid &= np.isfinite(a); vals=a[valid]
        if vals.size<classes: raise ValueError("Insufficient valid pixels.")
        cuts=np.quantile(vals,np.linspace(0,1,classes+1)[1:-1])
        out=np.zeros(a.shape,dtype="uint8"); out[valid]=np.digitize(vals,cuts)+1
        profile=src.profile.copy()
    profile.update(dtype="uint8",count=1,nodata=0,compress="deflate")
    name=f"LST_Change_Classification_{classes}Classes.tif"
    with rasterio.open(d/name,"w",**profile) as ds: ds.write(out,1)
    print("Class breaks:",cuts,"Output:",d/name)
if __name__=="__main__": main()
