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


## Example usages

Convert a single file: `python ./main.py --inputFile "./Marcelektro's server - Text Channels - general [735893720033132564].html"`<br>

Bulk-convert a folder with multiple files: `python ./main.py --inputDirectory "./Discord DM backups/"`<br>
<br>

This will create a folder with a converted export file and downloaded assets for each input file. (You can set its location using the `--outputDirectory` option.)


## Contact

If you have any questions related to this repo, feel free to ask them on my [Discord server](https://discord.gg/yaftWcn).

