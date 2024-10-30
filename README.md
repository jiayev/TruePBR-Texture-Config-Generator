# TruePBR-Texture-Config-Generator

A simple tool to generate a texture config file for TruePBR, to be used with ParralaxGen.

## Usage

1. Place this tool anywhere you like.

2. Make sure you have Python 3 installed. You'll need PyQT5, so run `pip install pyqt5` if you don't have it.

parser.add_argument('-n', '--mod_name', required=True, help='The name of the mod.')
    parser.add_argument('-s', '--submod_name', help='Name of the submod (optional).')
    parser.add_argument('-d', '--suffix', nargs='?', const='_d', default='', help='Diffuse suffix for the texture group (optional).')
    parser.add_argument('-p', '--path', help='Path to the mod folder.')
    parser.add_argument('-f', '--suffix_filter', help='Filter for the suffix of the texture group.')
    # Add an argument "override" to specifically set the settings in json file
    # e.g. -o "parallax=True,displacement_scale=1.0..."
    parser.add_argument('-o', '--override', help='Override settings for the texture group.')

3. Run the tool with `python3 genpatch2.py`, with the following arguments:

- `-n` or `--mod_name`: The name of the mod. Mandatory.
    The tool will search for textures in the path `path/mod_name`.
- `-s` or `--submod_name`: The name of the submod. Optional. (If you use this argument, it would only search for textures with this submod name in path.)
- `-d` or `--suffix`: Depreciated. Useless for latest ParallaxGen. Do not use.
- `-p` or `--path`: The path to the mod folder. Optional. If not provided, the tool uses the path in the code.
- `-f` or `--suffix_filter`: Also depreciated. Do not use.
- `-o` or `--override`: Override settings for the texture group. Optional. Use this to set specific settings for the texture group. Example: `parallax=True,displacement_scale=1.0...`

example: `python3 genpatch2.py -n "Iron Armor PBR" -s "helmet" -o "parallax=True,displacement_scale=1.0..."`

The tool will generate a `Iron Armor PBR - helmet.json` file in the PBRNifPatcher folder in the mod folder.

4. Run ParallaxGen with the generated json file.