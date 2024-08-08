import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio  # อย่าลืม import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="gm!", intents=intents)

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.command(name="join", help="เข้าร่วมช่องเสียง")
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("คุณต้องอยู่ในช่องเสียงเพื่อใช้คำสั่งนี้!")
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name="leave", help="ออกจากช่องเสียง")
async def leave(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("Bot ไม่ได้อยู่ในช่องเสียง")

@bot.command(name="play", help="เล่นเพลงจาก YouTube")
async def play(ctx, url):
    if ctx.voice_client is None:
        await ctx.send("Bot ไม่ได้อยู่ในช่องเสียง กรุณาใช้คำสั่ง !join ก่อน")
        return
    
    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=bot.loop)
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

    await ctx.send(f'กำลังเล่น: {player.title}')


@bot.command(name="pause", help="หยุดเพลงชั่วคราว")
async def pause(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send("ไม่มีเพลงที่กำลังเล่นอยู่")

@bot.command(name="resume", help="เล่นเพลงต่อ")
async def resume(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send("เพลงไม่ได้ถูกหยุดชั่วคราว")

@bot.command(name="stop", help="หยุดเล่นเพลง")
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.stop()
    else:
        await ctx.send("ไม่มีเพลงที่กำลังเล่นอยู่")

bot.run('MTI3MTA2ODE2NDEwMDQ2MDU4NA.Gd8nvr.eWZJ_ltcy7w3TaPJPuyuerOWUguuKTtFbP0VNg')
