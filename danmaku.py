import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate
def check_inscreen(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面外かを判定し，真理値タプルを返す関数
    """
    yoko, tate = True, True
    if obj_rct.right < 0 or WIDTH < obj_rct.left:
        yoko = False
    if obj_rct.bottom < 0 or HEIGHT < obj_rct.top:
        tate = False
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """
    引数：screen
    半透明の四角形とGameOverの文字列、
    """
    black_out_img = pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(black_out_img, (255, 0, 0), (0, 0, WIDTH, HEIGHT))
    black_out_img.set_alpha(100)
    fonto = pg.font.Font(None, 80)
    txt = fonto.render("GameOver", True, (255, 255, 255))  # 文字の設定
   
    screen.blit(black_out_img,(0, 0))
    screen.blit(txt, (400, 250))
    pg.display.update()
    time.sleep(5)

def gameclear(screen: pg.Surface) -> None:
    """
    引数：screen
    Congratulations!!の表示
    """
    clear_out_img = pg.Surface((WIDTH,HEIGHT))
    pg.draw.rect(clear_out_img, (255, 0, 0), (0, 0, WIDTH, HEIGHT))
    clear_out_img.set_alpha(0)
    fonto = pg.font.Font(None, 80)
    txt = fonto.render("Congratulations!!", True, (255, 255, 255))  # 文字の設定
    
    screen.blit(clear_out_img,(0, 0))
    screen.blit(txt, (300, 250))
    pg.display.update()  
    time.sleep(5)


def retire(screen: pg.Surface) -> None:
    """
    引数：screen
    Retireの表示
    """
    retire_out_img = pg.Surface((WIDTH,HEIGHT))
    pg.draw.rect(retire_out_img, (255, 0, 0), (0, 0, WIDTH, HEIGHT))
    retire_out_img.set_alpha(0)
    fonto = pg.font.Font(None, 80)
    txt = fonto.render("Retire...", True, (255, 255, 255))  # 文字の設定
    
    screen.blit(retire_out_img,(0, 0))
    screen.blit(txt, (450, 250))
    pg.display.update()  
    time.sleep(5)



class Player(pg.sprite.Sprite):
    """
    ゲームキャラクターに関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, xy: tuple[int, int]):
        """
        キャラクター画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/2091142.png"), 0, 0.9)
        self.image = pg.transform.scale(self.image, (50,50))
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10
        self.triple_beam_tmr = 0 #三方向ビームの時間
        self.fast_beam_tmr = 0 #ビームのクールタイムが短くなる時間
        self.shield_tmr = 0 #バリアの時間
        self.hp = 3
        self.hitbox=pg.Rect(self.rect.x+10, self.rect.y+10, 30, 30) #プレイヤーの当たり判定

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        self.hitbox=pg.Rect(self.rect.x+10, self.rect.y+10, 30, 30) #プレイヤーの当たり判定
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
        screen.blit(self.image, self.rect)


class Beam(pg.sprite.Sprite):
    """
      機体が放つビームに関するクラス
    """
    def __init__(self, player:"Player", angle = 0):
        """
        ビーム画像Surfaceを生成する
        引数 player：ビームを放つ機体（Playerインスタンス）
        """
        self.img = pg.image.load(f"fig/beam.png")
        self.rct = self.img.get_rect()
        self.rct.centery = player.rect.centery
        self.rct.left = player.rect.right
        rad = math.radians(angle)
        self.vx = 5 * math.cos(rad)
        self.vy = 5 * math.sin(rad)

    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rct.move_ip(self.vx, self.vy)
        if check_bound(self.rct) == (True, True):
            screen.blit(self.img, self.rct)


class Item(pg.sprite.Sprite):
    """
    アイテムに関するクラス
    """
    imgs = [pg.image.load(f"fig/item{i}.png") for i in range(1, 4)]
    
    def __init__(self, spawn_frame: int):
        super().__init__()
        self.item_type = random.randint(1, 3)
        self.image = pg.transform.rotozoom(__class__.imgs[self.item_type-1], 0, 0.04)
        self.rect = self.image.get_rect()
        img_width = self.rect.width
        img_height = self.rect.height
        x = random.randint(img_width // 2, WIDTH - img_width // 2)
        y = random.randint(img_height // 2, HEIGHT - img_height // 2)
        self.rect.center = (x, y)
        self.vx, self.vy = 0, 0
        self.spawn_frame = spawn_frame
        

    def update(self, screen: pg.Surface, tmr: int):
        """
        アイテムがあるかどうかの確認
        戻り値：画面内にアイテムがあるか
        """
        if tmr - self.spawn_frame >= 200:
            return False
        screen.blit(self.image, self.rect)
        return True
    
def calc_orientation(org,dst):
    """
    orgから見てdstがどこにあるかを計算し方向ベクトルをタプルで返す
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst[0]-org[0], dst[1]-org[1]
    norm = math.sqrt(x_diff**2+y_diff**2)
    if norm == 0:  # ゼロ除算を防ぐ
        return 0, 0
    return x_diff/norm, y_diff/norm


def facing(self_rect, player_rect):
    """
    self_rectがplayer_rectの方向を向く角度を計算してangleを返す
    """
    dx = player_rect.centerx - self_rect.centerx
    dy = player_rect.centery - self_rect.centery
    angle = math.degrees(math.atan2(-dy, dx))  # 反時計回りで計算
    return angle

def anglevector(angle):
    """
    angleのほう歩行に進むvx, vyを返す
    """
    radian = math.radians(angle)  # 角度をラジアンに変換
    vx = math.cos(radian)  # X方向の速度
    vy = -math.sin(radian) # Y方向の速度 (画面座標系に合わせるため符号を反転)
    return [vx, vy]


class Boss(pg.sprite.Sprite):
    """
    ボスに関するクラス
    """
    def __init__(self):
        super().__init__()
        self.image_path="fig/3.png"
        self.image = pg.image.load(f"fig/3.png")
        self.rect = self.image.get_rect()
        self.rect.center = 1200,HEIGHT/2-50
        self.state,self.keitai,self.state_num = "start","1",0
        self.image = pg.transform.scale(self.image,(200,200))
        self.stop_xy =[900,HEIGHT/2-50]  # 停止位置を指定 
        self.vx, self.vy,self.vx_sub, self.vy_sub = 0,0,0,0
        self.danmaku_cooltime=100
        self.cooltime=0
        self.hp=80
        self.count=0
        self.speed=10
        self.speed_sub=0
        self.random=[0,0,0,0]#[x,y,angle1,angle2]
        self.keep_xy=[0,0]
        self.circle_size=0
        self.hitbox=pg.Rect(self.rect.x, self.rect.y, 200, 200) #ボスの当たり判定
        self.state_dict={
            0:"attack0",
            1:"attack1",
            2:"attack2",
            3:"attack3",
            4:"attack4",
            5:"attack5",
            6:"attack6",
            7:"attack7",
        }

    def start(self):
        if self.rect.centerx > self.stop_xy[0]:
            self.rect.move_ip(-1,0)
            if self.rect.centerx < self.stop_xy[0]:
                self.rect.centerx = self.stop_xy[0]
        if self.rect.centerx == self.stop_xy[0] and self.count==500:
            self.state = "reset"

    def missile1(self,danmaku,playerrect):
        self.speed=4
        self.image = pg.image.load(f"fig/9.png")
        self.image_path="fig/9.png"
        if self.count%200==1:
            self.random[0]=random.randint(int(WIDTH/2),WIDTH)
            self.random[1]=random.randint(0,HEIGHT)
        if 30>self.count%50>0:
            self.speed_sub+=0.8
        if self.count%50==30:
            self.speed_sub=0
        if 50>self.count%50>30:
            self.vx, self.vy = calc_orientation([self.rect.centerx,self.rect.centery],self.random)
        if self.count%50==0:
            self.speed_sub=-10
            self.vx_sub,self.vy_sub=anglevector(facing(self.rect,playerrect))
            danmaku.add(Danmaku("missile",self.rect,0))
        if self.count>200:
            self.cooltime=100
            self.state = "reset"

    def missile2(self,danmaku):
        self.vx, self.vy = calc_orientation([self.rect.centerx,self.rect.centery],self.random)
        self.image = pg.image.load(f"fig/3.png")
        self.image_path="fig/3.png"
        self.image = pg.transform.scale(self.image,(200,200))
        if self.count==1:
            self.speed=4
            self.random[0]=random.randint(int(WIDTH/2),WIDTH)
            self.random[1]=0
        if self.rect.centery<10:
            self.speed=9
            self.random[0]=random.randint(int(WIDTH/2),WIDTH)
            self.random[1]=HEIGHT
            self.state_num=1
        if self.state_num==1:
            self.image = pg.image.load(f"fig/9.png")
            self.image_path="fig/9.png"
            if self.count%13==0:
                danmaku.add(Danmaku("missile",self.rect,0))
        if self.rect.centery>HEIGHT-10:
            self.cooltime=100   
            self.state = "reset"

    def circle_danmaku(self,danmaku):
        self.speed = 6
        self.vx, self.vy = calc_orientation([self.rect.centerx,self.rect.centery],self.random)#ランダムな方向へ向かう
        if  self.count%40==0:
            self.random[0]=random.randint(int(WIDTH-WIDTH/4),WIDTH)#ランダムな方向を設定
            self.random[1]=random.randint(0,HEIGHT)
        if self.count%50==0:
            self.image = pg.image.load(f"fig/6.png")
            self.image_path="fig/6.png"
            self.state_num+=1
            for i in range(27):#弾幕の数
                danmaku.add(Danmaku("danmaku",self.rect,(i-180)*15))#弾幕を発射
        if self.count >200:#countが200以上で終了
            self.cooltime=100
            self.state = "reset"

    def tossin(self,danmaku):
        if self.count==1:
            self.vx,self.vy=0,-2#上に行く
        if check_bound(self.rect) == (True, False):#画面恥に行ったらｖyを反転
            self.vy=self.vy*-1
        if self.count==110:
            self.vx,self.vy=3,0
        if self.count>110:
            self.vx-=0.2
        if self.vx<0:
            if self.vx>-1:
                self.keep_xy[0]=self.rect.centerx
                self.random[2]=random.randint(0,90)+45
                self.random[3]=self.random[2]+180
            if self.rect.centerx<self.keep_xy[0]-180*self.state_num+1 and self.vx<-1:#180が弾幕のx軸の感覚
                self.state_num+=1
                danmaku.add(Danmaku("danmaku",self.rect,self.random[2],WIDTH-30*self.state_num+1))
                danmaku.add(Danmaku("danmaku",self.rect,self.random[3],WIDTH-30*self.state_num+1))
            if self.vx<-5:
                if check_bound(self.rect) == (False, False) or check_bound(self.rect) == (False, True) :
                    self.cooltime=200
                    self.state = "reset"

    def hansya_danmaku(self,danmaku):
        self.speed = 6
        self.vx, self.vy = calc_orientation([self.rect.centerx,self.rect.centery],self.random)#ランダムな方向へ向かう
        if  self.count%40==0:
            self.random[0]=random.randint(int(WIDTH-WIDTH/4),WIDTH)#ランダムな方向を設定
            self.random[1]=random.randint(0,HEIGHT)
        if self.count==100:
            self.image = pg.image.load(f"fig/6.png")
            self.image_path="fig/6.png"
            self.state_num+=1
            danmaku.add(Danmaku("beam",self.rect,random.randint(0,140)-210))#弾幕を発射
        if self.count >200:#countが200以上で終了
            self.cooltime=100
            self.state = "reset"

    def kaiten_danmaku(self,danmaku):
        self.speed = 10
        self.vx, self.vy = calc_orientation([self.rect.centerx,self.rect.centery],self.random)#中心へ向かう
        if  self.count==1:
            self.random[2]=0.4
            self.random[0]=WIDTH/2-50
            self.random[1]=HEIGHT/2-50
        if self.count>100:
            self.random[2]+=0.05
            self.image = pg.image.load(f"fig/6.png")
            self.image_path="fig/6.png"
            if self.count%3==0:
                self.state_num+=self.random[2]
                danmaku.add(Danmaku("danmaku2",self.rect,self.state_num+90))#弾幕を発射
                danmaku.add(Danmaku("danmaku2",self.rect,self.state_num-90))#弾幕を発射
        if self.count >400:#countが200以上で終了
            self.cooltime=100
            self.state = "reset"

    def minikoukaton(self,minikoukaton):
        self.image = pg.image.load(f"fig/10.png")
        self.image_path = "fig/10.png"
        self.speed = 3
        self.vx, self.vy = calc_orientation([self.rect.centerx,self.rect.centery],self.random)#ランダムな方向へ向かう
        if  self.count%60==0:
            self.random[0]=random.randint(int(WIDTH-WIDTH/4),WIDTH)#ランダムな方向を設定
            self.random[1]=random.randint(0,HEIGHT)
            minikoukaton.add(Minikoukaton("minikoukaton",self.rect,random.randint(0,1)*180+90))#みにこうかとん出現
        if self.count >200:#countが200以上で終了
            self.cooltime=10
            self.state = "reset"

    def update(self,screen,danmaku,playerrect,minikoukaton):
        self.hitbox=pg.Rect(self.rect.x, self.rect.y, 200, 200) #当たり時判定更新
        self.count+=1
        if self.state != "attack4":
            if abs(self.rect.centerx - self.random[0]) < abs(self.speed* self.vx) or abs(self.rect.centery - self.random[1]) < abs(self.speed* self.vy):
                    self.vx,self.vy=0,0 #停止位置で止まる
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if self.speed_sub != 0:
            self.rect.move_ip(self.speed_sub*self.vx_sub,self.speed_sub*self.vy_sub)
        if self.state == "reset":
            self.speed=6
            self.speed_sub=0
            self.count = 1
            self.state_num=0
            self.state = "random"
            self.random[2]=0
            
        if self.state == "random":
            self.image = pg.image.load(f"fig/3.png")
            self.image_path="fig/3.png"
            self.image = pg.transform.scale(self.image,(200,200))
            if  self.count%20==0:
                self.random[0]=random.randint(int(WIDTH/2),WIDTH)
                self.random[1]=random.randint(0,HEIGHT)
            if self.rect.centerx != self.random[0] and self.rect.centery != self.random[1]:
                self.vx, self.vy = calc_orientation([self.rect.centerx,self.rect.centery],self.random)
            if self.rect.centerx == self.random[0] and self.rect.centery == self.random[1]:
                self.vx,self.vy=0,0
            if self.count>=self.cooltime:
                self.cooltime=0
                self.count = 1
                self.state=self.state_dict[random.randint(1,7)] #攻撃ランダム
                self.random[0]=random.randint(int(WIDTH/2),WIDTH)
                self.random[1]=random.randint(0,HEIGHT)
        if self.state == "start":
            self.start()
        if self.state=="attack1":   #ミサイル1
            self.missile1(danmaku,playerrect)
        if self.state=="attack2":   #ミサイル２
            self.missile2(danmaku)
        if self.state=="attack3":   #円形弾幕
            self.circle_danmaku(danmaku)
        if self.state=="attack4": #突進弾幕
            self.tossin(danmaku)
        if self.state=="attack5": #ビーム
            self.hansya_danmaku(danmaku)
        if self.state=="attack6": #回転弾幕
            self.kaiten_danmaku(danmaku)
        if self.state=="attack7": #ミニこうかとん召喚
            self.minikoukaton(minikoukaton)
        screen.blit(self.image,self.rect) 
            


class Bosscolor(pg.sprite.Sprite):
    """
    ボスの色を変えるクラス
    """
    def __init__(self,bossrect,image,type):
        super().__init__()
        self.image_path=image
        self.type=type
        self.image = pg.image.load(f"fig/3.png").convert_alpha()
        self.image = pg.transform.scale(self.image,(200,200))
        self.rect = bossrect
        self.tmr=0
    def update(self,screen,bossrect,count,image):
        if self.tmr==0:
            self.image = pg.image.load(image).convert_alpha()
            if image=="fig/3.png":
                    self.image = pg.transform.scale(self.image,(200,200))
            if self.type=="start":
                self.image.fill((0,0,0), special_flags=pg.BLEND_RGB_MULT)
                self.alpha=255
                self.num=0
            if self.type=="damage":
                self.image.fill((0,150,150), special_flags=pg.BLEND_RGB_SUB)
                self.alpha=130
                self.num=6
            if self.type=="kirari":
                self.image.fill((255,255,255), special_flags=pg.BLEND_RGB_ADD)
                self.alpha=200
                self.num=5  
        if self.num <40:
            self.num+=0.03
        if self.alpha>0 and count>400:
            self.alpha -= self.num
        if self.type=="damage":
            self.alpha -= self.num
        self.image.set_alpha(self.alpha)
        screen.blit(self.image,bossrect)
        self.tmr+=1
        if self.alpha <= 0:
            self.kill()
class Minikoukaton(pg.sprite.Sprite):
    """
    ミニこうかとんに関するクラス
    """
    def __init__(self,type,bossrect,angle):
        super().__init__()
        self.type=type
        self.danmaku_type={ #名前：[画像,サイズ,スピード]
            "minikoukaton":["fig/3.png",(70,70),1.7]
            }
        self.summonpoint={
            90:[(random.randint(int(WIDTH/4),WIDTH),HEIGHT),-2],
            270:[(random.randint(int(WIDTH/4),WIDTH),0),2]
        }
        self.angle = angle
        self.vx=0
        self.vy=self.summonpoint[self.angle][1]
        self.rad = math.radians(angle)
        self.image =  pg.image.load(self.danmaku_type[type][0])
        self.rect = self.image.get_rect()
        self.rect.topleft = bossrect.topleft
        self.image = pg.transform.scale(self.image,self.danmaku_type[type][1])
        self.rect.topleft=self.summonpoint[self.angle][0]
        self.speed = self.danmaku_type[type][2]
        self.random=random.randint(0,50)
        self.count = 0
    def update(self,screen,playerrect,danmaku):
        self.image.set_colorkey((0, 0, 0))
        self.count += 1
        self.rect.move_ip(round(self.speed*self.vx,10),round(self.speed*self.vy,10))
        if self.count%(60+self.random)==0:
            danmaku.add(Danmaku("danmaku",self.rect,facing(self.rect,playerrect)))
            danmaku.add(Danmaku("danmaku",self.rect,facing(self.rect,playerrect)+20))
            danmaku.add(Danmaku("danmaku",self.rect,facing(self.rect,playerrect)-20))
        screen.blit(self.image,self.rect)
        if self.count>=400:
            self.kill()


class Danmaku(pg.sprite.Sprite):
    """
    弾幕に関するクラス
    """
    def __init__(self,type,bossrect,angle,summonx=0):
        super().__init__()
        self.type=type
        self.danmaku_type={ #名前：[画像,サイズ,スピード]
            "missile":["fig/missile.png",(160,70),0],
            "danmaku":["fig/circle.png",(48,12),6.44],
            "danmaku2":["fig/circle.png",(48,12),12],
            "beam":["fig/circle.png",(120,120),10],
            "minikoukaton":["fig/10.png",(50,50),2]
            }
        self.bound={
            (True,True):[1,1],
            (True,False):[1,-1],
            (False,True):[-1,1],
            (False,False):[-1,-1]
        }
        self.summonpoint={
            90:(random.randint(int(WIDTH/4),WIDTH),HEIGHT),
            270:(random.randint(int(WIDTH/4),WIDTH),0)
        }
        if self.danmaku_type[type][0] != "None":
            self.image = pg.image.load(self.danmaku_type[type][0]).convert_alpha()
        if self.danmaku_type[type][0] == "None":
            self.image =  pg.Surface(self.danmaku_type[type][1])
        self.vx,self.vy=0,0
        self.rad = math.radians(angle)
        self.rect = self.image.get_rect()
        self.rect.topleft = bossrect.topleft
        self.image = pg.transform.scale(self.image,self.danmaku_type[type][1])
        self.original_image = self.image #回転用元画像
        self.angle = angle
        if type=="missile":
            self.rect.topleft = (bossrect.x -120, bossrect.y)
        if type=="danmaku2":
            self.rect.topleft = (WIDTH/2-50,HEIGHT/2-50)
        if type=="minikoukaton":
            self.rect.topleft=self.summonpoint[angle]
        if type !="missile" or type != "minikoukaton":
            self.image.set_colorkey((0, 0, 0))
            self.image = pg.transform.rotate(self.original_image, self.angle+180)#回転
            self.rect = self.image.get_rect(center=self.rect.center) # 回転後の座標調整
            self.vx=anglevector(self.angle)[0]
            self.vy=anglevector(self.angle)[1]
        self.speed = self.danmaku_type[type][2]
        self.list=[0,0]
        self.count = 0
    def update(self,screen,playerrect):
        self.image.set_colorkey((0, 0, 0))
        self.count += 1
        self.rect.move_ip(round(self.speed*self.vx,10),round(self.speed*self.vy,10))
        if self.type=="missile":
            self.image = pg.transform.rotate(self.original_image, self.angle+180)#回転
            self.rect = self.image.get_rect(center=self.rect.center)  # 回転後の座標調整
            self.speed+=0.4
            if self.count < 50:
                self.speed-=0.2
                self.angle = facing(self.rect,playerrect)
                self.vx=anglevector(self.angle)[0]
                self.vy=anglevector(self.angle)[1]
        if self.type=="danmaku":
            if self.speed > 1.5:
                self.speed-=0.01
        if self.type=="beam":
            self.image.set_alpha(160)#透明度
            self.speed+=0.01
            if self.list[0]<8:#8回だけバウンド
                self.vx*=self.bound[check_bound(self.rect)][0]
                self.vy*=self.bound[check_bound(self.rect)][1]
                if check_bound(self.rect)!=(True,True):
                    self.list[0]+=1
        self.image.set_colorkey((0, 0, 0))
        screen.blit(self.image,self.rect)
        if check_inscreen(self.rect) != (True, True):
            self.kill()

class My_Life(pg.sprite.Sprite):
    """
    自機のHP表示に関するクラス
    """
    def __init__(self, player: Player):
        super().__init__()
        self.player = player  
        self.font = pg.font.Font(None, 40)
        self.image = pg.Surface((player.hp * 60, 20))
        pg.draw.rect(self.image, (0, 0, 255), (0, 0, player.hp * 60, 20))
        self.rect = self.image.get_rect()
        self.rect.topleft = (5, 5)


    def update(self):
        hp = self.player.hp
        bar_width = max(hp * 60, 1)
        bar_height = 20
        text_height = 25
        total_height = bar_height + text_height

        # 新しいSurfaceを作成（透明背景）
        self.image = pg.Surface((bar_width + 100, total_height), pg.SRCALPHA)
        self.image.fill((0, 0, 0, 0))

        # ライフバーを描画
        pg.draw.rect(self.image, (0, 0, 255), (0, 0, bar_width, bar_height))

        # HP数値を描画
        text = self.font.render(f"HP: {hp}", True, (255, 255, 255))
        self.image.blit(text, (0, bar_height))

        # rectも更新
        self.rect = self.image.get_rect()
        self.rect.topleft = (5, 5)

class Boss_Life(pg.sprite.Sprite):
    """
    ボスのHP表示に関するクラス
    """
    def __init__(self, boss: Boss):
        super().__init__()
        self.boss = boss
        self.image = pg.Surface((boss.hp * 10, 20))
        pg.draw.rect(self.image, (255, 0, 0), (0, 0, boss.hp * 10, 20))
        self.rect = self.image.get_rect()
        self.rect.topright = (WIDTH-5, 5)


    def update(self):
        hp = self.boss.hp
        bar_width = max(hp * 10, 1)
        bar_height = 20

        # 新しいSurfaceを作成（透明背景）
        self.image = pg.Surface((bar_width , bar_height), pg.SRCALPHA)
        self.image.fill((0, 0, 0, 0))

        # ライフバーを描画
        pg.draw.rect(self.image, (255, 0, 0), (0, 0, bar_width, bar_height))

        # rectも更新
        self.rect = self.image.get_rect()
        self.rect.topright = (WIDTH-5, 5)



def main():
    pg.display.set_caption("墜ちろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/26466996.jpg")
    bg_img2 = pg.transform.flip(bg_img, True, False) 
    bg_width = bg_img.get_width()  # bg_imgの横幅の取得

    player = Player((200, HEIGHT/2))
    boss = pg.sprite.Group()
    beams = []
    items = []
    last_beam_time = 0   #最後に打ったビームの時間
    last_item_spawn = 0  #最後に現れたアイテムの時間
    next_spawn_interval = 200 #次にアイテムが出るまでの時間    boss = pg.sprite.Group()
    boss.add(Boss())#こうかとんを出現
    pg.mixer.init()
    pg.mixer.music.load("fig/fight.mp3")
    pg.mixer.music.play(-1)
    bosscolor=pg.sprite.Group()#こうかとんを出現2
    bosscolor.add(Bosscolor(boss.sprites()[0].rect,boss.sprites()[0].image_path,"start"))
    danmaku = pg.sprite.Group()
    minikoukaton = pg.sprite.Group()     
    my_life = pg.sprite.Group()
    my_life_bar = My_Life(player)
    my_life.add(my_life_bar)
    boss_life = pg.sprite.Group()
    boss_life_bar = Boss_Life(boss.sprites()[0])
    boss_life.add(boss_life_bar)


    tmr = 0
    scrollspeed = 0  # 背景画像の移動スピード
    accelerate = 0.1  # 背景画像の加速度
    maxspeed = 100
    scrollposition = 0  # 背景画像の位置座標
    clock = pg.time.Clock()
    mutekijikan = 0

    while True:
        screen.blit(bg_img, [0,0]) 
        mutekijikan += 1
  # --------------画面移動のプログラム----------------
        scrollposition += scrollspeed
        scrollposition %= bg_width * 2
        if scrollspeed < maxspeed:
            speed = tmr * (accelerate**5)  # 背景画像の加速度
            scrollspeed += speed
            screen.blit(bg_img, [-scrollposition, 0]) 
            screen.blit(bg_img2, [-scrollposition+bg_width, 0]) 
            screen.blit(bg_img, [-scrollposition+bg_width*2, 0])
        else:  # スクロールするスピードが指定したスピードになると速度が一定になる
            scrollspeed = maxspeed
            screen.blit(bg_img, [-scrollposition, 0]) 
            screen.blit(bg_img2, [-scrollposition+bg_width, 0]) 
            screen.blit(bg_img, [-scrollposition+bg_width*2, 0])
  # -------------------------------------------------

        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
        for danmaku_hit in danmaku:
            if player.hitbox.colliderect(danmaku_hit.rect): # プレイやーと衝突した弾幕リスト
                danmaku.remove(danmaku_hit)
                if player.shield_tmr == 0 and  mutekijikan>=30:
                    player.hp-=1#プレイヤーが当たった時にhp-1
                    mutekijikan =0
        for baem in beams:
            if boss.sprites()[0].hitbox.colliderect(baem.rct): #ボスのダメージ判定
                boss.sprites()[0].hp-=1
                beams.remove(baem)
                if tmr>400:
                    bosscolor.add(Bosscolor(boss.sprites()[0].rect,boss.sprites()[0].image_path,"damage"))
            for minikoukaton_hit in minikoukaton:
                if minikoukaton_hit.rect.colliderect(baem.rct):
                    minikoukaton_hit.kill()

        current_time = pg.time.get_ticks() #現在の時間

        if player.fast_beam_tmr > 0:
            beam_cool_tmr = 400 #ビームのクールタイム（アイテム使用時）
        else:
            beam_cool_tmr = 800 #ビームのクールタイム（通常）
            
        if key_lst[pg.K_SPACE]:    #スペースキー長押しでビーム投下
            if current_time - last_beam_time >= beam_cool_tmr:
                last_beam_time = current_time   
                beams.append(Beam(player)) 
                if player.triple_beam_tmr > 0: #三方向にビームを出す
                    for angle in [0, 30, -30]:
                        beams.append(Beam(player, angle))
                else:
                    beams.append(Beam(player)) #通常のビーム

        if player.shield_tmr > 0:
            pg.draw.circle(screen, (0, 255, 255), player.rect.center, 60, 5)

        if tmr - last_item_spawn >= next_spawn_interval:
            items.append(Item(tmr))
            last_item_spawn = tmr
            next_spawn_interval = random.randint(400, 600) #次のアイテムが400~600フレームの間に出現する

        for item in items:
            if player.rect.colliderect(item.rect):
                if item.item_type == 1:
                    player.triple_beam_tmr = 200 #200フレームの間三方向ビーム

                elif item.item_type == 2:
                    player.fast_beam_tmr = 200

                elif item.item_type == 3:
                    player.shield_tmr = 300
                items.remove(item)


        for i, beam in enumerate(beams):
            beams = [ beam for beam in beams if beam is not None]

        if player.triple_beam_tmr > 0:
            player.triple_beam_tmr -= 1
        if player.fast_beam_tmr >0:
            player.fast_beam_tmr -= 1
        if player.shield_tmr > 0:
            player.shield_tmr -= 1
        
        boss.update(screen,danmaku,player.rect,minikoukaton)
        minikoukaton.update(screen, player.rect,danmaku)
        bosscolor.update(screen,boss.sprites()[0].rect,boss.sprites()[0].count,boss.sprites()[0].image_path)
        danmaku.update(screen, player.rect) 

        if event.type == pg.KEYDOWN and event.key == pg.K_BACKSPACE:
                pg.mixer.init()
                pg.mixer.music.load("fig/death.mp3")
                pg.mixer.music.play()
                retire(screen)  # backspaceキーでリタイア
                return
        
        if player.hp == 0:  # プレイヤーのHPが0になったらgameover
            pg.mixer.init()
            pg.mixer.music.load("fig/death.mp3")
            pg.mixer.music.play()
            gameover(screen)
            return
        
        if boss.sprites()[0].hp == 0:  # ボスのHPｇが0になったらgameclear
            pg.mixer.init()
            pg.mixer.music.load("fig/clear.mp3")
            pg.mixer.music.play()
            gameclear(screen)
            return

        player.update(key_lst, screen)
        items = [item for item in items if item.update(screen, tmr)]          
        for beam in beams: 
            beam.update(screen)  

        my_life.update()
        my_life.draw(screen)
        boss_life.update()
        boss_life.draw(screen)
  # --------------デバッグ用コード-----------------
        print(f" timer = {tmr}                      speed = {int(scrollspeed)}")
        pg.display.update()
        tmr += 1
        clock.tick(50)
  # ---------------------------------------------


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()

