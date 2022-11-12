import sys
import os
import django

sys.dont_write_bytecode = True
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

import discord
import datetime as dt
from discord.ext import commands
from db.models import DiscordBreakUser
from settings import DISCORD_SECRET_TOKEN


intents = discord.Intents.all()
watching = discord.Game("시간을 엄격하게 측정")
minibot = commands.Bot(
    command_prefix="$$",
    status=discord.Status.online,
    active=watching,
    intents=intents,
)


# 명령어 1회당 10분이 기준
@minibot.command(
    aliases=[
        "휴식",
        "그만",
        "쉬기",
        "쉴래",
        "쉬자",
        "힘들어",
        "좀쉬자",
        "쉬는시간",
        "휴식시작",
        "자리비움",
    ]
)
async def start_break(ctx):
    start = dt.datetime.now()
    mentioned_member = str(ctx.author)[:3]
    if DiscordBreakUser.objects.filter(name=mentioned_member).exists():
        break_member = DiscordBreakUser.objects.get(name=mentioned_member)
        break_member.total_input += 1
        break_member.save()
    else:
        to_register = DiscordBreakUser()
        to_register.total_input = 1
        to_register.save()
    await ctx.send(mentioned_member)


# total_break = models.IntegerField()
# today_break = models.IntegerField()
# total_input = models.IntegerField()
# today_input = models.IntegerField()


@minibot.command(
    aliases=[
        "다시",
        "복귀",
        "일하기",
        "일하자",
        "개발하기",
        "개발하자",
        "그만쉬자",
        "그만쉬기",
    ]
)
async def end_break(ctx):
    end = dt.datetime.now()
    await ctx.send()


minibot.run(DISCORD_SECRET_TOKEN)
