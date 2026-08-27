from pathlib import Path

import pandas as pd


DATA_ROOT = Path(r"D:\SIH26142-DATA\WorldStrat")
METADATA_DIR = DATA_ROOT / "metadata"

TRAIN_INPUT = METADATA_DIR / "development_train.csv"
VAL_INPUT = METADATA_DIR / "development_val.csv"

TRAIN_OUTPUT = METADATA_DIR / "development_train_clean.csv"
VAL_OUTPUT = METADATA_DIR / "development_val_clean.csv"

KEEP_COLUMNS = [
    "tile",
    "bounds",
    "lowres_date",
    "highres_date",
    "area",
    "cloud_cover",
    "delta",
    "lon",
    "lat",
    "LCCS",
    "SMOD",
    "IPCC Class",
    "LCCS class",
    "SMOD Class",
    "source",
    "joint_class",
    "split",
    "abs_delta",
]


def clean_file(input_file: Path, output_file: Path) -> None:
    df = pd.read_csv(input_file)

    # The earlier inventory merge created *_x and *_y columns.
    # Prefer the authoritative values from the clean tile split.
    rename_map = {}

    for col in [
        "IPCC Class",
        "LCCS class",
        "SMOD",
        "SMOD Class",
        "source",
        "joint_class",
        "split",
    ]:
        if f"{col}_y" in df.columns:
            rename_map[f"{col}_y"] = col
        elif f"{col}_x" in df.columns:
            rename_map[f"{col}_x"] = col

    df = df.rename(columns=rename_map)

    # Keep only columns that actually exist.
    columns = [c for c in KEEP_COLUMNS if c in df.columns]

    missing = [
        c for c in KEEP_COLUMNS
        if c not in df.columns
    ]

    if missing:
        print(f"Warning: missing columns in {input_file.name}:")
        print(missing)

    clean = df[columns].copy()

    # Ensure tile IDs are unique.
    clean = clean.drop_duplicates(
        subset=["tile"],
        keep="first",
    )

    clean.to_csv(output_file, index=False)

    print(f"\nCreated: {output_file}")
    print("Rows:", len(clean))
    print("Unique tiles:", clean["tile"].nunique())
    print("Columns:", list(clean.columns))


def main() -> None:
    clean_file(TRAIN_INPUT, TRAIN_OUTPUT)
    clean_file(VAL_INPUT, VAL_OUTPUT)


if __name__ == "__main__":
    main()