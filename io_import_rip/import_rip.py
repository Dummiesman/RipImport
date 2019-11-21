# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons BY-NC-SA:
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, 2016
#
# ##### END LICENSE BLOCK #####

import bpy, bmesh, mathutils
import time, struct, os

######################################################
# GLOBAL VARIABLES
######################################################
semantic_autodetect = True

posx_idx = 0
posy_idx = 0
posz_idx = 0

normx_idx = 0
normy_idx = 0
normz_idx = 0

u_idx = 0
v_idx = 0

g_scale = 1.0

reuse_materials = False


######################################################
# IMPORT MAIN FILES
######################################################
def read_string(file):
    read_done = False
    read_str = ""
    
    while read_done == False:
      v = struct.unpack('B', file.read(1))[0]
      if v == 0:
        read_done = True
      else:
        read_str += chr(v)

    return read_str
    
def read_rip_file(file, object_name, tex_path):
    # check our signature / version before adding anything to the scene
    signature, version = struct.unpack('LL', file.read(8))
    
    if signature != 3735929054:
      file.close()
      raise Exception(object_name + " contains an invalid rip signature.")
    if version != 4:
      file.close()
      raise Exception(object_name + " contains an invalid rip version.")
      
    # add a mesh and link it to the scene
#   scn = bpy.context.scene
    me = bpy.data.meshes.new(object_name + "Mesh")
    ob = bpy.data.objects.new(object_name, me)

    bm = bmesh.new()
    bm.from_mesh(me)
    uv_layer = bm.loops.layers.uv.new()
    
#   scn.objects.link(ob)
    bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    
    # parsing variables
    vertex_attrib_types_array = []
    
    index_array = []
    position_array = []
    normal_array = []
    uv_array = []
    
    texture_files = []
    shader_files = []
    
    found_pos_index = False
    found_normal_index = False
    found_texcoord_index = False
    
    # continue reading the rip file      
    face_count, vertex_count, vertex_size, textures_count, shaders_count, attributes_count = struct.unpack('LLLLLL', file.read(24))
    
    # read in vertex attributes
    for x in range(attributes_count):
      semantic = read_string(file)
      semantic_index, offset, size, type_map_elements = struct.unpack('LLLL', file.read(16))
      for y in range(type_map_elements):
        type_element = struct.unpack('L', file.read(4))[0]
        vertex_attrib_types_array.append(type_element)
      
      # detect semantic
      if semantic_autodetect:
        if semantic == "POSITION" and not found_pos_index:
          global posx_idx, posy_idx, posz_idx
          posx_idx = offset / 4
          posy_idx = posx_idx + 1
          posz_idx = posx_idx + 2
          
          found_pos_index = True
          print("Detected POSITION layout [" + str(posx_idx) + ", " + str(posy_idx) + ", " + str(posz_idx) + "]")
        elif semantic == "NORMAL" and not found_normal_index:
          global normx_idx, normy_idx, normz_idx
          normx_idx = offset / 4
          normy_idx = normx_idx + 1
          normz_idx = normx_idx + 2
          
          found_normal_index = True
          print("Detected NORMAL layout [" + str(normx_idx) + ", " + str(normy_idx) + ", " + str(normz_idx) + "]")
        elif semantic == "TEXCOORD" and not found_texcoord_index:
          global u_idx, v_idx
          u_idx = offset / 4
          v_idx = u_idx + 1
          
          found_texcoord_index =  True
          print("Detected UV layout [" + str(u_idx) + ", " + str(v_idx) + "]")
        
    # read in texture file list
    for x in range(textures_count):
      texture_files.append(read_string(file))
      
    # read in shader file list
    for x in range(shaders_count):
      shader_files.append(read_string(file))
      
    # read in indices
    for x in range(face_count):
      index_array.append(struct.unpack('LLL', file.read(12)))
      
    # read in vertices
    for x in range(vertex_count):
      vx, vy, vz, nx, ny, nz, tu, tv = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
      
      # parse in elements
      for y in range(len(vertex_attrib_types_array)):
        attrib_value = None
        element_type = vertex_attrib_types_array[y]
        
        if element_type == 0:
          attrib_value = struct.unpack('f', file.read(4))[0]
        elif element_type == 1:
          attrib_value = float(struct.unpack('L', file.read(4))[0])
        elif element_type == 2:
          attrib_value = float(struct.unpack('l', file.read(4))[0])
        else:
          attrib_value = float(struct.unpack('L', file.read(4))[0])
          
        if y == posx_idx: vx = attrib_value * g_scale
        if y == posy_idx: vy = attrib_value * g_scale
        if y == posz_idx: vz = attrib_value * g_scale
        
        if y == normx_idx: nx = attrib_value
        if y == normy_idx: ny = attrib_value
        if y == normz_idx: nz = attrib_value
        
        if y == u_idx: tu = attrib_value
        if y == v_idx: tv = attrib_value
        
      # add data to our arrays
      position_array.append((vx * -1,vz,vy))
      normal_array.append((nx * -1,nz,ny))
      uv_array.append((tu,tv * -1))
    
    # setup our material
    texture_file = None if len(texture_files) == 0 else texture_files[0]
    material_name = None if texture_file is None else texture_file.replace(".","_")
    
    if texture_file is not None:
      texture_path = os.path.join(tex_path, texture_file)
    
    #
    mtl = None
    if material_name is not None and material_name in bpy.data.materials and reuse_materials:
      mtl = bpy.data.materials[material_name]
    elif texture_file is not None:
      mtl = bpy.data.materials.new(name=material_name)
	  
      mtl.use_nodes = True
      bsdf = mtl.node_tree.nodes["Principled BSDF"]
      
      # load texture onto the material
      if texture_file in bpy.data.textures:
        mtex = mtl.texture_slots.add()
        mtex.texture = bpy.data.textures[texture_file]
      elif os.path.isfile(texture_path):
        tex = mtl.node_tree.nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(texture_path)
        mtl.node_tree.links.new(bsdf.inputs['Base Color'], tex.outputs['Color'])
    
    if mtl is not None:
      ob.data.materials.append(mtl)
    
    # build mesh data
    for x in range(len(position_array)):
      vtx = bm.verts.new(position_array[x])
      vtx.normal = mathutils.Vector(normal_array[x])
    
    bm.verts.ensure_lookup_table()
    for f in index_array:
      try:
        face = bm.faces.new((bm.verts[f[0]], bm.verts[f[1]], bm.verts[f[2]]))
        face.smooth = True
        face.material_index = 0
        
        for uv_set_loop in range(3):
          face.loops[uv_set_loop][uv_layer].uv = uv_array[f[uv_set_loop]]
      except Exception as e:
        print(str(e))
                        
    # free resources
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bm.to_mesh(me)
    bm.free()
      

######################################################
# IMPORT
######################################################
def load_rip(filepath,
             context):

    print("importing rip: %r..." % (filepath))

    time1 = time.clock()
    file = open(filepath, 'rb')

    # start reading our rip file
    filepath_basename = os.path.basename(filepath)
    texture_search_path = filepath[:-len(filepath_basename)]
    
    read_rip_file(file, filepath_basename[:-4], texture_search_path)

    print(" done in %.4f sec." % (time.clock() - time1))
    file.close()


def load(operator,
         context,
         filepath="",
         semantic_setting = "AUTO",
         vxlayout = 0,
         vylayout = 1,
         vzlayout = 2,
         nxlayout = 3,
         nylayout = 4,
         nzlayout = 5,
         tulayout = 6,
         tvlayout = 7,
         scale = 1.0,
         reusemats = False,
         importall = False,
         ):
    
    # setup global variables
    global semantic_autodetect, g_scale, reuse_materials
    semantic_autodetect = True if semantic_setting == "AUTO" else False
    g_scale = scale
    reuse_materials = reusemats
    
    if semantic_autodetect == False:
      global posx_idx, posy_idx, posz_idx, normx_idx, normy_idx, normz_idx, u_idx, v_idx
      posx_idx = vxlayout
      posy_idx = vylayout
      posz_idx = vzlayout
      normx_idx = nxlayout
      normy_idx = nylayout
      normz_idx = nzlayout
      u_idx = tulayout
      v_idx  = tvlayout
      
    # load file(s)
    if importall:
      ripdir = os.path.dirname(filepath)
      for file in os.listdir(ripdir):
        if file.lower().endswith(".rip"):
          load_rip(os.path.join(ripdir, file), context)
    else:
      load_rip(filepath,
              context,
              )

    return {'FINISHED'}
