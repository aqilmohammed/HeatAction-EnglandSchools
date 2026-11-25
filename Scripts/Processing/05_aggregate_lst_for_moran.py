#!/usr/bin/env python3
"""Aggregate valid LST differences using masked averaging."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import rasterio
from rasterio.enums import Resampling
from common import config,outdir

def main():
    c=config(); factor=int(c["moran"]["aggregation_factor"]); r=c["raster"]; d=outdir("Raster")
    if factor<1: raise ValueError("aggregation_factor must be >= 1")
    with rasterio.open(d/r["difference_output"]) as src:
        w=(src.width+factor-1)//factor; h=(src.height+factor-1)//factor
        profile=src.profile.copy(); profile.update(width=w,height=h,transform=src.transform*src.transform.scale(src.width/w,src.height/h),dtype="float32",count=1,nodata=r["nodata"],compress="deflate")
        # Rasterio's average resampling averages valid source pixels; masked/Nodata cells do not contribute.
        a=src.read(1,out_shape=(h,w),resampling=Resampling.average,masked=True).astype("float32")
        out=np.where(np.ma.getmaskarray(a),r["nodata"],a.filled(r["nodata"])).astype("float32")
    with rasterio.open(d/"LST_Moran_Input.tif","w",**profile) as dst: dst.write(out,1)
    print("Created",d/"LST_Moran_Input.tif")
if __name__=="__main__": main()
