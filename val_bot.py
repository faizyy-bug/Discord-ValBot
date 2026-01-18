import discord
from discord.ext import commands
import requests
import sqlite3
import os
from dotenv import load_dotenv
from classes import RegisterModal

load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")
api_key = os.getenv("HENDRIK_TOKEN")

conn = sqlite3.connect("valdata.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    discord_id TEXT PRIMARY KEY,
    riot_name TEXT NOT NULL,
    riot_tag TEXT NOT NULL,
    region TEXT NOT NULL
)
""")
conn.commit()

# cur.execute("DROP TABLE IF EXISTS stats")
# conn.commit()

cur.execute("""
CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            riot_tag TEXT NOT NULL,
            kills INTEGER,
            deaths INTEGER,
            game_results TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP -- timestamp
)
""")
conn.commit()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


headers = {
    "Authorization": api_key,
    "Accept": "*/*"
}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands globally")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.command()
async def lastmatch(ctx, member: discord.Member):
    cur.execute("SELECT riot_name, riot_tag, region FROM users WHERE discord_id = ? ", [str(member.id)])
    row = cur.fetchone()
    
    if not row:
        await ctx.send("User is not registered. Use /register first.")
    name = row[0]
    tag = row[1]
    region = row[2]
    user_tag = f"{name}#{tag}"



    rank_res = requests.get(f"https://api.henrikdev.xyz/valorant/v1/mmr-history/{region}/{name}/{tag}",
            headers=headers
    )
    rank_data = rank_res.json()
    

    try:
        last_match = rank_data["data"][0]
        match_id = last_match["match_id"]
        rank = last_match["currenttierpatched"]
        game_map = rank_data["data"][0]["map"]["name"]

    except (KeyError, IndexError, TypeError):
        await ctx.send(f"Could not find any recent data for {name}# {tag}")
        return


    matches_res = requests.get(f"https://api.henrikdev.xyz/valorant/v2/match/{match_id}",
            headers=headers
    )
    matches_data = matches_res.json()

    kills = 0
    deaths = 0

    for event in matches_data["data"]["kills"]:
        if event["killer_display_name"].lower() == user_tag.lower():
            kills += 1
        
        if event["victim_display_name"].lower() == user_tag.lower():
            deaths += 1

    
    mmr_change = last_match.get("mmr_change_to_last_game", 0 )
    if mmr_change > 0:
        result = f"Won ({mmr_change} mmr)"
        color = discord.color.green()
    elif mmr_change < 0:
        result = f"Lost ({mmr_change} mmr)"
        color = discord.Color.red()
    else:
        result = f"DRAW ({mmr_change} mmr)"

    cur.execute("INSERT INTO stats (riot_tag, kills, deaths, game_results) VALUES (?, ?, ?, ?)", [tag, kills, deaths, result])
    conn.commit()


    embed = discord.Embed(
        title = f"{user_tag} —— LAST MATCH",
        color=color
    )

    embed.add_field(name= "Kills", value=str(kills), inline=True)
    embed.add_field(name= "Deaths", value=str(deaths), inline=True)
    embed.add_field(name= "Rank", value=str(rank), inline=True)
    embed.add_field(name="Map", value=str(game_map), inline=True)
    embed.add_field(name= "Result Game", value=str(result), inline=True)
    embed.set_footer(text= "*Valorant match stats*")
    embed.set_thumbnail(url=member.avatar.url)

    
    await ctx.send(embed=embed)


@bot.tree.command(name="register")
async def register(interaction: discord.Interaction):
    await interaction.response.send_modal(RegisterModal())




bot.run(discord_token)

if __name__ == "__main__":
    ()