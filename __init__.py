bl_info = {
    "name": "Collection Enforce",
    "author": "Gorgious56",
    "version": (1, 0),
    "blender": (4, 1, 0),
    "description": "This adds a feature to collections to let the user enforce props to the collection children, like viewport color, wire visibility, etc.",
    "doc_url": "https://github.com/Gorgious56/blender_collection_enforce_props/tree/main",
    "category": "Interface",
}


import bpy
from bpy.props import (
    PointerProperty,
    EnumProperty,
    BoolProperty,
    FloatVectorProperty,
    IntProperty,
)
from bpy.types import PropertyGroup
from bpy.app.handlers import persistent



def set_dirty(self, context):
    self.is_dirty = True
    self.should_enforce_any = any([getattr(self, attr) for attr in self.__annotations__ if attr.endswith("enforce")])


class GU_PG_EnforceProps(PropertyGroup):
    NOT_ENFORCED_ATTRIBUTE_NAMES = ("is_dirty", "last_item_count", "should_enforce_any")
    is_dirty: BoolProperty(default=False)
    last_item_count: IntProperty(default=-1, update=set_dirty)
    should_enforce_any: BoolProperty(default=False)

    show_name_enforce: BoolProperty(default=False, update=set_dirty)
    show_name: BoolProperty(default=False, update=set_dirty)

    show_axis_enforce: BoolProperty(default=False, update=set_dirty)
    show_axis: BoolProperty(default=False, update=set_dirty)

    show_wire_enforce: BoolProperty(default=False, update=set_dirty)
    show_wire: BoolProperty(default=False, update=set_dirty)

    show_all_edges_enforce: BoolProperty(default=False, update=set_dirty)
    show_all_edges: BoolProperty(default=False, update=set_dirty)

    show_texture_space_enforce: BoolProperty(default=False, update=set_dirty)
    show_texture_space: BoolProperty(default=False, update=set_dirty)

    show_in_front_enforce: BoolProperty(default=False, update=set_dirty)
    show_in_front: BoolProperty(default=False, update=set_dirty)

    display_type_enforce: BoolProperty(default=False, update=set_dirty)
    display_type: EnumProperty(
        items=(
            ("BOUNDS", "Bounds", ""),
            ("WIRE", "Wire", ""),
            ("SOLID", "Solid", ""),
            ("TEXTURED", "Textured", ""),
        ),
        default="TEXTURED",
        name="Display",
        update=set_dirty,
    )

    color_enforce: BoolProperty(default=False, update=set_dirty)
    color: FloatVectorProperty(
        subtype="COLOR",
        size=4,
        min=0,
        max=1,
        default=(1, 1, 1, 1),
        name="Color",
        update=set_dirty,
    )

    def draw(self, layout):
        layout = layout.column(align=True)
        for attr in self.__annotations__:
            if attr in GU_PG_EnforceProps.NOT_ENFORCED_ATTRIBUTE_NAMES:
                continue
            if attr.endswith("enforce"):
                continue
            row = layout.row(align=True, heading=attr.replace("_", " ").title())
            row.prop(self, attr + "_enforce", text="")
            col = row.row(align=True)
            col.prop(self, attr, text="")
            col.active = getattr(self, attr + "_enforce")

    def should_update_enforcement(self):
        if not self.should_enforce_any:
            return self.is_dirty
        if (objects_count := len(self.id_data.all_objects)) == self.last_item_count:
            return self.is_dirty
        else:
            self.last_item_count = objects_count
        return True

@persistent
def enforce(scene):
    for col in scene.collection.children_recursive:
        props = col.enforce
        children_recursive = col.children_recursive
        for col_children in children_recursive:
            if col_children.enforce.is_dirty:
                props.is_dirty = True
                break
        if not props.should_update_enforcement():
            continue
        for attr in props.__annotations__:
            if attr in GU_PG_EnforceProps.NOT_ENFORCED_ATTRIBUTE_NAMES:
                continue
            if attr.endswith("enforce"):
                continue
            if getattr(props, attr + "_enforce"):
                for obj in col.all_objects:
                    setattr(obj, attr, getattr(props, attr))
            for col_children in children_recursive:
                col_children.enforce.is_dirty = True

        props.is_dirty = False


class GU_PT_collection_enforce(bpy.types.Panel):
    bl_label = "Enforce"
    bl_idname = "GU_PT_collection_enforce"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "collection"

    def draw(self, context):
        context.collection.enforce.draw(self.layout)


def register():
    bpy.utils.register_class(GU_PT_collection_enforce)
    bpy.utils.register_class(GU_PG_EnforceProps)
    bpy.types.Collection.enforce = PointerProperty(type=GU_PG_EnforceProps)
    bpy.app.handlers.depsgraph_update_pre.append(enforce)


def unregister():
    bpy.app.handlers.depsgraph_update_pre.remove(enforce)
    del bpy.types.Collection.enforce
    bpy.utils.unregister_class(GU_PG_EnforceProps)
    bpy.utils.unregister_class(GU_PT_collection_enforce)


if __name__ == "__main__":
    register()
