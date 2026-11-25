#!/usr/bin/env python3
"""Global and local Moran's I on valid raster cells with rook adjacency.
NoData holes are supported: neighbours are built only between valid cells.
Isolated cells (no neighbours) are left NoData in the local outputs.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import rasterio
from libpysal.weights import W
from esda.moran import Moran, Moran_Local
from statsmodels.stats.multitest import multipletests
from common import config,outdir

def main():
    c=config(); m=c["moran"]; d=outdir("Raster"); source=d/"LST_Moran_Input.tif"
    with rasterio.open(source) as ds:
        values=ds.read(1).astype("float64"); valid=ds.read_masks(1)>0
        if ds.nodata is not None: valid &= values!=ds.nodata
        valid &= np.isfinite(values)
        rows,cols=np.where(valid)
        if not len(rows): raise ValueError("No valid input cells.")
        # Build cell ID lookup; edges connect orthogonal valid neighbours only.
        cell_ids=np.full(values.shape,-1,dtype="int64"); cell_ids[valid]=np.arange(valid.sum())
        neighbours={}; ids=[]
        for r,col in zip(rows,cols):
            i=int(cell_ids[r,col]); ns=[]
            for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)):
                nr,nc=r+dr,col+dc
                if 0<=nr<values.shape[0] and 0<=nc<values.shape[1] and valid[nr,nc]: ns.append(int(cell_ids[nr,nc]))
            if ns: neighbours[i]=ns; ids.append(i)
        if len(ids)<3: raise ValueError("Too few non-isolated valid cells for Moran's I.")
        # Remove isolated cells from the statistic, but retain them as NoData in output.
        ids_arr=np.asarray(ids,dtype=int); y=values[rows,cols]
        id_to_value={int(cell_ids[r,col]):values[r,col] for r,col in zip(rows,cols)}
        y_used=np.asarray([id_to_value[i] for i in ids],dtype=float)
        w=W(neighbours,ids=ids,silence_warnings=True); w.transform="R"
        global_m=Moran(y_used,w,permutations=int(m["permutations"]))
        local=Moran_Local(y_used,w,permutations=int(m["permutations"]),seed=12345)
        significant,_,_,_=multipletests(local.p_sim,alpha=float(m["fdr_alpha"]),method="fdr_bh")
        category=np.where(significant,local.q,0).astype("uint8")
        stat_out=np.full(values.shape,c["raster"]["nodata"],dtype="float32")
        cat_out=np.full(values.shape,255,dtype="uint8")
        for pos,cell in enumerate(ids):
            r,col=rows[cell],cols[cell]
            stat_out[r,col]=local.Is[pos]; cat_out[r,col]=category[pos]
        profile=ds.profile.copy()
    profile.update(count=1,compress="deflate",dtype="float32",nodata=c["raster"]["nodata"])
    with rasterio.open(d/"Local_MoransI.tif","w",**profile) as out: out.write(stat_out,1)
    profile.update(dtype="uint8",nodata=255)
    with rasterio.open(d/"Local_MoransI_Cluster.tif","w",**profile) as out: out.write(cat_out,1)
    text=(f"Global Moran's I: {global_m.I}\nExpected I: {global_m.EI}\nPermutation p-value: {global_m.p_sim}\n"
          f"Permutations: {m['permutations']}\nNeighbourhood: rook (4-neighbour)\nFDR alpha: {m['fdr_alpha']}\n"
          f"Valid cells: {int(valid.sum())}\nCells included (non-isolated): {len(ids)}\nIsolated cells: {int(valid.sum()-len(ids))}\n"
          f"Significant local cells after FDR: {int(significant.sum())}\n")
    (d/"MoransI_Summary.txt").write_text(text,encoding="utf-8"); print(text)
if __name__=="__main__": main()
