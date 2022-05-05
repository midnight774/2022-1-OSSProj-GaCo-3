# -*-coding:utf-8-*-

import pygame
from settings import *
from support import *
from debug import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, PLAYER_SIZE, groups, obstacle_sprites):
        pygame.sprite.Sprite.__init__(self, groups)
        self.image = pygame.image.load('image/player2/idle.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, PLAYER_SIZE)
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = pygame.Rect(self.rect[0]+7*PLAYER_SIZE[0]/16,self.rect[1]+7*PLAYER_SIZE[1]/16,PLAYER_SIZE[0]/8,PLAYER_SIZE[1]/8) # 아직 하는 일 없음. 충돌 검사 때 사용해야함

        #graphic setup
        self.import_player_assets()
        self.status = 'idle' # 시작은 오른쪽 방향을 보고 서있기
        self.status_num = 0  #0: idle, 1: run, 2: jump, 3: fall, 4: attack, 5: attack2, 6: hitted, 7: death

        # animation 바꿀 때 사용
        self.frame_index = 0
        self.animation_speed = 0.5

        # move(이동)함수, collision(충돌 검사)함수 등에 사용
        # 플레이어의 이동 방향
        self.direction = 0 # 가만히 서 있기 : 0 / 오른쪽 방향으로 이동시 : 1 / 왼쪽 방향으로 이동시 : -1

        # movement
        self.RUNNING_SPEED = 0.4  # 뛸 때 속도 상수
        self.JUMPMOVE_SPEED = 0.3
        self.RUNNINGATTACK_SPEED = 0.2
        self.DASHATTACK_SPEED = 0.8
        self.speed = self.RUNNING_SPEED # 플레이어 생성시, 걷는 속도로 초기화

        # jumping implementation by event.type == KEYDOWN
        self.jumping = False
        self.Jump_power = -1.4
        self.jump_value = self.Jump_power
        self.ground_line = self.hitbox.y

        self.obstacle_sprites = obstacle_sprites

    def import_player_assets(self):
        # 플레이어를 생성할 때 스프라이트 이미지 세트들도 함께 저장한다.
        # 스프라이트 구현할 때 편하게 하기 위해 각 상태의 이름은 이미지 폴더에 실재하는 이름과 같게 바꿨음
        # 더 많은 상태를 추가하고 싶을 경우,
        #   예를들어 'run attack.png' 이미지를 불러오고 싶다면
        #          아래의 self.spr 딕셔너리에
        #               'run attack1':[] 으로 key:item을 추가해준다.
        #          settings.py 에 있는 PLAYER_IMG_INFO 에도
        #                'run attack1': {'idx': 프레임수, 'size': (적절한_사이즈, 적절한_사이즈)} 를 추가로 작성해준다.
        #   어떤 key input이 들어왔을 때 'run attack1' 상태로 만들고싶은지를 고려하여
        #   아래의 input함수에 key 검사를 추가해준다.
        self.spr = {'idle':[], 'idleL':[],
                    'run':[], 'runL':[],
                    'jump':[], 'jumpL':[],
                    'fall':[], 'fallL':[],
                    'attack1':[], 'attack1L':[],
                    'attack2':[], 'attack2L':[],
                    'death':[], 'deathL':[],
                    'hitted':[], 'hittedL':[]
                    }

        for spr_name in self.spr.keys():
            self.spr[spr_name] = import_sprites_image(spr_name +'.png',
                                                      PLAYER_IMG_INFO[spr_name]['idx'],
                                                      PLAYER_IMG_INFO[spr_name]['size'])
            if 'L' in spr_name: #왼쪽방향일 경우 이미지 순서 뒤집어서 정렬해주기 -> 애니메이션 구현할 때 편하게 하려고 뒤집어줌.
                self.spr[spr_name].reverse()

    def input(self):
        ## 현재 눌린 키들의 리스트.
        # 여기에 우리가 검사할 키가 들어있는지 확인하고, 있으면 상태를 변경해줌
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            quit_check(event)
            #정지상태
            if self.status_num==0:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                    self.control(1,'run',0,1,False,self.RUNNING_SPEED)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                    self.control(-1,'runL',0,1,False,self.RUNNING_SPEED)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.status=='idle':
                    self.control(0,'jump',0,2,True,self.JUMPMOVE_SPEED)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.status=='idleL':
                    self.control(0,'jumpL',0,2,True,self.JUMPMOVE_SPEED)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_a and self.status=='idle':
                    self.control(0,'attack1',0,4,False,self.RUNNING_SPEED)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_a and self.status=='idleL':
                    self.control(0,'attack1L',0,4,False,self.RUNNING_SPEED)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_s and self.status=='idle':
                    self.control(0,'attack2',0,5,False,self.RUNNING_SPEED)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_s and self.status=='idleL':
                    self.control(0,'attack2L',0,5,False,self.RUNNING_SPEED)
            #달리기상태
            if self.status_num==1:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT and self.status=='runL':
                    self.control(1,'run',0,1,False,self.RUNNING_SPEED)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT and self.status=='run':
                    self.control(-1,'runL',0,1,False,self.RUNNING_SPEED)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.status=='run':
                    self.control(1,'jump',0,2,True,self.JUMPMOVE_SPEED)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.status=='runL':
                    self.control(-1,'jumpL',0,2,True,self.JUMPMOVE_SPEED)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_a and self.status=='run':
                    self.control(0,'attack1',0,4,False,self.RUNNING_SPEED)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_a and self.status=='runL':
                    self.control(0,'attack1L',0,4,False,self.RUNNING_SPEED)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_s and self.status=='run':
                    self.control(1,'attack2',0,5,False,self.RUNNINGATTACK_SPEED)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_s and self.status=='runL':
                    self.control(-1,'attack2L',0,5,False,self.RUNNINGATTACK_SPEED)
                if event.type == pygame.KEYUP and event.key == pygame.K_RIGHT and self.status=='run':
                    self.control(0,'idle',0,0,False,self.RUNNING_SPEED)
                if event.type == pygame.KEYUP and event.key == pygame.K_LEFT and self.status=='runL':
                    self.control(0,'idleL',0,0,False,self.RUNNING_SPEED)
            #점프상태
            if self.status_num==2:
                if keys[pygame.K_RIGHT]:
                    self.control(1,'jump',0,2,True,self.JUMPMOVE_SPEED)
                if keys[pygame.K_LEFT]:
                    self.control(-1,'jumpL',0,2,True,self.JUMPMOVE_SPEED)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_s and self.status=='jump':
                    self.control(1,'attack2',0,5,True,self.DASHATTACK_SPEED)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_s and self.status=='jumpL':
                    self.control(-1,'attack2L',0,5,True,self.DASHATTACK_SPEED)
            #떨어지는상태
            if self.status_num==3:
                if keys[pygame.K_RIGHT]:
                    self.control(1,'fall',0,3,True,self.JUMPMOVE_SPEED)
                if keys[pygame.K_LEFT]:
                    self.control(-1,'fallL',0,3,True,self.JUMPMOVE_SPEED)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_s and self.status=='fall':
                    self.control(1,'attack2',0,5,True,self.DASHATTACK_SPEED)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_s and self.status=='fallL':
                    self.control(-1,'attack2L',0,5,True,self.DASHATTACK_SPEED)
            
        #공격1상태, 공격2상태(각각 프레임이 일정수치에 가면 다음 상태로 넘어가도록 해줌)
        self.attack()
        #hitbox, attackbox
        
    #각종 상태 컨트롤해주는 함수
    def control(self, direction, status, index, num, isjumping, speed):
        self.direction = direction
        self.status = status
        self.frame_index = index
        self.status_num = num
        self.jumping = isjumping
        self.speed = speed

    def move(self,df):
        # 나중에 플레이어와 사물이 부딪힐 때를 대비해 player.rect 자체가 아니라 좀 더 작은 충돌 범위(hitbox)를 검사한다.
        self.hitbox.x += self.direction * self.speed * df

        # # 플레이어가 지정된 화면 밖으로 벗어나지 못하게 함.
        # # 카메라 구현 과정에서 이대로 둘 것인지 obstacle 그룹을 만들어서 경계를 관리할 것인지 결정할 필요가 있음
        if self.hitbox.x < 0:
            self.hitbox.x = 0
        if self.hitbox.x > 3200: # 바닥 이미지 크기 설정할 때 함께 바꿔주던가 해야함
            self.hitbox.x = 3200

        if self.jumping:
            self.jump(df)

        # 충돌 검사 (현재 : 왼쪽 오른쪽 벽에 대해서 대충 구현)
        self.collision('horizontal')
    
    def attack(self):
        if self.status_num == 4:
            if self.frame_index == 6:
                if self.status == 'attack1':
                    self.control(0,'idle',0,0,False,self.RUNNING_SPEED)
                if self.status == 'attack1L':
                    self.control(0,'idleL',0,0,False,self.RUNNING_SPEED)
        if self.status_num == 5:
            if self.frame_index == 6:
                if self.status == 'attack2':
                    self.control(0,'idle',0,0,False,self.RUNNING_SPEED)
                if self.status == 'attack2L':
                    self.control(0,'idleL',0,0,False,self.RUNNING_SPEED)

    def jump(self,df):
        # 점프할 때의 y값 변경
        self.hitbox.y += self.jump_value*df
        self.jump_value += 0.004*df
        if self.status == 'jump':
            if self.jump_value >= 0:
                self.status_num = 3
                self.status = 'fall'
        if self.status == 'jumpL':
            if self.jump_value >= 0:
                self.status_num = 3
                self.status = 'fallL'
        if self.jump_value > 15:
            self.jump_value = 15

        #점프에서 착지
        keys = pygame.key.get_pressed()
        if self.hitbox.y >= self.ground_line:
            self.jumping = False
            self.hitbox.y = self.ground_line
            self.jump_value = self.Jump_power
            self.speed = self.RUNNING_SPEED
            if self.direction == 0:
                if self.status == 'fall':
                    self.control(0,'idle',0,0,False,self.RUNNING_SPEED)
                if self.status == 'fallL':
                    self.control(0,'idleL',0,0,False,self.RUNNING_SPEED)
            else:
                if self.status == 'fall' and keys[pygame.K_RIGHT]:
                    self.control(1,'run',0,1,False,self.RUNNING_SPEED)
                elif self.status == 'fall' and not keys[pygame.K_RIGHT]:
                    self.control(0,'idle',0,0,False,self.RUNNING_SPEED)
                elif self.status == 'fallL' and keys[pygame.K_LEFT]:
                    self.control(-1,'runL',0,1,False,self.RUNNING_SPEED)
                elif self.status == 'fallL' and not keys[pygame.K_LEFT]:
                    self.control(0,'idleL',0,0,False,self.RUNNING_SPEED)

    def animate(self,df):
        # 플레이어 생성시 준비한 spr 딕셔너리에서
        # self.status에 맞는 스프라이트 세트를 가져온다.
        spr = self.spr[self.status]
        #0: idle, 1: run, 2: jump, 3: fall, 4: attack, 5: attack2, 6: hitted, 7: death
        # 기본적으로 0.33이나, 플레이어가 뛰어가는 동작을 하면 이미지를 더 빠르게 바꾸기 위해 speed를 높게 설정한다.
        if self.status_num==0:
            self.animation_speed = 0.01
        if self.status_num==1:
            self.animation_speed = 0.008
        if self.status_num==2:
            self.animation_speed = 0.01
        if self.status_num==3:
            self.animation_speed = 0.01
        if self.status_num==4:
            self.animation_speed = 0.015
        if self.status_num==5:
            self.animation_speed = 0.007
        if self.status_num==6:
            self.animation_speed = 0.01
        
        # loop over the frame index
        self.frame_index += self.animation_speed*df
        if self.frame_index >= len(spr) and (self.status != 'jump' and self.status != 'jumpL'): # 스프라이트 마지막 이미지까지 보여준 뒤
            self.frame_index = 0 # 다시 처음 이미지로 돌아가기
            
        # once frame index
        if self.frame_index >= len(spr)-1 and (self.status == 'jump' or self.status == 'jumpL' or self.status == 'attack1' or self.status == 'attack1L'
                                              or self.status == 'attack2' or self.status == 'attack2L'): # 스프라이트 마지막 이미지까지 보여준 뒤
            self.frame_index = len(spr)-1 #  마지막 프레임에서 고정

        # 위의 프레임 인덱스에 따라 플레이어 이미지를 바꿔줌
        self.image = spr[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)

    def collision(self, direction):
        # 파이게임은 충돌시에 아래 위 어느 방향에서 충돌했는지 알려주지 않음
        # 따라서 direction값으로 어느 방향으로 충돌검사 할 것인지를 인자로 받고
        # 만약 horizontal이면,
        #   self.direction이 0보다 클 때는 오른쪽으로 움직이다 충돌한 것이므로
        #       self.hitbox의 오른쪽과 방해물의 왼쪽 충돌검사를 한다.
        #   self.direction이 0보다 작을 때는, 왼쪽으로 움직이다 충돌한 것이므로
        #       self.hitbox의 왼쪽과 방해물의 왼쪽 충돌검사를 한다.
        # 충돌할 경우, 방해물을 통과하여 지나가지 못하도록 self.hitbox의 위치를 조정한다.
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: #collision occurs while moving right
                        self.hitbox.right = sprite.hitbox.left
                    elif self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right

    def weve_value(self):
        # 7시간 강의에서 나왔던 함수
        # 이미지의 투명도를 시간에 따라 조절하여 이미지가 깜빡거리도록 할 수 있음
        # 플레이어가 공격받거나 약해지거나 죽을 때 사용할 수 있을 듯함.
        # 현재 코드에서는 사용하고 있지 않음
        value = sin(pygame.time.get_ticks())
        if value >= 0:
            return 255
        else:
            return 0

    def update(self,df):
        self.input()
        self.move(df)
        self.animate(df)