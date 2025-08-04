import discord
from discord.ext import commands, tasks
import aiohttp
import datetime
import pytz

TOKEN = 'MTQwMTg2MjY3MTMxNzYwMjMyNQ.G1fith.WJ5ygKg95cGfpNHykbrZs0GzFEW9SyEgPUr8W4'
WEATHER_API_KEY = 'fa52b6d8fcff7fadf9351c887aab584c'
GUILD_ID = '1400562135599415387'
CHANNEL_ID = '1401668437968814080'

SILESIA_CITIES = [
    "Katowice", "Gliwice", "Zabrze", "Bytom", "Ruda Śląska",
    "Tychy", "Sosnowiec", "Dąbrowa Górnicza", "Częstochowa", "Bielsko-Biała"
]

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print("🔄 Komendy zsynchronizowane na guild")
    daily_weather.start()

async def get_weather(city: str):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=pl"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    "city": data["name"],
                    "temp": round(data["main"]["temp"]),
                    "desc": data["weather"][0]["description"].capitalize()
                }
            else:
                return None

@tasks.loop(minutes=1)
async def daily_weather():
    now = datetime.datetime.now(pytz.timezone("Europe/Warsaw"))
    if now.hour == 8 and now.minute == 0:
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            print("❌ Nie znaleziono kanału.")
            return

        lines = [f"📍 **Prognoza pogody – {now.strftime('%-d.%m.%Y')} (Śląsk)**\n"]
        for city in SILESIA_CITIES:
            weather = await get_weather(city)
            if weather:
                line = f"🌆 **{weather['city']}**: {weather['desc']}, {weather['temp']}°C"
                lines.append(line)
            else:
                lines.append(f"🌆 {city}: ❌ Błąd pobierania danych.")

        message = "\n".join(lines)
        await channel.send(message)

# --- PRZYKŁADOWE KOMENDY SLASH ---

@bot.tree.command(name="pogoda", description="Pobierz aktualną pogodę dla miasta")
@discord.app_commands.describe(miasto="Nazwa miasta na Śląsku")
async def pogoda(interaction: discord.Interaction, miasto: str):
    if miasto not in SILESIA_CITIES:
        await interaction.response.send_message(f"❌ Nieobsługiwane miasto. Wybierz z listy: {', '.join(SILESIA_CITIES)}", ephemeral=True)
        return
    weather = await get_weather(miasto)
    if weather:
        await interaction.response.send_message(f"🌆 **{weather['city']}**: {weather['desc']}, {weather['temp']}°C")
    else:
        await interaction.response.send_message("❌ Błąd pobierania danych.", ephemeral=True)

@bot.tree.command(name="poranek", description="Poranna prognoza pogody ze Śląska")
async def poranek(interaction: discord.Interaction):
    now = datetime.datetime.now(pytz.timezone("Europe/Warsaw"))
    lines = [f"🌅 **Poranna prognoza – {now.strftime('%-d.%m.%Y')} (Śląsk)**\n"]
    for city in SILESIA_CITIES:
        weather = await get_weather(city)
        if weather:
            line = f"🌆 **{weather['city']}**: {weather['desc']}, {weather['temp']}°C"
            lines.append(line)
        else:
            lines.append(f"🌆 {city}: ❌ Błąd pobierania danych.")
    message = "\n".join(lines)
    await interaction.response.send_message(message)

@bot.tree.command(name="wieczór", description="Wieczorna prognoza pogody ze Śląska")
async def wieczor(interaction: discord.Interaction):
    now = datetime.datetime.now(pytz.timezone("Europe/Warsaw"))
    lines = [f"🌙 **Wieczorna prognoza – {now.strftime('%-d.%m.%Y')} (Śląsk)**\n"]
    for city in SILESIA_CITIES:
        weather = await get_weather(city)
        if weather:
            line = f"🌆 **{weather['city']}**: {weather['desc']}, {weather['temp']}°C"
            lines.append(line)
        else:
            lines.append(f"🌆 {city}: ❌ Błąd pobierania danych.")
    message = "\n".join(lines)
    await interaction.response.send_message(message)

@bot.tree.command(name="mapa_pogody", description="Link do mapy pogody")
async def mapa_pogody(interaction: discord.Interaction):
    await interaction.response.send_message("🗺️ [Mapa pogody Śląska](https://www.windy.com/?region=pl)")

@bot.tree.command(name="pomoc", description="Pomoc z komendami bota")
async def pomoc(interaction: discord.Interaction):
    help_text = """
    **Dostępne komendy:**
    /pogoda [miasto] - aktualna pogoda dla miasta na Śląsku
    /poranek - poranna prognoza ze Śląska
    /wieczór - wieczorna prognoza ze Śląska
    /mapa_pogody - link do interaktywnej mapy pogody
    /pomoc - wyświetla tę pomoc
    """
    await interaction.response.send_message(help_text, ephemeral=True)

bot.run(TOKEN)