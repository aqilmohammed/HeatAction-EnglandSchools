import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

"""Export Local Moran cluster raster as PNG and PDF."""
import geopandas as gpd
import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show
from matplotlib.colors import ListedColormap,BoundaryNorm
from common import config,path,outdir

def main():
    c=config(); boundary=gpd.read_file(path(c["paths"]["study_area"]))
    p=outdir("Raster")/"Local_MoransI_Cluster.tif"; maps=outdir("Maps")
    with rasterio.open(p) as ds:
        if boundary.crs!=ds.crs: boundary=boundary.to_crs(ds.crs)
        fig,ax=plt.subplots(figsize=(12,9))
        cmap=ListedColormap(["#e6e6e6","#d7191c","#fdae61","#2c7bb6","#984ea3"])
        show(ds,ax=ax,cmap=cmap,vmin=0,vmax=4)
        boundary.boundary.plot(ax=ax,color="black",linewidth=.35)
        ax.set_title("Local Moran's I Cluster Analysis"); ax.set_axis_off()
        fig.tight_layout()
        fig.savefig(maps/"Local_MoransI_Cluster_Map.png",dpi=300,bbox_inches="tight")
        fig.savefig(maps/"Local_MoransI_Cluster_Map.pdf",bbox_inches="tight")
        plt.close(fig)
    print("Map exports saved in",maps)
if __name__=="__main__": main()
