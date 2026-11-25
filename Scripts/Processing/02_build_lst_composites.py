#!/usr/bin/env python3
"""Build per-pixel median composites in blocks to limit RAM use."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import rasterio
from common import config, path, outdir

def composite(files, destination, nodata, block_rows=256):
    if not files:
        raise FileNotFoundError(f"No scene rasters found for {destination.name}")
    opened=[]
    try:
        for f in files: opened.append(rasterio.open(f))
        ref=opened[0]
        grid=(ref.crs, ref.transform, ref.width, ref.height)
        for ds in opened[1:]:
            if (ds.crs, ds.transform, ds.width, ds.height)!=grid:
                raise ValueError(f"Scene grid mismatch: {ds.name}. Reproject/align before compositing.")
        profile=ref.profile.copy(); profile.update(dtype="float32",count=1,nodata=nodata,compress="deflate",tiled=True)
        destination.parent.mkdir(parents=True,exist_ok=True)
        with rasterio.open(destination,"w",**profile) as out:
            for row in range(0,ref.height,block_rows):
                height=min(block_rows,ref.height-row); window=rasterio.windows.Window(0,row,ref.width,height)
                stack=[]
                for ds in opened:
                    a=ds.read(1,window=window).astype("float32")
                    m=ds.read_masks(1,window=window)>0
                    if ds.nodata is not None: m &= a!=ds.nodata
                    m &= np.isfinite(a); a[~m]=np.nan; stack.append(a)
                with np.errstate(all="ignore"): med=np.nanmedian(np.stack(stack,axis=0),axis=0)
                out.write(np.where(np.isfinite(med),med,nodata).astype("float32"),1,window=window)
        print(f"{len(files)} scenes -> {destination}")
    finally:
        for ds in opened: ds.close()

def main():
    c=config(); r=c["raster"]; folder=path(c["paths"]["landsat_dir"]); o=outdir("Raster")
    baseline=sorted(folder.rglob(r["baseline_pattern"])); recent=sorted(folder.rglob(r["recent_pattern"]))
    composite(baseline,o/r["baseline_output"],r["nodata"])
    composite(recent,o/r["recent_output"],r["nodata"])
if __name__=="__main__": main()
