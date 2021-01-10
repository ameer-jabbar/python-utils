import hashlib
import os
import shutil
from datetime import datetime

from PIL import Image


def file_modified_date(filepath: str):
    try:
        file_info = os.stat(filepath)
        modified_time = file_info.st_mtime
        dt = datetime.fromtimestamp(modified_time)
        return "{}_{}_{}".format(dt.year, dt.month, dt.day)
    except Exception as e:
        print("Could not get modified data for {}".format(filepath), e)
        return None


def image_date_taken(filepath: str):
    """
    Returns the image date taken from the picture found in 'filepath'. 
    If the image date taken is not found, then the date modified for 
    the file will be returned. 
    The format of the date will be Year_Month_Day. Example: 2020_9_21
    Code taken (and modified) from:
         https://orthallelous.wordpress.com/2015/04/19/extracting-date-and-time-from-images-with-python/
    """
    try:
        std_fmt = '%Y:%m:%d %H:%M:%S.%f'

        tags = [(36867, 37521),  # (DateTimeOriginal, SubsecTimeOriginal)
                (36868, 37522),  # (DateTimeDigitized, SubsecTimeDigitized)
                (306, 37520), ]  # (DateTime, SubsecTime)
        exif = Image.open(filepath).getexif()

        if exif is None:
            return file_modified_date(filepath)

        sub = dat = None
        for t in tags:
            dat = exif.get(t[0])
            sub = exif.get(t[1], 0)

            # PIL.PILLOW_VERSION >= 3.0 returns a tuple
            dat = dat[0] if type(dat) == tuple else dat
            sub = sub[0] if type(sub) == tuple else sub
            if dat is not None:
                break

        if dat is None:
            return file_modified_date(filepath)
        full = '{}.{}'.format(dat, sub)
        dt = datetime.strptime(full, std_fmt)
        return "{}_{}_{}".format(dt.year, dt.month, dt.day)
    except Exception as e:
        print(e)
        return file_modified_date(filepath)


def gather_files(to_files: list, directory: str, ext_list_str: str):
    """
    File 'to_files' with a list of files that were found in 'directory'
    """
    for root, dirs, file_names in os.walk(directory):
        to_files.extend(
            [os.path.join(root, the_name) for the_name in file_names if one_of_the_extensions(the_name, ext_list_str)])


def files_to_date_taken_map(file_paths: list):
    """
    For the given list of 'file_paths', returns a dict() that maps the image date
    taken (or modified date) string with the a list of file_paths that were taken
    on that date.
    """
    dt_taken_map = dict()
    i = 0
    for filepath in file_paths:
        dt = image_date_taken(filepath)
        if dt is not None:
            update_date_taken_list(dt_taken_map, dt, filepath)
        else:
            update_date_taken_list(dt_taken_map, 'NO_DATE_TAKEN', filepath)
        i = i + 1
        if i % 1001 == 0:
            print("{}/{}".format(len(dt_taken_map), i))
    return dt_taken_map


def update_date_taken_list(my_map: dict, for_this_date: str, filepath: str):
    """
    Updates 'my_map' by adding 'filepath' into 'for_this_date' mapping
    """
    files_date_at_dt = my_map.get(for_this_date)
    if not files_date_at_dt:
        files_date_at_dt = list()
        my_map[for_this_date] = files_date_at_dt
    files_date_at_dt.append(filepath)


def one_of_the_extensions(filepath: str, ext_list_str: str):
    lc_filepath = filepath.lower()
    for ext in ext_list_str.split(","):
        if lc_filepath.endswith(ext.lower()):
            return True
    return False


def handle_duplicate_name(dst_dir: str, file_name: str, old_name: str):
    base_name, ext = os.path.splitext(file_name)
    file_name_hash = hashlib.sha1(bytes(old_name, "utf-8")).hexdigest()
    return os.path.join(dst_dir, "{}{}".format(file_name_hash, ext))


if __name__ == "__main__":
    import argparse

    description = """
    Search for pictures (or other files), categorizing them by date 
    taken (or date modified) and moving them to directories matching 
    those dates
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--search", "--src", "-s", default=".")
    parser.add_argument("--outdir", "--dst", "-o", default="Moved")
    parser.add_argument("--extensions", "-e", default="jpg,mp4,mov,avi,wmv,png")
    parser.add_argument("--dry-run", "-d", action='store_true')
    parser.add_argument("--verbose", "-v", action='store_true')
    parser.add_argument("--skip-replace", action='store_true')

    args = parser.parse_args()
    pictures_dir = args.search

    if args.dry_run:
        print("==== DRY RUN ====")

    all_files = list()
    print("Collecting files in " + pictures_dir)
    gather_files(all_files, pictures_dir, args.extensions)

    print("Filter to {} files. Categorizing files by date taken".format(len(all_files)))
    date_taken_map = files_to_date_taken_map(all_files)

    print("Will be moving files to {} directories in: {}".format(len(date_taken_map.keys()), args.outdir))
    if not args.dry_run:
        os.makedirs(args.outdir, exist_ok=True)

    if not args.dry_run:
        print("Moving files to date taken (or last modified) directories...")
        for date_taken_str, files in date_taken_map.items():
            date_taken_dir = os.path.join(args.outdir, date_taken_str)
            if args.verbose:
                print("+ mkdir " + date_taken_dir)
            os.makedirs(date_taken_dir, exist_ok=True)
            for name in files:
                new_name = os.path.join(date_taken_dir, os.path.basename(name))
                if os.path.exists(new_name):
                    print("Name {} already exists in {}".format(new_name, date_taken_dir))
                    if args.skip_replace:
                        print(" * Skipping replace")
                        continue
                    new_name = handle_duplicate_name(date_taken_dir, new_name, name)
                if args.verbose:
                    print("+ mv {} {}".format(name, new_name))
                shutil.move(name, new_name)
    else:
        for date_taken_str, files in date_taken_map.items():
            date_taken_dir = os.path.join(args.outdir, date_taken_str)
            print(date_taken_dir)
            for name in files:
                new_name = os.path.join(date_taken_dir, os.path.basename(name))
                if os.path.exists(new_name):
                    print("Name {} already exists in {}".format(new_name, date_taken_dir))
                    if args.skip_replace:
                        print(" * Skipping replace")
                        continue
                    new_name = handle_duplicate_name(date_taken_dir, new_name, name)

                print("Will move {} to {}".format(name, new_name))
