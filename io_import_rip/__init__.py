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
    "author": "Dummiesman, 2.8 compatibility by xpawelsky",
    "version": (0, 0, 2),
    "blender": (2, 80, 0),
    "location": "File > Import",
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

    semantic_setting = bpy.props.EnumProperty(items= (('AUTO', 'Auto', 'Automatically detect vertex layout'),      
                                                      ('MANUAL', 'Manual', 'Enter vertex layout details manually')),      
                                                      name = "Vertex Layout") 

    
    vxlayout = bpy.props.IntProperty(name="VX", default=0)
    vylayout = bpy.props.IntProperty(name="VY", default=1)
    vzlayout = bpy.props.IntProperty(name="VZ", default=2)
    
    nxlayout = bpy.props.IntProperty(name="NX", default=3)
    nylayout = bpy.props.IntProperty(name="NY", default=4)
    nzlayout = bpy.props.IntProperty(name="NZ", default=5)
    
    tulayout = bpy.props.IntProperty(name="TU", default=6)
    tvlayout = bpy.props.IntProperty(name="TV", default=7)
    
    scale = bpy.props.FloatProperty(name="Scale", default=1.0)
    
    reusemats = BoolProperty(name="Re-use materials", description="Re-use existing materials from other RIP files (especially useful when loading an entire folder)", default=True)
    importall = BoolProperty(name="Import entire folder", description="Import all meshes in this folder", default=False)
    
    def draw(self, context):
        layout = self.layout
        sub = layout.row()
        sub.prop(self, "semantic_setting")
        
        if self.semantic_setting == "MANUAL":
          sub = layout.row()
          sub.prop(self, "vxlayout")
          sub.prop(self, "nxlayout")
          sub.prop(self, "tulayout")
          sub = layout.row()
          sub.prop(self, "vylayout")
          sub.prop(self, "nylayout")
          sub.prop(self, "tvlayout")
          sub = layout.row()
          sub.prop(self, "vzlayout")
          sub.prop(self, "nzlayout")
          sub.label("")
          
        sub = layout.row()
        sub.prop(self, "scale")
        
        sub = layout.row()
        sub.prop(self, "reusemats")
        sub = layout.row()
        sub.prop(self, "importall")
        
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

#2.8 Fix

def register():
	from bpy.utils import register_class
	register_class(ImportRIP)
	
	bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
		
def unregister():
	from bpy.utils import unregister_class
	unregister_class(ImportRIP)
	
	bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

#def register():
#    bpy.utils.register_module(__name__)
#
#    bpy.types.INFO_MT_file_import.append(menu_func_import)


#def unregister():
#    bpy.utils.unregister_module(__name__)
#
#    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
