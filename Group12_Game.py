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
    ゲーム画面に出力させる文字を出力
    """
    def __init__(self):
        pass
    def sent(self, massage):
        pass

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
    def __init__(self):
        pass
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

class Bonus:

    def reward(self, player):
        """
        敵撃破後のボーナス(ステータスup & ヒール)
        """

        bonus = random.choice(["atk_up", "hp_up", "heal"])

        if bonus == "atk_up":
            value = random.randint(3, 5) # アタックを3~5で上昇
            player.atk += value
            Chat.sent(f"攻撃力が{value}上昇した！")
            
        elif bonus == "hp_up":
            value = random.randint(10, 20) # HPを5~15で上昇
            player.max_hp += value
            player.hp += value
            Chat.sent(f"最大HPが{value}上昇した！")

        elif bonus == "heal":
            value = random.randint(10, 20) # HPを10~20回復（上限は超えないように）
            player.hp = min(player.hp + value, player.max_hp)
            Chat.sent(f"HPを{value}回復した！")


def main():
    pg.display.set_caption("ゲーム")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"IMG_2090.jpg")
    bonus = Bonus()
    scene = "null"
    stage = 0

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
            Bonus.reward(player)
        elif scene == "select_action":
            Event.select()
        elif scene == "finish":
            continue

        
        screen.blit(bg_img, [0, 0])
        pg.display.update()

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()