from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi


DATASET = "jucor1/worldstrat"
OUTPUT = Path(
    r"D:\SIH26142-DATA\WorldStrat\metadata\kaggle_l2a_files.txt"
)


def main() -> None:
    api = KaggleApi()
    api.authenticate()

    page_token = None
    page_number = 0
    matches = []

    while True:
        page_number += 1

        result = api.dataset_list_files(
            DATASET,
            page_size=200,
            page_token=page_token,
        )

        files = result.files

        print(
            f"Page {page_number}: "
            f"{len(files)} files"
        )

        for item in files:
            name = item.name

            if "l2a" in name.lower():
                matches.append(name)

        next_token = result.nextPageToken

        if not next_token:
            break

        page_token = next_token

    matches = sorted(set(matches))

    OUTPUT.write_text(
        "\n".join(matches),
        encoding="utf-8",
    )

    print("\n=== RESULT ===")
    print("L2A files found:", len(matches))
    print("Saved to:")
    print(OUTPUT)

    print("\nFirst 20:")
    for name in matches[:20]:
        print(name)


if __name__ == "__main__":
    main()