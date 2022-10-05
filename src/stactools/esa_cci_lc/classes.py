# fmt: off
# flake8: noqa
from typing import Any, Dict, List

# Value, RGB, Name, Description, Regional (def: False), Nodata (def: False)

TABLE: List[List[Any]] = [
    [  0, [  0,  0,  0], "no-data", "No Data", False, True],
    [ 10, [255,255,100], "cropland-1", "Cropland, rainfed"],
    [ 11, [255,255,100], "cropland-1a", "Cropland, rainfed, herbaceous cover", True],
    [ 12, [255,255,  0], "cropland-1b", "Cropland, rainfed, tree, or shrub cover", True],
    [ 20, [170,240,240], "cropland-2", "Cropland, irrigated or post-flooding"],
    [ 30, [220,240,100], "cropland-3", "Mosaic cropland (>50%) / natural vegetation (tree, shrub, herbaceous cover) (<50%)"],
    [ 40, [200,200,100], "natural-veg", "Mosaic natural vegetation (tree, shrub, herbaceous cover) (>50%) / cropland (<50%)"],
    [ 50, [  0,100,  0], "tree-1", "Tree cover, broadleaved, evergreen, closed to open (>15%)"],
    [ 60, [  0,160,  0], "tree-2", "Tree cover, broadleaved, deciduous, closed to open (>15%)"],
    [ 61, [  0,160,  0], "tree-2a", "Tree cover, broadleaved, deciduous, closed (>40%)", True],
    [ 62, [170,200,  0], "tree-2b", "Tree cover, broadleaved, deciduous, open (15-40%)", True],
    [ 70, [  0, 60,  0], "tree-3", "Tree cover, needleleaved, evergreen, closed to open (>15%)"],
    [ 71, [  0, 60,  0], "tree-3a", "Tree cover, needleleaved, evergreen, closed (>40%)", True],
    [ 72, [  0, 80,  0], "tree-3b", "Tree cover, needleleaved, evergreen, open (15-40%)", True],
    [ 80, [ 40, 80,  0], "tree-4", "Tree cover, needleleaved, deciduous, closed to open (>15%)"],
    [ 81, [ 40, 80,  0], "tree-4a", "Tree cover, needleleaved, deciduous, closed (>40%)", True],
    [ 82, [ 40,100,  0], "tree-4b", "Tree cover, needleleaved, deciduous, open (15-40%)", True],
    [ 90, [120,130,  0], "tree-5", "Tree cover, mixed leaf type (broadleaved and needleleaved)"],
    [100, [140,160,  0], "tree-shrub", "Mosaic tree and shrub (>50%) / herbaceous cover (<50%)"],
    [110, [190,150,  0], "herbaceous", "Mosaic herbaceous cover (>50%) / tree and shrub (<50%)"],
    [120, [150,100,  0], "shrubland", "Shrubland"],
    [121, [150,100,  0], "shrubland-a", "Evergreen shrubland", True],
    [122, [150,100,  0], "shrubland-b", "Deciduous shrubland", True],
    [130, [255,180, 50], "grassland", "Grassland"],
    [140, [255,220,210], "lichens-moses", "Lichens and mosses"],
    [150, [255,235,175], "sparse-veg", "Sparse vegetation (tree, shrub, herbaceous cover) (<15%)"],
    [151, [255,200,100], "sparse-veg-a", "Sparse tree (<15%)", True],
    [152, [255,210,120], "sparse-veg-b", "Sparse shrub (<15%)", True],
    [153, [255,235,175], "sparse-veg-c", "Sparse herbaceous cover (<15%)", True],
    [160, [  0,120, 90], "flooded-tree-1", "Tree cover, flooded, fresh or brackish water"],
    [170, [  0,150,120], "flooded-tree-2", "Tree cover, flooded, saline water"],
    [180, [  0,220,130], "flooded-shrub-herbaceous", "Shrub or herbaceous cover, flooded, fresh/saline/brackish water"],
    [190, [195, 20,  0], "urban", "Urban areas"],
    [200, [255,245,215], "bare", "Bare areas"],
    [201, [220,220,220], "bare-a", "Consolidated bare areas", True],
    [202, [255,245,215], "bare-b", "Unconsolidated bare areas", True],
    [210, [  0, 70,200], "water", "Water bodies"],
    [220, [255,255,255], "snow-ice", "Permanent snow and ice"],
]

PROCESSED_FLAG_TABLE: List[List[Any]] = [
# [-1, None, "no-data", "No Data", False, True],
  [ 0, None, "not_processed", "Not processed"],
  [ 1, None, "processed", "Processed"],
]

CURRENT_PIXEL_STATE_TABLE: List[List[Any]] = [
# [-1, None, "no-data", "No Data", False, True],
  [ 1, None, "land", "Clear land"],
  [ 2, None, "water", "Clear water"],
  [ 3, None, "snow", "Clear snow / ice"],
  [ 4, None, "cloud", "Cloud"],
  [ 5, None, "cloud_shadow", "Cloud_shadow"],
  [ 6, None, "filled", "Filled"],
]

def to_stac(data: List[List[Any]] = TABLE, incldue_regional: bool = True) -> List[Dict[str, Any]]:
  stac_classes: List[Dict[str, Any]] = []
  for cls in data:
    regional = False
    if len(cls) >= 5 and cls[4] is True:
      regional = True
      if not incldue_regional:
        continue

    stac_class: Dict[str, Any] = {
      "value": cls[0],
      "name": cls[2],
      "description": cls[3],
    }

    if cls[1] is not None:
      rgb: List[int] = cls[1]
      r,g,b = rgb
      stac_class["color_hint"] = "{:02x}{:02x}{:02x}".format(r,g,b).upper()

    if regional:
      stac_class["regional"] = True
    if len(cls) >= 6 and cls[5] is True:
      stac_class["no_data"] = True

    stac_classes.append(stac_class)

  return stac_classes
