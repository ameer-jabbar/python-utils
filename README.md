# python-utils
Handy python utilities

# pix_by_date.py
```
usage: pix_by_date.py [-h] [--search SEARCH] [--outdir OUTDIR] [--extensions EXTENSIONS] [--dry-run] [--verbose] [--skip-replace]

Search for pictures (or other files), categorizing them by date taken (or date modified) and moving them to directories matching those dates

optional arguments:
  -h, --help            show this help message and exit
  --search SEARCH, --src SEARCH, -s SEARCH
  --outdir OUTDIR, --dst OUTDIR, -o OUTDIR
  --extensions EXTENSIONS, -e EXTENSIONS
  --dry-run, -d
  --verbose, -v
  --skip-replace
```

| Option | Default Value | Description and Notes |
|--------|---------------|-----------------------|
| `--search` | Current directory | Specifies the location in which to search for pictures, movies, etc. All files and directories under this directory will be searched. |
| `--outdir` | ./Moved | Specifies the location where to move files. Under this location, there will be directories created for each date taken/modified and files will be moved there. |
| `--extensions` | "jpg,mp4,mov,avi,wmv,png" | A comma delimited string value holding a list of file extensions to filter IN. That is only files with the specified extension will be moved. |
| `--verbose` | False | Enables verbose logging |
| `--dry-run` | False | When specified, searches through the directories and prints out files and where they will be moved. |
| `--skip-replace` | False | When specified, if the destination already has a file with same name, it will not be replaced. |

