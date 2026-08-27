from pathlib import Path

import pandas as pd


DATA_ROOT = Path(r"D:\SIH26142-DATA\WorldStrat")
METADATA_DIR = DATA_ROOT / "metadata"

INPUT_FILE = METADATA_DIR / "stratified_train_val_test_split.csv"
OUTPUT_FILE = METADATA_DIR / "clean_tile_split.csv"
CONFLICT_FILE = METADATA_DIR / "conflicting_tiles.csv"


def main() -> None:
    df = pd.read_csv(INPUT_FILE)

    print("Original split rows:", len(df))
    print("Original unique tiles:", df["tile"].nunique())

    # Find tiles that have more than one distinct split.
    split_counts = df.groupby("tile")["split"].nunique()

    conflicting_tiles = split_counts[
        split_counts > 1
    ].index.tolist()

    print(
        "Conflicting tile IDs:",
        len(conflicting_tiles),
    )

    # Save conflicts separately for audit/provenance.
    conflicts = df[
        df["tile"].isin(conflicting_tiles)
    ].sort_values("tile")

    conflicts.to_csv(CONFLICT_FILE, index=False)

    # Remove conflicting tiles completely.
    clean = df[
        ~df["tile"].isin(conflicting_tiles)
    ].copy()

    # Remove exact/duplicate rows having the same tile assignment.
    clean = clean.drop_duplicates(
        subset=["tile"],
        keep="first",
    )

    clean.to_csv(OUTPUT_FILE, index=False)

    print("\n=== CLEAN SPLIT ===")
    print("Rows:", len(clean))
    print("Unique tiles:", clean["tile"].nunique())

    print("\nSplit counts:")
    print(clean["split"].value_counts())

    print("\nConflicting tiles saved to:")
    print(CONFLICT_FILE)

    print("\nClean split saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()