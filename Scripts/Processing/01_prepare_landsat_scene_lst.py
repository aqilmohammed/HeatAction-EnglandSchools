
"""Convert Landsat 8/9 Collection 2 Level-2 ST_B10 DN to Celsius LST.

Filtering criterion:
    (QA_PIXEL & 191) == 0 AND ST_QA <= 500

Temperature conversion:
    ST_B10 * 0.00341802 + 149.0 - 273.15
"""

import argparse
from pathlib import Path

import numpy as np
import rasterio


def check_grid(reference, other, band_name):
    """Ensure all input bands use the same raster grid."""
    if (
        reference.crs != other.crs
        or reference.transform != other.transform
        or reference.shape != other.shape
    ):
        raise ValueError(
            f"{band_name} grid differs from ST_B10. "
            "All input bands must have matching CRS, "
            "dimensions and geotransform."
        )


def main():
    parser = argparse.ArgumentParser(
        description="Prepare Landsat surface temperature raster in Celsius."
    )

    parser.add_argument(
        "--st",
        required=True,
        help="Input ST_B10 GeoTIFF"
    )

    parser.add_argument(
        "--qa",
        required=True,
        help="Input QA_PIXEL GeoTIFF"
    )

    parser.add_argument(
        "--st-qa",
        required=True,
        help="Input ST_QA GeoTIFF"
    )

    parser.add_argument(
        "--out",
        required=True,
        help="Output LST GeoTIFF in Celsius"
    )

    args = parser.parse_args()

    with rasterio.open(args.st) as src:

        # Read original surface temperature band.
        dn = src.read(1).astype("float32")
        valid = src.read_masks(1) > 0

        # Read QA_PIXEL and check its grid.
        with rasterio.open(args.qa) as qa_src:

            check_grid(src, qa_src, "QA_PIXEL")

            qa = qa_src.read(1)

            valid &= qa_src.read_masks(1) > 0

        # Read ST_QA and check its grid.
        with rasterio.open(args.st_qa) as stqa_src:

            check_grid(src, stqa_src, "ST_QA")

            st_qa = stqa_src.read(1)

            valid &= stqa_src.read_masks(1) > 0

        # Apply the specified QA_PIXEL criterion.
        valid &= (qa & 191) == 0

        # Apply the specified ST_QA uncertainty threshold.
        valid &= st_qa <= 500

        # Exclude invalid ST_B10 values.
        valid &= dn > 0
        valid &= np.isfinite(dn)

        # Convert ST_B10 digital numbers to Celsius.
        lst = dn * 0.00341802 + 149.0 - 273.15

        # Exclude any non-finite calculated temperatures.
        valid &= np.isfinite(lst)

        # Assign NoData to excluded pixels.
        nodata = -9999.0

        output = np.where(
            valid,
            lst,
            nodata
        ).astype("float32")

        # Preserve the original raster's spatial information.
        profile = src.profile.copy()

    # Configure output raster.
    profile.update(
        dtype="float32",
        count=1,
        nodata=nodata,
        compress="deflate"
    )

    # Create output directory if necessary.
    Path(args.out).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Write output raster.
    with rasterio.open(args.out, "w", **profile) as dst:
        dst.write(output, 1)

    print("\n========== LST PROCESSING COMPLETE ==========")
    print(f"Output: {args.out}")
    print(f"Valid pixels: {np.count_nonzero(valid):,}")
    print(f"Excluded pixels: {valid.size - np.count_nonzero(valid):,}")

    if np.any(valid):
        print(f"Minimum LST: {np.min(lst[valid]):.2f} °C")
        print(f"Maximum LST: {np.max(lst[valid]):.2f} °C")
        print(f"Mean LST: {np.mean(lst[valid]):.2f} °C")

    print("===============================================")


if __name__ == "__main__":
    main()
