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
    scn = bpy.context.scene
    
    # add a mesh and link it to the scene
    me = bpy.data.meshes.new(object_name + "Mesh")
    ob = bpy.data.objects.new(object_name, me)

    bm = bmesh.new()
    bm.from_mesh(me)
    uv_layer = bm.loops.layers.uv.new()
    
    scn.objects.link(ob)
    scn.objects.active = ob
    
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    
    # semantic index data
    posx_idx = 0
    posy_idx = 0
    posz_idx = 0
    
    normx_idx = 0
    normy_idx = 0
    normz_idx = 0
    
    u_idx = 0
    v_idx = 0
    
    # parsing variables
    vertex_attrib_types_array = []
    
    index_array = []
    position_array = []
    normal_array = []
    uv_array = []
    
    texture_files = []
    shader_files = []
    
    temp_pos_index = 0
    temp_normal_index = 0
    temp_texcoord_index = 0
    
    # read in rip file!
    signature, version = struct.unpack('LL', file.read(8))
    
    if version != 4:
      raise Exception("Not RIP file")
      
    face_count, vertex_count, vertex_size, textures_count, shaders_count, attributes_count = struct.unpack('LLLLLL', file.read(24))
    
    # read in vertex attributes
    for x in range(attributes_count):
      semantic = read_string(file)
      semantic_index, offset, size, type_map_elements = struct.unpack('LLLL', file.read(16))
      for y in range(type_map_elements):
        type_element = struct.unpack('L', file.read(4))[0]
        vertex_attrib_types_array.append(type_element)
      
      # detect semantic
      if semantic == "POSITION" and temp_pos_index == 0:
        posx_idx = offset / 4
        posy_idx = posx_idx + 1
        posz_idx = posx_idx + 2
        temp_pos_index += 1
      elif semantic == "NORMAL" and temp_normal_index == 0:
        normx_idx = offset / 4
        normy_idx = normx_idx + 1
        normz_idx = normx_idx + 2
        temp_normal_index += 1
      elif semantic == "TEXCOORD" and temp_texcoord_index == 0:
        u_idx = offset / 4
        v_idx = u_idx + 1
        temp_texcoord_index += 1
        
    # read in texture file list
    for x in range(textures_count):
      texture_files.append(read_string(file))
      
    # read in shader file list
    for x in range(shaders_count):
      shader_files.append(read_string(file))
      
    # read in indices
    for x in range(face_count):
      i0, i1, i2 = struct.unpack('LLL', file.read(12))
      index_array.append((i0, i1, i2))
      
    # read in vertices
    for x in range(vertex_count):
      vx = 0.0
      vy = 0.0
      vz = 0.0
      nx = 0.0
      ny = 0.0
      nz = 0.0
      tu = 0.0
      tv = 0.0
      
      # parse in elements
      for y in range(len(vertex_attrib_types_array)):
        temp_data = None
        element_type = vertex_attrib_types_array[y]
        
        if element_type == 0:
          temp_data = struct.unpack('f', file.read(4))[0]
        elif element_type == 1:
          temp_data = struct.unpack('L', file.read(4))[0]
        elif element_type == 2:
          temp_data = struct.unpack('l', file.read(4))[0]
        else:
          temp_data = struct.unpack('L', file.read(4))[0]
          
        if y == posx_idx: vx = float(temp_data) 
        if y == posy_idx: vy = float(temp_data)
        if y == posz_idx: vz = float(temp_data)
        
        if y == normx_idx: nx = float(temp_data)
        if y == normy_idx: ny = float(temp_data)
        if y == normz_idx: nz = float(temp_data)
        
        if y == u_idx: tu = float(temp_data)
        if y == v_idx: tv = float(temp_data)
        
      # add data to our arrays
      position_array.append((vx * -1,vz,vy))
      normal_array.append((nx * -1,nz,ny))
      uv_array.append((tu,tv * -1))
    
    # setup our material
    texture_file = None if len(texture_files) == 0 else texture_files[0]
    texture_path = os.path.join(tex_path, texture_file)
    
    mtl = bpy.data.materials.new(name=object_name)
    if texture_file is not None and os.path.isfile(texture_path):
      tex = bpy.data.textures.new(texture_file, type='IMAGE')
      tex.image = bpy.data.images.load(texture_path)
      
      mtex = mtl.texture_slots.add()
      mtex.texture = tex
    else:
      print("this might be null (" + texture_file + ") or it doesn't exist")
      
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
         ):

    load_rip(filepath,
             context,
             )

    return {'FINISHED'}
