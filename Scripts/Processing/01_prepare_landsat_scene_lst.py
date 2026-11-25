import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

"""Convert Landsat 8/9 Collection 2 Level-2 ST_B10 DN to Celsius LST."""
import argparse
import numpy as np
import rasterio

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--st",required=True,help="ST_B10 GeoTIFF")
    p.add_argument("--out",required=True,help="Output scene LST GeoTIFF")
    p.add_argument("--qa",help="Optional QA_PIXEL GeoTIFF")
    p.add_argument("--mask-clouds",action="store_true")
    a=p.parse_args()
    with rasterio.open(a.st) as src:
        dn=src.read(1).astype("float32"); valid=src.read_masks(1)>0
        # Landsat Collection 2 Level-2 ST_B10 scale and offset.
        lst=dn*0.00341802+149.0-273.15
        valid &= dn>0
        if a.mask_clouds:
            if not a.qa: raise ValueError("--mask-clouds requires --qa")
            with rasterio.open(a.qa) as qsrc:
                if (qsrc.crs,qsrc.transform,qsrc.shape)!=(src.crs,src.transform,src.shape):
                    raise ValueError("QA_PIXEL grid differs from ST_B10.")
                qa=qsrc.read(1)
            # Fill, dilated cloud, cirrus, cloud, cloud shadow and snow.
            bad=sum(1<<bit for bit in (0,1,2,3,4,5))
            valid &= (qa & bad)==0
        nodata=src.nodata if src.nodata is not None else -9999.0
        out=np.where(valid & np.isfinite(lst),lst,nodata).astype("float32")
        profile=src.profile.copy()
    profile.update(dtype="float32",count=1,nodata=nodata,compress="deflate")
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    with rasterio.open(a.out,"w",**profile) as dst: dst.write(out,1)
    print("Created",a.out)
if __name__=="__main__": main()
