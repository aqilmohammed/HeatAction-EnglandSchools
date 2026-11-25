import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

"""Spatially assign school points, create buffers and rank valid buffer means."""
import geopandas as gpd
import pandas as pd
import rasterio
from rasterstats import zonal_stats
from common import config,path,outdir

def main():
    c=config(); s=c["schools"]; v=outdir("Vector"); t=outdir("Tables")
    src=path(c["paths"]["schools_file"])
    if src.suffix.lower()==".csv":
        df=pd.read_csv(src)
        schools=gpd.GeoDataFrame(df,geometry=gpd.points_from_xy(df[s["x_field"]],df[s["y_field"]]),crs=s["source_crs"])
    else: schools=gpd.read_file(src)
    priority=gpd.read_file(v/"Priority_Areas.gpkg")
    schools=schools.to_crs(priority.crs)
    joined=gpd.sjoin(schools,priority[["PRIORITY","geometry"]],how="left",predicate="within")
    joined.to_file(v/"Schools_Priority_Assigned.gpkg",layer="schools",driver="GPKG")
    buffers=joined.copy(); buffers["geometry"]=buffers.geometry.buffer(float(s["buffer_distance_m"]))
    buffers.to_file(v/"School_Buffers.gpkg",layer="buffers",driver="GPKG")
    raster=outdir("Raster")/c["raster"]["difference_output"]
    with rasterio.open(raster) as ds:
        b=buffers.to_crs(ds.crs)
        zs=zonal_stats(b.geometry,raster,stats=["mean","count"],nodata=ds.nodata)
    buffers["LST_mean"]=[x.get("mean") for x in zs]
    buffers["LST_count"]=[x.get("count") for x in zs]
    ranked=buffers[(buffers["PRIORITY"]==1)&(buffers["LST_count"].fillna(0)>0)].sort_values("LST_mean",ascending=False).head(int(s["top_n"]))
    ranked.drop(columns="geometry").to_csv(t/"Priority1_School_Buffer_Ranking.csv",index=False)
    print("School point join, buffers and ranking complete.")
if __name__=="__main__": main()
