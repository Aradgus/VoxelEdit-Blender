import bpy
from . import main
from . import group_select_pie

def register():
    group_select_pie.register()  
    main.register()  
    
def unregister():
    main.unregister()
    group_select_pie.unregister()


if __name__ == "__main__":
    register()

