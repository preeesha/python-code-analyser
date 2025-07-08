import os
import shutil
from pathlib import Path

def reset_dir(path: str, empty_ok: bool = True) -> None:
    if os.path.exists(path):
        if empty_ok:
            shutil.rmtree(path)
        else:                     
            raise FileExistsError(f"{path} already exists!")
    os.makedirs(path, exist_ok=True)
    

def copy_local_dir(src_dir: str, target_dir: str) -> Path:
    
    src    = Path(src_dir).resolve()
    dest   = Path(target_dir).resolve()

    # 1️⃣ Sanity checks
    if not src.is_dir():
        raise NotADirectoryError(src)

    # Prevent recursive self‑copy
    # (dest is src, or dest is a child of src)
    if dest == src or dest in src.parents:
        raise ValueError(
            f"Destination {dest} is inside source {src}. "
            "Choose a folder outside the source tree."
        )

    # 2️⃣ Wipe & recreate destination
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    # 3️⃣ Copy
    shutil.copytree(src, dest, dirs_exist_ok=True)

    return dest

