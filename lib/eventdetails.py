'''
Copyright (C) 2017 CG Cookie
http://cgcookie.com
hello@cgcookie.com

Created by Jonathan Denning, Jonathan Williamson

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from ..common.maths import Point2D

class EventDetails:
    def __init__(self):
        self.context = None
        self.region  = None
        self.r3d     = None
        self.width   = None     # region width
        self.height  = None     # region height
        
        self.event   = None
        
        self.ctrl  = False
        self.shift = False
        self.alt   = False
        self.oskey = False
        self.value = False
        self.type  = False
        
        self.ftype   = None
        self.press   = None
        self.release = None
        
        self.mouse     = None   # current mouse location (wrt region)
        self.mousedown = None   # where the mouse was last pressed down
        self.mousepre  = None   # previous location of mouse
        
    
    def update(self, context, event):
        event_ctrl  = 'CTRL+'  if event.ctrl  else ''
        event_shift = 'SHIFT+' if event.shift else ''
        event_alt   = 'ALT+'   if event.alt   else ''
        event_oskey = 'OSKEY+' if event.oskey else ''
        event_ftype = event_ctrl + event_shift + event_alt + event_oskey + event.type
        
        self.context = context
        self.region  = context.region
        self.r3d     = context.space_data.region_3d
        self.width   = context.region.width
        self.height  = context.region.height
        
        self.event   = event

        self.ctrl  = event.ctrl
        self.shift = event.shift
        self.alt   = event.alt
        self.oskey = event.oskey
        self.value = event.value
        self.type  = event.type

        self.ftype   = event_ftype
        self.press   = event_ftype if event.value=='PRESS'   else None
        self.release = event_ftype if event.value=='RELEASE' else None

        if event.value == 'PRESS' and event.type in {'LEFTMOUSE','MIDDLEMOUSE','RIGHTMOUSE'}:
            # TODO: only handles (correctly) one mousepress at a time!
            self.mousedown = Point2D((float(event.mouse_region_x), float(event.mouse_region_y)))
            if event.type == 'LEFTMOUSE':
                self.mousedown_left = self.mousedown
            elif event.type == 'MIDDLEMOUSE':
                self.mousedown_middle = self.mousedown
            elif event.type == 'RIGHTMOUSE':
                self.mousedown_right = self.mousedown
        self.mousepre = self.mouse
        self.mouse    = Point2D((float(event.mouse_region_x), float(event.mouse_region_y)))
    
    def valid_mouse(self, size):
        mx,my = self.mouse
        sx,sy = size
        return mx >= 0 and my >= 0 and mx < sx and my < sy
