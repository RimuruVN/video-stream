import os
from os import getenv
from dotenv import load_dotenv

if os.path.exists("local.env"):
    load_dotenv("local.env")

load_dotenv()
admins = {}
SESSION_NAME = getenv("SESSION_NAME", "session")
BOT_TOKEN = getenv("BOT_TOKEN")
BOT_NAME = getenv("BOT_NAME", "Video Stream")
API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
OWNER_NAME = getenv("OWNER_NAME", "gimsuri")
ALIVE_NAME = getenv("ALIVE_NAME", "Levina")
BOT_USERNAME = getenv("BOT_USERNAME", "veezvideobot")
ASSISTANT_NAME = getenv("ASSISTANT_NAME", "cleo_invida")
GROUP_SUPPORT = getenv("GROUP_SUPPORT", "owohub")
UPDATES_CHANNEL = getenv("UPDATES_CHANNEL", "kenhsex")
SUDO_USERS = list(map(int, getenv("SUDO_USERS").split()))
COMMAND_PREFIXES = list(getenv("COMMAND_PREFIXES", "/ ! ,").split())
ALIVE_IMG = getenv("ALIVE_IMG", "https://media.sproutsocial.com/uploads/2015/04/Meercat_Periscope_Ways-to-Use-01.png")
DURATION_LIMIT = int(getenv("DURATION_LIMIT", "200"))
IMG_1 = getenv("IMG_1", "https://www.dacast.com/static/1ea34a502783c0aaf5a5c2cf915526c9/99143/Live-Streaming-Solutions.jpg")
IMG_2 = getenv("IMG_2", "https://vitinhmiennam.com/upload/images/Live-stream-video.jpg")
IMG_3 = getenv("IMG_3", "https://i1.wp.com/buildingjerusalem.blog/wp-content/uploads/2020/04/livestream.jpg")
IMG_4 = getenv("IMG_4", "https://freshproductions.co.uk/wp-content/uploads/elementor/thumbs/Copy-of-Live-stream-social--e1585905617827-p4scltfv14j0ghq6yqfzfkms2tyi77tuugb2jdbsxc.png")
