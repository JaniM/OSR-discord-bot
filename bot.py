import os
import discord
from discord.ext import commands
import datetime
from datetime import datetime
from datetime import timedelta
import asyncio
import requests

from config import roles_dict, del_commands, minutes_in_a_day, guild_id, expiration_times, prefix
from utils import add_role

bot = commands.Bot(command_prefix=prefix)
roles_are_set = False

async def get_roles():
    global roles_are_set
    if not roles_are_set:
        for name, role_dict in roles_dict.items():
            role = discord.utils.get(bot.get_guild(guild_id).roles, id=role_dict['id'])
            roles_dict[name].update({"role": role})
        roles_are_set = True

async def add_role(ctx, role_name):
    role_dict = roles_dict[role_name]
    if str(ctx.message.channel) not in role_dict['allowed_channels']:
        message = "Please " + ctx.message.author.mention + ", use the appropriate channels for this command: "
        message += ' '.join(role_dict['allowed_channels'])
        await ctx.send(message)
        return

    role = role_dict["role"]
    if role in ctx.message.author.roles:
        await ctx.send("Hey, " + ctx.message.author.mention + " is still " + role_dict["verbose"] + ".")
    else:
        await ctx.message.author.add_roles(role)
        await ctx.send("Hey, " + ctx.message.author.mention + " is " + role_dict["verbose"] + ".")

@bot.event
async def on_message(message):
    if prefix + message.content in del_commands:
        await message.delete()
    try:
        await bot.process_commands(message)
    except "NOT FOUND":
        pass

# Here are the pictures commands. That's just for fun.


@bot.command(pass_context=True)
async def cho(ctx):
    embed = discord.Embed()
    embed.set_image(url="https://cdn.discordapp.com/attachments/456532168370290695/461802038276390923/cho.png")
    await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def cho_hug(ctx):
    embed = discord.Embed()
    embed.set_image(url="https://cdn.discordapp.com/attachments/430062036903395329/444192620504416268/WroCzKKKj7o.png")
    await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def chang_ho(ctx):
    embed = discord.Embed()
    embed.set_image(url="https://cdn.discordapp.com/attachments/430062036903395329/432619582054858806/153746110828-nong01.png")
    await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def yuta(ctx):
    embed = discord.Embed()
    embed.set_image(url="https://cdn.discordapp.com/attachments/430062036903395329/432619582054858806/153746110828-nong01.png")
    await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def kj_facepalm(ctx):
    embed = discord.Embed()
    embed.set_image(url="https://cdn.discordapp.com/attachments/366870031285616651/461813881900236821/iozlnkjg.png")
    await ctx.send(embed=embed)

# Roles managment start here


@bot.command(pass_context=True, aliases=["lfg", "game", "LFG", "play", "GO", "PLAY", "GAME"])
async def go(ctx, minutes=minutes_in_a_day):
    role_dict = roles_dict['go']

    if str(ctx.message.channel) not in role_dict['allowed_channels']:
        message = "Please " + ctx.message.author.mention + ", use the appropriate channels for this command: "
        message += ' '.join(role_dict['allowed_channels'])
        await ctx.send(message)
        return

    role = role_dict["role"]

    expiration_time = datetime.now() + timedelta(minutes=minutes)
    expiration_times[ctx.author.id] = expiration_time
    if role in ctx.message.author.roles:
        await ctx.send("Hey, <@&" + str(role_dict["id"]) + ">! " + ctx.message.author.mention + " is desperately looking for a game.")
    else:
        await ctx.message.author.add_roles(role)
        await ctx.send("Hey, <@&" + str(role_dict["id"]) + ">! " + ctx.message.author.mention + " is looking for a game.")

@bot.command(pass_context=True)
async def dan(ctx):
    await add_role(ctx, 'dan')


@bot.command(pass_context=True)
async def sdk(ctx):
    await add_role(ctx, 'sdk')


@bot.command(pass_context=True)
async def ddk(ctx):
    await add_role(ctx, 'ddk')


@bot.command(pass_context=True)
async def tsumego(ctx):
    await add_role(ctx, 'tsumego')


@bot.command(pass_context=True)
async def review(ctx):
    await add_role(ctx, 'review')

@bot.command(pass_context=True)
async def no(ctx, role_name):
    role_dict = roles_dict.get(role_name)
    if role_dict is None:
        return
    if str(ctx.message.channel) not in role_dict['allowed_channels']:
        message = "Please " + ctx.message.author.mention + ", use the appropriate channels for this command: "
        message += ' '.join(role_dict['allowed_channels'])
        await ctx.send(message)
        return
    role = role_dict["role"]

    await ctx.message.author.remove_roles(role)
    await ctx.send(ctx.message.author.mention + " is no longer " + role_dict["verbose"] + ".")


@bot.command(pass_context=True, aliases=["no_lfg", "no_game", "remove_lfg", "no_play"])
async def no_go(ctx, minutes=minutes_in_a_day):
    role_dict = roles_dict['go']

    if str(ctx.message.channel) not in role_dict['allowed_channels']:
        message = "Please " + ctx.message.author.mention + ", use the appropriate channels for this command: "
        message += ' '.join(role_dict['allowed_channels'])
        await ctx.send(message)
        return

    role = role_dict["role"]

    if role in ctx.message.author.roles:
        await ctx.message.author.remove_roles(role)
        await ctx.send(ctx.message.author.mention + " is no longer looking for a game.")



@bot.command(pass_context=True, aliases=["list"])
async def whos(ctx, role_name):
    role_dict = roles_dict.get(role_name)
    if role_dict is None:
        return
    if str(ctx.message.channel) not in role_dict['allowed_channels']:
        message = "Please " + ctx.message.author.mention + ", use the appropriate channels for this command: "
        message += ' '.join(role_dict['allowed_channels'])
        await ctx.send(message)
        return
    role = role_dict["role"]

    users = [x for x in role.members if str(x.status) == "online"]
    if len(users) > 0:
        uids = [member.id for member in users]
        infos = requests.get("https://openstudyroom.org/league/discord-api/", params={'uids': uids}).json()
        message = ctx.message.author.mention + ": The following users are " + role_dict['verbose'] + ":\n"
        for user in users:
            message += '**' + user.name + '**'
            info = infos.get(str(user.id))
            if info is not None:
                kgs_username = info.get('kgs_username')
                kgs_rank = info.get('kgs_rank')
                ogs_username = info.get('ogs_username')
                ogs_rank = info.get('ogs_rank')
                if kgs_username is not None or ogs_username is not None:
                    message += ':'
                    if ogs_username is not None:
                        message += ' OGS | ' + ogs_username + ' (' + ogs_rank + ') -'
                    if kgs_username is not None:
                        message += ' KGS | ' + kgs_username + ' (' + kgs_rank + ')'
            message += ' \n'
        await ctx.send(message)
    else:
        await ctx.send("Sorry " + ctx.message.author.mention + ". Unfortunately, nobody is " + role_dict['verbose'] + " right now. :(")

@bot.command(pass_context=True, aliases=["whos_lfg", "whos_go"])
async def whos_LFG(ctx):
    role_dict = roles_dict['go']

    if str(ctx.message.channel) not in role_dict['allowed_channels']:
        message = "Please " + ctx.message.author.mention + ", use the appropriate channels for this command: "
        message += ' '.join(role_dict['allowed_channels'])
        await ctx.send(message)
        return

    role = role_dict["role"]

    currently_looking = [x for x in role.members if str(x.status) == "online"]

    if len(currently_looking) > 0:
        uids = [member.id for member in currently_looking]
        infos = requests.get("https://openstudyroom.org/league/discord-api/", params={'uids': uids}).json()
        message = ctx.message.author.mention + ": The following users are looking for a game:\n"
        for user in currently_looking:
            message += '**' + user.name + '**'
            info = infos.get(str(user.id))
            if info is not None:
                kgs_username = info.get('kgs_username')
                kgs_rank = info.get('kgs_rank')
                ogs_username = info.get('ogs_username')
                ogs_rank = info.get('ogs_rank')
                if kgs_username is not None or ogs_username is not None:
                    message += ':'
                    if ogs_username is not None:
                        message += ' OGS | ' + ogs_username + ' (' + ogs_rank + ') -'
                    if kgs_username is not None:
                        message += ' KGS | ' + kgs_username + ' (' + kgs_rank + ')'
            message += ' \n'
        await ctx.send(message)
    else:
        await ctx.send("Sorry " + ctx.message.author.mention + ". Unfortunately, nobody is looking for a game right now. :(")



@bot.command(pass_context=True)
async def info(ctx):
    desc = "Keeps track of who is currently looking for a game.\nhttps://github.com/climu/OSR-discord-bot"
    embed = discord.Embed(title="OSR bot", description=desc, color=0xeee657)
    await ctx.send(embed=embed)

bot.remove_command('help')


@bot.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(title="Looking For Game (LFG) Bot", description="Keeps track of who is currently looking for a game. The following commands are available:", color=0xeee657)
    embed.add_field(name="!go [minutes]", value="Toggles your role for go. You can limit the length of time you will be LFG by entering a number of minutes after the command.", inline=False)
    embed.add_field(name="!no go", value="Removes the user from the LFG group.", inline=False)
    embed.add_field(name="!whos go", value="Tells you who is currently looking.", inline=False)
    embed.add_field(name="!info", value="Gives a little info about the bot.", inline=False)
    embed.add_field(name="!help", value="Gives this message.", inline=False)
    await ctx.send(embed=embed)


async def check_LFG():
    await bot.wait_until_ready()
    await get_roles()
    while not bot.is_closed:
        role = discord.utils.get(ctx.message.guild.roles, id=roles_dict['go']['id'])
        for uid, expiration_time in expiration_times.items():
            if datetime.now() > expiration_time:
                await discord.utils.get(bot.get_all_members(), id=uid).remove_roles(role)
        await asyncio.sleep(60)

bot.loop.create_task(check_LFG())
bot.run(os.environ["LFG_TOKEN"])
