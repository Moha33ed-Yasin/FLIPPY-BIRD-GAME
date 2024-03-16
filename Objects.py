from math import pi, sin, cos
from random import uniform
from statics import load_image, train_animate
from settings import WIDTH, HEIGHT, HALF_HEIGHT, HALF_WIDTH, LAND_HIGHT, DELAYTIME
import pygame as pg

class Bird(pg.sprite.Sprite):
    def __init__(self, size, jump_height, land_speed, collision_distance, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.screen = game.screen
        self.size = size
        self.collision_distance = collision_distance
        self.jump_height = jump_height
        self.landspeed = land_speed
        self.jump_limit = 0
        self.fly_timer = 0
        self.fail_timer = 0
        self.theta = 0
        self.angle = 0
        self.is_jumping = False
        self.is_landing = False
        self.is_died = False
        self.is_collide = False

        self.sdie_trigger = False

        #sounds
        self.jump_sound = game.sound.sjump
        self.died_sound = game.sound.sdied

        #images
        self.fly_actions = {0:load_image("assets/bird_status/fly1.png", self.size),
                            1:load_image("assets/bird_status/fly2.png", self.size), 
                            2:load_image("assets/bird_status/fly3.png", self.size)}# load bird image from resources
        self.jump_action = load_image("assets/bird_status/jump.png", self.size)# load bird actions image from resources
        self.fail_actions ={0:load_image("assets/bird_status/fail1.png", self.size),
                            1:load_image("assets/bird_status/fail2.png", self.size), 
                            2:load_image("assets/bird_status/fail3.png", self.size)}# load fails image from resources
        self.died = load_image("assets/bird_status/died.png", self.size)# load died bird image from resources

        self.image = self.fly_actions[1]
        self.rect = self.image.get_rect()
        self.rect.x = self.x = HALF_WIDTH // 1.15
        self.rect.y = self.y = HALF_HEIGHT // 1.4
    
    @property
    def land_curve(self)->float: return self.landspeed * sin(self.theta * self.game.fps)
    
    @property
    def jump_curve(self)->float: return self.jump_height * cos(self.theta * self.game.fps)

    def on_jump(self):
        self.jump_sound.play()
        self.jump_limit = self.y - self.jump_height // 3
        self.is_jumping = True
        self.is_landing = False
        self.theta = 0

    def on_land(self):
        self.is_jumping = False
        self.is_landing = True
        self.theta = 0

    def jump(self):
        self.theta = (self.theta + pi / 10) % pi / 2  
        self.rect.y = self.y = self.y - self.jump_curve
        self.image = self.jump_action
        self.angle = 35

    def land(self):
        self.theta = (self.theta + pi / 10) % pi / 2
        self.rect.y = self.y = self.y + self.land_curve

        if self.y >= self.jump_limit:
            self.image = self.fly_actions[0]
            self.angle = -35
        elif self.y >= self.jump_limit + 10:
            self.image = self.fly_actions[1]
            self.angle = -30
        else:
            self.image = self.jump_action
            self.angle = 35

    def update(self):
        if not self.is_died:
            if self.y <= self.jump_limit:self.on_land()
                
            if not self.is_jumping and not self.is_landing:
                self.image = train_animate(self.fly_timer, int(DELAYTIME * 3000), self.fly_actions)
                self.fly_timer += 1

            elif self.is_jumping:self.jump()

            elif self.is_landing: self.land()
            
            self.is_died = self.check_is_died(-(HEIGHT - 3 * LAND_HIGHT // 4), (HEIGHT - 3 * LAND_HIGHT // 4) ) 

        else:
            if not self.fail():
                self.land()
                self.image = train_animate(self.fail_timer, 50, self.fail_actions)
                self.angle = -60
                self.fail_timer += 1

            else:
                self.image = self.died
                self.angle = 0
                if not self.sdie_trigger:
                    self.died_sound.play()
                    self.sdie_trigger = True

        self.draw()

    def fail(self): return self.rect.collidepoint(self.x, HEIGHT - 3 * LAND_HIGHT // 4)

    def input(self, key:pg.event)->None: 
        if key == pg.K_SPACE and not self.is_died: self.on_jump()

    def draw(self):
        self.image = pg.transform.rotate(self.image, self.angle)
        self.screen.blit(self.image, [self.x, self.y])

    def check_is_died(self, top:float, bottom:float):
        self.is_collide = self.game.blocks.collide(self, self.collision_distance)
        return ( ( top >= self.y) | (self.y + self.size[1] >= bottom) ) or self.is_collide

class TwoStandBlocks(pg.sprite.Sprite):
    group = pg.sprite.AbstractGroup()
    def __init__(self, game, image, region, _spacebetween):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.screen = game.screen
        self.image = image
        self.inverse_image = pg.transform.rotate(self.image, 180)
        self.is_passed = False
        self.speed = .033
        self.dltspeed = 0
        self.rect = self.image.get_rect(left=WIDTH, top=uniform(*region))
        self.inverse_rect = pg.rect.Rect(self.rect.x, self.rect.y - _spacebetween - self.rect.height, self.rect.width, self.rect.height)
        self.intersection_rect = pg.rect.Rect(self.rect.x, self.rect.y - _spacebetween, self.rect.width, _spacebetween)
        self.group.add_internal(self)

    def on_slide(self, end:float, delay:float = .1):
        if delay != 0:
            if self.rect.x >= end:
                move = self.dltspeed // delay
                self.rect.x -= move
                self.inverse_rect.x -= move
                self.intersection_rect.x -= move
                self.dltspeed = (self.dltspeed % delay + self.speed)
            else: self.game.blocks.group.remove_internal(self)

    def draw(self):
        self.screen.blits([(self.image, [self.rect.x, self.rect.y]),
                           (self.inverse_image, [self.inverse_rect.x, self.inverse_rect.y])])

    def slide(self, end, delay:float =.1) -> None:
        self.on_slide(end, delay)
        self.draw()
    
    def face(self, sprite_right:pg.sprite.Sprite,):
        sprites = self.group.sprites()
        after = [s for s in sprites if s.rect.x >= sprite_right.rect.x]
        sprite_left = [s for s in after if s.rect.x == min([s.rect.x for s in after])][0]
        return sprite_left

    def collide(self, right_sprite:pg.sprite.Sprite, offset:float=0):
        right_rect = pg.Rect(right_sprite.rect.left + offset, right_sprite.rect.top + offset, right_sprite.rect.width, right_sprite.rect.height)
        return self.rect.colliderect(right_rect) or self.inverse_rect.colliderect(right_rect)

    def gate_pass(self, right_sprite:pg.sprite.Sprite, offset:int=0):
        _rect = pg.Rect(right_sprite.rect.left + offset, right_sprite.rect.top + offset, right_sprite.rect.width + offset, right_sprite.rect.height + offset)
        return self.intersection_rect.colliderect(_rect)