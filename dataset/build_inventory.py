from pathlib import Path

import pandas as pd


DATA_ROOT = Path(r"D:\SIH26142-DATA\WorldStrat")
METADATA_DIR = DATA_ROOT / "metadata"

METADATA_FILE = METADATA_DIR / "metadata.csv"
SPLIT_FILE = METADATA_DIR / "stratified_train_val_test_split.csv"

OUTPUT_FILE = METADATA_DIR / "scene_inventory.csv"


def main() -> None:
    print("Loading metadata...")

    metadata = pd.read_csv(METADATA_FILE)
    split = pd.read_csv(SPLIT_FILE)

    print(f"Metadata rows: {len(metadata)}")
    print(f"Metadata tiles: {metadata['tile'].nunique()}")

    # One authoritative row per tile from the official split.
    split_small = (
        split[
            [
                "tile",
                "IPCC Class",
                "SMOD",
                "source",
                "joint_class",
                "split",
            ]
        ]
        .drop_duplicates(subset=["tile"])
        .copy()
    )

    print(f"Split tiles: {len(split_small)}")

    # Metadata is the master table.
    # Every Sentinel-2 revisit must be retained.
    inventory = metadata.merge(
        split_small,
        on="tile",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    # Verify that the LEFT merge did not lose metadata rows.
    if len(inventory) != len(metadata):
        raise RuntimeError(
            f"ERROR: metadata rows changed from "
            f"{len(metadata)} to {len(inventory)}"
        )

    unmatched = inventory[
        inventory["_merge"] != "both"
    ]

    if len(unmatched) > 0:
        print(
            f"WARNING: {len(unmatched)} metadata rows "
            f"have no split match."
        )
        print(
            unmatched[
                ["tile"]
            ].drop_duplicates().to_string(index=False)
        )

    inventory.drop(columns=["_merge"], inplace=True)

    inventory.to_csv(OUTPUT_FILE, index=False)

    print("\n=== INVENTORY CREATED ===")
    print(f"Rows: {len(inventory)}")
    print(f"Unique tiles: {inventory['tile'].nunique()}")

    print("\nRows per split:")
    print(inventory["split"].value_counts(dropna=False))

    print("\nRevisits per tile:")
    print(
        inventory.groupby("tile")
        .size()
        .value_counts()
        .sort_index()
    )

    print("\nSaved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()