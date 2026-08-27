from pathlib import Path
from typing import Dict

import rasterio


def inspect_raster(path: str) -> Dict:
    """
    Read basic geospatial metadata from a raster file.
    """
    raster_path = Path(path)

    if not raster_path.exists():
        raise FileNotFoundError(f"Raster not found: {raster_path}")

    with rasterio.open(raster_path) as src:
        return {
            "path": str(raster_path.resolve()),
            "width": src.width,
            "height": src.height,
            "count": src.count,
            "dtype": src.dtypes,
            "crs": str(src.crs),
            "transform": tuple(src.transform),
            "bounds": {
                "left": src.bounds.left,
                "bottom": src.bounds.bottom,
                "right": src.bounds.right,
                "top": src.bounds.top,
            },
            "resolution": src.res,
            "nodata": src.nodata,
        }


def read_band(path: str):
    """
    Read a single-band raster as a NumPy array.
    """
    raster_path = Path(path)

    if not raster_path.exists():
        raise FileNotFoundError(f"Raster not found: {raster_path}")

    with rasterio.open(raster_path) as src:
        data = src.read(1)
        profile = src.profile.copy()

    return data, profile


if __name__ == "__main__":
    print("Sentinel loader module ready.")