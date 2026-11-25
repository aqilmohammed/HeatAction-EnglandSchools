import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import config,path,outdir
import rasterio, numpy as np
def main():

    c=config(); p=outdir("Raster")/f"LST_Change_Classification_{int(c['classification']['classes'])}Classes.tif"
    with rasterio.open(p) as ds:
        vals=np.unique(ds.read(1)); allowed=set(range(1,int(c["classification"]["classes"])+1))|{0}
        print("PASS" if set(vals).issubset(allowed) else "FAIL","values",vals)
        if not set(vals).issubset(allowed): raise SystemExit(1)

if __name__=="__main__": main()
