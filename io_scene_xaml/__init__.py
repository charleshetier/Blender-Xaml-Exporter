bl_info = {
    "name": "Xaml Model Format (.xaml)",
    "author": "Charles HETIER",
    "version": (0, 45),
    "blender": (2, 6, 3),
    "api": 36302,
    "location": "File > Export > Xaml (.xaml)",
    "description": "Exports in Xaml Model Format (.xaml)",
    "warning": "This is still a beta version...",
    "category": "Import-Export"}

   
import os
import bpy
from bpy.props import *
from mathutils import *

import imp
if "xaml" in locals():
    imp.reload(xaml)	
if "io_xaml_exporter" in locals():
    imp.reload(io_xaml_exporter)

class XamlExporter(bpy.types.Operator):
    """Export to the Xaml model format (.xaml)"""

    bl_idname = "export.xaml"
    bl_label = "Export Xaml"
    
    #File path property field
    filepath = StringProperty(subtype='FILE_PATH')
    
    # General options
    Comprehensive = BoolProperty(name="Comprehensice method", description="Loop on face instead of vertices (vertices dulication, smooth management ect...).", default=True)
    ApplyModifiers = BoolProperty(name="Apply Modifiers", description="Apply object modifiers before export.", default=True)
    AddDefaultNamespaces = BoolProperty(name="Add default namespaces", description="Determine whether default namespaces are added in root node.", default=True)
    ExportTextures = BoolProperty(name="Export Textures", description="Reference external image files to be used by the model.", default=True)
    IsInDebugmode = BoolProperty(name="Debug mode", description="Run the exporter in debug mode.  Check the console for output.", default=False)

    # custom init methods
    def execute(self, context):
        if not self.filepath.lower().endswith(".xaml"):
            self.filepath += ".xaml"
        
        from . import xaml
        from . import io_xaml_exporter            

        # Initialize exporter
        io_xaml_exporter.Comprehensive = self.Comprehensive
        io_xaml_exporter.ApplyModifiers = self.ApplyModifiers
        io_xaml_exporter.AddDefaultNamespaces = self.AddDefaultNamespaces
        io_xaml_exporter.ExportTextures = self.ExportTextures
        io_xaml_exporter.IsInDebugmode = self.IsInDebugmode

        # Initialize writer
        writer = xaml.StreamWriter()
        writer.openTag("Viewport3D")

        # Default namespaces
        if self.AddDefaultNamespaces:
            writer.newLine()
            writer.addProperty("xmlns", "http://schemas.microsoft.com/winfx/2006/xaml/presentation")
            writer.newLine()
            writer.addProperty("xmlns:x", "http://schemas.microsoft.com/winfx/2006/xaml")
            print("Default namespaces added")
        
        print("\n**Gathering scene...**")
        # Gather Blender cameras
        print("\n- Gathering cameras")
        cameraList = [object for object in context.scene.objects
                                if object.type in ("CAMERA")
                                and object.parent is None]
        print("  -> %i cameras found" % len(cameraList))
                                
        # Gather Blender meshes
        print("\n- Gathering meshes")
        meshList = [object for object in context.scene.objects
                                if object.type in ("MESH")]
        print("  -> %i meshes found" % len(meshList))
        
        # Gather mesh materials
        # Select distinct materials -> to be optimized
        print("\n- Gathering materials")
        materialNameList = []
        materialList = []
        for object in meshList:
            print("tesselating mesh: %s" % object.name)
            object.data.calc_tessface()            

            print("scanning mesh: %s" % object.name)
            for material in object.data.materials:
                if material is not None and material.name not in materialNameList:
                    materialNameList.append(material.name)
                    materialList.append(material)
        materialNameList = None
        print("  -> %i materials found" % len(materialList))
     
        # Gather Blender lights
        print("\n- Gathering lights")
        lightList = [object for object in context.scene.objects
                                if object.type in ("LAMP")
                                and object.parent is None]
        print("  -> %i lights found" % len(lightList))
        
        # Write Xaml Resources
        io_xaml_exporter.beginResources(writer)
        for material in materialList:
            io_xaml_exporter.writeMaterial(writer, material)
        io_xaml_exporter.endResources(writer)
       
        # Write Xaml Camera
        if len(cameraList) > 0:
            io_xaml_exporter.beginCamera(writer)
            #for item in cameraList:
            #   io_xaml_exporter.writeCamera(writer, item)
            io_xaml_exporter.writeCamera(writer, cameraList[0])
            io_xaml_exporter.endCamera(writer)
        
        # Beginning of Viewport children
        io_xaml_exporter.beginChildren(writer)
        
        # Write Xaml meshes
        if self.Comprehensive:
            meshListTransparent = []
            for item in meshList:
                if io_xaml_exporter.meshHasTransparency(item):
                    meshListTransparent.append(item)
                else:
                    print("exporting mesh %s" % item.name)
                    io_xaml_exporter.writeMeshComprehensive(writer, item, item.to_mesh(bpy.context.scene, self.ApplyModifiers, "PREVIEW"))
            for item in meshListTransparent:
                print("exporting mesh %s" % item.name)
                io_xaml_exporter.writeMeshComprehensive(writer, item, item.to_mesh(bpy.context.scene, self.ApplyModifiers, "PREVIEW"))
            meshListTransparent = None
        else:
            for item in meshList:
                print("exporting mesh %s" % item.name)
                io_xaml_exporter.writeMeshOptimized(writer, item.to_mesh(bpy.context.scene, self.ApplyModifiers, "PREVIEW"))
            
        # Write Xaml lights
        for light in lightList:
            io_xaml_exporter.writeLight(writer, light)
        
        print("\n** Finalizing exported file **")
        
        # End of Viewport children
        io_xaml_exporter.endChildren(writer)

        # Write the file
        writer.closeAllTags()
        writer.commit(self.filepath)
        print("Exportation completed successfuly")
        return {"FINISHED"}
            
    def invoke(self, context, event):
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}
        
def menu_func(self, context):
    default_path = os.path.splitext(bpy.data.filepath)[0] + ".xaml"
    self.layout.operator(XamlExporter.bl_idname, text="Export Xaml Scene (.xaml)").filepath = default_path

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)
    print("registered")


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)
    print("unregistered")
    
if __name__ == "__main__":
    register()