import asyncio

import pygame
import random
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.utils.markdown import *
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import filters

size = (750, 750)
pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Color game")
clock = pygame.time.Clock()

bot = Bot(token="5644768745:AAGOrfSr-ZI62Dylu6PXVgp4IBXBDFEf70U")
dp = Dispatcher(bot)

color = "red"

kb_main = InlineKeyboardMarkup()
kb_main.row(InlineKeyboardButton(text="left", callback_data="left"),
            InlineKeyboardButton(text="right", callback_data="right"),
            InlineKeyboardButton(text="up", callback_data="up"),
            InlineKeyboardButton(text="down", callback_data="down"))

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = pygame.image.load(
            "player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(
            center=(x, 0))
        self.rect.x = x
        self.rect.y = y

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, image, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = pygame.image.load(
            image).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(
            center=(x, 0))
        self.rect.x = x
        self.rect.y = y

player = Player(20, 20, (100, 100))
wall1 = Obstacle(150, 200, "brickwall.jpg", (100, 100))

background = pygame.image.load(
            "background.png")
background = pygame.transform.scale(background, (size[0], size[1]))

win = pygame.image.load(
            "win.jpg")
win = pygame.transform.scale(win, (size[0], size[1]))

dumpling = pygame.image.load(
            "dumpling.png")
dumpling = pygame.transform.scale(dumpling, (100, 100))
dumpling_rect = dumpling.get_rect()
dumpling_rect.x = 200
dumpling_rect.y = 50

dumplings = 0

is_win = False

speed = 50

def check_wall(obstacle, side):
    if side == "up":
        if (player.rect.y - speed < obstacle.rect.y + obstacle.size[1]) \
                and (player.rect.y + player.size[1] > obstacle.rect.y):
            if (player.rect.x < obstacle.rect.x + obstacle.size[0]) \
                    and (player.rect.x + player.size[0] > obstacle.rect.x):
                player.rect.y = obstacle.rect.y + obstacle.size[1]
                return False
            else:
                return True
        else:
            return True
    if side == "right":
        if (player.rect.x + player.size[0] + speed > obstacle.rect.x) \
                and (player.rect.x < obstacle.rect.x + obstacle.size[0]):
            if (player.rect.y + player.size[1] > obstacle.rect.y) \
                    and (player.rect.y < obstacle.rect.y + obstacle.size[1]):
                player.rect.x = obstacle.rect.x - player.size[0]
                return False
            else:
                return True
        else:
            return True
    if side == "left":
        if (player.rect.x + player.size[0] > obstacle.rect.x) \
                and (player.rect.x < obstacle.rect.x + obstacle.size[0] + speed):
            if (player.rect.y + player.size[1] > obstacle.rect.y) \
                    and (player.rect.y < obstacle.rect.y + obstacle.size[1]):
                player.rect.x = obstacle.rect.x + obstacle.size[0]
                return False
            else:
                return True
        else:
            return True
    if side == "down":
        if (player.rect.y + player.size[1] + speed > obstacle.rect.y) and \
                (player.rect.y < obstacle.rect.y + obstacle.size[1]):
            if (player.rect.x < obstacle.rect.x + obstacle.size[0]) \
                    and (player.rect.x + player.size[0] > obstacle.rect.x):
                player.rect.y = obstacle.rect.y - player.size[1]
                return False
            else:
                return True
        else:
            return True

@dp.message_handler(commands=["play"])
async def start(message: types.Message):
    global is_win
    dumplings = 0
    is_win = False
    await update(message, "draw")

game_message = types.Message
game_message_id = 0

async def update(message, mode):
    global game_message, game_message_id, dumplings, is_win
    if is_win:
        return
    if mode == "loop" and game_message_id == 0:
        return
    screen.blit(background, (0,0))
    screen.blit(wall1.image, wall1.rect)
    screen.blit(player.image, player.rect)

    if player.rect.colliderect(dumpling_rect):
        dumplings += 1
        dumpling_rect.x = random.randint(100, 650)
        dumpling_rect.y = random.randint(100, 650)
        if dumplings >= 1:
            is_win = True
            screen.blit(win, (0,0))

    screen.blit(dumpling, dumpling_rect)
    pygame.display.flip()
    pygame.image.save(screen, "screenshot.jpeg")
    if mode == "draw":
        file_path = "screenshot.jpeg"
        file = types.InputFile(file_path)
        game_message = await bot.send_photo(message.chat.id,
                         photo=file, reply_markup=kb_main)
        game_message_id = game_message["message_id"]

    elif game_message_id != 0 and mode == "update":
        file_path = "screenshot.jpeg"
        file = types.InputMedia(media=types.InputFile(file_path),
                                caption=f"Пока вы собрали {dumplings} пельмешек!")
        await bot.edit_message_media(chat_id=message.message.chat.id,
                                    message_id=message.message.message_id,
                                    media = file,
                                    reply_markup = kb_main)
    elif game_message_id != 0 and mode == "loop":
        file_path = "screenshot.jpeg"
        file = types.InputMedia(media=types.InputFile(file_path),
                                caption=f"Пока вы собрали {dumplings} пельмешек!")
        await bot.edit_message_media(chat_id=message.chat.id,
                                    message_id=message.message_id,
                                    media = file,
                                    reply_markup = kb_main)

@dp.callback_query_handler(lambda c: c.data == 'up')
async def process_callback_button_right(callback_query: types.CallbackQuery):
    if check_wall(wall1, "up"):
        player.rect.y -= speed
    await update(callback_query, "update")

@dp.callback_query_handler(lambda c: c.data == 'right')
async def process_callback_button_right(callback_query: types.CallbackQuery):
    if check_wall(wall1, "right"):
        player.rect.x += speed
    await update(callback_query, "update")

@dp.callback_query_handler(lambda c: c.data == 'left')
async def process_callback_button_right(callback_query: types.CallbackQuery):
    if check_wall(wall1, "left"):
        player.rect.x -= speed
    await update(callback_query, "update")

@dp.callback_query_handler(lambda c: c.data == 'down')
async def process_callback_button_right(callback_query: types.CallbackQuery):
    if check_wall(wall1, "down"):
        player.rect.y += speed
    await update(callback_query, "update")

async def change_dampling_position():
    dumpling_rect.x = random.randint(100, 650)
    dumpling_rect.y = random.randint(100, 650)
    await update(game_message, "loop")

executor.start_polling(dp, skip_updates=True)

