from pathlib import Path

import pandas as pd


DATA_ROOT = Path(r"D:\SIH26142-DATA\WorldStrat")
METADATA_DIR = DATA_ROOT / "metadata"

INVENTORY_FILE = METADATA_DIR / "scene_inventory.csv"
CLEAN_SPLIT_FILE = METADATA_DIR / "clean_tile_split.csv"

TRAIN_OUTPUT = METADATA_DIR / "development_train.csv"
VAL_OUTPUT = METADATA_DIR / "development_val.csv"


TRAIN_TILES_PER_CLASS = 15
VAL_TILES_PER_CLASS = 3


def select_best_revisit(df: pd.DataFrame) -> pd.DataFrame:
    """
    Select one Sentinel-2 observation per tile.

    Priority:
    1. |delta| <= 90 days
    2. cloud cover <= 20%
    3. smallest |delta|
    4. lowest cloud cover
    """

    df = df.copy()

    df["abs_delta"] = df["delta"].abs()

    preferred = df[
        (df["abs_delta"] <= 90)
        & (df["cloud_cover"] <= 20)
    ].copy()

    fallback = df[
        (df["abs_delta"] <= 180)
        & (df["cloud_cover"] <= 30)
    ].copy()

    selected = []

    for tile, tile_df in df.groupby("tile"):

        candidates = preferred[
            preferred["tile"] == tile
        ]

        if candidates.empty:
            candidates = fallback[
                fallback["tile"] == tile
            ]

        if candidates.empty:
            continue

        best = candidates.sort_values(
            ["abs_delta", "cloud_cover"]
        ).iloc[0]

        selected.append(best)

    return pd.DataFrame(selected)


def stratified_sample(
    df: pd.DataFrame,
    split_name: str,
    samples_per_class: int,
) -> pd.DataFrame:

    df = df[df["split"] == split_name].copy()

    # Remove unknown class from the first development experiment.
    df = df[df["IPCC Class"].notna()].copy()

    selected = []

    for class_name, class_df in df.groupby("IPCC Class"):

        n = min(samples_per_class, len(class_df))

        sampled = class_df.sample(
            n=n,
            random_state=42,
        )

        selected.append(sampled)

    if not selected:
        return pd.DataFrame()

    result = pd.concat(
        selected,
        ignore_index=True,
    )

    return result


def main() -> None:

    print("Loading clean split...")
    clean_split = pd.read_csv(CLEAN_SPLIT_FILE)

    print(
        "Clean tiles:",
        clean_split["tile"].nunique(),
    )

    print("Loading scene inventory...")
    inventory = pd.read_csv(INVENTORY_FILE)

    # Keep only tiles present in the clean split.
    valid_tiles = set(clean_split["tile"])

    inventory = inventory[
        inventory["tile"].isin(valid_tiles)
    ].copy()

    # Attach authoritative clean split assignment.
    split_info = clean_split[
        ["tile", "split", "IPCC Class", "SMOD", "source"]
    ].copy()

    inventory = inventory.drop(
        columns=[
            c
            for c in [
                "split",
                "IPCC Class",
                "SMOD",
                "source",
            ]
            if c in inventory.columns
        ]
    )

    inventory = inventory.merge(
        split_info,
        on="tile",
        how="inner",
        validate="many_to_one",
    )

    # Select one good Sentinel-2 revisit per tile.
    best = select_best_revisit(inventory)

    print(
        "\nTiles with usable Sentinel-2 observation:",
        best["tile"].nunique(),
    )

    # Development samples.
    train = stratified_sample(
        best,
        "train",
        TRAIN_TILES_PER_CLASS,
    )

    val = stratified_sample(
        best,
        "val",
        VAL_TILES_PER_CLASS,
    )

    train = train.sort_values(
        ["IPCC Class", "tile"]
    )

    val = val.sort_values(
        ["IPCC Class", "tile"]
    )

    train.to_csv(TRAIN_OUTPUT, index=False)
    val.to_csv(VAL_OUTPUT, index=False)

    print("\n=== DEVELOPMENT TRAIN ===")
    print("Tiles:", train["tile"].nunique())
    print(train["IPCC Class"].value_counts())

    print("\n=== DEVELOPMENT VALIDATION ===")
    print("Tiles:", val["tile"].nunique())
    print(val["IPCC Class"].value_counts())

    print("\nSaved:")
    print(TRAIN_OUTPUT)
    print(VAL_OUTPUT)


if __name__ == "__main__":
    main()