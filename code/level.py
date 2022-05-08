#-*-coding:utf-8-*-

import random
import pygame
from settings import *
from support import *
from player import *
from Bringer import *
from random import choice
from debug import *

class Level:
    def __init__(self):
        # game state for scene transition
        self.game_state = 'intro' # intro 부터 시작
        self.level_start_time = None

        #get the display surface
        self.display_surface = pygame.display.get_surface()

        #sprite group setup
        self.visible_sprites = CameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        #sprite setup
        self.create_map()

    def create_map(self):
        # player 생성
        self.player = Player(PLAYER_COOR_ini, PLAYER_SIZE, [self.visible_sprites], self.obstacle_sprites)
        # monster 생성
        self.monster = Bringer(BRINGER_COOR_ini, BRINGER_SIZE, [self.visible_sprites], self.obstacle_sprites)


    def run(self,df):
        # self.game_state 에 따라 장면이 전환됨

        if self.game_state == 'intro': # 마우스 클릭시 레벨1로
            self.intro()

        if self.game_state == 'level1': # 일정 시간 지난 뒤 레벨2로
            self.level1(df)

        if self.game_state == 'level2': # 일정 시간 지난 뒤 레벨3으로
            self.level2(df)

        if self.game_state == 'level3': # 일정 시간 지난 뒤 엔딩으로
            self.level3(df)

        if self.game_state == 'ending': # 일정 시간 지난 뒤 엔딩으로
            self.ending()

    def intro(self):
        self.display_surface.fill((0, 0, 0))
        debug('intro', WIDTH//2, HEIGHT//2)
        for event in pygame.event.get():
            quit_check(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.level_start_time = pygame.time.get_ticks()
                self.game_state = 'level1'

        pygame.display.flip()

    def level1(self, df): #몬스터1
        self.visible_sprites.custom_draw(self.player)
        self.player.update(df)
        self.monster.update(df)

        debug('level1', WIDTH // 2, HEIGHT // 2)

        # 몬스터 상호작용 때 수정해야 함
        current_time = pygame.time.get_ticks()
        if current_time - self.level_start_time > 1500:
            # 플레이어 위치 초기화
            self.player.set_pos(PLAYER_COOR_ini)
            self.game_state = 'level2'

        pygame.display.flip()

    def level2(self, df): #몬스터2
        self.visible_sprites.custom_draw(self.player)
        self.player.update(df)
        self.monster.update(df) # 몬스터 객체 새로 만드는 코드 필요

        debug('level2', WIDTH // 2, HEIGHT // 2)

        # 몬스터 상호작용 때 수정해야 함
        current_time = pygame.time.get_ticks()
        if current_time - self.level_start_time > 3000:
            # 플레이어 위치 초기화
            self.player.set_pos(PLAYER_COOR_ini)
            self.game_state = 'level3'

        pygame.display.flip()

    def level3(self, df): #몬스터3
        self.visible_sprites.custom_draw(self.player)
        self.player.update(df)
        self.monster.update(df) #마찬가지로 몬스터 객체 새로 만드는 코드 필요

        debug('level3', WIDTH // 2, HEIGHT // 2)

        current_time = pygame.time.get_ticks()
        if current_time - self.level_start_time > 4500:
            # 플레이어 위치 초기화
            self.player.set_pos(PLAYER_COOR_ini)
            self.game_state = 'ending'

        # 몬스터 상호작용 때 수정해야 함
        # for event in pygame.event.get():
        #     quit_check(event)
        #     if event.type == pygame.MOUSEBUTTONDOWN:
        #          self.game_state = 'ending'
        pygame.display.flip()

    def ending(self):
        self.display_surface.fill((0, 0, 0))
        debug('ending', WIDTH // 2, HEIGHT // 2)

        for event in pygame.event.get():
            quit_check(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                 self.game_state = 'intro'
        pygame.display.flip()

class CameraGroup(pygame.sprite.Group): # for level1, level2, level3
    def __init__(self):
        # general settings
        super(CameraGroup, self).__init__()
        self.display_surface = pygame.display.get_surface()

        # for camera
        self.half_width = self.display_surface.get_width() // 2 # x 포지션에 사용할 화면 크기
        self.half_height = self.display_surface.get_height() // 2 # 층 만들면 그때 사용할 예정

        # 오프셋 세팅
        self.offset = [0, 0]

        # 오프셋 변경 기준 x점
        self.left_x_point = 640 # 이 오프셋 포인트 기준으로 플레이어가 오른쪽으로 향하면 그 후로는 플레이어가 화면 중심에 있음
        self.right_x_point = 1850 # 이 오프셋 포인트 기준으로 플레이어가 왼쪽으로 향하면 그 후로는 플레이어가 화면 중심에 있음
        # 위의 포인트 사이에 있을 경우 플레이어는 항상 화면 가운데에 있지만
        # left 포인트보다 왼쪽에 있을 경우에는 오프셋은 left_x_point가 기준이된다. 반대의 경우도 마찬가지다. # custom_draw의 해당 코드에 또 주석 달아놓았음

        #creating the floor s
        self.background_mountain_surf = pygame.image.load('image/map/background.png')
        self.background_mountain_surf = pygame.transform.scale(self.background_mountain_surf, (1900, 720))
        self.background_mountain_rect = self.background_mountain_surf.get_rect(topleft=(0,0))

        self.background_floor_surf = pygame.image.load('image/map/new_floor.png')
        self.background_floor_surf = pygame.transform.scale(self.background_floor_surf, (2500, 800)) # 화면 변화 속도가 달라서 바닥만 대충 크게 리사이즈함. 이미지 리소스 바꾸면 값 바꿀 것
        self.background_floor_rect = self.background_floor_surf.get_rect(topleft=(0,0))

    def custom_draw(self, player):
        # offset setting
        if player.hitbox.centerx <= self.left_x_point: # 시작 화면으로부터 left_x_point 범위에 플레이어가 있을 때는 카메라 이동 없음
            self.offset[0] = self.left_x_point - self.half_width
        elif player.hitbox.centerx >= self.right_x_point: # right_x_point 부터 끝 장면까지 범위에 플레이어가 있을 때는 카메라 이동 없음
            self.offset[0] = self.right_x_point - self.half_width
        else: # left_x_point ~ right_x_point 사이에 플레이어가 있을 때는 플레이어가 중심에 있을 수 있도록 카메라를 이동시킴
            self.offset[0] = player.hitbox.centerx - self.half_width

        # 멀리 있는 물체가 더 느리게 변화하고 바닥 물체가 더 빠르게 변화하므로 바닥이 멀리 있는 물체보다 이미지 사이즈가 커야함.
        floor_offset_pos = sub_Coordinate(self.background_floor_rect.topleft, self.offset)
        sky_offset_pos = sub_Coordinate(self.background_mountain_rect.topleft, self.offset)
        sky_offset_pos[0] *= 0.3 # 멀리있는 하늘은 x포지션의 변화 속도를 가까이있는 바닥보다 느리게 만들기

        self.display_surface.blit(self.background_mountain_surf, sky_offset_pos)
        self.display_surface.blit(self.background_floor_surf, add_Coordinate(floor_offset_pos, (0, -80)))

        # 플레이어 히트박스 그리기
        pygame.draw.rect(self.display_surface, (255, 255, 255),
                         sub_Coordinate(player.hitbox, (self.offset[0], self.offset[1],
                                                        0, 0)), 3)

        for sprite in sorted(self.sprites(), key= lambda sprite: sprite.rect.centery):
            offset_position = sub_Coordinate(sprite.rect.topleft, self.offset)
            self.display_surface.blit(sprite.image, offset_position)