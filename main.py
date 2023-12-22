import random
import math
import pygame
import os
from os import listdir
from os.path import isfile, join

pygame.init()

pygame.display.set_caption("The Game")

Bg_color = (255, 255, 255)
wid, hei = 1200, 720
fps = 60
velocity = 10
gravity=2
ANIMATION_DELAY=5

window = pygame.display.set_mode((wid, hei))

def flip(sprites):
    return[pygame.transform.flip(sprite,True,False)for sprite in sprites]

def load_sprite_sheet(dir1,dir2,width,height,direction=False):
    path=join("assets",dir1,dir2)
    images=[f for f in listdir(path) if isfile(join(path,f))]

    all_sprites={}

    for image in images:
        sprite_sheet =pygame.image.load(join(path,image)).convert_alpha()
        sprites=[]
        for i in range(sprite_sheet.get_width()//width):
            surface = pygame.Surface((width,height),pygame.SRCALPHA,32)
            rect=pygame.Rect(i*width,0,width,height)
            surface.blit(sprite_sheet,(0,0),rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png","")+"_right"]=sprites
            all_sprites[image.replace(".png","")+"_left"]=flip(sprites)
        else:
            all_sprites[image.replace(".png","")+""]=sprites

    return all_sprites

def load_block(size):
    path=join("assets","Terrain","Terrain.png")
    image=pygame.image.load(path).convert_alpha()
    surface=pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect=pygame.Rect(96,128,size,size)
    surface.blit(image,(0,0),rect)
    return pygame.transform.scale2x(surface)

class object(pygame.sprite.Sprite):
    def __init__(self, x,y,width,height,name=None):
        self.rect=pygame.Rect(x,y,width,height)
        self.image = pygame.Surface((width,height),pygame.SRCALPHA)
        self.width=width
        self.height=height
        self.name=name
    
    def draw(self,win,offset_x):
        win.blit(self.image,(self.rect.x-offset_x,self.rect.y))

class Block(object):
    def __init__(self,x,y,size):
        super().__init__(x,y,size,size,"Terrain")
        block=load_block(size)
        self.image.blit(block,(0,0))
        self.mask= pygame.mask.from_surface(self.image)

# class Screen(object):
#     def __init__(self, x, y, width=240, height=140, name="Endings"):
#         super().__init__(x, y, width, height, name)
#         self.state="YouLose"
#         self.screen=load_sprite_sheet("Screens",name,width,height)
#         self.image=self.screen[self.state][0]
#         self.mask=pygame.mask.from_surface(self.image)

class trap(object):
    def __init__(self, x, y, width=16, height=32, name="Fire"):
        super().__init__(x, y, width, height, name)
        self.trap=load_sprite_sheet("Traps",name,width,height)
        self.animation_name="on"
        self.image=self.trap[self.animation_name][0]
        self.mask=pygame.mask.from_surface(self.image)
        self.animation_count=0

    def on(self):
        self.animation_name="on"

    def off(self):
        self.animation_name="off"
        
    def loop(self):
        sprites=self.trap[self.animation_name]
        sprite_index=(self.animation_count//ANIMATION_DELAY)%len(sprites)
        self.sprite=sprites[sprite_index]
        self.animation_count+=1
        self.rect=self.image.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask=pygame.mask.from_surface(self.image)

        if self.animation_count//ANIMATION_DELAY>len(sprites):
            self.animation_count=0



class Player(pygame.sprite.Sprite):
    COLOR="red"
    GRAVITY=gravity
    SPRITES=load_sprite_sheet("MainCharacters","VirtualGuy",32,32,True)
    def __init__(self, x,y,width,height):
        self.rect=pygame.Rect(x,y,width,height)
        self.x_vel=0
        self.y_vel=0
        self.mask=None
        self.direction="right"
        self.fall_count=0
        self.sprites=[]
        self.animation_count=0
        self.jump_count=0
        self.hit=False
        self.hit_count=0

        self.current_health = 500
        self.target_health = 500
        self.max_health = 1000
        self.health_bar_length = 400
        self.health_ratio = self.max_health / self.health_bar_length

    def jump(self,factor=8):
        if self.jump_count>1:
            return
        self.y_vel =-self.GRAVITY*factor
        self.animation_count=0
        self.jump_count+=1
        if self.jump_count==1:
            self.fall_count=0

    def add_health(self,dHealth):
        if self.current_health + dHealth>self.max_health:
            self.current_health=self.max_health
        elif self.current_health + dHealth<0:
            self.current_health=0
        else:
            self.current_health=self.current_health+dHealth

    def move(self,dx,dy):
        self.rect.x +=dx
        self.rect.y +=dy

    def move_left(self,vel):
        self.x_vel=-vel
        if self.direction !="left":
            self.direction="left"
            self.animation_count=0

    def move_right(self,vel):
        self.x_vel=vel
        if self.direction !="right":
            self.direction="right"
            self.animation_count=0

    def landed(self):
        self.fall_count=0
        self.y_vel=0
        self.jump_count=0

    def make_hit(self):
        self.hit=True
        self.hit_count=0

    def hit_head(self):
        self.count=0
        self.y_vel*=-1

    def loop(self,fps):
        self.y_vel +=min(1,self.fall_count/fps*self.GRAVITY)
        self.move(self.x_vel,self.y_vel)
        if self.hit:
            self.hit_count+=1
        if self.hit_count>fps:
            self.hit_count=0
            self.hit=False
        self.fall_count+=1
        self.update_sprite()

    def update(self):
        self.rect=self.sprite.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask=pygame.mask.from_surface(self.sprite)
    

    def update_sprite(self):
        if self.hit:
            sprite_sheet="hit"
            self.current_health-=1
        elif self.y_vel>0.5:
            if self.jump_count==1:
                sprite_sheet="jump"
            if self.jump_count==2:
                sprite_sheet="double_jump"
            else:
                sprite_sheet="fall"
        elif self.x_vel!=0:
            sprite_sheet="run"
        else: 
            sprite_sheet="idle"
        
        
        sprite_sheet_name =sprite_sheet+"_"+self.direction
        self.sprites=self.SPRITES[sprite_sheet_name]
        sprite_index=(self.animation_count//ANIMATION_DELAY)%len(self.sprites)
        self.sprite=self.sprites[sprite_index]
        self.animation_count+=1
        self.update()


    def draw(self,win,offset_x):
        pygame.draw.rect(win,(255,0,0),(10,10,self.current_health*self.health_ratio/5,25))
        pygame.draw.rect(win,"white",(10,10,self.health_bar_length,25),4)
        self.update_sprite()
        win.blit(self.sprite,(self.rect.x-offset_x,self.rect.y))

def draw(window,background,bg_image,player,objects,offset_x):
    for tile in background:
        window.blit(bg_image,tile)

    for obj in objects:
        obj.draw(window,offset_x)

    player.draw(window,offset_x)

    pygame.display.update()

def handle_vertical_collision(player,objects,dy):
    collided_objects=[]
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            if dy>0:
                player.rect.bottom=obj.rect.top
                player.landed()
            elif dy<0:
                player.rect.top=obj.rect.bottom
                player.hit_head()
            collided_objects.append(obj)

    return collided_objects

def handle_horizontal_collision(player,objects,dx):
    player.move(dx,0)
    player.update()
    collided_object=None
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            collided_object=obj
            break

    player.move(-dx,0)
    player.update()
    return collided_object

def handle_move(player,objects):
    keys=pygame.key.get_pressed()

    player.x_vel = 0
    collide_left=handle_horizontal_collision(player,objects,-velocity*2)
    collide_right=handle_horizontal_collision(player,objects,velocity*2)
    if keys[pygame.K_a] or keys[pygame.K_LEFT] and not collide_left:
        player.move_left(velocity)
    if keys[pygame.K_d] or keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(velocity)
        
    vertical_collide=handle_vertical_collision(player,objects,player.y_vel)

    to_check=[collide_left,collide_right,*vertical_collide]
    for obj in to_check:
        if obj and obj.name=='Fire':
            player.make_hit()


def get_BG(name):
    image = pygame.image.load(join("assets","Background",name))
    _,_,width,height=image.get_rect()
    tiles=[]
    for i in range(wid//width+1):
        for j in range(hei//height+1):
                pos = (i*width,j*height)
                tiles.append(pos)

    return tiles,image


def main(window):
    clock = pygame.time.Clock()
    background, bg_image=get_BG("BlueSky.png")
    offset_x=0
    block_size=96
    scroll_area_width=300
    player=Player(50,50,50,50)

    losing_screen= pygame.image.load("assets\\screens\\YouLose.png")
    losing_screen.convert()
    winning_screen= pygame.image.load("assets\\screens\\YouWin.png")
    winning_screen.convert()
    screen=losing_screen
    
    floor=[Block(i*2*block_size,hei-block_size,block_size) for i in range(0,wid//block_size)]
    traps=[trap(32+4*(i+1)*block_size,hei-(64+block_size)) for i in range(0,wid//(2*block_size)-1)]

    floor.append(Block(0,hei-block_size*2,block_size))
    floor=floor+traps

    run = True
    while player.current_health>0 and player.rect.y<hei and run:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    player.jump(8)
        player.loop(fps)
        for fire in traps:
            fire.loop()
        handle_move(player,floor)
        draw(window,background,bg_image,player,floor,offset_x)

        if (player.rect.right-offset_x>=wid-scroll_area_width and player.x_vel>0) or (
            player.rect.left-offset_x<=scroll_area_width and player.x_vel<0):
            offset_x += player.x_vel
        if player.rect.x>2*wid-(3*block_size) and player.y_vel==0:
            screen=winning_screen
            run=False

    rect=screen.get_rect()
    rect.center=wid//2,hei//2
    window.blit(screen,rect)
    pygame.draw.rect(window,(255,0,0),rect,1)
    pygame.display.update()
    while True:
        event=pygame.event.wait()
        if event.type == pygame.QUIT:    
            break
        elif event.type==pygame.KEYDOWN:
            break
    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)
