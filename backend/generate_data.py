"""Command-line data generator for the prototype."""

from pathlib import Path
import json

from app.data_generator import generate_dataset


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "antarctic_data.json"


def main() -> None:
    seed = 42
    dataset = generate_dataset(seed)

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(dataset, file, indent=2)

    print("Generated SYNTHETIC DEMONSTRATION DATA.")
    print(f"Seed: {seed}")
    print(f"Grid points: {len(dataset['points'])}")
    print(f"Icebergs: {len(dataset['icebergs'])}")
    print(f"Saved to: {DATA_FILE}")


if __name__ == "__main__":
    main()
