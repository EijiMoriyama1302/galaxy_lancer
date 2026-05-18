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
        self.emy_f = [False]*self.ENEMY_MAX
        self.transform = [Transform() for _ in range(self.ENEMY_MAX)]
        self.emy_type = [0]*self.ENEMY_MAX
        self.emy_shield = [0]*self.ENEMY_MAX
        self.emy_count = [0]*self.ENEMY_MAX
        self.boss_defeated = False
        self.se_explosion = pygame.mixer.Sound("sound_gl/explosion.ogg")

    def bring(self, tmr): #敵を出す
        sec = tmr/30

        if tmr == 30: #ボス出現
            self.set_enemy(480, -210, DIRECTION_DOWN, EMY_BOSS, 4, 200)

    def set_enemy(self, x, y, a, ty, sp, sh): #敵機をセットする
        while True:
            if self.emy_f[self.emy_no] == False:
                self.emy_f[self.emy_no] = True
                self.transform[self.emy_no].set_position(x, y, a, sp)
                self.emy_type[self.emy_no] = ty
                self.emy_shield[self.emy_no] = sh
                self.emy_count[self.emy_no] = 0
                break
            self.emy_no = (self.emy_no+1)%self.ENEMY_MAX
    
    def shoot_once(self, x, y, direction):
        self.set_enemy(x, y, direction, EMY_BULLET, 6, 0)

    def shoot_barrage(self, x, y):
        for j in range(0, 10):
            self.set_enemy(x, y, j*20, EMY_BULLET, 6, 0)

    def move_zako(self, i):
        self.transform[i].move()
        if self.emy_type[i] == 4: #進行方向を変える敵
            self.emy_count[i] = self.emy_count[i] + 1
            ang = self.emy_count[i]*10
            if self.transform[i].position.y > 240 and self.transform[i].direction == DIRECTION_DOWN:
                self.transform[i].direction = random.choice([50,70,110,130])
                self.shoot_once(self.transform[i].position.x, self.transform[i].position.y, DIRECTION_DOWN)
        if self.transform[i].position.x < LINE_L or LINE_R < self.transform[i].position.x or self.transform[i].position.y < LINE_T or LINE_B < self.transform[i].position.y:
            self.emy_f[i] = False
    
    def move_boss(self, i, tmr):
        if self.emy_count[i] == 0:
            self.transform[i].set_position(self.transform[i].position.x, self.transform[i].position.y, DIRECTION_DOWN, 2)
            self.transform[i].move()
            if self.transform[i].position.y >= 200:
                self.emy_count[i] = 1
        elif self.emy_count[i] == 1:
            self.transform[i].set_position(self.transform[i].position.x, self.transform[i].position.y, DIRECTION_LEFT, self.transform[i].speed)
            self.transform[i].move()
            if self.transform[i].position.x < 200:
                self.shoot_barrage(self.transform[i].position.x, self.transform[i].position.y+80)
                self.emy_count[i] = 2
        else:
            self.transform[i].set_position(self.transform[i].position.x, self.transform[i].position.y, DIRECTION_RIGHT, self.transform[i].speed)
            self.transform[i].move()
            if self.transform[i].position.x > 760:
                self.shoot_barrage(self.transform[i].position.x, self.transform[i].position.y+80)
                self.emy_count[i] = 1
            if self.emy_shield[i] < 100 and tmr%30 == 0:
                self.shoot_once(self.transform[i].position.x, self.transform[i].position.y+80, random.randint(60, 120))
    
    def is_hit_by_missile(self, i, msl):
        w = self.img_enemy[self.emy_type[i]].get_width()
        h = self.img_enemy[self.emy_type[i]].get_height()
        r = int((w+h)/4)+12
        if msl.has_hit_enemy(self.transform[i].position, r):
            return True
        return False
    
    def explode(self, i, eff):
        w = self.img_enemy[self.emy_type[i]].get_width()
        h = self.img_enemy[self.emy_type[i]].get_height()
        er = int((w+h)/4)
        eff.set_effect(self.transform[i].position.x+random.randint(-er, er), self.transform[i].position.y+random.randint(-er, er))
    
    def defeat_boss(self, i, eff):
        self.boss_defeated = True
        for j in range(10):
            self.explode(i, eff)
        self.se_explosion.play()
    
    def draw(self, i, scrn, flash:bool):
        if self.emy_type[i] == EMY_BOSS:
            ang = DIRECTION_UP-DIRECTION_DOWN
        else:
            ang = -90-self.transform[i].direction
        png = self.emy_type[i]
        if flash:
            png = EMY_BOSS + 1
        img_rz = pygame.transform.rotozoom(self.img_enemy[png], ang, 1.0)
        scrn.blit(img_rz, [self.transform[i].position.x-img_rz.get_width()/2, self.transform[i].position.y-img_rz.get_height()/2])
    
    def action(self ,scrn ,msl:missile ,eff:effect, shield:shield, score:score, tmr, idx): #敵機の移動
        for i in range(self.ENEMY_MAX):
            if self.emy_f[i] == True:
                flash = False
                if self.emy_type[i] < EMY_BOSS: #ザコの動き
                    self.move_zako(i)
                else: #ボスの動き
                    self.move_boss(i, tmr)
                
                if self.emy_type[i] != EMY_BULLET: #プレイヤーと玉とのヒットチェック
                    if self.is_hit_by_missile(i, msl):
                        self.explode(i, eff)
                        if self.emy_type[i] == EMY_BOSS: #ボスはフラッシュさせる
                            flash = True
                        self.emy_shield[i] = self.emy_shield[i] - 1
                        score.up(100)
                        if self.emy_shield[i] == 0:
                            self.emy_f[i] = False
                            shield.heal()
                            if self.emy_type[i] == EMY_BOSS and idx == 1: #ボスを倒すとクリア
                                self.defeat_boss(i, eff)
                    
                self.draw(i, scrn, flash)
    
    def has_hit_player(self ,player:Position):
        for i in range(self.ENEMY_MAX): #敵とのヒットチェック
            if self.emy_f[i] == True:
                w = self.img_enemy[self.emy_type[i]].get_width()
                h = self.img_enemy[self.emy_type[i]].get_height()
                r = int((w+h)/4 + (74+96)/4)
                if self.transform[i].get_distance(player) < r*r:
                    if self.emy_type[i] < EMY_BOSS:
                        self.emy_f[i] = False
                    return True
        return False
    
    def clear(self):
        for i in range(self.ENEMY_MAX):
            self.emy_f[i] = False
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
            emy.action(screen,msl,eff,sld,scr,tmr,idx)
            if emy.is_boss_defeated():
                idx = 3
                tmr = 0

        
        if idx == 2: #ゲームオーバー
            msl.action(screen)
            emy.action(screen,msl,eff,sld,scr,tmr,idx)
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
    