from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ScenePair:
    scene_id: str
    lr_path: Path
    hr_path: Path

    lr_resolution_m: float
    hr_resolution_m: float

    lr_crs: Optional[str] = None
    hr_crs: Optional[str] = None

    acquisition_difference_days: Optional[float] = None

    bands: tuple[str, ...] = (
        "B02",
        "B03",
        "B04",
        "B08",
    )

    def validate_basic(self) -> None:
        if self.lr_resolution_m <= 0:
            raise ValueError("Invalid LR resolution.")

        if self.hr_resolution_m <= 0:
            raise ValueError("Invalid HR resolution.")

        if not self.lr_path.exists():
            raise FileNotFoundError(
                f"LR file does not exist: {self.lr_path}"
            )

        if not self.hr_path.exists():
            raise FileNotFoundError(
                f"HR file does not exist: {self.hr_path}"
            )