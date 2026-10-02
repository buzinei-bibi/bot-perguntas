import discord

from discord.ext import commands
from quiz_cyber import QUIZZES
from database import (  # type: ignore[import-not-found]
    criar_usuario,
    salvar_resposta,
    ranking
)

token = ""

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


quiz_atual = None
mensagem_quiz_atual = None
respostas = {}


class QuizView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    async def responder(
        self,
        interaction: discord.Interaction,
        alternativa: str
    ):

        global quiz_atual

        if quiz_atual is None:
            await interaction.response.send_message(
                "não há nenhum quiz ativo.",
                ephemeral=True
            )
            return

        usuario = interaction.user

        if usuario.id in respostas:
            await interaction.response.send_message(
                "você já respondeu este quiz!",
                ephemeral=True
            )
            return

        criar_usuario(
            usuario.id,
            usuario.display_name
        )

        respostas[usuario.id] = alternativa

        await interaction.response.send_message(
            f"você respondeu **{alternativa}**!",
            ephemeral=True
        )

    @discord.ui.button(
        label="a",
        style=discord.ButtonStyle.secondary
    )
    async def botao_a(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button
    ):
        await self.responder(
            interaction,
            "a"
        )

    @discord.ui.button(
        label="b",
        style=discord.ButtonStyle.secondary
    )
    async def botao_b(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button
    ):
        await self.responder(
            interaction,
            "b"
        )

    @discord.ui.button(
        label="c",
        style=discord.ButtonStyle.secondary
    )
    async def botao_c(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button
    ):
        await self.responder(
            interaction,
            "c"
        )

    @discord.ui.button(
        label="d",
        style=discord.ButtonStyle.secondary
    )
    async def botao_d(
        self,
        interaction: discord.Interaction,
        _button: discord.ui.Button
    ):
        await self.responder(
            interaction,
            "d"
        )


async def enviar_quiz(canal):

    global quiz_atual, mensagem_quiz_atual

    quiz_atual = QUIZZES[0]
    respostas.clear()

    quiz = quiz_atual

    embed = discord.Embed(
        title=(
            f"quiz #{quiz['id']} — "
            f"{quiz['categoria']}"
        ),
        description=(
            f"🟢 **dificuldade:** "
            f"{quiz['dificuldade']}\n\n"
            f"**{quiz['texto']}**\n\n"
            f"a) {quiz['alternativas']['a']}\n"
            f"b) {quiz['alternativas']['b']}\n"
            f"c) {quiz['alternativas']['c']}\n"
            f"d) {quiz['alternativas']['d']}\n\n"
            "👇 clique em um botão para responder.\n\n"
            "⏰ a resposta será revelada mais tarde!"
        )
    )

    mensagem_quiz_atual = await canal.send(
        embed=embed,
        view=QuizView()
    )


async def revelar_quiz(canal):

    global quiz_atual, mensagem_quiz_atual

    if quiz_atual is None:
        await canal.send(
            "não há nenhum quiz ativo."
        )
        return

    quiz = quiz_atual
    correta = quiz["correta"]

    for usuario_id, resposta in respostas.items():

        acertou = resposta == correta

        salvar_resposta(
            usuario_id,
            quiz["id"],
            resposta,
            acertou
        )

    # fecha a pergunta original: tira as alternativas e os botões
    if mensagem_quiz_atual is not None:
        embed_fechado = discord.Embed(
            title=(
                f"quiz #{quiz['id']} — "
                f"{quiz['categoria']}"
            ),
            description=(
                f"🟢 **dificuldade:** "
                f"{quiz['dificuldade']}\n\n"
                f"**{quiz['texto']}**\n\n"
                "🔒 quiz encerrado — veja a resposta abaixo."
            )
        )
        try:
            await mensagem_quiz_atual.edit(
                embed=embed_fechado,
                view=None
            )
        except discord.HTTPException:
            pass

    # erradas riscadas, correta em negrito + ✅ (sem risco)
    texto_alternativas = ""

    for letra, texto in quiz["alternativas"].items():

        letra_maiuscula = letra.upper()

        if letra == correta:
            texto_alternativas += (
                f"**{letra_maiuscula}) {texto}** ✅\n"
            )
        else:
            texto_alternativas += (
                f"~~{letra_maiuscula}) {texto}~~\n"
            )

    dados_ranking = ranking(3)

    top = ""

    medalhas = {
        1: "🥇",
        2: "🥈",
        3: "🥉"
    }

    for posicao, (
        usuario_id,
        nome_salvo,
        pontos
    ) in enumerate(
        dados_ranking,
        start=1
    ):

        top += (
            f"{medalhas[posicao]} "
            f"<@{usuario_id}> — "
            f"**{pontos} pts**\n"
        )

    if not top:
        top = "ainda não há pontuação."

    embed = discord.Embed(
        title=(
            f"✅ resposta — "
            f"quiz #{quiz['id']} "
            f"({quiz['categoria']})"
        ),
        description=(
            f"{texto_alternativas}\n"
            f"**explicação:** "
            f"{quiz['explicacao']}\n\n"
            f"🏆 **ranking:**\n"
            f"{top}"
        )
    )

    await canal.send(
        embed=embed
    )

    quiz_atual = None
    mensagem_quiz_atual = None
    respostas.clear()


@bot.command()
async def pergunta(ctx):

    await enviar_quiz(
        ctx.channel
    )


@bot.command()
async def resposta(ctx):

    await revelar_quiz(
        ctx.channel
    )


@bot.event
async def on_ready():

    print(
        f"bot conectado como {bot.user}"
    )

bot.run("")