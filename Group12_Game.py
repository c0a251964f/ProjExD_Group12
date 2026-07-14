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
        # 90% 戦闘のみ、10% 戦闘 + 宝箱
        self.mode = "battle_only" if random.random() < 0.9 else "battle_or_treasure"

    def select(self):
        keys = pg.key.get_pressed()
        chat = Chat()

        # 90% 戦闘のみ
        if self.mode == "battle_only":
            chat.sent("戦闘: F")
            if keys[pg.K_f]:
                return "battle_myTurn"
            return "select_action"
        
        # 10% 戦闘 + 宝箱
        else:
            chat.sent("戦闘: F 宝箱: T")
            if keys[pg.K_f]:
                return "battle_myTurn"
            if keys[pg.K_t]:
                return "treasure_chest"
            return "select_action"


class Player:
    """
    プレイヤーキャラクターを管理するクラス
    """
    def __init__(self, hp=100, atk=20):
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.is_defending = False
        self.is_buffed = False

    def action(self, enemy, command):
        """
        プレイヤーの行動処理
        command: 1(攻撃), 2(防御), 3(自己強化)
        """
        self.is_defending = False

        if command == 1:
            return self._attack(enemy)
        elif command == 2:
            return self._defend()
        elif command == 3:
            return self._buff()
        else:
            Chat.sent("無効なコマンドです。")
            return

    def _attack(self, enemy):
        Chat.sent("プレイヤーの攻撃！")

        # 乱数によるダメージ変動（0.8倍〜1.2倍のブレ）
        variance = random.uniform(0.8, 1.2)
        dmg = int(self.atk * variance)

        if self.is_buffed:
            dmg = int(dmg * 2.5)
            self.is_buffed = False
            Chat.sent(f"自己強化によりダメージが {dmg} にアップ！")

        result = enemy.attacked(dmg)
        return result

    def _defend(self):
        Chat.sent("プレイヤーは防御の態勢をとった！")
        self.is_defending = True
        return

    def _buff(self):
        Chat.sent("プレイヤーは力を溜めている…！次の攻撃力が2.5倍！")
        self.is_buffed = True
        return

    def take_damage(self, dmg):
        """
        敵から攻撃を受ける際の処理
        """
        if self.is_defending:
            dmg = int(dmg * 0.5)
            Chat.sent("防御によりダメージを半減した！")

        self.hp -= dmg
        Chat.sent(f"プレイヤーに {dmg} ダメージ！ 残りHP:{self.hp}")

        if self.hp <= 0:
            Chat.sent("プレイヤーは倒れた…")
            return
        return


class Enemy:
    """
    敵キャラを管理するクラス
    """
    def __init__(self, name, hp, atk,img_path,special=False):
        self.name = name
        self.hp = hp
        self.atk = atk
        self.special = special  # 特殊敵（攻撃されたらゲームオーバー）
        # 敵画像を読み込む
        self.image = pg.image.load(img_path)



        # 画像位置：横中央、縦は上に張り付き
        self.x = (WIDTH - self.image.get_width()) // 2
        self.y = 0

        # 貯め攻撃用
        self.charge_turn = 0

    @staticmethod
    def apper():
        """
        敵を確率で出現させる
        1: hp10 atk10（80%）
        2: hp300 atk100（15%）
        3: hp10000 atk0（5%）攻撃されたらゲームオーバー
        """
        r = random.random()

        if r < 0.80:
            # 80%
            enemy = Enemy("廃れた像", 10, 10,"IMG_廃れた像.jpg")
        elif r < 0.95:
            # 15%
            # 黄金像の強化処理
            base_hp = 300
            base_atk = 50

            Enemy.golden_count = 0

            hp = base_hp * (2**Enemy.golden_count)
            atk = base_atk * (2**Enemy.golden_count)

            Enemy.golden_count += 1

            enemy = Enemy("黄金像", hp, atk, "IMG_黄金像.jpg")
        else:
            # 5%
            enemy = Enemy("退学馬", 10000, 0,"IMG_退学馬.jpg", special=True)

        Chat.sent(f"{enemy.name} が現れた！")
        return enemy

    def action(self, player):
        """
        敵の行動（攻撃・回復・貯め攻撃）
        """
        # 特殊敵は攻撃しない
        if self.special:
            Chat.sent(f"{self.name} はこちらを見つめている…")
            return

        # 行動をランダム選択
        act = random.choice(["attack", "heal"])

        # 通常攻撃
        if act == "attack":
            dmg = self.atk
            Chat.sent(f"{self.name} の攻撃！ {dmg} ダメージ！")
            player.hp -= dmg

        # 回復（自分のHPの半分回復)
        elif act == "heal":
            heal_amount = self.hp // 4
            self.hp += heal_amount
            Chat.sent(f"{self.name} は{heal_amount}回復した！")

            
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
            Bonus.reward(Player)
            event = Event()
            scene = "select_action"
        elif scene == "select_action":
            scene = event.select()
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

