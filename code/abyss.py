from random import getstate
import pygame
from settings import *
from support import *
from game import *
from Monster import *
from level import *
from debug import *

class Abyss(Monster):
    def __init__(self, pos, MONSTER_SIZE, groups, obstacle_sprites):
        self.image = pygame.image.load('image/Monster/abyss/idleL.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, MONSTER_SIZE)

        super().__init__(pos, MONSTER_SIZE, groups, obstacle_sprites)
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-200, -200) # rect를 양옆, 위아래 방향으로 100씩 줄임
        self.OffsetX = self.scale[0] / 4 #??????????????????????????????????????????
        self.look_direction = -1

        # 공격
        self.targetPos = 200.0 # 맨 처음에 플레이어 위치를 타겟으로 설정하는 건가?
        self.attackBox = pygame.Rect(self.rect[0] , self.rect[1], self.scale[0]/2, self.scale[1])
        # 아직 어비스 주문 마법을 생성하지 않았으므로 브링어의 주문을 일단 생성
        self.spell = BringerSpell((-500, -500), BRINGER_SPELL_SIZE, groups, self.obstacle_sprites)
        self.isAttack = False
        self.isDead = False

        self.AttackPower = 40 # 공격력
        self.hp = ABYSS_HP # 체력
        self.hittedTime = 0 # 무적 시간

        # 죽은 상태 판별
        self.is_death = False

    def spellON(self): # 얘는 하는 일이 너무 적음. 수정 필요할 듯
        self.spell.ON(self.targetPos)

    def import_monster_assets(self):
        self.spr = {'idleL':[], 'idleR':[],
                    'runL':[], 'runR':[],
                    'attack1L':[], 'attack1R':[], #어비스 이미지 이름은 attack1L, attack1R 로 되어있음. 이거 수정하면 됨
                    'deathL':[], 'deathR':[],
                    'hurtL':[], 'hurtR':[]}

        super(Abyss, self).import_monster_assets('image/Monster/abyss/', ABYSS_IMG_INFO, 'L')

    def animate(self, df):
        dt = df

        #피격 모션인 경우 애니메이션이 느리게 재생되도록 줄어든 델타타임을 인자로 넘김
        if 'hurt' in self.status:
            dt /= 2.0

            if self.frame_index == len(self.spr['hurtL'])-1:
                self.status = 'idleL' if 'L' in self.status else 'idleR'
                # 플레이어 어택박스가 사라지지 않고 몬스터를 계속 공격하는 현상 발견.
                # 플레이어 어택박스 위치가 바뀌면 hurt상태를 벗어남. -> colission check 방식을 바꿔야하나?
                # 일단은 hurt 마지막 프레임에서 플레이어 어택박스 위치를 임의로 화변 밖으로 위치시켜서 해당 현상 해결
                self.playerAttackbox.x = - 50

        super().animate(dt)

        spr = self.spr[self.status]
        if 'death' in self.status and self.animation_end:
            #임시적 조치로 죽음 모션의 마지막 프레임일 경우 화면 밖으로 내보낸다.
            self.kill()
            self.hitbox.x = 90000
            return

    def AI(self, df):
        # 플레이어 hitbox의 x 좌표 : self.targetPosp
        # 플레이어와 몬스터의 x좌표 거리가 200이상일 경우, 플레이어 쪽으로 몬스터를 이동시킨다.
        distanceX = self.getHitBox().x - self.targetPos # 0보다 크면 플레이어가 왼쪽에 있음, 0보다 작으면 플레이어가 오른쪽에 있음
        if abs(distanceX) > 200: # 플레이어와의 거리가 200 이상일 경우에, 플레이어 쪽으로 움직이기.
            if distanceX > 0: # 플레이어가 왼쪽에 있으면
                self.status = 'runL' # 왼쪽으로 움직이는 상태로 변경
                self.direction = -1 # 움직일 때 x값이 작아질 수 있게.
                self.look_direction = -1

            else: # 플레이어가 오른쪽에 있으면
                self.status = 'runR' # 오른쪽으로 움직이는 상태로 변경
                self.direction = 1 # 움직일 때 x값이 커질 수 있게.
                self.look_direction = 1

    def move(self):
        if 'run' in self.status:
            self.hitbox.x += self.direction * self.speed

        if self.hitbox.x < 0:
            self.hitbox.x = 0

        self.collision('horizontal')

    def update(self, df):
        self.AI(df)
        self.animate(df)
        self.get_status()
        self.move()

        # 어택 박스 정보 갱신 -> 하는 일이 뭐지..? attack_hitbox...?
        attack_hitbox = sub_Coordinate(self.attackBox, (self.CameraOffset[0], self.CameraOffset[1], 0, 0)) # 이 계산을 왜 여기서 하지?

        # attack animation notify
        # 애니메이션 프레임에 따라서, 스프라이트의 몇 번째 그림에 정확히 공격 이미지가 생성되고 사라지는지를
        # 공격시 어택박스 생성, isAttack 시그널로 사용하기.
        if 'attack' in self.status:
            if (self.frame_index < 7 and self.frame_index > 3): # 어비스 공격 스프라이트의 4, 5, 6 에 공격 이미지 있음
                pygame.draw.rect(self.display_surface, (255, 0, 0), attack_hitbox, 3) # 빨간 색으로 그림
                self.isAttack = True
            else:
                self.isAttack = False

        # 브링어는 spell 공격 전, 준비된 행동이 있음(cast). 하지만 어비스는 일단 없음.
        # elif 'cast' in self.status and self.animation_end:
        #     self.spellON()

        # -> 어비스에서 attack을 해줄 때 self.spellON() 해줘야함.

        self.spell.CameraOffset = self.CameraOffset
        self.spell.update(df)

        # 충돌
        # 플레이어 어택박스, 몬스터 히트박스 충돌시
        if collision_check(self.playerAttackbox, self.getHitBox()) and self.playerAttackbox and self.hittedTime < 0:
            self.hp -= self.playerPower
            self.hittedTime = 0.5 # ?

            if not 'attack' in self.status:
                self.status = 'hurtR' if self.look_direction == 1 else 'hurtL'

            if self.hp <= 0: # 몬스터 피가 0이하가 되면 죽음 상태로 변경
                self.status = 'deathR' if self.look_direction == 1 else 'deathL'
                self.is_death = True

        # 데미지 사이 시간
        self.hittedTime -= df/1000.0

    # scene.py > level_update() 에서 player.hitbox의 x좌표 값을 받아옴.
    # 플레이어를 따라다닐 때 사용할 것.
    def setTargetPos(self, posX):
        self.targetPos = posX

    def getHitBox(self):
        return self.hitbox

    def getAttackBox(self):
        return self.attackBox # self.attackbox 는 안 쓰는 건가보네

    def getSpellAttackBox(self):
        return self.spell.getHitBox()