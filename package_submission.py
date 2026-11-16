"""Create a clean, standardized academic submission ZIP bundle for college evaluation."""

import os
import zipfile
import shutil
from datetime import datetime

def package_project():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    scratch_dir = os.path.dirname(base_dir)
    output_zip = os.path.join(scratch_dir, "pm-internship-allocation-submission.zip")
    internal_zip = os.path.join(base_dir, "pm-internship-allocation-submission.zip")

    print(f"Packaging Project from: {base_dir}")
    print(f"Target Submission Archive: {output_zip}")

    # Exclusions
    exclude_dirs = {
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        "venv",
        ".git"
    }
    exclude_extensions = {".pyc", ".pyo", ".log"}

    total_files = 0
    total_bytes = 0

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            # Prune excluded directories in-place
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in exclude_extensions:
                    continue
                if file.endswith("-submission.zip"):
                    continue

                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)
                archive_name = os.path.join("pm-internship-allocation", rel_path)

                zipf.write(full_path, archive_name)
                total_files += 1
                total_bytes += os.path.getsize(full_path)

    zip_size_mb = round(os.path.getsize(output_zip) / (1024 * 1024), 2)
    # Copy inside project root too
    shutil.copyfile(output_zip, internal_zip)

    print("\n" + "=" * 60)
    print("  SUBMISSION BUNDLE GENERATED SUCCESSFULLY")
    print("=" * 60)
    print(f"  * Total Files Packaged:     {total_files}")
    print(f"  * Uncompressed Size:        {round(total_bytes / (1024 * 1024), 2)} MB")
    print(f"  * Compressed Archive Size:  {zip_size_mb} MB")
    print(f"  * Output Archive Path:      {output_zip}")
    print(f"  * Internal Project Copy:    {internal_zip}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    package_project()
