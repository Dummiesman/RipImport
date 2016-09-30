# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, 2016
#
# ##### END LICENSE BLOCK #####

bl_info = {
    "name": "NinjaRipper RIP Format",
    "author": "Dummiesman",
    "version": (0, 0, 1),
    "blender": (2, 77, 0),
    "location": "File > Impor",
    "description": "Import RIP files",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.7/Py/"
                "Scripts/Import-Export/NINJARIPPER",
    "support": 'COMMUNITY',
    "category": "Import"}

import bpy
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        StringProperty,
        CollectionProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        )

class ImportRIP(bpy.types.Operator, ImportHelper):
    """Import from RIP file format (.rip)"""
    bl_idname = "import_scene.rip"
    bl_label = 'Import NinjaRipper (*.rip)'
    bl_options = {'UNDO'}

    filename_ext = ".rip"
    filter_glob = StringProperty(default="*.rip", options={'HIDDEN'})

    def execute(self, context):
        from . import import_rip
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            ))

        return import_rip.load(self, context, **keywords)


# Add to a menu
def menu_func_import(self, context):
    self.layout.operator(ImportRIP.bl_idname, text="NinjaRipper (.rip)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
