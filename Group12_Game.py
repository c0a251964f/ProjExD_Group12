import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Chat:
    """
    ゲーム画面にメッセージを出力
    """
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.font = pg.font.SysFont("meiryo", 32)
    def sent(self, message: str):
        pg.draw.rect(self.screen, (0, 0, 0), (0, HEIGHT - 80, WIDTH, 80))
        text = self.font.render(message, True, (255, 255, 255))
        self.screen.blit(text, (20, HEIGHT - 55))
        pg.display.update()

class Event:
    """
    戦闘をするか宝箱を取るか選択する。
    どちらが出るかはランダム
    """
    def __init__(self):
        pass
    def select():
        pass

class Player:
    def __init__(self, atk, hp, max_hp):
        self.atk = atk
        self.hp = hp
        self.max_hp = max_hp
    def action():
        pass
    def winBounus():
        pass

class Enemy:
    def __init__(self):
        pass
    def apper():
        pass
    def action():
        pass

class TreasureChest:
    """
    宝箱を取得した時のクラス
    Playerのhpか攻撃力をランダムで上昇させる
    """
    def __init__(self):
        self.chesNum = random.randint(0, 1)
    def getTreasure(self, Player_attack: Player.atk, Player_hp: Player.hp, Player_max_hp: Player.max_hp, scene: str, chat: Chat):
        if self.chesNum == 0:
            attack = random.randint(10, 15)
            Player_attack += attack #攻撃力を上昇
            chat.sent(f"攻撃力が{attack}アップした！")
        if self.chesNum == 1:
            hp = random.randint(50, 80)
            Player_max_hp += hp #maxhpとhpを上昇
            Player_hp += hp
            chat.sent(f"HPが{hp}回復した！")
        scene = "select_action" # シーン切り替え


def main():
    pg.display.set_caption("ゲーム")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"IMG_2090.jpg")
    scene = "null"
    stage = 0
    chat = Chat(screen)
    treasureChest = TreasureChest(chat)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
        
        if scene == "start":
            continue
        elif scene == "battle_myTurn":
            Player.action()
            scene = Player.finishScene()
        elif scene == "battle_enemyTurn":
            Enemy.apper()
            Enemy.action()
        elif scene == "finish_battle":
            Player.winBounus()
        elif scene == "select_action":
            Event.select()
        elif scene == "treasure_chest":
            treasureChest.getTreasure(Player.atk, Player.hp, screen, scene, chat)
        elif scene == "finish":
            continue

        
        screen.blit(bg_img, [0, 0])
        pg.display.update()

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()