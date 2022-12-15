from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

import rasterio
from stactools.core.io import ReadHrefModifier
from shapely.geometry import box, mapping


@dataclass(frozen=True)
class COGMetadata:
    id: str
    title: str
    geometry: Dict[str, Any]
    bbox: List[float]
    start_datetime: str
    end_datetime: str
    version: str
    tile: str
    epsg: int
    proj_shape: List[int]
    proj_transform: List[float]

    @classmethod
    def from_cog(
        cls, href: str, read_href_modifier: Optional[ReadHrefModifier]
    ) -> "COGMetadata":
        if read_href_modifier:
            modified_href = read_href_modifier(href)
        else:
            modified_href = href
        with rasterio.open(modified_href) as dataset:
            bbox = dataset.bounds
            geometry = mapping(box(*bbox))
            shape = dataset.shape
            transform = list(dataset.transform)[0:6]
            epsg = dataset.crs.epsg

        fileparts = Path(href).stem.split("-")
        id = "-".join(fileparts[:-1])
        start_datetime = f"{fileparts[-4]}-01-01T00:00:00Z"
        end_datetime = f"{fileparts[-4]}-12-31T23:59:59Z"
        version = fileparts[-3]
        tile = fileparts[-2]
        title = (
            f"European Space Agency Climate Change Initiative (ESA CCI) "
            f"{fileparts[-4]} Land Cover Map Tile {tile}"
        )

        return COGMetadata(
            id=id,
            title=title,
            geometry=geometry,
            bbox=bbox,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            version=version,
            tile=tile,
            epsg=epsg,
            proj_shape=shape,
            proj_transform=transform,
        )
