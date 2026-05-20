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

    def move(self):
        self.position.x = self.position.x + self.speed * math.cos(math.radians(self.direction))
        self.position.y = self.position.y + self.speed * math.sin(math.radians(self.direction))

    def get_distance(self, target:Position):
        return( (self.position.x-target.x)*(self.position.x-target.x) + (self.position.y-target.y)*(self.position.y-target.y) )


class player:
    def __init__(self):
        #画面の読み込み
        self.img_sship = [
            pygame.image.load("image_gl/starship.png"),
            pygame.image.load("image_gl/starship_l.png"),
            pygame.image.load("image_gl/starship_r.png"),
            pygame.image.load("image_gl/starship_burner.png")
        ]
        self.transform = Transform()
        self.ss_d = 0
        self.key_spc = 0
        self.key_z = 0
        self.ss_muteki = 0
        self.se_damage = pygame.mixer.Sound("sound_gl/damage.ogg")
    
    def move(self, key):
        self.ss_d = 0
        if key[pygame.K_UP] == 1:
            self.transform.set_position(self.transform.position.x, self.transform.position.y, DIRECTION_UP, 20)
            self.transform.move()
            if self.transform.position.y < 80:
                self.transform.position.y = 80
        if key[pygame.K_DOWN] == 1:
            self.transform.set_position(self.transform.position.x, self.transform.position.y, DIRECTION_DOWN, 20)
            self.transform.move()
            if self.transform.position.y > 640:
                self.transform.position.y = 640
        if key[pygame.K_LEFT] == 1:
            self.ss_d = 1
            self.transform.set_position(self.transform.position.x, self.transform.position.y, DIRECTION_LEFT, 20)
            self.transform.move()
            if self.transform.position.x < 40:
                self.transform.position.x = 40
        if key[pygame.K_RIGHT] == 1:
            self.ss_d = 2
            self.transform.set_position(self.transform.position.x, self.transform.position.y, DIRECTION_RIGHT, 20)
            self.transform.move()
            if self.transform.position.x > 920:
                self.transform.position.x = 920
    
    def shoot_missile(self, key, missile, shield):
        self.key_spc = (self.key_spc+1)*key[K_SPACE]
        if self.key_spc%5 == 1:
            missile.shoot_once(self.transform.position.x,self.transform.position.y)
        self.key_z = (self.key_z+1)*key[K_z]
        if self.key_z == 1 and shield.can_shoot_barrage():
            missile.shoot_barrage(self.transform.position.x,self.transform.position.y)
            shield.down()
    
    def draw(self, scrn, tmr):
        if self.ss_muteki%2 == 0:
            scrn.blit(self.img_sship[3], [self.transform.position.x-8, self.transform.position.y+40+(tmr%3)*2])
            scrn.blit(self.img_sship[self.ss_d], [self.transform.position.x-37, self.transform.position.y-48])

    def action(self, scrn, key, missile, shield, tmr): #自機の移動
        self.move(key)
        self.shoot_missile(key, missile, shield)
        self.draw(scrn, tmr)
    
    def initialize(self):
        self.transform.position.x = 480
        self.transform.position.y = 600
        self.ss_d = 0
        self.ss_muteki = 0
    
    def is_muteki(self):
        if self.ss_muteki > 0:
            self.ss_muteki = self.ss_muteki - 1
            return True
        return False
    
    def set_effect(self, effect): 
        effect.set_effect(self.transform.position.x, self.transform.position.y)
    
    def take_damage(self):
        if self.ss_muteki == 0:
            self.ss_muteki = 60
            self.se_damage.play()
    
    def explode(self, effect, tmr):
        if tmr%5 == 0:
            effect.set_effect(self.transform.position.x+random.randint(-60,60), self.transform.position.y+random.randint(-60,60))
        if tmr%10 == 0:
            self.se_damage.play()


class missile:
    def __init__(self):
        self.img_weapon = pygame.image.load("image_gl/bullet.png")
        self.MISSILE_MAX = 200
        self.msl_no = 0
        self.msl_f = [False]*self.MISSILE_MAX
        self.transform = [Transform() for _ in range(self.MISSILE_MAX)]
        self.se_shot = pygame.mixer.Sound("sound_gl/shot.ogg")
        self.se_barrage = pygame.mixer.Sound("sound_gl/barrage.ogg")
    
    def set(self, x, y, direction):
        self.msl_f[self.msl_no] = True
        self.transform[self.msl_no].set_position(x, y, direction, 36)
        self.msl_no = (self.msl_no+1)%self.MISSILE_MAX

    def shoot_once(self,ss_x,ss_y):
        self.set(ss_x, ss_y-50, DIRECTION_UP)
        self.se_shot.play()

    def shoot_barrage(self,ss_x,ss_y):
        for a in range(160, 390, 10):
            self.set(ss_x, ss_y-50, a)
        self.se_barrage.play()
    
    def move(self, i):
        self.transform[i].move()
        if self.is_out_of_display(i):
            self.msl_f[i] = False
    
    def draw(self, i ,scrn):
        self.img_rz = pygame.transform.rotozoom(self.img_weapon, -90-self.transform[i].direction, 1.0)
        scrn.blit(self.img_rz, [self.transform[i].position.x-self.img_rz.get_width()/2, self.transform[i].position.y-self.img_rz.get_height()/2])

    def action(self, scrn): #球の移動
        for i in range(self.MISSILE_MAX):
            if self.msl_f[i] == True:
                self.move(i)
                self.draw(i,scrn)
    
    def has_hit_enemy(self, target:Position, r):
        for n in range(self.MISSILE_MAX):
            if self.msl_f[n] == True and self.transform[n].get_distance(target) < r*r:
                self.msl_f[n] = False
                return True
        return False
    
    def clear(self):
        for i in range(self.MISSILE_MAX):
            self.msl_f[i] = False
    
    def is_out_of_display(self,i):
        if self.transform[i].position.y < 0 or self.transform[i].position.x < 0 or self.transform[i].position.x > 960:
            return True
        return False


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


class EnemyChara:
    def __init__(self):
        self.emy_f = False
        self.transform = Transform()
        self.emy_type = 0
        self.emy_shield = 0
        self.emy_count = 0
        self.width = 0
        self.height = 0
        self.boss_state = 0
    
    def set(self, x:int, y:int, angle:int, speed:int, type:int, shield:int, width:int, height:int):
        self.emy_f = True
        self.transform.set_position(x, y, angle, speed)
        self.emy_type = type
        self.emy_shield = shield
        self.emy_count = 0
        self.width = width
        self.height = height
    
    def clear(self):
        self.emy_f = False
    
    def move(self):
        self.transform.move()
        if self.transform.position.x < LINE_L or LINE_R < self.transform.position.x or self.transform.position.y < LINE_T or LINE_B < self.transform.position.y:
            self.clear()
    
    def move_boss(self, tmr):
        shot = 0
        if self.boss_state == 0:
            self.transform.set_position(self.transform.position.x, self.transform.position.y, DIRECTION_DOWN, 2)
            self.transform.move()
            if self.transform.position.y >= 200:
                self.boss_state = 1
        elif self.boss_state == 1:
            self.transform.set_position(self.transform.position.x, self.transform.position.y, DIRECTION_LEFT, self.transform.speed)
            self.transform.move()
            if self.transform.position.x < 200:
                shot = 2
                self.boss_state = 2
        else:
            self.transform.set_position(self.transform.position.x, self.transform.position.y, DIRECTION_RIGHT, self.transform.speed)
            self.transform.move()
            if self.transform.position.x > 760:
                shot = 2
                self.boss_state = 1
            if self.emy_shield < 100 and tmr%30 == 0:
                shot = 1
        return shot
    
    def has_hit_and_run(self):
        if self.emy_type == 4: #進行方向を変える敵
            if self.transform.position.y > 240 and self.transform.direction == DIRECTION_DOWN:
                self.transform.direction = random.choice([50,70,110,130])
                return True
        return False
    
    def get_hit_area(self):
        r = int((self.width+self.height)/4)+12
        return r
    
    def has_hit_player(self, player:Position):
        if self.emy_f == True:
            r = int((self.width+self.height)/4 + (74+96)/4)
            if self.transform.get_distance(player) < r*r:
                if self.emy_type < EMY_BOSS:
                    self.clear()
                return True
        return False

    def explode(self, eff:effect):
        er = int((self.width+self.height)/4)
        eff.set_effect(self.transform.position.x+random.randint(-er, er), self.transform.position.y+random.randint(-er, er))
    
    def draw(self, scrn, image):
        self.emy_count = self.emy_count + 1
        if self.emy_type == 4: #進行方向を変える敵
            ang = self.emy_count*10
        else:
            ang = -90-self.transform.direction
        img_rz = pygame.transform.rotozoom(image, ang, 1.0)
        scrn.blit(img_rz, [self.transform.position.x-img_rz.get_width()/2, self.transform.position.y-img_rz.get_height()/2])
    
    def is_defeat(self):
        self.emy_shield = self.emy_shield - 1
        if self.emy_shield == 0:
            self.clear()
            return True
        return False
    
    def get_shoot_param(self, direction:int):
        transform = Transform()
        transform.set_position(self.transform.position.x, self.transform.position.y, direction, 6)
        return transform


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
            if self.charactor[self.emy_no].emy_f == False:
                self.charactor[self.emy_no].set(x, y, a, sp, ty, sh, self.img_enemy[ty].get_width(), self.img_enemy[ty].get_height())
                break
            self.emy_no = (self.emy_no+1)%self.ENEMY_MAX
    
    def shoot_once(self, x, y, direction):
        self.set_enemy(x, y, direction, EMY_BULLET, 6, 0)

    def shoot_barrage(self, x, y):
        for j in range(0, 10):
            self.set_enemy(x, y, j*20, EMY_BULLET, 6, 0)

    def defeat_boss(self, i, eff):
        self.boss_defeated = True
        for j in range(10):
            self.charactor[i].explode(eff)
        self.se_explosion.play()
    
    def draw(self, i, scrn, flash:bool):
        if self.charactor[i].emy_type == EMY_BOSS:
            ang = DIRECTION_UP-DIRECTION_DOWN
            png = self.charactor[i].emy_type
            if flash:
                png = EMY_BOSS + 1
            img_rz = pygame.transform.rotozoom(self.img_enemy[png], ang, 1.0)
            scrn.blit(img_rz, [self.charactor[i].transform.position.x-img_rz.get_width()/2, self.charactor[i].transform.position.y-img_rz.get_height()/2])
        else:
            self.charactor[i].draw(scrn, self.img_enemy[self.charactor[i].emy_type])
    
    def action(self ,scrn ,msl:missile ,eff:effect, shield:shield, score:score, tmr, inplay:bool): #敵機の移動
        for i in range(self.ENEMY_MAX):
            if self.charactor[i].emy_f == True:
                flash = False
                if self.charactor[i].emy_type < EMY_BOSS: #ザコの動き
                    if self.charactor[i].has_hit_and_run():
                        self.shoot_once(self.charactor[i].transform.position.x, self.charactor[i].transform.position.y, DIRECTION_DOWN)
                    self.charactor[i].move()
                else: #ボスの動き
                    shot = self.charactor[i].move_boss(tmr)
                    if shot == 1:
                        self.shoot_once(self.charactor[i].transform.position.x, self.charactor[i].transform.position.y+80, random.randint(60, 120))
                    elif shot == 2:
                        self.shoot_barrage(self.charactor[i].transform.position.x, self.charactor[i].transform.position.y+80)
                
                if self.charactor[i].emy_type != EMY_BULLET: #プレイヤーと玉とのヒットチェック
                    if msl.has_hit_enemy(self.charactor[i].transform.position, self.charactor[i].get_hit_area()):
                        self.charactor[i].explode(eff)
                        if self.charactor[i].emy_type == EMY_BOSS: #ボスはフラッシュさせる
                            flash = True
                        score.up(100)
                        if self.charactor[i].is_defeat():
                            shield.heal()
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
    ss = player()
    msl = missile()
    emy = enemy()
    eff = effect()
    sld = shield()
    scr = score()

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
                scr.clear()
                ss.initialize()
                sld.initialize()
                emy.clear()
                msl.clear()
                pygame.mixer.music.load("sound_gl/bgm.ogg")
                pygame.mixer.music.play(-1)
            
        if idx == 1: #ゲームプレイ中
            ss.action(screen, key, msl, sld, tmr)
            if ss.is_muteki() == False:
                if emy.has_hit_player(ss.transform.position): #敵とのヒットチェック
                    ss.set_effect(eff)
                    sld.down()
                    if sld.is_zero():
                        idx = 2
                        tmr = 0
                    ss.take_damage()
            msl.action(screen)
            emy.bring(tmr)
            emy.action(screen,msl,eff,sld,scr,tmr,True)
            if emy.is_boss_defeated():
                idx = 3
                tmr = 0

        
        if idx == 2: #ゲームオーバー
            msl.action(screen)
            emy.action(screen,msl,eff,sld,scr,tmr,False)
            if tmr == 1:
                pygame.mixer.music.stop()
            if tmr <= 90:
                ss.explode(eff, tmr)
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
            ss.action(screen, key, msl, sld, tmr)
            ss.is_muteki()
            msl.action(screen)
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
        
        eff.draw_effect(screen) #爆発の演出
        scr.draw(screen)
        if idx != 0: #シールドの表示
            sld.draw_shield(screen)

        pygame.display.update()
        clock.tick(30)

if __name__ == '__main__':
    main()
    