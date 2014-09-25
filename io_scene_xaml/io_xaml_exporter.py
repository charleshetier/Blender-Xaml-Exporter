from mathutils import Vector
from math import atan
from math import degrees
from math import sqrt
from math import acos

# Parameters
Comprehensive = False
ApplyModifiers = False
AddDefaultNamespaces = False
ExportTextures = False
IsInDebugmode = False

# Formats the name of the material
def formatMaterialName(material):
    return "M_%s" % (material.name.replace("."," ").replace(" ","_"))

def meshHasTransparency(mesh):
    return len([1 for material in mesh.data.materials
                    if material is not None and material.use_transparency]) > 0

# Begins the Viewport3D Resources tag
def beginResources(writer):
    writer.openTag("Viewport3D.Resources")

# Ends the Viewport3D Resources tag
def endResources(writer):
    writer.closeTagName("Viewport3D.Resources")

# Add a material
def writeMaterial(writer, material):
    print("\n** Processing material... **")
    writer.openTag("MaterialGroup")
    writer.addProperty("x:Key", formatMaterialName(material))
    
    # Diffuse material
    writer.openTag("DiffuseMaterial")
    writer.openTag("DiffuseMaterial.Brush")
    if len(material.texture_slots) > 0 and material.texture_slots[0] is not None and material.texture_slots[0].texture_coords == 'UV' and material.texture_slots[0].texture.image is not None:
        writer.openTag("ImageBrush")
        writer.addProperty("ImageSource", material.texture_slots[0].texture.image.filepath)
    else:
        writer.openTag("SolidColorBrush")
        writer.addColorProperty("Color", material.diffuse_color)
    if material.use_transparency and material.alpha < 1:
        writer.addProperty("Opacity", material.alpha)
    writer.closeTagName("DiffuseMaterial")
    
    # TODO manage texture
    # bpy.context.active_object.data.materials[0].texture_slots[0].texture.image.filepath
        
    
    # Check whether material has specularity
    if material.specular_intensity > 0:
        writer.openTag("SpecularMaterial")
        
        # Check specularity shader for specular power property
        if material.specular_shader == "BLINN":
            writer.addProperty("SpecularPower", material.specular_hardness * 100)
        elif material.specular_shader == "WARDISO":
            writer.addProperty("SpecularPower", material.specular_slope * 100)
        elif material.specular_shader == "TOON":
            writer.addProperty("SpecularPower", material.specular_toon_size * 100)
        elif material.specular_shader == "PHONG":
            writer.addProperty("SpecularPower", material.specular_hardness * 100)
        elif material.specular_shader == "COOKTORR":
            writer.addProperty("SpecularPower", material.specular_hardness * 100)
        writer.openTag("SpecularMaterial.Brush")
        writer.openTag("SolidColorBrush")
        writer.addColorProperty("Color", material.specular_color)
        writer.addProperty("Opacity", material.specular_intensity)
        writer.closeTagName("SpecularMaterial")
    
    # Check whether material has some emit
    elif material.emit > 0:
        writer.openTag("EmissiveMaterial")
        writer.openTag("SpecularMaterial.Brush")
        writer.openTag("SolidColorBrush")
        writer.addColorProperty("Color", material.diffuse_color)
        writer.addProperty("Opacity", material.emit)
        writer.closeTagName("SpecularMaterial")
    
    writer.closeTagName("MaterialGroup")
    print("Material exportation done")

# Begins the camera tag
def beginCamera(writer):
    writer.openTag("Viewport3D.Camera")
    
# Ends the camera tag
def endCamera(writer):
    writer.closeTagName("Viewport3D.Camera")

# Add camera objects
def writeCamera(writer, camera):
    print("\n** Processing camera... **")
    print("camera found!")
    if camera.data.type == "PERSP":
        writer.openTag("PerspectiveCamera")
        writer.addProperty("FieldOfView", degrees(atan(16/camera.data.lens)*2))
        
    else:
        writer.openTag("OrthographicCamera")
        writer.addProperty("Width", camera.data.ortho_scale)
    writer.addVectorProperty("Position", camera.location)
    writer.addProperty("NearPlaneDistance", camera.data.clip_start)
    writer.addProperty("FarPlaneDistance", camera.data.clip_end)
    writer.addEulerDirectionProperty("LookDirection", camera.matrix_local.to_euler())
    writer.addVectorProperty("UpDirection", Vector((0,0,1)))
    print("Camera exportation done")

# Begins the mesh tag
def beginChildren(writer):
    writer.openTag("Viewport3D.Children")
    
# Ends the mesh tag
def endChildren(writer):
    writer.closeTagName("Viewport3D.Children")

# Add a ligth object
def writeLight(writer, light):
    print("\n** Processing light... **")
    writer.openTag("ModelVisual3D")
    writer.openTag("ModelVisual3D.Content")
    
    if light.data.type == "POINT":
        writer.openTag("PointLight")
        writer.addVectorProperty("Position", light.location)
        
    elif light.data.type == "SPOT":
        writer.openTag("SpotLight")
        writer.addEulerDirectionProperty("Direction", light.rotation_euler)
        writer.addVectorProperty("Position", light.location)
        
    elif light.data.type == "SUN":
        writer.openTag("DirectionalLight")
        writer.addEulerDirectionProperty("Direction", light.rotation_euler)
        
    elif light.data.type == "AREA":
        writer.openTag("DirectionalLight")
        writer.addEulerDirectionProperty("Direction", light.rotation_euler)
        
    elif light.data.type == "HEMI":
        writer.openTag("AmbientLight")
    
    else:
        print("no type match for the LAMP!")
    
    writer.addColorProperty("Color", light.data.color)
    writer.closeTagName("ModelVisual3D")
    print("Light exportation done")

# Add mesh object
def writeMeshOptimized(writer, mesh):
    print("\n** Processing mesh with minimalist method... **")
    writer.openTag("ModelVisual3D")
    writer.openTag("ModelVisual3D.Content")
    writer.openTag("GeometryModel3D")
    writer.openTag("GeometryModel3D.Geometry")
    writer.openTag("MeshGeometry3D")
    
    print(" -> gathering data")
    # Get vertices
    vertices = [vertex.co for vertex in mesh.vertices]
    
    # Get vertex normals
    normals = [vertex.normal for vertex in mesh.vertices]
    
    # Create triangles from vertex indices
    indices = [face.vertices for face in mesh.tessfaces
                if len(face.vertices) == 3]
    indicesQuad = [face.vertices for face in mesh.tessfaces
                if len(face.vertices) == 4]
    indices.extend([[indice[0],indice[1],indice[3]] for indice in indicesQuad])
    indices.extend([[indice[1],indice[2],indice[3]] for indice in indicesQuad])
    
    # Get Texture UV Coordinates
    # TODO
    
    print(" -> writting data")
    # Set Geometry properties
    writer.newLine()
    writer.addVectorListProperty("Positions", vertices)
    writer.newLine()
    writer.addListListProperty("TriangleIndices", indices)
    writer.newLine()
    writer.addVectorListProperty("Normals", normals)
    writer.closeTagName("GeometryModel3D.Geometry")
    
    # Set material properties
    writer.openTag("GeometryModel3D.Material")
    writer.openTag("DiffuseMaterial")
    writer.openTag("DiffuseMaterial.Brush")
    writer.openTag("SolidColorBrush")
    writer.addProperty("Color", "Red")
    writer.addProperty("Opacity", 1)

    # end of list of meshes
    writer.closeTagName("ModelVisual3D")
    print("Minimalist method exportation done")

def writeMeshComprehensiveMaterialIteration(writer, mesh, meshData, material):
   
    currentVertexIndex = 0
    hasUvs = len(meshData.uv_textures) > 0
    if hasUvs:
        print("UV coordinates detected for mesh [%s] with material [%s]" % (mesh.name, material.name))

    vertices = []
    indices = []
    normals = []
    uvs = []
    
    # If there is no material assigned, material index is 0
    if material is None:
        materialIndex = 0
    else:
        materialIndex = [m.name for m in meshData.materials if m is not None].index(material.name)

    # for each face from current material, collect data
    for i, face in enumerate([f for f in meshData.tessfaces if f.material_index == materialIndex]):
        vertices.extend( [meshData.vertices[vertex].co for vertex in face.vertices] )
        if len(face.vertices) == 3:
            indices.append([currentVertexIndex, currentVertexIndex + 1, currentVertexIndex + 2])
            if hasUvs:
                #print("Triangle uv face detected")
                uvs.extend([meshData.tessface_uv_textures.active.data[i].uv3, meshData.tessface_uv_textures.active.data[i].uv2, meshData.tessface_uv_textures.active.data[i].uv1])
        if len(face.vertices) == 4:
            indices.append([currentVertexIndex, currentVertexIndex + 1, currentVertexIndex + 3])
            indices.append([currentVertexIndex + 1, currentVertexIndex + 2, currentVertexIndex + 3])
            if hasUvs:
                #print("Quad uv face detected")
                uvs.extend([meshData.tessface_uv_textures.active.data[i].uv4, meshData.tessface_uv_textures.active.data[i].uv3, meshData.tessface_uv_textures.active.data[i].uv2, meshData.tessface_uv_textures.active.data[i].uv1])
        if face.use_smooth:
            normals.extend([meshData.vertices[index].normal for index in face.vertices])
        else:
            normals.extend([face.normal]*(len(face.vertices)))
        currentVertexIndex += len(face.vertices)
        
    if len(vertices) == 0:
        print("no face found for mesh [%s] with material [%s]: skipping this geometry..." % (meshData.name if meshData is not None else "no meshData", material.name if material is not None else "No material"))
        return
    
    # Initialize GeometryModel
    writer.openTag("GeometryModel3D")
    if material is not None:
        writer.addProperty("Material", "{StaticResource %s}" % (formatMaterialName(material)))
    writer.openTag("GeometryModel3D.Geometry")
    writer.openTag("MeshGeometry3D")
    
    # Set Geometry properties
    writer.newLine()
    writer.addVectorListProperty("Positions", vertices)
    writer.newLine()
    writer.addListListProperty("TriangleIndices", indices)
    writer.newLine()
    writer.addVectorListProperty("Normals", normals)
    if hasUvs:
        writer.newLine()
        writer.addPointListProperty("TextureCoordinates", uvs)
        
    # End of material-dependant mesh block
    writer.closeTagName("GeometryModel3D")

# Add mesh with comprehensice method
def writeMeshComprehensive(writer, mesh, meshData):
    print("\n** Processing mesh %s with comprehensice method... **" % meshData.name)

    writer.openTag("ModelVisual3D")
    writer.openTag("ModelVisual3D.Content")
    writer.openTag("Model3DGroup")
    
    if len(meshData.materials) > 0:
        # Split the mesh in the group based on materials
        print(" -> splitting mesh according to materials repartition")
        for material in meshData.materials:
            writeMeshComprehensiveMaterialIteration(writer, mesh, meshData, material)
    else:
        # The entire mesh with no associated material is taken into account
        print(" -> no material defined, mesh is kept in one block")
        writeMeshComprehensiveMaterialIteration(writer, mesh, meshData, None)
    
    writer.openTag("Model3DGroup.Transform")
    writer.openTag("Transform3DGroup")
    writer.openTag("Transform3DGroup.Children")
    
    # Scale transform
    print(" -> computing scale")
    writer.openTag("ScaleTransform3D")
    writer.addProperty("ScaleX", mesh.scale.x)
    writer.addProperty("ScaleY", mesh.scale.y)
    writer.addProperty("ScaleZ", mesh.scale.z)
    writer.closeTag()
    
    # Rotation transform
    print(" -> computing rotate")
    writer.openTag("RotateTransform3D")
    writer.openTag("RotateTransform3D.Rotation")
    writer.openTag("AxisAngleRotation3D ")
	
    writer.addEulerProperty("Axis",  mesh.matrix_local.to_euler())
    writer.addProperty("Angle", degrees(2 * acos(mesh.matrix_local.to_quaternion()[0])))
    writer.closeTagName("RotateTransform3D")
    
    # Translation transform
    print(" -> computing translate")
    writer.openTag("TranslateTransform3D")
    writer.addProperty("OffsetX", mesh.location.x)
    writer.addProperty("OffsetY", mesh.location.y)
    writer.addProperty("OffsetZ", mesh.location.z)
    writer.closeTagName("Model3DGroup")
    
    # end of list of meshes
    writer.closeTagName("ModelVisual3D")
    print("comprehensive method exportation done")