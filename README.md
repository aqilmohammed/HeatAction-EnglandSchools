# HeatAction - EnglandSchools

Reusable Python workflow for assessing changes in satellite-derived land surface temperature (LST), identifying spatial clusters, overlaying them with area-level deprivation, and examining school locations in priority areas.

**This repository contains code and workflow documentation only. Source datasets and example rasters are intentionally excluded.** Obtain the data from official providers and store them locally.

## Folder structure

```text
HeatAction - EnglandSchools/
├── README.md
├── requirements.txt
├── .gitignore
├── Config/project_config.json
├── Data/
│   ├── Landsat/
│   ├── Boundaries/
│   ├── Deprivation/
│   └── Schools/
├── Scripts/
│   ├── common.py
│   ├── Processing/
│   └── Validation/
├── QGIS/
├── Outputs/
│   ├── Raster/
│   ├── Vector/
│   ├── Tables/
│   └── Maps/
└── Report/
```

## Official data sources

- Landsat Collection 2 Level-2: [USGS EarthExplorer](https://earthexplorer.usgs.gov/) and [USGS Landsat Collection 2](https://www.usgs.gov/landsat-missions/landsat-collection-2)
- Administrative and small-area boundaries: [ONS Open Geography Portal](https://geoportal.statistics.gov.uk/)
- Deprivation statistics: [IMD 2025: English Indices of Deprivation 2025](https://www.gov.uk/government/statistics/english-indices-of-deprivation-2025/)
- School locations: [Get Information About Schools](https://get-information-schools.service.gov.uk/)


Check release dates, licensing, metadata, field definitions and coverage before using any dataset. The scripts do not download source data.

## Required input file types and naming

### Landsat scene folders

Place each acquisition in its own folder below `Data/Landsat/`. Keep original downloaded files in that folder. The scene-level LST raster is also stored there.

```text
Data/Landsat/
├── scene1_2015aug15/
│   ├── original Landsat files...
│   └── lst_baseline_scene1.tif
├── scene2_2016jul05/
│   ├── original Landsat files...
│   └── lst_baseline_scene2.tif
└── scene1_2026aug11/
    ├── original Landsat files...
    └── lst_recent_scene1.tif
```

Naming convention:
- Baseline-period scene LST: `lst_baseline_scene<number>.tif`
- Recent-period scene LST: `lst_recent_scene<number>.tif`

The number identifies the scene within its period. The folder name should identify the acquisition, preferably with a scene number and date. Original provider filenames need not be renamed. The composite script searches recursively for the two LST patterns, so individual scene folders can remain separate.

The scene preparation script accepts Landsat Collection 2 Level-2 `ST_B10` and optional `QA_PIXEL` GeoTIFF bands and writes a Celsius LST GeoTIFF. Review the product metadata and quality-mask choices before applying it. The script does not discard negative LST differences or selectively exclude scenes based on their resulting values.

### Other required source files

| Input | Format | Minimum required content |
|---|---|---|
| Study-area boundary | GeoPackage (`.gpkg`) or Shapefile | Polygon geometry |
| Small-area boundaries | GeoPackage or Shapefile | Polygon geometry and unique area code |
| Deprivation data | CSV | Matching area code and deprivation decile (or adapt the script for another measure) |
| School locations | CSV or GeoPackage | School ID, school name and point coordinates/geometry |

Suggested local names:
- `Data/Boundaries/Study_Area.gpkg`
- `Data/Boundaries/Small_Areas.gpkg`
- `Data/Deprivation/Deprivation.csv`
- `Data/Schools/Schools.csv` or `Schools.gpkg`

Field names and paths are configured in `Config/project_config.json`. For CSV schools, provide coordinate columns and their source CRS.

### Main generated outputs

| Output | Format | Description |
|---|---|---|
| `LST_Baseline_Median.tif` | GeoTIFF | Per-pixel median of baseline scene rasters |
| `LST_Recent_Median.tif` | GeoTIFF | Per-pixel median of recent scene rasters |
| `LST_Increase.tif` | GeoTIFF | Recent median minus baseline median, in °C |
| `LST_Change_Classification_5Classes.tif` | GeoTIFF | Optional quantile classification |
| `LST_Moran_Input.tif` | GeoTIFF | Coarser raster for spatial autocorrelation |
| `Local_MoransI.tif` | GeoTIFF | Local Moran's I statistic |
| `Local_MoransI_Cluster.tif` | GeoTIFF | Cluster codes: 0 not significant, 1 HH, 2 LH, 3 LL, 4 HL |
| `Priority_Areas.gpkg` | GeoPackage | Small areas with cluster coverage, deprivation and priority |
| `Schools_Priority_Assigned.gpkg` | GeoPackage | School points joined to priority areas |
| `School_Buffers.gpkg` | GeoPackage | Configurable buffers around school points |
| `Priority1_School_Buffer_Ranking.csv` | CSV | Ranked school-buffer summaries |
| `Local_MoransI_Cluster_Map.png/.pdf` | PNG/PDF | Local cluster map exports |

Intermediate files are not prescribed unless a later step requires them. Keep scene rasters in their individual scene folders rather than creating duplicate copies in a central folder.

## Coordinate reference system and alignment

Set a projected CRS appropriate to the study area in the configuration. Area and distance operations must use a suitable projected CRS. All rasters used in pixel-wise calculations must have the same CRS, pixel size, grid alignment, dimensions and extent. Reproject/resample before differencing. The example configuration uses EPSG:27700 and 30 m; change these for other study areas.

## Run order

Run commands from the repository root:

```bash
python Scripts/Processing/01_prepare_landsat_scene_lst.py --st path/to/ST_B10.TIF --out path/to/lst_baseline_scene1.tif --qa path/to/QA_PIXEL.TIF --mask-clouds
python Scripts/Processing/02_build_lst_composites.py
python Scripts/Processing/03_calculate_lst_difference.py
python Scripts/Processing/04_classify_lst_difference.py
python Scripts/Processing/05_aggregate_lst_for_moran.py
python Scripts/Processing/06_run_morans_i.py
python Scripts/Processing/07_build_priority_areas.py
python Scripts/Processing/08_assign_schools_and_rank_buffers.py
python Scripts/Processing/09_export_local_morans_map.py
```

Run the matching scripts in `Scripts/Validation/` after each processing stage. Validation scripts are read-only and do not repair inputs. A general metadata validator is also provided: `Scripts/Validation/validate_raster_metadata.py`.

## Interpretation and limitations

- Satellite-derived LST is not air temperature and is not a direct measure of human heat exposure.
- Composite differences are estimates. Results can be influenced by seasonal sampling, acquisition time, cloud/quality screening, sensor and retrieval conditions, and data availability.
- Retain positive and negative differences unless a documented quality criterion justifies excluding a pixel or scene. Do not remove data simply because it produces a negative difference.
- Global Moran's I measures overall spatial autocorrelation. Local Moran's I identifies local clusters and spatial outliers relative to neighbouring cells. A significant high-high cluster represents a local grouping of relatively high values, not causation.
- Overlaying cluster coverage and deprivation is a prioritisation exercise. It does not, by itself, establish a correlation or causal relationship between deprivation and LST change.
- School point buffers are analytical neighbourhoods, not school property boundaries or schoolyards.
- Report data coverage, missingness, parameter choices, sensitivity checks and uncertainty with the results.

## Reproducibility

Record dataset versions and download dates, scene selection, quality-screening rules, CRS/grid settings, Moran's I weights and permutations, significance correction, area thresholds, buffer distance and ranking criteria. Review all validation reports before interpreting results.
