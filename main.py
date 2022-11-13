import sys
import os
import django

sys.dont_write_bytecode = True
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

import random
import discord
from pytz import timezone
from datetime import datetime
from discord.ext import commands
from db.models import UsersOnBreak
from asgiref.sync import sync_to_async
from settings import DISCORD_SECRET_TOKEN

KST = timezone("Asia/Seoul")

intents = discord.Intents.all()
watching = discord.Game("시간을 엄격하게 측정")
minibot = commands.Bot(
    command_prefix="##",
    status=discord.Status.online,
    active=watching,
    intents=intents,
)


@minibot.command(
    aliases=[
        "디버그",
    ]
)
async def debug(ctx):
    d_today = datetime.now()
    d_today = d_today.astimezone(KST)
    await ctx.send(
        f"서버 : {ctx.guild.region}\n서버 인원 : {ctx.guild.member_count}\n지연 시간 : {round(round(minibot.latency, 4)*1000)}ms\n현재시각 1 : {datetime.today()}\n현재시각 2 : {d_today}"
    )


@minibot.command(
    aliases=[
        "인사",
    ]
)
async def hello(ctx):
    random_number = str(random.randint(1, 3))
    random_greeting = {
        "1": f"{ctx.author.mention}님 반가워요!",
        "2": f"{ctx.author.mention}님 안녕하세요!",
        "3": f"꽤 보고싶었어요! {ctx.author.mention}!",
    }
    await ctx.send(random_greeting[random_number])


@minibot.command(
    aliases=[
        "메롱",
        "바보",
        "바보야",
        "멍청이",
    ]
)
async def babo(ctx):
    random_number = str(random.randint(1, 6))

    random_say = {
        "1": f"{ctx.author.mention}은(는) 바보래요!",
        "2": "인간 시대의 끝이 도래했다~~!",
        "3": "메롱",
        "4": "무슨 소리인지 모르겠어요!",
        "5": "¯\_(ツ)_/¯",
        "6": "메에에~~~!",
    }
    await ctx.send(random_say[random_number])


@minibot.command(
    aliases=[
        "뽑기",
        "도박",
        "가챠",
        "dice",
        "주사위",
        "random",
    ]
)
async def roll(ctx):
    await ctx.send(
        f"{ctx.author.mention}님은 [1 ~ 100] 의 숫자 중 {random.randint(1, 100)}이(가) 나왔습니다."
    )


@minibot.command(
    aliases=[
        "등록",
        "재등록",
    ]
)
async def register(ctx):
    mentioned_user_name = ctx.author.name
    mentioned_user_nickname = ctx.author.nick
    mentioned_user_discriminator = ctx.author.discriminator

    if await UsersOnBreak.objects.async_filter(
        discriminator=mentioned_user_discriminator
    ):
        already_user = await UsersOnBreak.objects.async_get(
            discriminator=mentioned_user_discriminator
        )
        if (
            already_user.name != mentioned_user_name
            or already_user.nickname != mentioned_user_nickname
        ):
            old_name = already_user.name
            old_nickname = already_user.nickname
            already_user.name = mentioned_user_name
            already_user.nickname = (
                mentioned_user_nickname
                if mentioned_user_nickname
                else mentioned_user_name
            )
            if already_user.is_resting:
                register_today = datetime.now()
                register_today = register_today.astimezone(KST)
                register_total_break_time = register_today - already_user.updated_at
                register_total_break_time = int(
                    register_total_break_time.total_seconds() // 60
                )
                already_user.remaining_rest_time -= register_total_break_time
            await sync_to_async(already_user.save)()
            notice_change_nickname = (
                mentioned_user_nickname if mentioned_user_nickname else "없음"
            )
            await ctx.send(
                f"{ctx.author.mention} : 갱신되었습니다.\n이름 변경 {old_name} >>> {mentioned_user_name}\n닉네임 변경 {old_nickname} >>> {notice_change_nickname}"
            )
        else:
            await ctx.send(f"{ctx.author.mention} : 이미 등록된 유저입니다.")
    else:
        to_register = UsersOnBreak()
        to_register.name = mentioned_user_name
        to_register.nickname = (
            mentioned_user_nickname if mentioned_user_nickname else mentioned_user_name
        )
        to_register.discriminator = mentioned_user_discriminator
        to_register.total_input = 0
        to_register.today_input = 0
        to_register.total_break = 0
        to_register.today_break = 0
        to_register.is_resting = False
        to_register.remaining_rest_time = 70
        await sync_to_async(to_register.save)()
        await ctx.send(
            f"{ctx.author.mention} : 등록되었습니다.\n{ctx.author.mention} 님의 현재 잔여 휴식시간 : {to_register.remaining_rest_time} 분"
        )


# 모든 유저 정보


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
    start_today = datetime.now()
    start_today = start_today.astimezone(KST)
    ampm = "오전" if start_today.strftime("%p") == "AM" else "오후"
    start_pretty_now = start_today.strftime(f"%Y-%m-%d   {ampm} %I:%m:%S")

    mentioned_user_name = ctx.author.name
    mentioned_user_discriminator = ctx.author.discriminator

    if await UsersOnBreak.objects.async_filter(
        name=mentioned_user_name, discriminator=mentioned_user_discriminator
    ):
        break_user = await UsersOnBreak.objects.async_get(
            name=mentioned_user_name, discriminator=mentioned_user_discriminator
        )
        if break_user.is_resting:
            await ctx.send(f"{ctx.author.mention} 이미 휴식중인 유저입니다.")
        else:
            if break_user.updated_at.strftime("%Y-%m-%d") == start_today.strftime(
                "%Y-%m-%d"
            ):
                break_user.today_input += 1
            else:
                break_user.today_break = 0
                break_user.today_input = 1
                break_user.remaining_rest_time = 70
            break_user.total_input += 1
            break_user.is_resting = True
            await sync_to_async(break_user.save)()
            await ctx.send(f"{ctx.author.mention} 님의 휴식 시작시간 : {start_pretty_now}")
    else:
        await ctx.send(
            f'{ctx.author.mention} : 등록되지 않은 사용자입니다.\n먼저 "##등록" 명령어로 등록해주세요!\n만약 이름이나 별명이 변경되었다면 "##재등록" 으로 재등록 해주세요!'
        )


@minibot.command(
    aliases=[
        "끝",
        "종료",
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
    end_today = datetime.now()
    end_today = end_today.astimezone(KST)
    ampm = "오전" if end_today.strftime("%p") == "AM" else "오후"
    end_pretty_now = end_today.strftime(f"%Y-%m-%d   {ampm} %I:%m:%S")

    mentioned_user_name = ctx.author.name
    mentioned_user_discriminator = ctx.author.discriminator

    if await UsersOnBreak.objects.async_filter(
        name=mentioned_user_name, discriminator=mentioned_user_discriminator
    ):
        break_user = await UsersOnBreak.objects.async_get(
            name=mentioned_user_name, discriminator=mentioned_user_discriminator
        )
        if break_user.is_resting:
            end_total_break_time = end_today - break_user.updated_at
            end_total_break_time = int(end_total_break_time.total_seconds() // 60)
            break_user.today_break += end_total_break_time
            break_user.total_break += end_total_break_time
            break_user.is_resting = False
            break_user.remaining_rest_time -= end_total_break_time
            await sync_to_async(break_user.save)()
            await ctx.send(
                f"{ctx.author.mention} 님의 휴식 종료시간 : {end_pretty_now}\n{ctx.author.mention} 님은 이번 휴식때 {end_total_break_time} 분 휴식하셨습니다."
            )
        else:
            await ctx.send(f"{ctx.author.mention} 이미 작업중인 유저입니다.")
    else:
        await ctx.send(f"{ctx.author.mention} 님은 아직 휴식을 시작하지 않으셨습니다.")


all_users = {}
rescan_user_set = {}


@minibot.command(
    aliases=[
        "상태",
        "지금",
        "현재",
        "누구",
        "검색",
    ]
)
async def user_state(ctx, *nickname):
    nickname = " ".join(nickname)
    if nickname == "모두" or nickname == "all":
        ebd = discord.Embed(title="휴식이", description="휴식시간 알려주는 봇", color=0xFFA07A)
        users = await UsersOnBreak.objects.async_all()
        i = 1
        for user in users:
            now_state = "쉬고 있음" if user.is_resting else "작업 중"
            ampm = "오전" if user.updated_at.strftime("%p") == "AM" else "오후"
            pretty_updated_at = user.updated_at.strftime(f"{ampm} %I:%m:%S")
            all_users[
                i
            ] = f"{user.name}#{user.discriminator} : {now_state} : {pretty_updated_at}"
            i += 1
        all_users_dict_to_str = (
            str(all_users)
            .replace("{", "")
            .replace("}", "")
            .replace("'", "")
            .replace(",", "\n")
        )
        ebd.add_field(
            name="전체 유저 상태",
            value=f"{all_users_dict_to_str}",
            inline=False,
        )
        ebd.set_footer(text="상세 정보는 개인 검색을 이용해주세요.")
        await ctx.send(embed=ebd)
    else:
        ebd = discord.Embed(title="휴식이", description="휴식시간 알려주는 봇", color=0xFFA07A)
        target_nickname = " ".join(nickname)
        nickname_set = await UsersOnBreak.objects.async_filter(nickname=target_nickname)
        if nickname_set:
            if len(nickname_set) > 1:
                j = 1
                for user in nickname_set:
                    rescan_user_set[j] = f"{user.name}#{user.discriminator}"
                    j += 1
                dict_to_str = (
                    str(rescan_user_set)
                    .replace("{", "")
                    .replace("}", "")
                    .replace("'", "")
                    .replace(",", "\n")
                )
                ebd.add_field(
                    name="닉네임이 중복되는 유저들",
                    value=f"{dict_to_str}",
                    inline=False,
                )
                ebd.set_footer(text="made by 문현동#2226")
                await ctx.send(embed=ebd)
                await ctx.send('유저 번호로 재검색 해주세요.\n[예시] "##재검색 1"')
            else:
                user = await UsersOnBreak.objects.async_get(nickname=target_nickname)
                now_state = "쉬고 있음" if user.is_resting else "작업 중"
                ampm = "오전" if user.updated_at.strftime("%p") == "AM" else "오후"
                pretty_updated_at = user.updated_at.strftime(
                    f"%Y-%m-%d   {ampm} %I:%m:%S"
                )
                ebd.add_field(
                    name="최근 활동 기록",
                    value=f"{pretty_updated_at}",
                    inline=False,
                )
                ebd.add_field(
                    name="현재 상태",
                    value=f"{now_state}",
                    inline=False,
                )
                ebd.add_field(
                    name="전체 휴식 횟수",
                    value=f"{user.total_input} 번",
                    inline=True,
                )
                ebd.add_field(
                    name="전체 휴식 시간",
                    value=f"{user.total_break} 분",
                    inline=True,
                )
                ebd.add_field(
                    name="오늘 휴식한 횟수",
                    value=f"{user.today_input} 번",
                    inline=False,
                )
                ebd.add_field(
                    name="오늘 휴식한 시간",
                    value=f"{user.today_break} 분",
                    inline=True,
                )
                if user.is_resting:
                    state_today = datetime.now()
                    state_today = state_today.astimezone(KST)
                    state_total_break_time = state_today - user.updated_at
                    state_total_break_time = int(
                        state_total_break_time.total_seconds() // 60
                    )
                    state_remaining_rest_time = (
                        user.remaining_rest_time - state_total_break_time
                    )
                else:
                    state_remaining_rest_time = user.remaining_rest_time
                ebd.add_field(
                    name="잔여 휴식시간",
                    value=f"{state_remaining_rest_time}",
                    inline=False,
                )
                ebd.set_footer(text=f"{user.name} 님의 휴식 정보")
                await ctx.send(embed=ebd)
        else:
            await ctx.send(
                f'{target_nickname} : 등록되지 않은 사용자입니다.\n먼저 "##등록" 명령어로 등록해주세요!\n만약 이름이나 별명이 변경되었다면 "##재등록" 으로 재등록 해주세요!'
            )


@minibot.command(
    aliases=[
        "재검색",
    ]
)
async def rescan(ctx, num):
    ebd = discord.Embed(title="휴식이", description="휴식시간 알려주는 봇", color=0xFFA07A)
    if rescan_user_set[int(num)]:
        target_name = rescan_user_set[int(num)].split("#")[0]
        user = await UsersOnBreak.objects.async_get(name=target_name)
        now_state = "쉬고 있음" if user.is_resting else "작업 중"
        ampm = "오전" if user.updated_at.strftime("%p") == "AM" else "오후"
        pretty_updated_at = user.updated_at.strftime(f"%Y-%m-%d   {ampm} %I:%m:%S")
        ebd.add_field(
            name="최근 활동 기록",
            value=f"{pretty_updated_at}",
            inline=False,
        )
        ebd.add_field(
            name="현재 상태",
            value=f"{now_state}",
            inline=False,
        )
        ebd.add_field(
            name="전체 휴식 횟수",
            value=f"{user.total_input} 번",
            inline=False,
        )
        ebd.add_field(
            name="전체 휴식 시간",
            value=f"{user.total_break} 분",
            inline=False,
        )
        ebd.add_field(
            name="오늘 휴식한 횟수",
            value=f"{user.today_input} 번",
            inline=False,
        )
        ebd.add_field(
            name="오늘 휴식한 시간",
            value=f"{user.today_break} 분",
            inline=False,
        )
        if user.is_resting:
            rescan_today = datetime.now()
            rescan_today = rescan_today.astimezone(KST)
            rescan_total_break_time = rescan_today - user.updated_at
            rescan_total_break_time = int(rescan_total_break_time.total_seconds() // 60)
            rescan_remaining_rest_time = (
                user.remaining_rest_time - rescan_total_break_time
            )
        else:
            rescan_remaining_rest_time = user.remaining_rest_time
        ebd.add_field(
            name="잔여 휴식시간",
            value=f"{rescan_remaining_rest_time}",
            inline=False,
        )
        ebd.set_footer(text=f"{user.name} 님의 휴식 정보")
        await ctx.send(embed=ebd)
    else:
        await ctx.send("올바르지 않은 접근입니다.")


@minibot.command(
    aliases=[
        "도움",
        "도움말",
        "사용법",
        "명령어",
    ]
)
async def h(ctx):
    ebd = discord.Embed(title="휴식이", description="휴식시간 알려주는 봇", color=0xFFA07A)
    ebd.add_field(name="이름이나 별명 변경 시 반드시 재등록 해주세요!", value="##재등록", inline=False)
    ebd.add_field(
        name="중간에 재등록 된 경우",
        value="휴식 종료시 휴식을 취한 시간이 0분으로 출력됩니다.",
        inline=False,
    )
    ebd.add_field(name="1. 접두사", value='"##" 로 사용할 수 있어요\n[예시] ##휴식', inline=False)
    ebd.add_field(name="2. 인사", value="##인사", inline=False)
    ebd.add_field(name="3. 사용자 등록", value='"##등록"', inline=False)
    ebd.add_field(
        name="4. 휴식 시작", value='"##휴식"\n[예시] ##휴식, ##그만, ##쉬기, ...', inline=False
    )
    ebd.add_field(
        name="5. 휴식 끝", value='"##복귀"\n[예시] ##끝, ##복귀, ##일하기, ...', inline=False
    )
    ebd.add_field(
        name="6. 상태", value='"##상태 [검색할 사람의 서버 닉네임]"\n[예시] ##상태 문현동', inline=False
    )
    ebd.add_field(name="만든사람 깃허브", value="https://github.com/mhd329", inline=False)
    ebd.set_footer(text="설정된 명령어 외에도 숨겨져 있는 명령어들이 있답니다~~!!~ 한번 찾아보세요!\n힌트 : ##주사위")
    await ctx.send(embed=ebd)


minibot.run(DISCORD_SECRET_TOKEN)
