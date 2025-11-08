import os
import discord
from discord.ext import commands

# Intents — required for moderation features
intents = discord.Intents.all()

# Command prefix
bot = commands.Bot(command_prefix="!", intents=intents)

# When bot is ready
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# Welcome new members
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"👋 Welcome {member.mention} to the server!")

# Kick command
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    try:
        await member.kick(reason=reason)
        await ctx.send(f"✅ {member} has been kicked!")
    except:
        await ctx.send("❌ I cannot kick this member!")

# Ban command
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    try:
        await member.ban(reason=reason)
        await ctx.send(f"✅ {member} has been banned!")
    except:
        await ctx.send("❌ I cannot ban this member!")

# Mute command
@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name="Muted")
    if not role:
        # Create Muted role if it doesn't exist
        role = await guild.create_role(name="Muted")
        for channel in guild.channels:
            await channel.set_permissions(role, speak=False, send_messages=False)
    await member.add_roles(role)
    await ctx.send(f"🔇 {member} has been muted!")

# Unmute command
@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if role:
        await member.remove_roles(role)
        await ctx.send(f"🔊 {member} has been unmuted!")
    else:
        await ctx.send("❌ Muted role does not exist!")

# Clear messages
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"🧹 Cleared {amount} messages!", delete_after=3)

# Run the bot using environment variable
TOKEN = os.environ.get("TOKEN")
bot.run(TOKEN)
