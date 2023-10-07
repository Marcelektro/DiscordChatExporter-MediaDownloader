import argparse
import json
import os.path
import re
from datetime import datetime
from urllib.parse import urlparse

import requests
from tqdm import tqdm

# ################################ #
#      Created by Marcelektro      #
#  https://github.com/Marcelektro  #
# ################################ #


# Extensions DCE exports can have
valid_input_file_extensions = ['.html', '.txt', '.json', '.csv']

# A regex to match all Discord CDN links
discord_cdn_link_regex = re.compile(r'(https://(?:cdn\.discordapp\.com|media\.discordapp\.com)/[^\s"<]+)')


def main():
    parser = argparse.ArgumentParser(
        prog='DiscordChatExporter-MediaDownloader',
        description='A program for downloading Discord CDN attachments from DiscordChatExporter (DCE) exports.',
        epilog='For further help, see README.md'
    )

    parser.add_argument('--inputFile', help='A DCE export file to convert')
    parser.add_argument('--inputDirectory', help='Directory with DCE export files to convert')
    parser.add_argument('--outputDirectory', help='Directory, where output dirs for each input file will be created')

    args = parser.parse_args()

    arg_file = args.inputFile
    args_directory = args.inputDirectory
    args_out_dir = args.outputDirectory

    if arg_file is None and args_directory is None:
        print('Please specify input file or directory.')
        parser.print_help()
        return

    print('Scanning input files...')

    # List of absolute file paths to convert
    files = []

    # Add the single input file, if it was provided
    if arg_file is not None:

        if not os.path.isfile(arg_file):
            print('Ignoring --inputFile argument, as provided path is not a file.')

        else:
            files.append(os.path.abspath(arg_file))


    # Add files from input directory, if it was provided
    if args_directory is not None:

        if not os.path.isdir(args_directory):
            print('Ignoring --inputDirectory argument, as provided path is not a directory.')

        else:
            for filename in os.listdir(args_directory):
                file_path = os.path.join(args_directory, filename)

                # Ensure the file is a DCE export file
                if os.path.isfile(file_path) and os.path.splitext(filename)[1] in valid_input_file_extensions:
                    files.append(file_path)


    # If no files were found, exit.
    if len(files) == 0:
        print('No files were matched; quitting.')
        return

    # Print all matches
    print('--------------------')
    print(f'Matched files ({len(files)}):')
    print(' - ' + '\n - '.join(files))
    print('--------------------')

    # Ask user whether to start processing the files
    confirmUserInput = input('Would you like to start conversion on those files? (Y/N) ')

    if not confirmUserInput.lower() in ['y', 'yes', 'confirm']:
        print('Cancelled, quitting.')
        return

    # Processing part

    # Directory in which output directories will be created
    out_root_dir = './'
    # If argument is provided, use it.
    if args_out_dir is not None:
        out_root_dir = args_out_dir

    # For each file we found ...
    for file in files:

        # ... create an output folder
        output_dir = DownloadsFolder(os.path.join(out_root_dir, f'./output-{os.path.basename(file)}'))

        # Output folder has a lock file to prevent modifying it while it's used.
        # When the app e.g. crashes, it does not remove the lock file correctly.
        while True:
            try:
                output_dir.open()
                break
            except LockFileExistsException:
                # We'll ask user whether to delete it.
                print('==================================================================')
                print('Output folder has lock file (probably is in-use).')
                print(f'Folder path: {output_dir}')
                print('If you\'re already running this program on that directory, wait for it to exit, '
                      'otherwise you may delete the lock file.')
                print('==================================================================')
                if input('Do you want to delete it (Y), or (QUIT)? ').lower() in ['y', 'yes']:
                    os.remove(output_dir.lockfile_path)
                else:
                    exit(0)

        # Load already found 'dc cdn -> local file' mappings of files in that directory.
        media_links = output_dir.load_mappings()

        # Find media links in the file
        ml = get_media_links(file)

        # Add each link we found to media_links dict, if not present
        for link in ml:
            if link not in media_links:
                media_links[link] = ml[link]

        print(f'File `{file}` has {len(media_links)} links.')


        # Save mappings file
        output_dir.save_mappings(media_links)

        # Download all non-downloaded files
        progress_bar = tqdm(total=sum(1 for value in media_links.values() if value is None))

        # For each entry in mappings dictionary
        # TODO: Implement multithreading
        i = 0
        for cdn_url, local_file in media_links.items():

            # If the value (local file path) is set and exists on the system, ignore (as it's already there).
            if local_file is not None and os.path.exists(os.path.join(output_dir.path, local_file)):
                continue

            # Get a path for where to download the attachment.
            # ./<output_dir>/<attachments_dir>/<file>
            out_path = os.path.join(output_dir.attachments_dir, extract_filename_from_discord_cdn_url(cdn_url))

            # Try to download file (if exists, will append _1, _2 etc. to filename)
            try:
                out_path = download_file(cdn_url, out_path)

                # Since this is after download, we will only add successfully downloaded files to mappings.
                # ./<attachments_dir>/<file>
                mapping_path = os.path.join(os.path.basename(output_dir.attachments_dir), os.path.basename(out_path))
                media_links[cdn_url] = mapping_path

            except Exception as e:
                # Inform about the error
                # (Use tqdm write instead of print, so that the progress bar doesn't break.)
                progress_bar.write(f"Failed to download file from `{cdn_url}`: `{str(e)}`")

            # Increment progress bar by 1.
            progress_bar.update()

            # Save mappings every 5 downloads
            if i % 5 == 0:
                output_dir.save_mappings(media_links)

            i += 1

        # Save mappings file
        output_dir.save_mappings(media_links)

        progress_bar.close()

        # Generate offline version of the file referencing to downloaded files
        orig_name, orig_ext = os.path.splitext(os.path.basename(file))

        # Create offline version of the 'file' file, to outputDir/file.offline.ext, using media_links dictionary.
        create_offline_version(file, os.path.join(output_dir.path, f'{orig_name}.offline{orig_ext}'), media_links)

        # "Close" output directory (also release the lock)
        output_dir.close()


# A function to get all Discord CDN links in a file
# Returns a dictionary with keys being Discord CDN urls, and values being null values (later local downloaded files).
def get_media_links(file_path) -> dict:
    links = {}

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            link_matches = discord_cdn_link_regex.findall(line)

            for link_match in link_matches:
                # The dictionary is 'Discord cdn url -> local file', so for now value (local file) is None.
                links[link_match] = None

    return links


def create_offline_version(input_filepath, output_filepath, cdn_local_mappings):

    # Copy input file into output file line by line, while replacing
    # found Discord links with their local file equivalents.
    with open(input_filepath, 'r', encoding='utf-8') as input_file:
        with open(output_filepath, 'w', encoding='utf-8') as output_file:
            for input_line in input_file:
                link_matches = discord_cdn_link_regex.findall(input_line)

                # Initially, the line we'll append is the same
                line_edited = input_line

                # Replace all found links with replacements from the dictionary
                for link_match in link_matches:
                    replacement = cdn_local_mappings[link_match]

                    if replacement is None:
                        continue

                    line_edited = line_edited.replace(link_match, replacement)

                # Append the line to the new file
                output_file.write(line_edited)



def extract_filename_from_discord_cdn_url(cdn_url):
    # Remove query params by getting just the path
    path_without_query = urlparse(cdn_url).path

    # Get the filename from the decoded path
    filename = os.path.basename(path_without_query)

    return filename


def download_file(url, output_path_in):
    headers = {
        'User-Agent': 'Mozilla/5.0 (DiscordChatExporter-MediaDownloader)'
    }

    # Send the request
    response = requests.get(url, headers=headers, stream=True)

    # Throw an exception if status code is not OK
    response.raise_for_status()

    output_path = get_unique_filepath(output_path_in)

    with open(output_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

    # Handle Last-Modified header and update file modification date accordingly
    last_modified_header = response.headers.get('Last-Modified')
    if last_modified_header:
        last_modified_timestamp = datetime.strptime(last_modified_header, '%a, %d %b %Y %H:%M:%S %Z')
        last_modified_timestamp = last_modified_timestamp.timestamp()

        # Set the last modified timestamp of the downloaded file
        # TODO: Handle user PC having different timezone than GMT
        os.utime(output_path, (last_modified_timestamp, last_modified_timestamp))

    # print(f'File downloaded to {output_path}')
    return output_path


def get_unique_filepath(filepath):
    base_dir, file_name = os.path.split(filepath)
    base_name, extension = os.path.splitext(file_name)
    counter = 1

    while os.path.exists(filepath):
        base_name_with_counter = f'{base_name}_{counter}'
        new_file_name = f'{base_name_with_counter}{extension}'
        filepath = os.path.join(base_dir, new_file_name)
        counter += 1

    return filepath


class DownloadsFolder:

    def __init__(self, path):
        self.path = path
        self.lockfile_path = os.path.join(self.path, 'downloads_folder.lock')
        self.attachment_mapping_file = os.path.join(self.path, 'attachment_mapping_file.json')
        self.attachments_dir = os.path.join(self.path, 'attachments')


    def open(self):

        if os.path.exists(self.lockfile_path):
            raise LockFileExistsException()

        # Ensure the directory exists
        os.makedirs(self.path, exist_ok=True)

        # Ensure the attachments_dir exists
        os.makedirs(self.attachments_dir, exist_ok=True)

        with open(self.lockfile_path, 'w'):
            pass

        return self


    def close(self):
        os.remove(self.lockfile_path)


    def save_mappings(self, data):
        with open(self.attachment_mapping_file, 'w') as fp:
            json.dump(data, fp, indent=2)


    def load_mappings(self) -> dict:

        if not os.path.exists(self.attachment_mapping_file):
            return {}

        with open(self.attachment_mapping_file, 'r') as fp:
            data = json.load(fp)

        return data


class LockFileExistsException(Exception):
    pass



if __name__ == '__main__':
    main()
