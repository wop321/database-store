import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

from keep_alive import keep_alive
from github_api import github_add_entry

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("DISCORD_TOKEN missing in .env")

DATABASE_CHANNEL_ID = 1441459681439780905
PASSWORD = "abcd980"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def get_db_channel():
    ch = bot.get_channel(DATABASE_CHANNEL_ID)
    if ch is None:
        ch = await bot.fetch_channel(DATABASE_CHANNEL_ID)
    return ch


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()
    print("Slash commands synced.")


@bot.tree.command(name="add", description="Add a module to the database.")
@app_commands.describe(name="Name", url="URL")
async def add(interaction: discord.Interaction, name: str, url: str):
    chan = await get_db_channel()
    entry = f"{name} - {url}"

    # check duplicate
    msgs = [m async for m in chan.history(limit=None)]
    for m in msgs:
        if m.content.startswith(name + " -"):
            await interaction.response.send_message("Entry already exists.", ephemeral=True)
            return

    # write to Discord
    await chan.send(entry)

    # write to GitHub API
    github_add_entry(entry)

    await interaction.response.send_message("module upload successful.", ephemeral=True)


@bot.tree.command(name="list", description="List all entries.")
async def list_cmd(interaction: discord.Interaction):
    chan = await get_db_channel()
    msgs = [m async for m in chan.history(limit=None)]

    entries = [m.content for m in msgs if " - " in m.content]
    full = "\n".join(entries)

    if len(full) <= 1950:
        await interaction.response.send_message(full)
    else:
        with open("modules.txt", "w", encoding="utf-8") as f:
            f.write(full)
        await interaction.response.send_message(
            "List too long — sending file.",
            file=discord.File("modules.txt")
        )


@bot.tree.command(name="delete", description="Delete an entry.")
@app_commands.describe(name="Name", password="Password")
async def delete(interaction: discord.Interaction, name: str, password: str):
    if password != PASSWORD:
        await interaction.response.send_message("Incorrect password.", ephemeral=True)
        return

    chan = await get_db_channel()
    msgs = [m async for m in chan.history(limit=None)]

    for m in msgs:
        if m.content.startswith(name + " -"):
            await m.delete()
            await interaction.response.send_message("Deleted.", ephemeral=True)
            return

    await interaction.response.send_message("Not found.", ephemeral=True)


keep_alive()
bot.run(TOKEN)
