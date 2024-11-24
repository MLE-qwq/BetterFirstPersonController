from turtle import position,pu
from ursina import *
from panda3d.core import WindowProperties
import math,time
import mouse as cursor

app=Ursina(size=Vec2(1270,768))

#Constants
WALKING_SPEED=5
FLYING_SPEED=15
FLYING_SPEED_H=8
CROUCH_SPEED=2.5
SPRINTING_SPEED=7
SPRINTING_FOV=SPRINTING_SPEED
GRAVITY=20
MAX_JUMP_HEIGHT=1.2
JUMPLING_SPEED=math.sqrt(2*GRAVITY*MAX_JUMP_HEIGHT)
TERMINAL_VELOCITY=50

MOVEMENT_ACC_ADD=2
MOVEMENT_ACC=0.8
HOVERING_ACC_ADD=1
HOVERING_ACC=0.2

PLAYER_HEIGHT=1.8
PLAYER_WIDTH=0.7
PLAYER_CAMERA_POSITION=0.95
PLAYER_CROUCH_CAMERA_POSITION=0.8
MAX_REACH=8
PLAYER_FOV=90.0
PLAYER_SPRINTING_FOV=8.0
FOV_OFFSET_DELTA=1.5
CAMERA_OFFSET_DELTA=0.05

#Variables
world={}

grass_texture=load_texture('assets\\textures\\grass_block.png')
stone_texture=load_texture('assets\\textures\\stone.png')
dirt_texture=load_texture('assets\\textures\\dirt.png')
glass_texture=load_texture('assets\\textures\\glass.png')
#sky_texture=load_texture('assets\\textures\\Skybox.png')
punch_sound=Audio('assets\\sounds\\Punch_Sound.wav', loop=False, autoplay=False)
block_pick=1
last_trigger=0

_window_x,_window_y,_window_w,_window_h=0,0,0,0
fullscreen_cd=0
paused=False
custom_fullscreen=False
pause_menu=Panel(scale=(5,1),position=(0,0),model='quad')
pause_menu.enabled=False

def round_(x):
    a=x*10
    if (a%10>=5):
        return math.ceil(x)
    return math.floor(x)

def normalize(position):
    x,y,z=position
    x,y,z=x,y,z
    x,y,z=(int(round_(x)),int(round_(y)),int(round_(z)))
    return (x,y,z)
    

def add_block(x,y,z,bid,txt):
    if (normalize((x,y,z)) in world):
        return
    voxel=Voxel(position=(x,y,z),texture=txt)
    world[normalize((x,y,z))]=(bid,txt,voxel)

def remove_block(x,y,z):
    if (normalize((x,y,z)) in world):
        destroy(world[normalize((x,y,z))][2])
        del world[normalize((x,y,z))]
        
def collide(position):
    if (normalize(position) in world):
        return True
    return False

def timer_1000():
   update_resolution
   
def update_resolution():
    global window
    try:
        if os_name == 'Windows':     # windows
            import ctypes
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            self.screen_resolution = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))

        elif os_name == 'Linux':
            import Xlib
            import Xlib.display
            resolution = Xlib.display.Display().screen().root.get_geometry()
            self.screen_resolution = Vec2(resolution.width, resolution.height)

        elif os_name == 'Darwin':     # mac
            from AppKit import NSScreen
            size = NSScreen.mainScreen().frame().size
            self.screen_resolution = [size.width, size.height]
    except:
        from screeninfo import get_monitors
        self.screen_resolution = [get_monitors()[0].width, get_monitors()[0].height]

#Updates every frame
def update():
    #print(base.win.getWindowHandle().getIntHandle())
    global custom_fullscreen,fullscreen_cd,_window_x,_window_y,_window_w,_window_h
    if not(custom_fullscreen):
        if (time.time()-fullscreen_cd>=0.5):
            window_x,window_y=base.win.properties.getXOrigin(),base.win.properties.getYOrigin()
            window_w,window_h=base.win.properties.getXSize(),base.win.properties.getYSize()
            if (window_w==window.screen_resolution[0]) and (window_x==0):
                custom_fullscreen=True
                window.fullscreen=True
                window.setFullscreen(True)
                base.win.requestProperties(window)
            else:
                _window_x,_window_y,_window_w,_window_h=window_x,window_y,window_w,window_h
    
    global block_pick,last_trigger,paused
    if held_keys['1']: block_pick=1
    if held_keys['2']: block_pick=2
    if held_keys['3']: block_pick=3
    if held_keys['4']: block_pick=4
    
    if not(paused):
        if (not base.win.properties.getForeground()) or (base.win.properties.getMinimized()):
            player.pause(True)
            held_keys['w'],held_keys['s'],held_keys['a'],held_keys['d'],held_keys['space'],held_keys['shift'],held_keys['control'],held_keys['tab']=0,0,0,0,0,0,0,0
    
    dt=time.time()-last_trigger
    if (dt>=1.0):
        last_trigger=time.time()
        timer_1000()


class Voxel(Button):
    def __init__(self, position=(0, 0, 0), texture=grass_texture):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0,
            texture=texture,
            color=color.color(0,0,random.uniform(0.85,1)),
            scale=1
        )
    
    #What happens to blocks on inputs
    def input(self,key):
        global paused
        if (paused):
            return
        if self.hovered:
            if key=='right mouse down':
                nx,ny,nz=self.position.x+mouse.normal.x,self.position.y+mouse.normal.y,self.position.z+mouse.normal.z
                global player
                x,y,z=player.position.x,player.position.y,player.position.z
                if (sqrt((nx-x)*(nx-x)+(ny-y)*(ny-y)+(nz-z)*(nz-z))<=MAX_REACH):
                    if not(normalize((nx,ny,nz)) in world):
                        vx=[-PLAYER_WIDTH/2,PLAYER_WIDTH/2,-PLAYER_WIDTH/2,PLAYER_WIDTH/2,-PLAYER_WIDTH/2,PLAYER_WIDTH/2,-PLAYER_WIDTH/2,PLAYER_WIDTH/2,-PLAYER_WIDTH/2,PLAYER_WIDTH/2,-PLAYER_WIDTH/2,PLAYER_WIDTH/2]
                        vy=[0,0,0,0,PLAYER_HEIGHT/2,PLAYER_HEIGHT/2,PLAYER_HEIGHT/2,PLAYER_HEIGHT/2,PLAYER_HEIGHT,PLAYER_HEIGHT,PLAYER_HEIGHT,PLAYER_HEIGHT]
                        vz=[-PLAYER_WIDTH/2,-PLAYER_WIDTH/2,PLAYER_WIDTH/2,PLAYER_WIDTH/2,-PLAYER_WIDTH/2,-PLAYER_WIDTH/2,PLAYER_WIDTH/2,PLAYER_WIDTH/2,-PLAYER_WIDTH/2,-PLAYER_WIDTH/2,PLAYER_WIDTH/2,PLAYER_WIDTH/2]
                        legal=True
                        for i in range(12):
                            if (normalize((x+vx[i],y+vy[i],z+vz[i]))==normalize((nx,ny,nz))):
                                legal=False
                                break
                        if (legal):
                            if block_pick==1:
                                add_block(nx,ny,nz,'grass_block',grass_texture)
                            if block_pick==2:
                                add_block(nx,ny,nz,'dirt',dirt_texture)
                            if block_pick==3:
                                add_block(nx,ny,nz,'stone',stone_texture)
                            if block_pick==4:
                                add_block(nx,ny,nz,'glass',glass_texture)
                            punch_sound.play()
            if key=='left mouse down':
                punch_sound.play()
                remove_block(self.position.x,self.position.y,self.position.z)
        
class FirstPersonController(Entity):
    def __init__(self, **kwargs):
        self.cursor=Entity(parent=camera.ui, model='quad', color=rgb(220,220,220), scale=.005, rotation_z=45)
        super().__init__()
        self.speed=WALKING_SPEED
        self.camera_pivot=Entity(parent=self, y=PLAYER_HEIGHT*PLAYER_CAMERA_POSITION)
        self._cp=PLAYER_HEIGHT*PLAYER_CAMERA_POSITION #camera_pivot y pos offset
        camera.parent=self.camera_pivot
        camera.position=(0,0,0)
        camera.rotation=(0,0,0)
        camera.fov=PLAYER_FOV
        #mouse.locked=True
        self._fov=PLAYER_FOV
        self.__fov=-1
        self.mouse_sensitivity=0.2
        self.crouching=False
        self.sprinting=False
        self.dy=0
        self.grounded=False
        self.head_bonked=False
        self.flying=False
        self.move_a=MOVEMENT_ACC
        self.vx=0 #Velocity on each direction
        self.vz=0
        self.last_called=-1
        window.set_cursor_hidden(True)
        window.set_title('BetterFirstPersonController - MLE_qwq')
        #window.set_icon()
        base.win.requestProperties(window)
        for key, value in kwargs.items():
            setattr(self, key ,value)
        self.position=Vec3(0,5,0)
    
    def update(self):
        dt=time.dt
        if (self.last_called==-1):
            self.last_called=0
            window_x,window_y=base.win.properties.getXOrigin(),base.win.properties.getYOrigin()
            window_w,window_h=base.win.properties.getXSize(),base.win.properties.getYSize()
            center_x=window_x+window_w//2
            center_y=window_y+window_h//2
            cursor.move(center_x,center_y,absolute=True,duration=0)
            
        global paused
        if (paused):
            return
        #Process camera rotation
        cursor_pos=cursor.get_position()
        cursor_x,cursor_y=cursor_pos[0],cursor_pos[1]
        window_x,window_y=base.win.properties.getXOrigin(),base.win.properties.getYOrigin()
        window_w,window_h=base.win.properties.getXSize(),base.win.properties.getYSize()
        cursor_velocity_x,cursor_velocity_y=cursor_x-window_x-window_w//2,cursor_y-window_y-window_h//2
        self.rotation_y+=cursor_velocity_x*self.mouse_sensitivity
        self.camera_pivot.rotation_x+=cursor_velocity_y*self.mouse_sensitivity
        self.camera_pivot.rotation_x=clamp(self.camera_pivot.rotation_x, -90, 90)
        
        center_x=window_x+window_w//2
        center_y=window_y+window_h//2
        cursor.move(center_x,center_y,absolute=True,duration=0)
        
        #Process new position
        
        #Every vertex of the player's hitbox
        vx=[-PLAYER_WIDTH/2,PLAYER_WIDTH/2,-PLAYER_WIDTH/2,PLAYER_WIDTH/2,-PLAYER_WIDTH/2,PLAYER_WIDTH/2,-PLAYER_WIDTH/2,PLAYER_WIDTH/2,-PLAYER_WIDTH/2,PLAYER_WIDTH/2,-PLAYER_WIDTH/2,PLAYER_WIDTH/2]
        vy=[0,0,0,0,PLAYER_HEIGHT/2,PLAYER_HEIGHT/2,PLAYER_HEIGHT/2,PLAYER_HEIGHT/2,PLAYER_HEIGHT,PLAYER_HEIGHT,PLAYER_HEIGHT,PLAYER_HEIGHT]
        vz=[-PLAYER_WIDTH/2,-PLAYER_WIDTH/2,PLAYER_WIDTH/2,PLAYER_WIDTH/2,-PLAYER_WIDTH/2,-PLAYER_WIDTH/2,PLAYER_WIDTH/2,PLAYER_WIDTH/2,-PLAYER_WIDTH/2,-PLAYER_WIDTH/2,PLAYER_WIDTH/2,PLAYER_WIDTH/2]
        
        x,y,z=self.position
        dx,dy,dz=0.0,0.0,0.0
        
        if not(self.flying):
            if (held_keys['shift']>0):
                self.sprinting=False
                self.crouching=True
                self._cp=PLAYER_CROUCH_CAMERA_POSITION*PLAYER_HEIGHT
                self.speed=CROUCH_SPEED
            elif (held_keys['control']>0):
                self.sprinting=True
                self.crouching=False
                self.speed=SPRINTING_SPEED
                self._cp=PLAYER_CAMERA_POSITION*PLAYER_HEIGHT
            else:
                self.crouching=False
                self._cp=PLAYER_CAMERA_POSITION*PLAYER_HEIGHT
        else:
            self.speed=FLYING_SPEED
            self.sprinting=False
            self.crouching=False
            self._cp=PLAYER_CAMERA_POSITION*PLAYER_HEIGHT
        
        if (self.camera_pivot.y<self._cp):
            self.camera_pivot.y+=CAMERA_OFFSET_DELTA
            if (self.camera_pivot.y+CAMERA_OFFSET_DELTA>=self._cp):
                self.camera_pivot.y=self._cp
        if (self.camera_pivot.y>self._cp):
            self.camera_pivot.y-=CAMERA_OFFSET_DELTA
            if (self.camera_pivot.y-CAMERA_OFFSET_DELTA<=self._cp):
                self.camera_pivot.y=self._cp
        
        if (self.flying):
            self.dy=0
            if (held_keys['space']>0):
                dy=FLYING_SPEED_H*dt
            if (held_keys['shift']>0):
                dy=-FLYING_SPEED_H*dt
        else:
            if (self.grounded):
                if (held_keys['space']>0):
                    self.dy=JUMPLING_SPEED
                    self.grounded=False
                    dy=JUMPLING_SPEED*dt
            else:
                self.dy-=dt*GRAVITY
                self.dy=max(self.dy,-TERMINAL_VELOCITY)
                dy+=self.dy*dt
                detected=False
                i=ceil(y)
                while (i>=floor(y+dy)):
                    for j in range(12):
                        if (collide(normalize((x+vx[j],i,z+vz[j])))):
                            dy=max(math.floor(i)+0.5-y,dy)
                            detected=True
                            break
                    if (detected):
                        break
                    i-=1
                          
        self.direction=Vec3(self.forward*(held_keys['w']-held_keys['s'])+ self.right*(held_keys['d']-held_keys['a'])).normalized()
        move_amount=self.direction*self.speed
        dx,dz=move_amount.x,move_amount.z
        
        #Velocity stuff
        '''
        self.vx,self.vz: Current velocity on each direrction
        dx,dz: Target velocity
        '''
        x0,x1,z0,z1=self.vx,dx,self.vz,dz
        v_dist=sqrt((x0-x1)*(x0-x1)+(z0-z1)*(z0-z1))
        if (self.flying):
            if (x1+z1==0):
                self.move_a=HOVERING_ACC
            else:
                self.move_a=HOVERING_ACC_ADD
        else:
            if (x1+z1==0):
                self.move_a=MOVEMENT_ACC
            else:
                self.move_a=MOVEMENT_ACC_ADD
        if (v_dist!=0):
            ax=self.move_a*abs(x0-x1)/v_dist
            az=self.move_a*abs(z0-z1)/v_dist
            if (x0<x1):
                x0+=ax
                if (x0>x1):
                    x0=x1
            elif (x0>x1):
                x0-=ax
                if (x0<x1):
                    x0=x1
            if (z0<z1):
                z0+=az
                if (z0>z1):
                    z0=z1
            elif (z0>z1):
                z0-=az
                if (z0<z1):
                    z0=z1
            self.vx,self.vz=x0,z0
            dx,dz=x0*dt,z0*dt
            #print('△x=%.2f,△z=%.2f,位移=%.2f,a=%.2f,△v_x=%.2f,△v_z=%.2f,v_x=%.2f,v_z=%.2f'%(abs(x0-x1),abs(z0-z1),abs(v_dist),self.move_a,ax,az,x0,z0))
        else:
            dx,dz=x0*dt,z0*dt
            #print('△v_x=%.2f,△v_z=%.2f'%(x0,z0))
            
        #Detect X position
        detected=False
        wont_fall=False
        for i in range(12): #Once added dx the position has a block in its place, dx is illegal
            if (collide(normalize((x+vx[i]+dx,y+vy[i],z+vz[i])))):
                detected=True
        for i in range(12): #Crouching stuff, once added dx every vertex isn't on a block, dx is illegal 
            if (collide(normalize((x+vx[i]+dx,y+vy[i]-1,z+vz[i])))):
                wont_fall=True
        if (detected or (self.crouching and (not wont_fall))):
            dx=0
        #Detect Y position
        self.grounded=False
        self.head_bonked=False
        detected=False
        for i in range(4):
            if (collide(normalize((x+vx[i],y+vy[i]+dy-0.05,z+vz[i])))):
                detected=True
                break
        if (detected):
            dy=math.floor(y+dy)+0.5-y  
            self.dy=0
            self.grounded=True
        else:
            self.grounded=False
        detected=False
        for i in range(8,12):
            if (collide(normalize((x+vx[i],y+vy[i]+dy+0.05,z+vz[i])))):
                detected=True
                break
        if (detected):
            self.head_bonked=True
            dy=math.floor(y+dy)+2.5-0.05-PLAYER_HEIGHT-y 
            if not(self.flying):
                if (self.dy>0):
                    self.dy=-self.dy*0.2
        else:
            self.head_bonked=False
        #Detect Z position
        detected=False
        wont_fall=False
        for i in range(12):
            if (collide(normalize((x+vx[i],y+vy[i],z+vz[i]+dz)))):
                detected=True
                break
        for i in range(12):
            if (collide(normalize((x+vx[i],y+vy[i]-1,z+vz[i]+dz)))):
                wont_fall=True
        if (detected or (self.crouching and (not wont_fall))):
            dz=0
        
        if (dx==0) and (dz==0):
            if (self.sprinting):
                self.speed=WALKING_SPEED
            self.sprinting=False
        if (held_keys['c']>0):
            if (self.__fov==-1):
                self.__fov=camera.fov
            camera.fov=45.0
        else:
            if (self.__fov!=-1):
                camera.fov=self.__fov
                self.__fov=-1
            if (dx!=0) and (dz!=0):
                if (self.sprinting):
                    self._fov=PLAYER_FOV+PLAYER_SPRINTING_FOV
                else:
                    self._fov=PLAYER_FOV
            else:
                self._fov=PLAYER_FOV
            if (camera.fov<self._fov):
                camera.fov+=FOV_OFFSET_DELTA
                if (camera.fov>=self._fov):
                    camera.fov=self._fov
            elif (camera.fov>self._fov):
                camera.fov-=FOV_OFFSET_DELTA
                if (camera.fov<=self._fov):
                    camera.fov=self._fov
        self.position=Vec3(self.position.x+dx,self.position.y+dy,self.position.z+dz)
        #print(self.grounded,self.head_bonked)

    def input(self,key):
        global paused,window,custom_fullscreen
        if (key=='escape'):
            self.pause(not paused)
        if (key=='f11'):
            if (custom_fullscreen):
                print('!!')
                window.fullscreen=False
                window.setFullscreen(False)
                window.setOrigin(_window_x,_window_y)
                window.setSize(_window_w,_window_h)
                base.win.requestProperties(window)
                custom_fullscreen=False
                global fullscreen_cd
                fullscreen_cd=time.time()
        if (paused):
            return
        if (key=='tab'):
            self.flying=not(self.flying)
    
    def pause(self,newval):
        global paused,window
        pause_menu.enabled=newval
        #mouse.locked=not newval
        window.set_cursor_hidden(not newval)
        window_x,window_y=base.win.properties.getXOrigin(),base.win.properties.getYOrigin()
        window_w,window_h=base.win.properties.getXSize(),base.win.properties.getYSize()
        window.setOrigin(window_x,window_y)
        window.setSize(window_w,window_h)
        base.win.requestProperties(window)
        center_x=window_x+window_w//2
        center_y=window_y+window_h//2
        cursor.move(center_x,center_y,absolute=True,duration=0)
        paused=newval
        
    def on_enable(self):
        pass

    def on_disable(self):
        pass

#Increase the numbers for more cubes. For exapmle: for z in range(20)
for z in range(-15,15):
    for x in range(-15,15):
        add_block(x,0,z,'grass_block',grass_texture)

player=FirstPersonController()
#sky=Sky(model='sphere', texture=sky_texture, double_sided=True)
window.color=rgb(197,231,245)
window.borderless=False
window.exit_button.visible=False
window.vsync=False
application.hot_reloader.enabled=False

app.run()
