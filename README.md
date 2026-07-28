# DiscordChatExporter Media Downloader

A program for downloading attachments from Discord chat exports created by [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) by [Tyrrrz](https://github.com/Tyrrrz).


## About

On 29/09/2023, in the Discord Developers server, [an announcement related to Discord CDN](https://discord.com/channels/613425648685547541/697138785317814292/1157372186160537750) was posted.
It mentions the upcoming introduction of authentication parameters for attachment urls. This means that it will no longer be possible to simply copy an attachment link and use it anywhere at any time.<br>
DiscordChatExporter copies links to Discord CDN (if attachment download option is disabled). As a result, any exports you've previously created without downloaded attachments will no longer include them after this update gets implemented.<br>
<br>
This tool is to help you download attachments (images, videos and other files) from already created chat exports of any format (json, html, csv, or txt).


## How does it work?

The program takes an input file, finds all matching links, and downloads the attachments. Then, it downloads all the found files to a folder. Finally, a copy of the input file is created, with the original CDN links replaced with local file paths.<br>

## Getting started

1. Clone the repository: `git clone https://github.com/Marcelektro/DiscordChatExporter-MediaDownloader`
2. Get into the project root: `cd DiscordChatExporter-MediaDownloader`
3. Create a python venv: `python3 -m venv .venv`
4. Activate the venv: `source .venv/bin/activate`
5. Download dependencies: `pip install -r requirements.txt`
6. Run the app: `python3 ./main.py --help`


## Example usage

```bash
$ ./main.py --help
usage: DiscordChatExporter-MediaDownloader [-h] [--inputFile INPUTFILE] [--inputDirectory INPUTDIRECTORY] [--outputDirectory OUTPUTDIRECTORY] [--mergeOutput] [inputItems ...]

A program for downloading Discord CDN attachments from DiscordChatExporter (DCE) exports.

positional arguments:
  inputItems            Files or directories to process

options:
  -h, --help            show this help message and exit
  --inputFile INPUTFILE
                        A DCE export file to convert
  --inputDirectory INPUTDIRECTORY
                        Directory with DCE export files to convert
  --outputDirectory OUTPUTDIRECTORY
                        Directory, where output dirs for each input file will be created (or the single combined output dir, if --mergeOutput is used)
  --mergeOutput         Instead of creating a separate output folder per input file, put all attachments in one shared attachments/ folder, and all offline chatlogs in one shared chatlogs/ folder.

For further help, see this readme
```


### Convert export(s) into individual directories

- Convert a single file:   
  ```bash
  python3 ./main.py "./marCloud Community - Text Channels - en-main [553995222284238874].html"
  ```
- Bulk-convert a folder with multiple files in it:   
  ```bash
  python3 ./main.py "./Discord DM backups/"
  ```
- Bulk convert multiple files/folders:   
  ```bash
  python3 ./main.py
    "./marCloud Community - Text Channels - en-main [553995222284238874].html"
    "./genCloud - Text Channels - General [1435475714219708539].html"
  ```

For each inputted source chat export file, the program will create a separate folder inside the output directory with:
- the converted export chatlog file (with local attachment references)
- downloaded assets in `attachments` subfolder 


### Convert export(s) into a single **merged** directory

This will create a shared `attachments` directory, and all chatlogs will be placed
in the **same directory** next to each other.

```bash
python3 ./main.py
  --mergeOutput
  --outputDirectory "./My communities/"
  "./marCloud Community - Text Channels - en-main [553995222284238874].html"
  "./genCloud - Text Channels - General [1435475714219708539].html"
```

The above command will result in creating a shared `attachments` directory and converted chat logs
being placed in the output directory, all together.


### Customize output directory

You can set the output directory using the `--outputDirectory` flag.
```bash
python3 ./main.py 
  --outputDirectory "./MyCommunity Exports/" 
  "./marCloud Community - Text Channels - en-main [553995222284238874].html"
```


## Contact

If you have any questions related to this repo, feel free to ask them on my [Discord server](https://discord.gg/yaftWcn).

