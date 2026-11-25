import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

"""Calculate HH-cluster coverage by small area and join deprivation attributes."""
import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape
from common import config,path,outdir

def main():
    c=config(); s=c["small_areas"]; v=outdir("Vector")
    with rasterio.open(outdir("Raster")/"Local_MoransI_Cluster.tif") as ds:
        a=ds.read(1); geoms=[shape(g) for g,val in shapes(a,mask=(a==1),transform=ds.transform) if val==1]
        hh=gpd.GeoDataFrame({"HH":[1]*len(geoms)},geometry=geoms,crs=ds.crs)
    areas=gpd.read_file(path(c["paths"]["small_areas"]))
    if areas.crs!=hh.crs: areas=areas.to_crs(hh.crs)
    code=s["area_code_field"]
    areas["AREA_M2"]=areas.geometry.area
    inter=gpd.overlay(areas[[code,"AREA_M2","geometry"]],hh,how="intersection")
    inter["HH_M2"]=inter.geometry.area
    sums=inter.groupby(code)["HH_M2"].sum()
    areas["HH_M2"]=areas[code].map(sums).fillna(0)
    areas["HH_PCT"]=(areas["HH_M2"]/areas["AREA_M2"]*100).clip(0,100)
    dep=pd.read_csv(path(c["paths"]["deprivation_csv"]))
    areas=areas.merge(dep,left_on=code,right_on=s["deprivation_code_field"],how="left")
    dec=s["deprivation_decile_field"]; t=float(s["hh_threshold_percent"])
    areas["PRIORITY"]=0; eligible=areas["HH_PCT"]>=t
    areas.loc[eligible & (areas[dec]<=s["most_deprived_max_decile"]),"PRIORITY"]=1
    areas.loc[eligible & (areas[dec]>s["most_deprived_max_decile"]) & (areas[dec]<s["least_deprived_min_decile"]),"PRIORITY"]=2
    areas.loc[eligible & (areas[dec]>=s["least_deprived_min_decile"]),"PRIORITY"]=3
    areas.loc[areas[dec].isna(),"PRIORITY"]=-1
    areas.to_file(v/"Priority_Areas.gpkg",layer="priority_areas",driver="GPKG")
    print("Created",v/"Priority_Areas.gpkg")
if __name__=="__main__": main()
