import discord
import sqlite3

conn = sqlite3.connect("valdata.db")
cur = conn.cursor()

class RegisterModal(discord.ui.Modal, title="Register Valorant Account"):
    name = discord.ui.TextInput(label="Riot Name", placeholder="fill name", required=True)
    tag = discord.ui.TextInput(label="Riot Tag (without #)", placeholder="fill tag", required=True)
    region = discord.ui.TextInput(label="Region (eu/na)", placeholder="fill region", required=True, max_length=2) 

    async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value
        tag = self.tag.value
        region = self.region.value.lower()
        discord_id = str(interaction.user.id)


        cur.execute("INSERT OR REPLACE INTO users (discord_id, riot_name, riot_tag, region) VALUES(?,?,?,?)", [discord_id, name, tag, region])
        conn.commit()

        await interaction.response.send_message("Registration succesfull")