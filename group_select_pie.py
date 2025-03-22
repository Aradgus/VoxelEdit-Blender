import bpy
from bpy.types import Menu, Operator

# spawn an edit mode selection pie (run while object is in edit mode to get a valid output)

class OBJECT_OT_set_active_vertex_group(Operator):
    bl_idname = "object.set_active_vertex_group"
    bl_label = "Set Active Vertex Group"
    bl_description = "Set the active vertex group"

    group_index: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH' and obj.vertex_groups:
            obj.vertex_groups.active_index = self.group_index
            return {'FINISHED'}
        return {'CANCELLED'}

class VIEW3D_MT_PIE_vgroup_select(Menu):
    # label is displayed at the center of the pie menu.
    bl_idname = "VIEW3D_MT_PIE_vgroup_select"
    bl_label = "Select V-Group"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        obj = context.active_object
        if obj and obj.type == 'MESH':
            if obj.vertex_groups:
                for group in obj.vertex_groups:
                    pie.operator("object.set_active_vertex_group", text=group.name).group_index = group.index
            pie.operator("dialog.new_v_group", text="New Group")

class DialogNewVertexGroup(bpy.types.Operator):
    bl_idname = "dialog.new_v_group"
    bl_label = "New Vertex Group"
    bl_property = "new_v_group"
    new_v_group : bpy.props.StringProperty(name = "Name: ", default = "")

    def execute(self, context):
        obj = context.active_object
        bpy.ops.object.vertex_group_add()
        obj.vertex_groups.active.name = self.new_v_group 
        return {'FINISHED'}
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

classes = [OBJECT_OT_set_active_vertex_group, VIEW3D_MT_PIE_vgroup_select, DialogNewVertexGroup]
# Factory function to register classes
class_register, class_unregister = bpy.utils.register_classes_factory(classes)

def register():
    class_register()

def unregister():
    class_unregister()


if __name__ == "__main__":
    register()
    bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_PIE_vgroup_select")
