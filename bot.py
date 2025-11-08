import os
import discord
from discord.ext import commands
import json

# --- CONFIG FILE ---
CONFIG_FILE = "config.json"

# Load or initialize config
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
else:
    config = {}

# --- INTENTS ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- HELPER FUNCTIONS ---
def get_guild_config(guild_id):
    if str(guild_id) not in config:
        config[str(guild_id)] = {
            "welcome_channel": "general",
            "mod_log_channel": "mod-log"
        }
        save_config()
    return config[str(guild_id)]

def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def get_channel(guild, name):
    return discord.utils.get(guild.text_channels, name=name)

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    guild_config = get_guild_config(member.guild.id)
    channel = get_channel(member.guild, guild_config["welcome_channel"])
    if channel:
        await channel.send(f"👋 Welcome {member.mention} to the server!")

# --- MODERATION COMMANDS ---
async def log_action(ctx, action, member, reason=None):
    guild_config = get_guild_config(ctx.guild.id)
    log_channel = get_channel(ctx.guild, guild_config["mod_log_channel"])
    if log_channel:
        embed = discord.Embed(title=f"Moderation Action: {action}", color=discord.Color.red())
        embed.add_field(name="Member", value=member.mention, inline=False)
        embed.add_field(name="By", value=ctx.author.mention, inline=False)
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        await log_channel.send(embed=embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    try:
        await member.kick(reason=reason)
        await ctx.send(f"✅ {member} has been kicked!")
        await log_action(ctx, "Kick", member, reason)
    except:
        await ctx.send("❌ I cannot kick this member!")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    try:
        await member.ban(reason=reason)
        await ctx.send(f"✅ {member} has been banned!")
        await log_action(ctx, "Ban", member, reason)
    except:
        await ctx.send("❌ I cannot ban this member!")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name="Muted")
    if not role:
        role = await guild.create_role(name="Muted")
        for channel in guild.channels:
            await channel.set_permissions(role, speak=False, send_messages=False)
    await member.add_roles(role)
    await ctx.send(f"🔇 {member} has been muted!")
    await log_action(ctx, "Mute", member)

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if role:
        await member.remove_roles(role)
        await ctx.send(f"🔊 {member} has been unmuted!")
        await log_action(ctx, "Unmute", member)
    else:
        await ctx.send("❌ Muted role does not exist!")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"🧹 Cleared {amount} messages!", delete_after=3)

# --- CONFIGURATION COMMANDS ---
@bot.command()
@commands.has_permissions(administrator=True)
async def setwelcome(ctx, channel_name):
    guild_config = get_guild_config(ctx.guild.id)
    guild_config["welcome_channel"] = channel_name
    save_config()
    await ctx.send(f"✅ Welcome channel set to #{channel_name}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setmodlog(ctx, channel_name):
    guild_config = get_guild_config(ctx.guild.id)
    guild_config["mod_log_channel"] = channel_name
    save_config()
    await ctx.send(f"✅ Mod log channel set to #{channel_name}")

# --- HELP COMMAND ---
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="PhoenixBot Commands", color=discord.Color.purple())
    embed.add_field(name="!kick @user [reason]", value="Kick a member", inline=False)
    embed.add_field(name="!ban @user [reason]", value="Ban a member", inline=False)
    embed.add_field(name="!mute @user", value="Mute a member", inline=False)
    embed.add_field(name="!unmute @user", value="Unmute a member", inline=False)
    embed.add_field(name="!clear <number>", value="Delete messages", inline=False)
    embed.add_field(name="!setwelcome <channel>", value="Set welcome channel", inline=False)
    embed.add_field(name="!setmodlog <channel>", value="Set mod log channel", inline=False)
    await ctx.send(embed=embed)

# --- RUN BOT ---
TOKEN = os.environ.get("TOKEN")
bot.run(TOKEN)
