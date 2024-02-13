#! /bin/bash

# refresh derived resources
inkscape swap_stubs_dark.svg -w 24 -h 24 -o swap_stubs_dark.png
inkscape swap_stubs_light.svg -w 24 -h 24 -o swap_stubs_light.png
inkscape swap_stubs_light.svg -w 64 -h 64 -o swap_stubs.png

# refresh the GUI design
wxformbuilder -g error_dialog_GUI.fbp

# grab version and parse it into metadata.json
cp metadata_source.json metadata_package.json
version=`cat version.txt`
# remove all but the latest version in package metadata
python3 parse_metadata_json.py
sed -i -e "s/VERSION/$version/g" metadata.json

# cut the download, sha and size fields
sed -i '/download_url/d' metadata.json
sed -i '/download_size/d' metadata.json
sed -i '/install_size/d' metadata.json
sed -i '/download_sha256/d' metadata.json

# prepare the package
mkdir plugins
cp swap_stubs_dark.png plugins
cp swap_stubs_light.png plugins
cp __init__.py plugins
cp action_swap_stubs.py plugins
cp error_dialog_GUI.py plugins
cp swap_stubs.py plugins
cp version.txt plugins
mkdir resources
cp swap_stubs.png resources/icon.png

zip -r SwapStubs-$version-pcm.zip plugins resources metadata.json

# clean up
rm -r resources
rm -r plugins
rm metadata.json

# get the sha, size and fill them in the metadata
cp metadata_source.json metadata.json
version=`cat version.txt`
sed -i -e "s/VERSION/$version/g" metadata.json
zipsha=`sha256sum SwapStubs-$version-pcm.zip | xargs | cut -d' ' -f1`
sed -i -e "s/SHA256/$zipsha/g" metadata.json
unzipsize=`unzip -l SwapStubs-$version-pcm.zip | tail -1 | xargs | cut -d' ' -f1`
sed -i -e "s/INSTALL_SIZE/$unzipsize/g" metadata.json
dlsize=`ls -al SwapStubs-$version-pcm.zip | tail -1 | xargs | cut -d' ' -f5`
sed -i -e "s/DOWNLOAD_SIZE/$dlsize/g" metadata.json
