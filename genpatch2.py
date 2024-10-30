import os
import json
import argparse
# import tkinter as tk
# from tkinter import ttk
import sys
import re


# Constants
BASE_MOD_FOLDER = "F:/Games/JueLun V3.1/iniRePather-Skyrim/Mod Organizer 2/mods/" # Set the base mod folder here (I use Mod Organizer 2)
mod_folder = None

from PyQt5.QtWidgets import QApplication, QWidget, QTreeWidget, QTreeWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QColor

class TextureGroupOrganizer(QWidget):
    def __init__(self, texture_groups):
        super().__init__()
        self.texture_groups = texture_groups
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Texture Group Organizer')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Texture Sets'])
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)
        self.tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.tree.setDragDropMode(QTreeWidget.InternalMove)

        self.populate_tree()

        layout.addWidget(self.tree)

        button_layout = QHBoxLayout()
        confirm_button = QPushButton('Confirm')
        confirm_button.clicked.connect(self.confirm)
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.cancel)
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def populate_tree(self):
        main_items = {}
        for name, group in self.texture_groups.items():
            if group['is_main']:
                item = QTreeWidgetItem([f"{name} (Main)"])
                item.setFlags(item.flags() & ~Qt.ItemIsDragEnabled)
                item.setForeground(0, QColor('blue'))  # Set color for Main
                self.tree.addTopLevelItem(item)
                main_items[name] = item
            else:
                sub_item = QTreeWidgetItem([f"{name} (Sub)"])
                closest_main = self.find_closest_main(name)
                if closest_main in main_items:
                    main_items[closest_main].addChild(sub_item)
                    sub_item.setForeground(0, QColor('green'))  # Set color for categorized Sub
                else:
                    self.tree.addTopLevelItem(sub_item)
                    sub_item.setForeground(0, QColor('red'))  # Set color for uncategorized Sub

    def find_closest_main(self, sub_name):
        main_groups = [name for name, group in self.texture_groups.items() if group['is_main']]
        return min(main_groups, key=lambda x: self.levenshtein_distance(sub_name, x))

    @staticmethod
    def levenshtein_distance(s1, s2):
        if len(s1) < len(s2):
            return TextureGroupOrganizer.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    def confirm(self):
        self.update_texture_groups()
        self.close()

    def cancel(self):
        sys.exit()

    def update_texture_groups(self):
        for i in range(self.tree.topLevelItemCount()):
            main_item = self.tree.topLevelItem(i)
            main_name = re.match(r"(.+?) \(", main_item.text(0)).group(1)
            for j in range(main_item.childCount()):
                sub_item = main_item.child(j)
                sub_name = re.match(r"(.+?) \(", sub_item.text(0)).group(1)
                self.texture_groups[sub_name]['main'] = main_name

    def run(self):
        self.show()
        QApplication.instance().exec_()

    def get_organized_groups(self):
        return self.texture_groups

# Helper function to create JSON object for a texture group
def create_texture_group_json(texture_group, main_group=None, override=None):
    texture_root = texture_group['name']
    suffix = texture_group.get('suffix', '')
    if main_group:
        # If it is a secondary group, derive from the main group
        texture_data = {
            "texture": texture_root.replace("/", "\\") + suffix,
            "emissive": 'g_path' in main_group,
            "parallax": 'p_path' in main_group,
            "subsurface": 's_path' in main_group,
            "multilayer": 'cnr_path' in main_group,
            "subsurface_foliage": False,
            "specular_level": 0.04,
            "subsurface_color": [1, 1, 1],
            "roughness_scale": 1,
            "subsurface_opacity": 1,
            "displacement_scale": 0.5,
            "smooth_angle": 70.0,
            # "rename": main_group['name'].replace("/", "\\"),
            # "lock_diffuse": True,
            "slot2": "textures\\pbr\\" + main_group['n_path'].replace("/", "\\"),
            # "slot4": "textures\\pbr\\" + main_group.get('p_path', '').replace("/", "\\"),
            "slot6": "textures\\pbr\\" + main_group['rmaos_path'].replace("/", "\\"),
        }
        if 'g_path' in main_group:
            full_g_path = "textures\\pbr\\" + main_group.get('g_path', '').replace("/", "\\")
            texture_data['slot3'] = full_g_path
        if 'p_path' in main_group:
            full_p_path = "textures\\pbr\\" + main_group.get('p_path', '').replace("/", "\\")
            texture_data['slot4'] = full_p_path
        if 's_path' in main_group:
            full_s_path = "textures\\pbr\\" + main_group.get('s_path', '').replace("/", "\\")
            texture_data['slot8'] = full_s_path
        if 'cnr_path' in main_group:
            texture_data['subsurface'] = False
            full_cnr_path = "textures\\pbr\\" + main_group['cnr_path'].replace("/", "\\")
            texture_data['slot7'] = full_cnr_path
        if suffix:
            texture_data['rename'] = texture_root.replace("/", "\\")
        if 'coat_path' in main_group:
            texture_data['subsurface'] = False
            texture_data['multilayer'] = True
            full_n_path = "textures\\pbr\\" + main_group['n_path'].replace("/", "\\")
            full_coat_path = "textures\\pbr\\" + main_group['coat_path'].replace("/", "\\")
            if 'cnr_path' not in main_group:
                texture_data['slot7'] = full_n_path
            texture_data['slot8'] = full_coat_path
    else:
        # Main group
        texture_data = {
            "texture": texture_root.replace("/", "\\") + suffix,
            # "match_normal": texture_root.replace("/", "\\") + suffix,
            "emissive": 'g_path' in texture_group,
            "parallax": 'p_path' in texture_group,
            "subsurface": 's_path' in texture_group,
            "multilayer": 'cnr_path' in texture_group,
            "subsurface_foliage": False,
            "specular_level": 0.04,
            "subsurface_color": [1, 1, 1],
            "roughness_scale": 1,
            "subsurface_opacity": 1,
            "displacement_scale": 0.5,
            "smooth_angle": 70.0,
        }
        if suffix:
            texture_data['rename'] = texture_root.replace("/", "\\")
        if 'coat_path' in texture_group:
            texture_data['subsurface'] = False
            texture_data['multilayer'] = True
            full_n_path = "textures\\pbr\\" + texture_group['n_path'].replace("/", "\\")
            full_coat_path = "textures\\pbr\\" + texture_group['coat_path'].replace("/", "\\")
            texture_data['slot7'] = full_n_path
            texture_data['slot8'] = full_coat_path
    if texture_data['multilayer']:
        texture_data['subsurface'] = False
        texture_data['coat_strength'] = 1.0
        texture_data['coat_roughness'] = 1.0
        texture_data['coat_specular_level'] = 0.04
        texture_data['coat_diffuse'] = True
        texture_data['coat_parallax'] = True
        texture_data['coat_normal'] = True
    
    # Override settings
    if override:
        # First check if override is valid
        try:
            override_dict = {}
            for setting in override.split(","):
                key, value = setting.split("=")
                # If the value can be converted to a float, do so
                try:
                    value = float(value)
                except ValueError:
                    pass
                override_dict[key] = value
            texture_data.update(override_dict)
        except Exception as e:
            print(f"Error: {e}")
            print("Invalid override settings. Ignoring.")
    print(f"Generated JSON data: {texture_data}")
    return texture_data

# Main function to process directories and files
def main(mod_name, submod_name=None, suffix='', path=None, suffix_filter=None, override=None):
    app = QApplication(sys.argv)
    # Initialize paths
    if not path:
        path = BASE_MOD_FOLDER
    base_path = os.path.join(path, mod_name, 'textures', 'pbr')
    patcher_path = os.path.join(path, mod_name, 'PBRNifPatcher')

    # Prepare output directory
    if not os.path.exists(patcher_path):
        os.makedirs(patcher_path)

    # Collect all texture files
    texture_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.dds'):
                file_path = os.path.relpath(os.path.join(root, file), base_path) 
                if submod_name and submod_name not in file_path:
                    continue
                file_path = file_path.lower()
                print(f"Found texture: {file_path}")
                texture_files.append(file_path.replace("\\", "/"))

    print(f"Found {len(texture_files)} texture files.")
    # Organize texture files into groups
    texture_groups = {}
    current_main_group = None

    for file_path in sorted(texture_files):
        file_name = os.path.splitext(file_path)[0]
        # set all names to lower case
        file_name = file_name.lower()
        print(f"Processing: {file_name}")
        valid_suffixes = ['_n', '_rmaos', '_s', '_g', '_p', '_cnr', '_coat', '_fuzz']
        if any(file_name.endswith(suffix) for suffix in valid_suffixes):
            # n or rmaos indicates the start of a new main group
            # s, g, p are secondary textures
            name = file_name.rsplit('_', 1)[0]
        else:
            name = file_name
        if name not in texture_groups:
            texture_groups[name] = {'name': name, 'is_main': False, 'main': None}
            if suffix and (not suffix_filter or suffix_filter in file_path):
                texture_groups[name]['suffix'] = suffix
                print(f"Suffix for {name}: {suffix}")
            print(f"New group: {name}")
        if name + '.dds' in texture_files:
            texture_groups[name]['d_path'] = name + '.dds'
        if name + '_n.dds' in texture_files:
            texture_groups[name]['n_path'] = name + '_n.dds'
            texture_groups[name]['is_main'] = True
            current_main_group = texture_groups[name]
        if name + '_rmaos.dds' in texture_files:
            texture_groups[name]['rmaos_path'] = name + '_rmaos.dds'
            texture_groups[name]['is_main'] = True
            current_main_group = texture_groups[name]
        if name + '_s.dds' in texture_files:
            texture_groups[name]['s_path'] = name + '_s.dds'
        if name + '_g.dds' in texture_files:
            texture_groups[name]['g_path'] = name + '_g.dds'
        if name + '_p.dds' in texture_files:
            texture_groups[name]['p_path'] = name + '_p.dds'
        if name + '_cnr.dds' in texture_files:
            texture_groups[name]['cnr_path'] = name + '_cnr.dds'
        if name + '_coat.dds' in texture_files:
            texture_groups[name]['coat_path'] = name + '_coat.dds'
        if name + '_fuzz.dds' in texture_files:
            texture_groups[name]['fuzz_path'] = name + '_fuzz.dds'
        if 'n_path' not in texture_groups[name] or 'rmaos_path' not in texture_groups[name]:
            texture_groups[name]['is_main'] = False
            if current_main_group:
                texture_groups[name]['main'] = current_main_group['name']

    print(f"Found {len(texture_groups)} texture groups.")
    print(texture_groups)

    # 使用组织器
    organizer = TextureGroupOrganizer(texture_groups)
    organizer.run()
    texture_groups = organizer.get_organized_groups()

    # 生成 JSON 数据
    json_data = []
    main_groups = {key: group for key, group in texture_groups.items() if group.get('is_main')}
    print(f"Found {len(main_groups)} main groups.")
    
    for group_name, group in texture_groups.items():
        if group['is_main']:
            json_data.append(create_texture_group_json(group, None, override))
        elif group['main']:
            main_group = texture_groups[group['main']]
            json_data.append(create_texture_group_json(group, main_group, override))

    print(json_data)

    # Output file name
    json_file_name = f"{mod_name}"
    if submod_name:
        json_file_name += f" - {submod_name}"
    json_file_name += ".json"

    # Write JSON to file
    json_path = os.path.join(patcher_path, json_file_name)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

    print(f"JSON configuration written to: {json_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate texture configuration JSON for Skyrim modding.')
    parser.add_argument('-n', '--mod_name', required=True, help='The name of the mod.')
    parser.add_argument('-s', '--submod_name', help='Name of the submod (optional).')
    parser.add_argument('-d', '--suffix', nargs='?', const='_d', default='', help='Diffuse suffix for the texture group (optional).')
    parser.add_argument('-p', '--path', help='Path to the mod folder.')
    parser.add_argument('-f', '--suffix_filter', help='Filter for the suffix of the texture group.')
    # Add an argument "override" to specifically set the settings in json file
    # e.g. -o "parallax=True,displacement_scale=1.0..."
    parser.add_argument('-o', '--override', help='Override settings for the texture group.')

    args = parser.parse_args()
    main(args.mod_name, args.submod_name, args.suffix, args.path, args.suffix_filter, args.override)