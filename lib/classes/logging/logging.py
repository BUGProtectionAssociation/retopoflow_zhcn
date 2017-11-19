import bpy
from ...common_utilities import showErrorMessage
from ....options import options

class OpenLog(bpy.types.Operator):
    """Open log text files in new window"""
    bl_idname = "wm.open_log"
    bl_label = "Open Log in Text Editor"
    
    @classmethod
    def poll(cls, context):
        return options['log_filename'] in bpy.data.texts

    def execute(self, context):
        self.openTextFile(options['log_filename'])
        return {'FINISHED'}

    def openTextFile(self, filename):

        # play it safe!
        if filename not in bpy.data.texts:
            showErrorMessage('Log file not found')
            return

        # duplicate the current area then change it to a text edito
        area_dupli = bpy.ops.screen.area_dupli('INVOKE_DEFAULT')
        win = bpy.context.window_manager.windows[-1]
        area = win.screen.areas[-1]
        area.type = 'TEXT_EDITOR'

        # load the text file into the correct space
        for space in area.spaces:
            if space.type == 'TEXT_EDITOR':
                space.text = bpy.data.texts[filename]

