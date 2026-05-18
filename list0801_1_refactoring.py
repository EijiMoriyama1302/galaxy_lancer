import pygame
import sys
import math
import random
from pygame.locals import *


BLACK = (  0,   0,   0)
SILVER= (192, 208, 224)
RED   = (255,   0,   0)
CYAN  = (  0, 224, 255)

#SEを読み込む変数
se_explosion = None

EMY_BULLET = 0
LINE_T = -80
LINE_B = 800
LINE_L = -80
LINE_R = 1040

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


def draw_text(scrn, txt, x, y, siz, col): #文字の表示
    fnt = pygame.font.Font(None, siz)
    sur = fnt.render(txt, True, col)
    x = x - sur.get_width()/2
    y = y - sur.get_height()/2
    scrn.blit(sur, [x, y])

class score:
    def __init__(self):
        self.score = 0
    
    def up(self, point):
        self.score = self.score + point
    
    def clear(self):
        self.score = 0
    
    def draw(self, screen):
        draw_text(screen, "SCORE "+str(self.score), 200, 30, 50, SILVER)


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


class player:
    def __init__(self,x,y):
        #画面の読み込み
        self.img_sship = [
            pygame.image.load("image_gl/starship.png"),
            pygame.image.load("image_gl/starship_l.png"),
            pygame.image.load("image_gl/starship_r.png"),
            pygame.image.load("image_gl/starship_burner.png")
        ]
        self.ss_x = x
        self.ss_y = y
        self.ss_d = 0
        self.key_spc = 0
        self.key_z = 0
        self.ss_muteki = 0
        self.se_barrage = pygame.mixer.Sound("sound_gl/barrage.ogg")
        self.se_damage = pygame.mixer.Sound("sound_gl/damage.ogg")
        self.se_shot = pygame.mixer.Sound("sound_gl/shot.ogg")

    def move_starship(self, scrn, key, missile, shield, tmr): #自機の移動
        self.ss_d = 0
        if key[pygame.K_UP] == 1:
            self.ss_y = self.ss_y - 20
            if self.ss_y < 80:
                self.ss_y = 80
        if key[pygame.K_DOWN] == 1:
            self.ss_y = self.ss_y + 20
            if self.ss_y > 640:
                self.ss_y = 640
        if key[pygame.K_LEFT] == 1:
            self.ss_d = 1
            self.ss_x = self.ss_x - 20
            if self.ss_x < 40:
                self.ss_x = 40
        if key[pygame.K_RIGHT] == 1:
            self.ss_d = 2
            self.ss_x = self.ss_x + 20
            if self.ss_x > 920:
                self.ss_x = 920
        self.key_spc = (self.key_spc+1)*key[K_SPACE]
        if self.key_spc%5 == 1:
            missile.set_missile(self.ss_x,self.ss_y,0)
            self.se_shot.play()
        self.key_z = (self.key_z+1)*key[K_z]
        if self.key_z == 1 and shield.can_shoot_barrage():
            missile.set_missile(self.ss_x,self.ss_y,10)
            shield.down()
            self.se_barrage.play()
        
        if self.ss_muteki%2 == 0:
            scrn.blit(self.img_sship[3], [self.ss_x-8, self.ss_y+40+(tmr%3)*2])
            scrn.blit(self.img_sship[self.ss_d], [self.ss_x-37, self.ss_y-48])
    
    def initialize(self):
        self.ss_x = 480
        self.ss_y = 600
        self.ss_d = 0
        self.ss_muteki = 0
    
    def is_muteki(self):
        if self.ss_muteki > 0:
            self.ss_muteki = self.ss_muteki - 1
            return True
        return False
    
    def set_effect(self, effect): 
        effect.set_effect(self.ss_x, self.ss_y)
    
    def take_damage(self):
        if self.ss_muteki == 0:
            self.ss_muteki = 60
            self.se_damage.play()
    
    def explode(self, effect, tmr):
        if tmr%5 == 0:
            effect.set_effect(self.ss_x+random.randint(-60,60), self.ss_y+random.randint(-60,60))
        if tmr%10 == 0:
            self.se_damage.play()


class missile:
    def __init__(self):
        self.img_weapon = pygame.image.load("image_gl/bullet.png")
        self.MISSILE_MAX = 200
        self.msl_no = 0
        self.msl_f = [False]*self.MISSILE_MAX
        self.msl_x = [0]*self.MISSILE_MAX
        self.msl_y = [0]*self.MISSILE_MAX
        self.msl_a = [0]*self.MISSILE_MAX

    def set_missile(self,ss_x,ss_y,typ): #自機の発射する球をセットする
        if typ == 0: #単発
            self.msl_f[self.msl_no] = True
            self.msl_x[self.msl_no] = ss_x
            self.msl_y[self.msl_no] = ss_y-50
            self.msl_a[self.msl_no] = 270
            self.msl_no = (self.msl_no+1)%self.MISSILE_MAX
        if typ == 10: #弾幕
            for a in range(160, 390, 10):
                self.msl_f[self.msl_no] = True
                self.msl_x[self.msl_no] = ss_x
                self.msl_y[self.msl_no] = ss_y-50
                self.msl_a[self.msl_no] = a
                self.msl_no = (self.msl_no+1)%self.MISSILE_MAX

    def move_missile(self, scrn): #球の移動
        for i in range(self.MISSILE_MAX):
            if self.msl_f[i] == True:
                self.msl_x[i] = self.msl_x[i] + 36*math.cos(math.radians(self.msl_a[i]))
                self.msl_y[i] = self.msl_y[i] + 36*math.sin(math.radians(self.msl_a[i]))
                self.img_rz = pygame.transform.rotozoom(self.img_weapon, -90-self.msl_a[i], 1.0)
                scrn.blit(self.img_rz, [self.msl_x[i]-self.img_rz.get_width()/2, self.msl_y[i]-self.img_rz.get_height()/2])
                if self.msl_y[i] < 0 or self.msl_x[i] < 0 or self.msl_x[i] > 960:
                    self.msl_f[i] = False
    
    def has_hit_enemy(self, emy_x, emy_y, r):
        for n in range(self.MISSILE_MAX):
            if self.msl_f[n] == True and get_dis(emy_x, emy_y, self.msl_x[n], self.msl_y[n]) < r*r:
                self.msl_f[n] = False
                return True
        return False
    
    def clear(self):
        for i in range(self.MISSILE_MAX):
            self.msl_f[i] = False


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
        self.eff_x  = [0]*self.EFFECT_MAX
        self.eff_y  = [0]*self.EFFECT_MAX

    def set_effect(self, x, y): #爆発をセットする
        self.eff_p[self.eff_no] = 1
        self.eff_x[self.eff_no] = x
        self.eff_y[self.eff_no] = y
        self.eff_no = (self.eff_no+1)%self.EFFECT_MAX

    def draw_effect(self,scrn): #爆発の演出
        for i in range(self.EFFECT_MAX):
            if self.eff_p[i] > 0:
                scrn.blit(self.img_explode[self.eff_p[i]], [self.eff_x[i]-48, self.eff_y[i]-48])
                self.eff_p[i] = self.eff_p[i] + 1
                if self.eff_p[i] == 6:
                    self.eff_p[i] = 0


class enemy:
    def __init__(self):
        self.img_enemy = [
            pygame.image.load("image_gl/enemy0.png"),
            pygame.image.load("image_gl/enemy1.png")
        ]
        self.ENEMY_MAX = 100
        self.emy_no = 0
        self.emy_f = [False]*self.ENEMY_MAX
        self.emy_x = [0]*self.ENEMY_MAX
        self.emy_y = [0]*self.ENEMY_MAX
        self.emy_a = [0]*self.ENEMY_MAX
        self.emy_type = [0]*self.ENEMY_MAX
        self.emy_speed = [0]*self.ENEMY_MAX

    def bring_enemy(self, tmr): #敵を出す求めるｒｙｋ
        if tmr % 30 == 0:
            self.set_enemy(random.randint(20, 940), LINE_T, 90, 1, 6)


    def set_enemy(self, x, y, a, ty, sp): #敵機をセットする
        while True:
            if self.emy_f[self.emy_no] == False:
                self.emy_f[self.emy_no] = True
                self.emy_x[self.emy_no] = x
                self.emy_y[self.emy_no] = y
                self.emy_a[self.emy_no] = a
                self.emy_type[self.emy_no] = ty
                self.emy_speed[self.emy_no] = sp
                break
            self.emy_no = (self.emy_no+1)%self.ENEMY_MAX


    def move_enemy(self ,scrn ,msl:missile ,eff:effect, shield:shield, score:score): #敵機の移動
        for i in range(self.ENEMY_MAX):
            if self.emy_f[i] == True:
                ang = -90-self.emy_a[i]
                png = self.emy_type[i]
                self.emy_x[i] = self.emy_x[i] + self.emy_speed[i]*math.cos(math.radians(self.emy_a[i]))
                self.emy_y[i] = self.emy_y[i] + self.emy_speed[i]*math.sin(math.radians(self.emy_a[i]))
                if self.emy_type[i] == 1 and self.emy_y[i] > 360:
                    self.set_enemy(self.emy_x[i], self.emy_y[i], 90, 0, 8)
                    self.emy_a[i] = -45
                    self.emy_speed[i] = 16
                if self.emy_x[i] < LINE_L or LINE_R < self.emy_x[i] or self.emy_y[i] < LINE_T or LINE_B < self.emy_y[i]:
                    self.emy_f[i] = False
                
                if self.emy_type[i] != EMY_BULLET: #プレイヤーと玉とのヒットチェック
                    w = self.img_enemy[self.emy_type[i]].get_width()
                    h = self.img_enemy[self.emy_type[i]].get_height()
                    r = int((w+h)/4)+12
                    if msl.has_hit_enemy(self.emy_x[i], self.emy_y[i], r):
                        eff.set_effect(self.emy_x[i], self.emy_y[i])
                        score.up(100)
                        self.emy_f[i] = False
                        shield.heal()
                    
                img_rz = pygame.transform.rotozoom(self.img_enemy[png], ang, 1.0)
                scrn.blit(img_rz, [self.emy_x[i]-img_rz.get_width()/2, self.emy_y[i]-img_rz.get_height()/2])
    
    def has_hit_player(self ,ss_x ,ss_y):
        for i in range(self.ENEMY_MAX): #敵とのヒットチェック
            if self.emy_f[i] == True:
                w = self.img_enemy[self.emy_type[i]].get_width()
                h = self.img_enemy[self.emy_type[i]].get_height()
                r = int((w+h)/4 + (74+96)/4)
                if get_dis(self.emy_x[i], self.emy_y[i], ss_x, ss_y) < r*r:
                    self.emy_f[i] = False
                    return True
        return False
    
    def clear(self):
        for i in range(self.ENEMY_MAX):
            self.emy_f[i] = False


MY_BULLET = 0
LINE_T = -80
LINE_B = 800
LINE_L = -80
LINE_R = 1040



def get_dis(x1, y1, x2, y2): #二点間の距離を求める
    return( (x1-x2)*(x1-x2) + (y1-y2)*(y1-y2) )




def main(): #メインループ
    global se_explosion
    idx = 0
    tmr = 0

    pygame.init()
    pygame.display.set_caption("Galaxy Lancer")
    screen = pygame.display.set_mode((960, 720))
    clock = pygame.time.Clock()
    se_explosion = pygame.mixer.Sound("sound_gl/explosion.ogg")

    ttl = title()
    bg = background("image_gl/galaxy.png")
    ss = player(480, 360)
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
            ss.move_starship(screen, key, msl, sld, tmr)
            if ss.is_muteki() == False:
                if emy.has_hit_player(ss.ss_x, ss.ss_y): #敵とのヒットチェック
                    ss.set_effect(eff)
                    sld.down()
                    if sld.is_zero():
                        idx = 2
                        tmr = 0
                    ss.take_damage()
            msl.move_missile(screen)
            emy.bring_enemy(tmr)
            emy.move_enemy(screen,msl,eff,sld,scr)
            if tmr == 30*60:
                idx = 3
                tmr = 0
        
        if idx == 2: #ゲームオーバー
            msl.move_missile(screen)
            emy.move_enemy(screen,msl,eff,sld,scr)
            if tmr == 1:
                pygame.mixer.music.stop()
            if tmr <= 90:
                ss.explode(eff, tmr)
            if tmr == 120:
                pygame.mixer.music.load("sound_gl/gameover.ogg")
                pygame.mixer.music.play(0)
            if tmr > 120:
                draw_text(screen, "GAME_OVER", 480, 300, 80, RED)
            if tmr == 400:
                idx = 0
                tmr = 0
        
        if idx == 3: #ゲームクリア
            ss.move_starship(screen, key, msl, sld, tmr)
            ss.is_muteki()
            msl.move_missile(screen)
            if tmr == 1:
                pygame.mixer.music.stop()
            if tmr == 2:
                pygame.mixer.music.load("sound_gl/gameclear.ogg")
                pygame.mixer.music.play(0)
            if tmr > 20:
                draw_text(screen, "GAME CLEAR", 480, 300, 80, SILVER)
            if tmr == 300:
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
    