import pygame
import sys
import math
import random
from pygame.locals import *

BLACK = (  0,   0,   0)
SILVER= (192, 208, 224)
RED   = (255,   0,   0)
CYAN  = (  0, 224, 255)

EMY_BULLET = 0
EMY_ZAKO = 1
EMY_BOSS = 5
LINE_T = -80
LINE_B = 800
LINE_L = -80
LINE_R = 1040

DIRECTION_UP = 270
DIRECTION_DOWN = 90
DIRECTION_LEFT = 180
DIRECTION_RIGHT = 0

class title:
    def __init__(self):
        self.img_title = [
            pygame.image.load("image_gl/nebula.png"),
            pygame.image.load("image_gl/logo.png")
        ]
    
    def draw(self, screen, tmr):
        img_rz = pygame.transform.rotozoom(self.img_title[0], -tmr%360, 1.0)
        screen.blit(img_rz, [480-img_rz.get_width()/2, 280-img_rz.get_height()/2])
        screen.blit(self.img_title[1], [70, 160])
        draw_text(screen, "Press [SPACE] to start", 480, 600, 50, SILVER)


def draw_text(scrn, txt, x, y, siz, col): #立体的な文字の表示
    fnt = pygame.font.Font(None, siz)
    cr = int(col[0]/2)
    cg = int(col[1]/2)
    cb = int(col[2]/2)
    sur = fnt.render(txt, True, (cr,cg,cb))
    x = x - sur.get_width()/2
    y = y - sur.get_height()/2
    scrn.blit(sur, [x+1, y+1])
    cr = col[0]+128
    if cr > 255: cr = 255
    cg = col[1]+128
    if cg > 255: cg = 255
    cb = col[2]+128
    if cb > 255: cb = 255
    sur = fnt.render(txt, True, (cr,cg,cb))
    scrn.blit(sur, [x-1, y-1])
    sur = fnt.render(txt, True, col)
    scrn.blit(sur, [x, y])


class score:
    def __init__(self):
        self.score = 0
        self.hisco = 10000
        self.new_record = False
    
    def up(self, point):
        self.score = self.score + point
        if self.score > self.hisco:
            self.hisco = self.score
            self.new_record = True
    
    def clear(self):
        self.score = 0
        self.new_record = False
    
    def draw(self, screen):
        draw_text(screen, "SCORE "+str(self.score), 200, 30, 50, SILVER)
        draw_text(screen, "HISCORE "+str(self.hisco), 760, 30, 50, CYAN)

    def draw_new_record_text(self, screen):
        if self.new_record == True:
            draw_text(screen, "NEW RECORD "+str(self.hisco), 480, 400, 60, CYAN)


class shield:
    def __init__(self):
        self.img_shield = pygame.image.load("image_gl/shield.png")
        self.ss_shield = 100
    
    def draw_shield(self, screen):
        screen.blit(self.img_shield, [40, 680])
        pygame.draw.rect(screen, (64,32,32), [40+self.ss_shield*4, 680, (100-self.ss_shield)*4, 12])

    def down(self):
        self.ss_shield = self.ss_shield - 10

    def can_shoot_barrage(self):
        if self.ss_shield > 10:
            return True
        return False
    
    def heal(self):
        if self.ss_shield < 100:
            self.ss_shield = self.ss_shield + 1
    
    def is_zero(self):
        if self.ss_shield <= 0:
            self.ss_shield = 0
            return True
        return False
    
    def initialize(self):
        self.ss_shield = 100


class background:
    def __init__(self,image_path):
        self.bg_y = 0
        #画面の読み込み
        self.img_galaxy = pygame.image.load(image_path)

    def scroll_horizontal(self,screen):
        #背景のスクロール
        self.bg_y = (self.bg_y+16)%720
        screen.blit(self.img_galaxy, [0, self.bg_y-720])
        screen.blit(self.img_galaxy, [0, self.bg_y])


class Position:
    def __init__(self):
        self.x = 0
        self.y = 0
    
    def set(self, x, y):
        self.x = x
        self.y = y
    
    def get_distance(self, target:"Position"):
        return( (self.x-target.x)*(self.x-target.x) + (self.y-target.y)*(self.y-target.y) )


class Transform:
    def __init__(self):
        self.position = Position()
        self.direction = 0
        self.speed = 0
    
    def set_position(self, x, y, direction, speed):
        self.position.set(x, y)
        self.direction = direction
        self.speed = speed

    def change_moving(self, direction:int, speed:int):
        self.direction = direction
        self.speed = speed

    def move(self):
        self.position.x = self.position.x + self.speed * math.cos(math.radians(self.direction))
        self.position.y = self.position.y + self.speed * math.sin(math.radians(self.direction))

    def get_distance(self, target:Position):
        return( (self.position.x-target.x)*(self.position.x-target.x) + (self.position.y-target.y)*(self.position.y-target.y) )


class Charactor:
    def __init__(self):
        self.transform = Transform()
        self.now_disp = False
    
    def set(self, x, y, direction, speed):
        self.transform.set_position(x, y, direction, speed)
        self.now_disp = True
    
    def clear(self):
        self.now_disp = False
    
    def move(self):
        if self.now_disp:
            self.transform.move()

    def is_out_of_display(self):
        if self.now_disp and self.transform.position.x < LINE_L or LINE_R < self.transform.position.x or self.transform.position.y < LINE_T or LINE_B < self.transform.position.y:
            return True
        return False
    
    def change_moving(self, direction:int, speed:int):
        if self.now_disp:
            self.transform.change_moving(direction, speed)
    
    def draw(self, screen, img, direction:int):
        if self.now_disp:
            img_rz = pygame.transform.rotozoom(img, -90-direction, 1.0)
            screen.blit(img_rz, [self.transform.position.x-img_rz.get_width()/2, self.transform.position.y-img_rz.get_height()/2])
    
    def has_hit_target(self, target:Position, r):
        if self.now_disp and self.transform.get_distance(target) < r*r:
            return True


class effect:
    def __init__(self):
        self.img_explode = [
            None,
            pygame.image.load("image_gl/explosion1.png"),
            pygame.image.load("image_gl/explosion2.png"),
            pygame.image.load("image_gl/explosion3.png"),
            pygame.image.load("image_gl/explosion4.png"),
            pygame.image.load("image_gl/explosion5.png")
        ]
        self.EFFECT_MAX = 100
        self.eff_no = 0
        self.eff_p  = [0]*self.EFFECT_MAX
        self.position = [Position() for _ in range(self.EFFECT_MAX)]

    def set_effect(self, x, y): #爆発をセットする
        self.eff_p[self.eff_no] = 1
        self.position[self.eff_no].set(x, y)
        self.eff_no = (self.eff_no+1)%self.EFFECT_MAX
    
    def draw(self, i, scrn):
        if self.eff_p[i] > 0:
            scrn.blit(self.img_explode[self.eff_p[i]], [self.position[i].x-48, self.position[i].y-48])
            self.eff_p[i] = self.eff_p[i] + 1
            if self.eff_p[i] == 6:
                self.eff_p[i] = 0

    def draw_effect(self,scrn): #爆発の演出
        for i in range(self.EFFECT_MAX):
            self.draw(i, scrn)
    
    def explode(self, position:Position, effect_range:int):
        self.set_effect(position.x+random.randint(-effect_range, effect_range), position.y+random.randint(-effect_range, effect_range))


class Starship:
    def __init__(self):
        #画面の読み込み
        self.img_sship = [
            pygame.image.load("image_gl/starship.png"),
            pygame.image.load("image_gl/starship_l.png"),
            pygame.image.load("image_gl/starship_r.png"),
            pygame.image.load("image_gl/starship_burner.png")
        ]
        self.charactor = Charactor()
        self.ss_d = 0
        self.key_spc = 0
        self.key_z = 0
        self.ss_muteki = 0
        self.se_damage = pygame.mixer.Sound("sound_gl/damage.ogg")
    
    def initialize(self):
        self.charactor.set(480, 600, DIRECTION_UP, 20)
        self.ss_d = 0
        self.ss_muteki = 0
    
    def hide(self):
        self.charactor.clear()
    
    def move(self, key):
        self.ss_d = 0
        if key[pygame.K_UP] == 1:
            self.charactor.change_moving(DIRECTION_UP, 20)
            self.charactor.move()
            if self.charactor.transform.position.y < 80:
                self.charactor.transform.position.y = 80
        if key[pygame.K_DOWN] == 1:
            self.charactor.change_moving(DIRECTION_DOWN, 20)
            self.charactor.move()
            if self.charactor.transform.position.y > 640:
                self.charactor.transform.position.y = 640
        if key[pygame.K_LEFT] == 1:
            self.ss_d = 1
            self.charactor.change_moving(DIRECTION_LEFT, 20)
            self.charactor.move()
            if self.charactor.transform.position.x < 40:
                self.charactor.transform.position.x = 40
        if key[pygame.K_RIGHT] == 1:
            self.ss_d = 2
            self.charactor.change_moving(DIRECTION_RIGHT, 20)
            self.charactor.move()
            if self.charactor.transform.position.x > 920:
                self.charactor.transform.position.x = 920
    
    def get_shoot_position(self):
        position = Position()
        position.set(self.charactor.transform.position.x, self.charactor.transform.position.y-50)
        return position
    
    def shoot_missile(self, key, missile, shield):
        self.key_spc = (self.key_spc+1)*key[K_SPACE]
        if self.key_spc%5 == 1:
            missile.shoot_once(self.get_shoot_position())
        self.key_z = (self.key_z+1)*key[K_z]
        if self.key_z == 1 and shield.can_shoot_barrage():
            missile.shoot_barrage(self.get_shoot_position())
            shield.down()
    
    def draw(self, scrn, tmr):
        if self.ss_muteki%2 == 0:
            if self.charactor.now_disp:
                scrn.blit(self.img_sship[3], [self.charactor.transform.position.x-8, self.charactor.transform.position.y+40+(tmr%3)*2])
            self.charactor.draw(scrn, self.img_sship[self.ss_d], DIRECTION_UP)

    def action(self, key, missile, shield): #自機の移動
        self.move(key)
        self.shoot_missile(key, missile, shield)
    
    def is_muteki(self):
        if self.ss_muteki > 0:
            self.ss_muteki = self.ss_muteki - 1
            return True
        return False
    
    def set_effect(self, effect): 
        effect.set_effect(self.charactor.transform.position.x, self.charactor.transform.position.y)
    
    def take_damage(self):
        if self.ss_muteki == 0:
            self.ss_muteki = 60
            self.se_damage.play()
    
    def explode(self, effect:effect, tmr:int):
        if tmr%5 == 0:
            effect.explode(self.charactor.transform.position, 60)
        if tmr%10 == 0:
            self.se_damage.play()


class missile:
    def __init__(self):
        self.img_weapon = pygame.image.load("image_gl/bullet.png")
        self.MISSILE_MAX = 200
        self.msl_no = 0
        self.charactor = [Charactor() for _ in range(self.MISSILE_MAX)]
        self.se_shot = pygame.mixer.Sound("sound_gl/shot.ogg")
        self.se_barrage = pygame.mixer.Sound("sound_gl/barrage.ogg")
    
    def set(self, x, y, direction):
        self.charactor[self.msl_no].set(x, y, direction, 36)
        self.msl_no = (self.msl_no+1)%self.MISSILE_MAX

    def shoot_once(self, position:Position):
        self.set(position.x, position.y, DIRECTION_UP)
        self.se_shot.play()

    def shoot_barrage(self, position:Position):
        for a in range(160, 390, 10):
            self.set(position.x, position.y, a)
        self.se_barrage.play()
    
    def action(self): #球の移動
        for i in range(self.MISSILE_MAX):
            self.charactor[i].transform.move()
            if self.charactor[i].is_out_of_display():
                self.charactor[i].clear()
    
    def draw(self, scrn):
        for i in range(self.MISSILE_MAX):
            self.charactor[i].draw(scrn, self.img_weapon, self.charactor[i].transform.direction)
    
    def has_hit_enemy(self, target:Position, r):
        for n in range(self.MISSILE_MAX):
            if self.charactor[n].has_hit_target(target, r):
                self.charactor[n].clear()
                return True
        return False
    
    def clear(self):
        for i in range(self.MISSILE_MAX):
            self.charactor[i].clear()


class PlayerSide:
    def __init__(self):
        self.ss = Starship()
        self.msl = missile()
        self.sld = shield()
    
    def initialize(self):
        self.ss.initialize()
        self.sld.initialize()
        self.msl.clear()
    
    def action(self, key):
        self.ss.action(key, self.msl, self.sld)
        self.msl.action()
    
    def draw(self, screen, tmr:int):
        self.ss.draw(screen, tmr)
        self.msl.draw(screen)
    
    def is_defeated(self, emy, eff):
        defeated = False
        if self.ss.is_muteki() == False:
            if emy.has_hit_player(self.ss.charactor.transform.position): #敵とのヒットチェック
                self.ss.set_effect(eff)
                self.sld.down()
                if self.sld.is_zero():
                    self.ss.hide()
                    defeated = True
                self.ss.take_damage()
        return defeated
    
    def explode_startship(self, effect:effect, tmr:int):
        self.ss.explode(effect, tmr)


class EnemyChara:
    def __init__(self):
        self.charactor = Charactor()
        self.emy_type = 0
        self.emy_shield = 0
        self.emy_count = 0
        self.width = 0
        self.height = 0
        self.boss_state = 0
    
    def set(self, x:int, y:int, direction:int, speed:int, type:int, shield:int, width:int, height:int):
        self.charactor.set(x, y, direction, speed)
        self.emy_type = type
        self.emy_shield = shield
        self.emy_count = 0
        self.width = width
        self.height = height
    
    def clear(self):
        self.charactor.clear()
    
    def move(self):
        self.charactor.move()
        if self.charactor.is_out_of_display():
            self.charactor.clear()
    
    def move_boss(self, tmr):
        shot = 0
        if self.boss_state == 0:
            self.charactor.change_moving(DIRECTION_DOWN, 2)
            self.charactor.move()
            if self.charactor.transform.position.y >= 200:
                self.boss_state = 1
        elif self.boss_state == 1:
            self.charactor.change_moving(DIRECTION_LEFT, self.charactor.transform.speed)
            self.charactor.move()
            if self.charactor.transform.position.x < 200:
                shot = 2
                self.boss_state = 2
        else:
            self.charactor.change_moving(DIRECTION_RIGHT, self.charactor.transform.speed)
            self.charactor.move()
            if self.charactor.transform.position.x > 760:
                shot = 2
                self.boss_state = 1
            if self.emy_shield < 100 and tmr%30 == 0:
                shot = 1
        return shot
    
    def has_hit_and_run(self):
        if self.charactor.now_disp:
            if self.emy_type == 4: #進行方向を変える敵
                if self.charactor.transform.position.y > 240 and self.charactor.transform.direction == DIRECTION_DOWN:
                    self.charactor.change_moving(random.choice([50,70,110,130]), self.charactor.transform.speed)
                    return True
        return False
    
    def get_hit_area(self):
        r = int((self.width+self.height)/4)+12
        return r
    
    def has_hit_player(self, player:Position):
        r = int((self.width+self.height)/4 + (74+96)/4)
        if self.charactor.has_hit_target(player, r):
            if self.emy_type < EMY_BOSS:
                self.charactor.clear()
            return True
        return False

    def explode(self, eff:effect):
        er = int((self.width+self.height)/4)
        eff.explode(self.charactor.transform.position, er)
    
    def draw(self, scrn, image):
        if self.emy_type == EMY_BOSS:
            self.charactor.draw(scrn, image, DIRECTION_DOWN)
        else:
            self.emy_count = self.emy_count + 1
            if self.emy_type == 4: #進行方向を変える敵
                angle = self.emy_count*10
            else:
                angle = self.charactor.transform.direction
            self.charactor.draw(scrn, image, angle)
    
    def draw_boss(self, scrn, image):
        self.charactor.draw(scrn, image, DIRECTION_DOWN)
    
    def is_defeat(self):
        self.emy_shield = self.emy_shield - 1
        if self.emy_shield == 0:
            self.charactor.clear()
            return True
        return False
    
    def get_position(self):
        return self.charactor.transform.position
    
    def get_boss_shoot_position(self):
        position = Position()
        position.set(self.charactor.transform.position.x, self.charactor.transform.position.y+80)
        return position
    

class enemy:
    def __init__(self):
        self.img_enemy = [
            pygame.image.load("image_gl/enemy0.png"),
            pygame.image.load("image_gl/enemy1.png"),
            pygame.image.load("image_gl/enemy2.png"),
            pygame.image.load("image_gl/enemy3.png"),
            pygame.image.load("image_gl/enemy4.png"),
            pygame.image.load("image_gl/enemy_boss.png"),
            pygame.image.load("image_gl/enemy_boss_f.png")
        ]
        self.ENEMY_MAX = 100
        self.emy_no = 0
        self.charactor = [EnemyChara() for _ in range(self.ENEMY_MAX)]
        self.boss_defeated = False
        self.se_explosion = pygame.mixer.Sound("sound_gl/explosion.ogg")

    def bring(self, tmr): #敵を出す
        sec = tmr/30
        if 0 < sec and sec < 25: #スタートして25秒間
            if tmr%15 == 0:
                self.set_enemy(random.randint(20, 940), LINE_T, DIRECTION_DOWN, EMY_ZAKO, 8, 1) #敵1
        if 30 < sec and sec < 55: # 30～55秒
            if tmr%10 == 0:
                self.set_enemy(random.randint(20, 940), LINE_T, DIRECTION_DOWN, EMY_ZAKO+1, 12, 1) #敵2
        if 60 < sec and sec < 85: # 60～85秒
            if tmr%15 == 0:
                self.set_enemy(random.randint(100, 860), LINE_T, random.randint(60, 120), EMY_ZAKO+2, 6, 3) #敵3
        if 90 < sec and sec < 115: # 90～115秒
            if tmr%20 == 0:
                self.set_enemy(random.randint(100, 860), LINE_T, DIRECTION_DOWN, EMY_ZAKO+3, 12, 2) #敵4
        if 120 < sec and sec < 145: # 120～145秒 2種類
            if tmr%20 == 0:
                self.set_enemy(random.randint(20, 940), LINE_T, DIRECTION_DOWN, EMY_ZAKO, 8, 1) #敵1
                self.set_enemy(random.randint(100, 860), LINE_T, random.randint(60, 120), EMY_ZAKO+2, 6, 3) #敵3
        if 150 < sec and sec < 175: # 150～175秒 2種類
            if tmr%20 == 0:
                self.set_enemy(random.randint(20, 940), LINE_B, DIRECTION_UP, EMY_ZAKO, 8, 1) #敵1 下から上に
                self.set_enemy(random.randint(20, 940), LINE_T, random.randint(70, 110), EMY_ZAKO+1, 12, 1) #敵2
        if 180 < sec and sec < 205: # 180～205秒 2種類
            if tmr%20 == 0:
                self.set_enemy(random.randint(100, 860), LINE_T, random.randint(60, 120), EMY_ZAKO+2, 6, 3) #敵3
                self.set_enemy(random.randint(100, 860), LINE_T, DIRECTION_DOWN, EMY_ZAKO+3, 12, 2) #敵4
        if 210 < sec and sec < 235: # 210～235秒 2種類
            if tmr%20 == 0:
                self.set_enemy(LINE_L, random.randint(40, 680), DIRECTION_RIGHT, EMY_ZAKO, 12, 1) #敵1
                self.set_enemy(LINE_R, random.randint(40, 680), DIRECTION_LEFT, EMY_ZAKO+1, 18, 1) #敵2
        if 240 < sec and sec < 265: # 240～265秒 総攻撃
            if tmr%30 == 0:
                self.set_enemy(random.randint(20, 940), LINE_T, DIRECTION_DOWN, EMY_ZAKO, 8, 1) #敵1
                self.set_enemy(random.randint(20, 940), LINE_T, DIRECTION_DOWN, EMY_ZAKO+1, 12, 1) #敵2
                self.set_enemy(random.randint(100, 860), LINE_T, random.randint(60, 120), EMY_ZAKO+2, 6, 3) #敵3
                self.set_enemy(random.randint(100, 860), LINE_T, DIRECTION_DOWN, EMY_ZAKO+3, 12, 2) #敵4

        if tmr == 30*270: #ボス出現
            self.set_enemy(480, -210, DIRECTION_DOWN, EMY_BOSS, 4, 200)

    def set_enemy(self, x, y, a, ty, sp, sh): #敵機をセットする
        while True:
            if self.charactor[self.emy_no].charactor.now_disp == False:
                self.charactor[self.emy_no].set(x, y, a, sp, ty, sh, self.img_enemy[ty].get_width(), self.img_enemy[ty].get_height())
                break
            self.emy_no = (self.emy_no+1)%self.ENEMY_MAX
    
    def shoot_once(self, position:Position, direction):
        self.set_enemy(position.x, position.y, direction, EMY_BULLET, 6, 0)

    def shoot_barrage(self, position:Position):
        for j in range(0, 10):
            self.set_enemy(position.x, position.y, j*20, EMY_BULLET, 6, 0)

    def defeat_boss(self, i, eff):
        self.boss_defeated = True
        for j in range(10):
            self.charactor[i].explode(eff)
        self.se_explosion.play()
    
    def draw(self, i, scrn, flash:bool):
        png = self.charactor[i].emy_type
        if self.charactor[i].emy_type == EMY_BOSS and flash:
            png = EMY_BOSS + 1
        self.charactor[i].draw(scrn, self.img_enemy[png])
    
    def action(self ,scrn ,player:PlayerSide ,eff:effect, scr:score, tmr, inplay:bool): #敵機の移動
        for i in range(self.ENEMY_MAX):
            if self.charactor[i].charactor.now_disp:
                flash = False
                if self.charactor[i].emy_type < EMY_BOSS: #ザコの動き
                    if self.charactor[i].has_hit_and_run():
                        self.shoot_once(self.charactor[i].get_position(), DIRECTION_DOWN)
                    self.charactor[i].move()
                else: #ボスの動き
                    shot = self.charactor[i].move_boss(tmr)
                    if shot == 1:
                        self.shoot_once(self.charactor[i].get_boss_shoot_position(), random.randint(60, 120))
                    elif shot == 2:
                        self.shoot_barrage(self.charactor[i].get_boss_shoot_position())
                
                if self.charactor[i].emy_type != EMY_BULLET: #プレイヤーと玉とのヒットチェック
                    if player.msl.has_hit_enemy(self.charactor[i].get_position(), self.charactor[i].get_hit_area()):
                        self.charactor[i].explode(eff)
                        if self.charactor[i].emy_type == EMY_BOSS: #ボスはフラッシュさせる
                            flash = True
                        scr.up(100)
                        if self.charactor[i].is_defeat():
                            player.sld.heal()
                            if self.charactor[i].emy_type == EMY_BOSS and inplay: #ボスを倒すとクリア
                                self.defeat_boss(i, eff)
                    
                self.draw(i, scrn, flash)
    
    def has_hit_player(self ,player:Position):
        for i in range(self.ENEMY_MAX): #敵とのヒットチェック
            if self.charactor[i].has_hit_player(player):
                return True
        return False
    
    def clear(self):
        for i in range(self.ENEMY_MAX):
            self.charactor[i].clear()
        self.boss_defeated = False
    
    def is_boss_defeated(self):
        return self.boss_defeated


MY_BULLET = 0
LINE_T = -80
LINE_B = 800
LINE_L = -80
LINE_R = 1040


def main(): #メインループ
    idx = 0
    tmr = 0

    pygame.init()
    pygame.display.set_caption("Galaxy Lancer")
    screen = pygame.display.set_mode((960, 720))
    clock = pygame.time.Clock()

    ttl = title()
    bg = background("image_gl/galaxy.png")
    player = PlayerSide()
    scr = score()
    emy = enemy()
    eff = effect()

    while True:
        tmr = tmr + 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    screen = pygame.display.set_mode((960, 720), pygame.FULLSCREEN)
                if event.key == pygame.K_F2 or event.key == pygame.K_ESCAPE:
                    screen = pygame.display.set_mode((960, 720))
        
        #背景のスクロール
        bg.scroll_horizontal(screen)

        key = pygame.key.get_pressed()

        if idx == 0: #タイトル
            ttl.draw(screen, tmr)
            if key[K_SPACE] == 1:
                idx = 1
                tmr = 0
                player.initialize()
                scr.clear()
                emy.clear()
                pygame.mixer.music.load("sound_gl/bgm.ogg")
                pygame.mixer.music.play(-1)
            
        if idx == 1: #ゲームプレイ中
            player.action(key)
            if player.is_defeated(emy, eff):
                idx = 2
                tmr = 0
            emy.bring(tmr)
            emy.action(screen,player,eff,scr,tmr,True)
            if emy.is_boss_defeated():
                idx = 3
                tmr = 0
        
        if idx == 2: #ゲームオーバー
            player.action(key)
            emy.action(screen,player,eff,scr,tmr,False)
            if tmr == 1:
                pygame.mixer.music.stop()
            if tmr <= 90:
                player.explode_startship(eff, tmr)
            if tmr == 120:
                pygame.mixer.music.load("sound_gl/gameover.ogg")
                pygame.mixer.music.play(0)
            if tmr > 120:
                draw_text(screen, "GAME OVER", 480, 300, 80, RED)
                scr.draw_new_record_text(screen)
            if tmr == 400:
                idx = 0
                tmr = 0
        
        if idx == 3: #ゲームクリア
            player.action(key)
            player.ss.is_muteki()
            if tmr == 1:
                pygame.mixer.music.stop()
            if tmr < 30 and tmr%2 == 0:
                pygame.draw.rect(screen, (192, 0,0), [0, 0, 960, 720])
            if tmr == 120:
                pygame.mixer.music.load("sound_gl/gameclear.ogg")
                pygame.mixer.music.play(0)
            if tmr > 120:
                draw_text(screen, "GAME CLEAR", 480, 300, 80, SILVER)
                scr.draw_new_record_text(screen)
            if tmr == 400:
                idx = 0
                tmr = 0
        
        if idx != 0:
            player.draw(screen, tmr)
        eff.draw_effect(screen) #爆発の演出
        scr.draw(screen)

        pygame.display.update()
        clock.tick(30)

if __name__ == '__main__':
    main()
    