import os
import shutil
from pathlib import Path
from typing import List, Tuple

import numpy as np
from sklearn.model_selection import train_test_split

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}

def list_images_per_class(source_root: Path) -> List[Tuple[str, Path]]:
    items: List[Tuple[str, Path]] = []
    for cls_dir in sorted(p for p in source_root.iterdir() if p.is_dir()):
        cls_name = cls_dir.name
        for f in cls_dir.iterdir():
            if f.is_file():
                ext = f.suffix.lower()
                if ext in IMAGE_EXTS and f.name not in {"Thumbs.db", ".DS_Store"}:
                    items.append((cls_name, f))
    return items

def materialize_split(target_root: Path, split_name: str, items: List[Tuple[str, Path]]):
    split_root = target_root / split_name
    split_root.mkdir(parents=True, exist_ok=True)
    for cls_name, src_path in items:
        dst_dir = split_root / cls_name
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst_path = dst_dir / src_path.name
        if not dst_path.exists():
            shutil.copy2(src_path, dst_path)

def main():
    source_root = Path("dataset")
    target_root = Path("consolidated_medical_data")

    if not source_root.exists():
        print(f"Source dataset not found: {source_root}")
        return

    items = list_images_per_class(source_root)
    if not items:
        print("No images found under dataset/<class>/")
        return

    classes = np.array([c for c, _ in items])
    paths = np.array([p for _, p in items])

    X_train, X_temp, y_train, y_temp = train_test_split(
        paths, classes, test_size=0.30, random_state=42, stratify=classes
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=1/3, random_state=42, stratify=y_temp
    )

    train_items = list(zip(y_train.tolist(), X_train.tolist()))
    val_items = list(zip(y_val.tolist(), X_val.tolist()))
    test_items = list(zip(y_test.tolist(), X_test.tolist()))

    # Clean existing target split directories to avoid duplicates
    for split in ("train", "val", "test"):
        split_dir = target_root / split
        if split_dir.exists():
            shutil.rmtree(split_dir)

    materialize_split(target_root, "train", train_items)
    materialize_split(target_root, "val", val_items)
    materialize_split(target_root, "test", test_items)

    print("Stratified splits created at 'consolidated_medical_data/{train,val,test}'.")

if __name__ == "__main__":
    main()