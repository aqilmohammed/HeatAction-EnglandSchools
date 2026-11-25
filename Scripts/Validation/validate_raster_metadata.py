"""Read-only general raster metadata/valid-data validator."""
import argparse
import rasterio
import numpy as np
def main():
    p=argparse.ArgumentParser(); p.add_argument("rasters",nargs="+"); a=p.parse_args()
    failed=False
    for f in a.rasters:
        try:
            with rasterio.open(f) as ds:
                x=ds.read(1,masked=True).compressed(); ok=x.size>0
                print(("PASS" if ok else "FAIL"),f)
                print(f" CRS={ds.crs}; shape={ds.shape}; resolution={ds.res}; nodata={ds.nodata}; valid={x.size}")
                if ok: print(f" min={x.min():.4f}; max={x.max():.4f}; mean={x.mean():.4f}")
                failed|=not ok
        except Exception as e: print("FAIL",f,e); failed=True
    raise SystemExit(1 if failed else 0)
if __name__=="__main__": main()
