from pathlib import Path
import shutil
import sys

from page_generator import generate_pages_recursive


def copy_files_recursive(source, destination):
    source = Path(source)
    destination = Path(destination)
    if not source.is_dir():
        raise ValueError(f"Source directory does not exist: {source}")

    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    for entry in sorted(source.iterdir()):
        target = destination / entry.name
        if entry.is_dir():
            copy_files_recursive(entry, target)
        else:
            print(f"Copying {entry} -> {target}")
            shutil.copy(entry, target)


def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    project_root = Path(__file__).resolve().parent.parent
    copy_files_recursive(project_root / "static", project_root / "docs")
    generate_pages_recursive(
        project_root / "content",
        project_root / "template.html",
        project_root / "docs",
        basepath,
    )


if __name__ == "__main__":
    main()
