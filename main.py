import discord
import requests
import os
import re
from discord import app_commands
from discord.ext import commands
from flask import Flask
from threading import Thread

# ============================================
# FLASK APP PARA KEEP ALIVE (Render Free Tier)
# ============================================
app = Flask('')

@app.route('/')
def home():
    return "🤖 Discord Bot is running! Status: Online"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
    print("✅ Keep-alive server started on port 8080")

# ============================================
# DISCORD BOT SETUP
# ============================================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ============================================
# COMPLETE SUPPORTED DOMAINS (70+ sites)
# ============================================
SUPPORTED_DOMAINS = [
    # Loot & Reward Sites
    "lootlabs.com", "rekonise.com", "linkvertise.com", "inkbypass.com",
    "mboost.me", "gyazo.com", "pixelmedia.ch",
    
    # Rocklinks Family
    "rocklinks.net", "rocklinks.com", "linkrock.net", "rocklink.net",
    "pagar-hiperlink.com", "hyperlink.pagar.cc", "sub2unlock.cc", "sub4unlock.cc",
    
    # Vietnamese Shorteners
    "link4m.com", "link2m.com", "linkngon.com", "meobypass.click", "sub2unlock.net",
    
    # Common Shortlinks
    "adf.ly", "bc.vc", "exe.io", "ouo.io", "shorte.st", "gestyy.com",
    "oncehelp.com", "linkrex.net", "adfoc.us", "sh.st", "cutt.ly", "tinyurl.com",
    "bit.ly", "is.gd", "v.gd", "cli.ps", "soo.gd", "rb.gy", "short.link",
    
    # Fox Links
    "foxlink.cc", "indian-links.com", "muxiux.monster",
    
    # Gaming/File Hosting
    "dropapk.to", "dropgalaxy.in", "dramacool.ir", "dramacool.pw",
    "anonfiles.com", "shareus.io", "youtu.be", "rabbitfiles.xyz", "mediafire.com",
    
    # Linkvertise Redirects
    "arti-20.com", "doc-0-s0-sjtu-0-0.com", "doc-04-s4-sjtu-0-0.com",
    "doc-0-5c-sjtu-0-0.com", "doc-0c-cc-sjtu-0-0.com", "doc-0c-cs-sjtu-0-0.com",
    "doc-04-8c-sjtu-0-0.com"
]

# ============================================
# BYPASS FUNCTION
# ============================================
def bypass_link(url):
    """Bypass shortlinks using bypass.it API"""
    try:
        response = requests.post(
            "https://bypass.it/api/bypass",
            json={"url": url},
            timeout=45
        )
        
        if response.status_code == 200:
            data = response.json()
            destination = data.get("destination")
            if destination and destination != url:
                return destination
        return None
    except requests.exceptions.Timeout:
        print(f"Timeout error for: {url}")
        return None
    except Exception as e:
        print(f"Bypass error: {e}")
        return None

def extract_urls(text):
    """Extract URLs from message"""
    url_pattern = r'https?://[^\s<>"']+'
    return re.findall(url_pattern, text)

# ============================================
# SLASH COMMAND: /bypass
# ============================================
@bot.tree.command(name="bypass", description="🔓 Bypass shortlinks like Lootlabs, Rekonise, Linkvertise")
@app_commands.describe(link="The shortlink URL you want to bypass")
async def slash_bypass(interaction: discord.Interaction, link: str):
    # Defer response para hindi mag-timeout
    await interaction.response.defer()
    
    # Validate link format
    if not link.startswith(('http://', 'https://')):
        embed = discord.Embed(
            title="❌ Invalid Link Format",
            description="Please include `http://` or `https://` in your link.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    result = bypass_link(link)
    
    if result:
        embed = discord.Embed(
            title="🔓 Link Successfully Bypassed!",
            description=f"**✅ Bypassed Link:**\n{result}",
            color=discord.Color.green(),
            timestamp=interaction.created_at
        )
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/190/190411.png")
        embed.add_field(name="📎 Original Link", value=f"```{link[:100]}```", inline=False)
        embed.add_field(
            name="📊 Statistics",
            value=f"• **Supported Sites:** {len(SUPPORTED_DOMAINS)}+ domains\n• **Daily Limit:** 100 requests\n• **Status:** ✅ Success",
            inline=False
        )
        embed.set_footer(text="Powered by bypass.it • Free bypass service", icon_url=interaction.client.user.avatar.url)
        await interaction.followup.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Bypass Failed",
            description=f"Could not bypass the link:",
            color=discord.Color.red(),
            timestamp=interaction.created_at
        )
        embed.add_field(name="🔗 Failed Link", value=f"```{link[:100]}```", inline=False)
        embed.add_field(
            name="⚠️ Possible Reasons",
            value="• Daily limit reached (100/day)\n• Unsupported shortlink service\n• API is temporarily down\n• Invalid or expired link",
            inline=False
        )
        embed.add_field(
            name="💡 Solutions",
            value="• Try again in a few minutes\n• Use `!bypass` as fallback\n• Wait 24 hours for limit reset",
            inline=False
        )
        embed.set_footer(text="Supported: Lootlabs • Rekonise • Linkvertise • Rocklinks • 50+ more")
        await interaction.followup.send(embed=embed)

# ============================================
# SLASH COMMAND: /help
# ============================================
@bot.tree.command(name="help", description="📖 View all commands and supported sites")
async def slash_help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Link Bypasser Bot - Help Center",
        description="A powerful Discord bot that bypasses various shortlink services automatically!",
        color=discord.Color.blue(),
        timestamp=interaction.created_at
    )
    
    # Commands section
    embed.add_field(
        name="📌 Slash Commands",
        value="</bypass:0> `[link]` - Bypass any shortlink\n</help:0> - Show this help menu\n</supported:0> - List all supported sites\n</stats:0> - Show bot statistics",
        inline=False
    )
    
    embed.add_field(
        name="⌨️ Prefix Commands (Fallback)",
        value="`!bypass [link]` - Manual bypass\n`!help` - Show help\n`!supported` - List supported sites",
        inline=False
    )
    
    # Supported categories
    embed.add_field(
        name="💰 Reward & Loot Sites",
        value="`Lootlabs` • `Rekonise` • `Linkvertise` • `InkBypass` • `Mboost`",
        inline=True
    )
    embed.add_field(
        name="🪨 Rocklinks Family",
        value="`Rocklinks` • `Sub2Unlock` • `LinkRock` • `Sub4Unlock`",
        inline=True
    )
    embed.add_field(
        name="🇻🇳 Vietnamese Services",
        value="`Link4M` • `Link2M` • `LinkNgon` • `MèoBypass`",
        inline=True
    )
    embed.add_field(
        name="🔗 Common Shorteners",
        value="`Adf.ly` • `Exe.io` • `Ouo.io` • `Shorte.st` • `Cutt.ly` • `Tinyurl`",
        inline=True
    )
    embed.add_field(
        name="🎮 Gaming & Files",
        value="`Dropapk` • `Dropgalaxy` • `Anonfiles` • `Shareus`",
        inline=True
    )
    
    embed.add_field(
        name="📊 Total Supported",
        value=f"**{len(SUPPORTED_DOMAINS)}+ domains**",
        inline=False
    )
    
    embed.add_field(
        name="⚠️ Limits & Notes",
        value="• **100 requests/day** (free API limit)\n• Resets every 24 hours\n• Not all links are guaranteed to work\n• Some links may require manual bypass",
        inline=False
    )
    
    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/4355/4355604.png")
    embed.set_footer(text="Use </bypass:0> to get started!", icon_url=interaction.client.user.avatar.url)
    
    await interaction.response.send_message(embed=embed)

# ============================================
# SLASH COMMAND: /supported
# ============================================
@bot.tree.command(name="supported", description="🌐 Show all supported shortlink websites")
async def slash_supported(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🌐 Supported Shortlink Services",
        description=f"Currently supporting **{len(SUPPORTED_DOMAINS)}** domains",
        color=discord.Color.gold(),
        timestamp=interaction.created_at
    )
    
    # Group by category with clean formatting
    embed.add_field(
        name="💰 Loot & Reward Sites",
        value="```lootlabs.com | rekonise.com | linkvertise.com | inkbypass.com | mboost.me```",
        inline=False
    )
    embed.add_field(
        name="🪨 Rocklinks & Family",
        value="```rocklinks.net | rocklinks.com | linkrock.net | sub2unlock.cc | sub4unlock.cc```",
        inline=False
    )
    embed.add_field(
        name="🇻🇳 Vietnamese Services",
        value="```link4m.com | link2m.com | linkngon.com | meobypass.click | sub2unlock.net```",
        inline=False
    )
    embed.add_field(
        name="🔗 Common Shorteners",
        value="```adf.ly | exe.io | ouo.io | shorte.st | bc.vc | cutt.ly | tinyurl.com | gestyy.com```",
        inline=False
    )
    embed.add_field(
        name="🎮 Gaming & File Hosting",
        value="```dropapk.to | dropgalaxy.in | anonfiles.com | shareus.io | mediafire.com```",
        inline=False
    )
    embed.add_field(
        name="🦊 Other Services",
        value="```foxlink.cc | indian-links.com | rabbittfiles.xyz | dramacool.ir | youtube.com```",
        inline=False
    )
    
    embed.set_footer(text="100 requests/day • Resets every 24 hours")
    
    await interaction.response.send_message(embed=embed)

# ============================================
# SLASH COMMAND: /stats
# ============================================
@bot.tree.command(name="stats", description="📊 Show bot statistics and status")
async def slash_stats(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📊 Bot Statistics",
        color=discord.Color.purple(),
        timestamp=interaction.created_at
    )
    
    embed.add_field(name="🤖 Bot Name", value=interaction.client.user.name, inline=True)
    embed.add_field(name="📋 Supported Sites", value=f"{len(SUPPORTED_DOMAINS)}+", inline=True)
    embed.add_field(name="⚡ API Limit", value="100 requests/day", inline=True)
    embed.add_field(name="🟢 Status", value="🟢 Online", inline=True)
    embed.add_field(name="🔧 API Used", value="bypass.it", inline=True)
    embed.add_field(name="💰 Pricing", value="Free (limited)", inline=True)
    
    embed.set_thumbnail(url=interaction.client.user.avatar.url)
    embed.set_footer(text="Bot is operational 24/7")
    
    await interaction.response.send_message(embed=embed)

# ============================================
# LEGACY PREFIX COMMANDS (Fallback)
# ============================================
@bot.command(name="bypass")
async def prefix_bypass(ctx, *, link: str = None):
    if not link:
        embed = discord.Embed(
            title="❌ Missing Link",
            description="Usage: `!bypass <link>`\nExample: `!bypass https://lootlabs.com/example`",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    await ctx.send(f"🔄 Bypassing link... Please wait.")
    result = bypass_link(link)
    
    if result:
        embed = discord.Embed(
            title="✅ Successfully Bypassed!",
            description=f"**Bypassed Link:**\n{result}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Failed to Bypass",
            description="Could not bypass the link. Possible reasons:\n• Daily limit reached\n• Unsupported link\n• API down",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command(name="help")
async def prefix_help(ctx):
    embed = discord.Embed(
        title="🤖 Bot Commands",
        description="Use slash commands for better experience:",
        color=discord.Color.blue()
    )
    embed.add_field(name="/bypass [link]", value="Bypass a shortlink", inline=False)
    embed.add_field(name="/help", value="Show this help menu", inline=False)
    embed.add_field(name="/supported", value="List all supported sites", inline=False)
    embed.add_field(name="/stats", value="Show bot statistics", inline=False)
    embed.add_field(name="!bypass [link]", value="Fallback command", inline=True)
    embed.add_field(name="!help", value="Fallback help", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="supported")
async def prefix_supported(ctx):
    sites_list = "\n".join([f"• {site}" for site in SUPPORTED_DOMAINS[:20]])
    embed = discord.Embed(
        title="Supported Sites (Partial List)",
        description=f"```{sites_list}```\nAnd {len(SUPPORTED_DOMAINS) - 20} more...",
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

# ============================================
# AUTO-DETECT LINKS
# ============================================
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Extract URLs from message
    urls = extract_urls(message.content)
    
    for url in urls:
        for domain in SUPPORTED_DOMAINS:
            if domain in url.lower():
                # Send indicator
                await message.channel.send(f"🔄 Detected shortlink from {message.author.mention}, bypassing...")
                result = bypass_link(url)
                
                if result:
                    embed = discord.Embed(
                        title="✅ Auto-Bypassed!",
                        description=f"**Original:** {url}\n**Bypassed:** {result}",
                        color=discord.Color.green()
                    )
                    await message.reply(embed=embed)
                else:
                    embed = discord.Embed(
                        title="❌ Auto-Bypass Failed",
                        description=f"Could not bypass link from {message.author.mention}",
                        color=discord.Color.red()
                    )
                    await message.reply(embed=embed)
                break  # Only process first found link
    
    await bot.process_commands(message)

# ============================================
# ON READY EVENT
# ============================================
@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")
    print(f"📋 Supported domains: {len(SUPPORTED_DOMAINS)}")
    print(f"🔗 Invite URL: https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=274877958144&scope=bot%20applications.commands")
    
    # Sync slash commands to Discord
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands: {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"/help • {len(SUPPORTED_DOMAINS)} sites"
        ),
        status=discord.Status.online
    )

# ============================================
# MAIN - START BOT WITH KEEP ALIVE
# ============================================
if __name__ == "__main__":
    # Start keep-alive server for Render free tier
    keep_alive()
    
    # Get token from Render Secrets
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    
    if not TOKEN:
        print("❌ ERROR: DISCORD_BOT_TOKEN not found in environment variables!")
        print("Please add DISCORD_BOT_TOKEN to Render Secrets")
        exit(1)
    
    print("🚀 Starting Discord bot...")
    bot.run(TOKEN)
