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
    def __init__(self, screen: pg.Surface, ):
        self.screen = screen
        self.font = pg.font.SysFont("meiryo", 32)
    def sent(self, message: str):
        pg.draw.rect(self.screen, (0, 0, 0), (0, HEIGHT - 80, WIDTH, 80))
        text = self.font.render(message, True, (255, 255, 255))
        self.screen.blit(text, (20, HEIGHT - 55))
        pg.display.update()
        time.sleep(1)


class Event:
    """
    戦闘をするか宝箱を取るか選択する。
    どちらが出るかはランダム
    """
    def __init__(self, screen, chat):
        # 90% 戦闘のみ、10% 戦闘 + 宝箱
        self.mode = "battle_only" if random.random() < 0.7 else "battle_or_treasure"
        self.screen = screen
        self.chat = chat
    
    def _clear_message(self):
        # 下の黒帯を再描画してメッセージを消す
        pg.draw.rect(self.screen, (0, 0, 0), (0, HEIGHT - 80, WIDTH, 80))
        pg.display.update()

    def select(self, key):
        if self.mode == "battle_only":
            self.chat.sent("戦闘: Fキー")
            if key == "f":
                self._clear_message()
                return "battle_myTurn"
            return "select_action"
        else:
            self.chat.sent("戦闘: Fキー 宝箱: Tキー")
            if key == "f":
                self._clear_message()
                return "battle_myTurn"
            elif key == "t":
                self._clear_message()
                return "treasure_chest"
            return "select_action"


class Player:
    """
    プレイヤーキャラクターを管理するクラス
    """
    def __init__(self, chat, hp=100, atk=20):
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.is_defending = False
        self.is_buffed = False
        self.chat = chat

    def get_command(self, key):
        """
        プレイヤーの行動コマンドを取得する
        1: 攻撃 2: 防御 3: 自己強化
        """
        self.chat.sent("行動を選択してください: 1(攻撃), 2(防御), 3(自己強化)")
        print("行動を選択してください: 1(攻撃), 2(防御), 3(自己強化)")

        return key

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
            return "noKey"

    def _attack(self, enemy):
        self.chat.sent("プレイヤーの攻撃！")
        print("プレイヤーの攻撃！")

        # 乱数によるダメージ変動（0.8倍〜1.2倍のブレ）
        variance = random.uniform(0.8, 1.2)
        dmg = int(self.atk * variance)

        if self.is_buffed:
            dmg = int(dmg * 2.5)
            self.is_buffed = False
            self.chat.sent(f"自己強化によりダメージが {dmg} にアップ！")
            print(f"自己強化によりダメージが {dmg} にアップ！")

        return enemy.attacked(dmg)

    def _defend(self):
        self.chat.sent("プレイヤーは防御の態勢をとった！")
        print("プレイヤーは防御の態勢をとった！")
        self.is_defending = True
        return None

    def _buff(self):
        self.chat.sent("プレイヤーは力を溜めている…！次の攻撃力が2.5倍！")
        print("プレイヤーは力を溜めている…！次の攻撃力が2.5倍！")
        self.is_buffed = True
        return None

    def take_damage(self, dmg):
        """
        敵から攻撃を受ける際の処理
        """
        if self.is_defending:
            dmg = int(dmg * 0.5)
            self.chat.sent("防御によりダメージを半減した！")
            print("防御によりダメージを半減した！")

        self.hp -= dmg
        self.chat.sent(f"プレイヤーに {dmg} ダメージ！ 残りHP:{self.hp}")
        print(f"プレイヤーに {dmg} ダメージ！ 残りHP:{self.hp}")

        if self.hp <= 0:
            self.chat.sent("プレイヤーは倒れた…")
            print("プレイヤーは倒れた…")
            return
        return


class Enemy:
    """
    敵キャラを管理するクラス
    """
    def __init__(self,chat, name="敵", hp=1, atk=1,img_path=None,special=False):
        self.chat=chat
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
    def apper(chat, screen):
        """
        敵を確率で出現させる
        1: hp10 atk10（80%）
        2: hp300 atk100（15%）
        3: hp10000 atk0（5%）攻撃されたらゲームオーバー
        """
        r = random.random()

        if r < 0.80:
            # 80%
            enemy = Enemy(chat, "廃れた像", 10, 10,"IMG_廃れた像.jpg")
        elif r < 0.95:
            # 15%
            # 黄金像の強化処理
            base_hp = 300
            base_atk = 50

            # golden_count をリセットしない
            if not hasattr(Enemy, "golden_count"):
                Enemy.golden_count = 0

            hp = base_hp * (2**Enemy.golden_count)
            atk = base_atk * (2**Enemy.golden_count)

            Enemy.golden_count += 1

            enemy = Enemy(chat, "黄金像", hp, atk, "IMG_黄金像.jpg")
        else:
            # 5%
            enemy = Enemy(chat, "退学馬", 10000, 0,"IMG_退学馬.jpg", special=True)

        
        chat.sent(f"{enemy.name} が現れた！")
        screen.blit(enemy.image, [enemy.x, enemy.y])
        pg.display.update()
        print(f"{enemy.name} が現れた！")
        return enemy
    
    def attacked(self, dmg):
        """
        プレイヤーから攻撃されたときの処理
        """
        if self.special:
            self.chat.sent("退学馬に触れてしまった…強制的にゲームオーバー！")
            return "GAMEOVER"
    
        self.hp -= dmg
        self.chat.sent(f"{self.name} に {dmg} ダメージ！ 残りHP:{self.hp}")
        print(f"{self.name} に {dmg} ダメージ！ 残りHP:{self.hp}")

        if self.hp <= 0:
            self.chat.sent(f"{self.name} を倒した！")
            print(f"{self.name} を倒した！")
            return "DEFEATED"

        return "CONTINUE"

    def action(self, player):
        """
        敵の行動（攻撃・回復）
        """
        # 特殊敵は攻撃しない
        if self.special:
            self.chat.sent(f"{self.name} はこちらを見つめている…")
            print(f"{self.name} はこちらを見つめている…")
            return

        # 行動をランダム選択
        act = random.choice(["attack", "heal"])

        # 通常攻撃
        if act == "attack":
            dmg = self.atk
            self.chat.sent(f"{self.name} の攻撃！ {dmg} ダメージ！")
            print(f"{self.name} の攻撃！ {dmg} ダメージ！")
            player.take_damage(dmg)

        # 回復（自分のHPの半分回復)
        elif act == "heal":
            heal_amount = self.hp // 4
            self.hp += heal_amount
            self.chat.sent(f"{self.name} は{heal_amount}回復した！")
            print(f"{self.name} は{heal_amount}回復した！")

            
class TreasureChest:
    """
    宝箱を取得した時のクラス
    Playerのhpか攻撃力をランダムで上昇させる
    """
    def __init__(self):
        self.chesNum = random.randint(0, 1)
    def getTreasure(self, Player_attack, Player_hp, Player_max_hp, chat: Chat):
        self.chesNum = random.randint(0, 1)
        if self.chesNum == 0:
            attack = random.randint(10, 15)
            Player_attack += attack #攻撃力を上昇
            chat.sent(f"攻撃力が{attack}アップした！")
            print(f"攻撃力が{attack}アップした！")
        if self.chesNum == 1:
            hp = random.randint(50, 80)
            Player_max_hp += hp #maxhpとhpを上昇
            Player_hp += hp
            chat.sent(f"HPが{hp}回復した！")
            print(f"HPが{hp}回復した！")

class Bonus:
    def __init__(self, chat):
        self.chat = chat

    def reward(self, player):
        """
        敵撃破後のボーナス(ステータスup & ヒール)
        """

        bonus = random.choice(["atk_up", "hp_up", "heal"])

        if bonus == "atk_up":
            value = random.randint(5, 40) # アタックを5~40で上昇
            player.atk += value
            self.chat.sent(f"攻撃力が{value}上昇した！")
            print(f"攻撃力が{value}上昇した！")
            
        elif bonus == "hp_up":
            value = random.randint(10, 20) # HPを10~20で上昇
            player.max_hp += value
            player.hp += value
            self.chat.sent(f"最大HPが{value}上昇した！")
            print(f"最大HPが{value}上昇した！")    

        elif bonus == "heal":
            value = random.randint(10, 20) # HPを10~20回復（上限は超えないように）
            player.hp = min(player.hp + value, player.max_hp)
            self.chat.sent(f"HPを{value}回復した！")
            print(f"HPを{value}回復した！")
            
def draw_game_over(screen, chat, defeated_count):
    # 黒背景
    screen.fill((0, 0, 0))

    font = pg.font.SysFont("meiryo", 80) #ゲームオーバーと記入
    text = font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 100))

    font3 = pg.font.SysFont("meiryo", 40) #倒した数を記入
    text3 = font3.render(f"倒した数: {defeated_count} 体", True, (255, 255, 255))
    screen.blit(text3, (WIDTH//2 - text3.get_width()//2, HEIGHT//2 - 20))

    font2 = pg.font.SysFont("meiryo", 40) #Rスタートを記入
    text2 = font2.render("Rキーで再スタート", True, (255, 255, 255))
    screen.blit(text2, (WIDTH//2 - text2.get_width()//2, HEIGHT//2 + 60))

    pg.display.update()

def main():
    pg.display.set_caption("ゲーム")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"IMG_2090.jpg")
    chat = Chat(screen)
    player = Player(chat)
    enemy = None
    bonus = Bonus(chat)
    scene = "battle_myTurn"
    stage = 0
    screen.blit(bg_img, [0, 0])
    pg.display.update()
    treasureChest = TreasureChest()

    defeated_count = 0

    while True:
        nowKey = None
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_1:
                    nowKey = 1
                elif event.key == pg.K_2:
                    nowKey = 2
                elif event.key == pg.K_3:
                    nowKey = 3
                elif event.key == pg.K_f:
                    nowKey = "f"
                elif event.key == pg.K_t:
                    nowKey = "t"

        if scene == "start":
            continue
        elif scene == "battle_myTurn":
            if enemy is None:
                enemy = Enemy.apper(chat, screen)

            result = player.action(enemy, player.get_command(nowKey))
            screen.blit(enemy.image, [enemy.x, enemy.y])


            if result == "GAMEOVER":
                scene = "finish"   # ゲームオーバー画面へ
                continue

            if player.hp <= 0:
                scene = "finish"
                continue

            if result == "DEFEATED":
                enemy = None
                scene = "finish_battle"
            elif nowKey != None:
                scene = "battle_enemyTurn"
        elif scene == "battle_enemyTurn":
            enemy.action(player)

            if player.hp <= 0:
                scene = "finish"
            else:
                scene = "battle_myTurn"
        elif scene == "finish_battle":
            defeated_count += 1 
            chat.sent(f"これまでに {defeated_count} 体の敵を倒した！")
            bonus.reward(player)
            events = Event(screen, chat)
            scene = "select_action"
        elif scene == "select_action":
            scene = events.select(nowKey)
        elif scene == "treasure_chest":
            events = Event(screen, chat)
            treasureChest.getTreasure(player.atk, player.hp, player.max_hp, chat)
            scene = "select_action"
        elif scene == "finish":
            draw_game_over(screen, chat, defeated_count)

            keys = pg.key.get_pressed()
            if keys[pg.K_r]:
                # ゲームをリセット
                player = Player(chat)
                enemy = None
                defeated_count = 0
                scene = "select_action"
        
        if scene != "finish":
            screen.blit(bg_img, [0, 0])
        if enemy is not None and scene != "finish":
            screen.blit(enemy.image, (enemy.x, enemy.y))
        pg.display.update()

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()

