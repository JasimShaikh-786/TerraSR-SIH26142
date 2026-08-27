from pathlib import Path
import time

from kaggle.api.kaggle_api_extended import KaggleApi


DATASET = "jucor1/worldstrat"

OUTPUT = Path(
    r"D:\SIH26142-DATA\WorldStrat\metadata\kaggle_all_files.txt"
)


def main():
    api = KaggleApi()
    api.authenticate()

    token = None
    page = 0
    matches = []

    while True:
        page += 1

        print(f"Requesting page {page}...")

        result = api.dataset_list_files(
            DATASET,
            page_size=200,
            page_token=token,
        )

        for item in result.files:
            name = item.name

            # Save only useful metadata.
            if (
                "hr_dataset" in name.lower()
                or "lr_dataset" in name.lower()
            ):
                matches.append(name)

        token = result.nextPageToken

        if not token:
            break

        # Avoid Kaggle rate limiting.
        time.sleep(2.0)

    matches = sorted(set(matches))

    OUTPUT.write_text(
        "\n".join(matches),
        encoding="utf-8",
    )

    print()
    print("Finished.")
    print("Files recorded:", len(matches))
    print("Saved:", OUTPUT)

    print()
    print("L2A count:",
          sum("l2a" in x.lower() for x in matches))

    print("HR count:",
          sum("hr_dataset" in x.lower() for x in matches))


if __name__ == "__main__":
    main()