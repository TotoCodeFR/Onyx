from discord.ext import commands  # type: ignore
from datetime import datetime
import discord  # type: ignore
import random
import settings
from flask import Flask  # type: ignore
from threading import Thread
from getpass import getpass

logger = settings.logging.getLogger("bot")


def run():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    def log_file(content, ctx):
        f = open("logs/actions.log", "a")
        now = datetime.now()
        time = now.strftime("%d/%m/%Y, %H:%M:%S")
        f.write(
            f"({ctx.guild.id}, {ctx.message.channel.id} @ {time}) : " + content + "\n")
        f.close()

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")
        print("="*50)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="les utilisateurs :3 !"))
        app = Flask(__name__)

        @app.route('/')
        def index():
            return '''<body style="margin: 0; padding: 0;">
            <iframe width="100%" height="100%" src="https://totocodefr.github.io/" frameborder="0" allowfullscreen></iframe>
        </body>'''

        def run():
            app.run(host='0.0.0.0', port=8080)

        def keep_alive():
            t = Thread(target=run)
            t.start()

        keep_alive()

    @bot.command(
        aliases=["p"],
        help="Pong!",
        description="Ping?",
        brief="Pong!",
        enable=True
    )
    async def ping(ctx):
        await ctx.send("pong")
        log_file(f"{ctx.message.author.id} a utilisé pong.", ctx)

    @bot.command(
        aliases=["s"],
        help="Dire ce que tu veux",
        enable=True
    )
    async def say(ctx, *a):
        await ctx.send(" ".join(a))
        a = " ".join(a)
        log_file(f"{ctx.message.author.id} a fait dire {a}", ctx)

    @bot.command(
        aliases=["roll"],
        help="Donner un chiffre entre 1 et 6",
        enable=True
    )
    async def dice(ctx):
        number = random.randint(1, 6)
        await ctx.send(str(number))
        log_file(f"{ctx.message.author.id} a lancé le dé et il a donné {number}", ctx)

    @bot.command(
        aliases=["additionner"],
        help="Additionner 2 nombres",
        enable=True
    )
    async def add(ctx, a, b):
        await ctx.send(int(a) + int(b))
        log_file(f"{ctx.message.author.id} a additionné {a} et {b}", ctx)

    @bot.command(
        aliases=["soustraire"],
        help="Soustraire 2 nombres",
        enable=True
    )
    async def sou(ctx, a, b):
        await ctx.send(int(a) - int(b))
        log_file(f"{ctx.message.author.id} a soustrait {a} et {b}", ctx)

    @bot.command(
        aliases=["multiplier"],
        help="Multiplier 2 nombres",
        enable=True
    )
    async def mul(ctx, a, b):
        await ctx.send(int(a) * int(b))
        log_file(f"{ctx.message.author.id} a multiplié {a} et {b}", ctx)

    @bot.command(
        aliases=["diviser"],
        help="Diviser 2 nombres",
        enable=True
    )
    async def div(ctx, a, b):
        await ctx.send(int(a) / int(b))
        log_file(f"{ctx.message.author.id} a divisé {a} et {b}", ctx)

    @bot.command(
        aliases=["bannir"],
        help="Bannir une personne pour une raison",
        enable=True
    )
    async def ban(ctx, who: discord.Member, reason: str):
        for id_ in settings.owner_ids:
            if ctx.message.author.id != id_:
                await who.ban(reason=reason)
                await ctx.send(f"{who.name} a été banni.")
                log_file(f"{who.name} a été banni", ctx)
            else:
                await ctx.send("Vous n'avez pas la permission d'utiliser cette commande!")
                log_file(
                    f"{ctx.message.author.id} a essayé d'utiliser la commande !modnick sans permission.", ctx)

    @bot.command(
        aliases=["mn"],
        help='Changer le nom de l\'utilisateur par "Nom modéré [6 chiffres aléatoires]".',
        enable=True
    )
    async def modnick(ctx, who: discord.Member, reset=False):
        for id_ in settings.owner_ids:
            if ctx.message.author.id != id_:
                if reset == False:
                    log_file(f"Nom de {who.name} modéré.", ctx)
                    await who.edit(nick=f"Nom modéré {random.randint(100000, 999999)}")
                    await ctx.send(f"Nom de {who.mention} changé avec succès!")
                else:
                    log_file(f"Nom de {who.name} réinitialisé.", ctx)
                    await who.edit(nick=None)
                    await ctx.send(f"Nom de {who.mention} réinitialisé avec succès!")
                break
        await ctx.send("Vous n'avez pas la permission d'utiliser cette commande!")
        log_file(f"{ctx.message.author.id} a essayé d'utiliser la commande !modnick sans permission.", ctx)

    @bot.command(
        aliases=["logging"],
        help='Ajouter du texte dans logs/actions.log',
        enable=True,
        hidden=True
    )
    async def log(ctx, *content):
        for id_ in settings.owner_ids:
            if ctx.message.author.id != id_:
                content = " ".join(content)
                log_file(f"(De {ctx.author.id}) : {content}", ctx)
                await ctx.send(f'```Ajout de "{content}" dans logs/actions.log fait avec succès!```')
            else:
                await ctx.send("Vous n'avez pas la permission d'utiliser cette commande!")
                log_file(
                    f"{ctx.message.author.id} a essayé d'utiliser la commande !log sans permission.", ctx)

    @bot.command(
        aliases=["sl"],
        help='Donne une partie où l\'entierté du fichier logs/actions.log.',
        enable=True,
        hidden=True
    )
    async def showlog(ctx, limit="25"):
        for id_ in settings.owner_ids:
            if ctx.message.author.id != id_:
                if limit == "a":
                    await ctx.send(f"```Voici le contenu entier de logs/actions.log```")
                    with open("logs/actions.log") as f:
                        for line in f.readlines():
                            await ctx.send(f"`{line}`")
                else:
                    await ctx.send(f"```Voici les {limit} dernières lignes de logs/actions.log```")
                    num = 0
                    limit = int(limit)
                    with open("logs/actions.log") as f:
                        for line in f.readlines():
                            if num == limit:
                                break
                            else:
                                await ctx.send(f"`{line}`")
                                num += 1
            else:
                await ctx.send("Vous n'avez pas la permission d'utiliser cette commande!")
                log_file(
                    f"{ctx.message.author.id} a essayé d'utiliser la commande !showlog sans permission.", ctx)

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)


if __name__ == "__main__":
    if getpass("Input password : ") == settings.PASSWORD:
        run()
    else:
        print("Wrong password!")
