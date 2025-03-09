import discord
from discord.ext import commands, tasks
import random
import os
from datetime import timedelta

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Dicionário para armazenar o saldo dos usuários
saldo_usuarios = {}

# Dicionário para armazenar o dinheiro no banco dos usuários
banco_usuarios = {}

# ID do usuário com permissões especiais (você)
ADMIN_ID = 616018693016649858

# Variáveis para armazenar o próximo resultado
proximo_resultado_cara_coroa = None
proximo_numero_premiado = None

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} está online!')
    ganho_automatico.start()  # Inicia a tarefa de ganho automático

@tasks.loop(minutes=3)  # Executa a cada 3 minutos
async def ganho_automatico():
    for user_id in saldo_usuarios:
        saldo_usuarios[user_id] += 10
    print("Todos os usuários receberam 10 reais.")

@bot.command(name="ajuda")
async def ajuda(ctx):
    ajuda_msg = f"""
    **Comandos disponíveis:**
    !depositar <quantia> - Deposita uma quantia do seu saldo para o banco.
    !apostar <quantia> <cara/coroa> - Aposta uma quantia do banco em cara ou coroa.
    !numeros <quantia> <número de 1 a 5> - Aposta uma quantia do banco em um número de 1 a 5.
    !saldo - Mostra seu saldo atual e o dinheiro no banco.
    !sacar <quantia> - Saca uma quantia do banco para o seu saldo.
    !ajuda - Mostra esta mensagem de ajuda.
    """
    await ctx.send(f"{ctx.author.mention}, {ajuda_msg}")

@bot.command(name="h")
async def ajuda_adm(ctx):
    # Verifica se o usuário é o administrador
    if ctx.author.id != ADMIN_ID:
        await ctx.send(f"{ctx.author.mention}, você não tem permissão para usar este comando.")
        return

    ajuda_adm_msg = f"""
    **Comandos de Administração:**
    !d - Mostra o próximo resultado de cara/coroa ou número premiado.
    !add @usuário <quantia> - Adiciona uma quantia ao saldo de um usuário.
    !reset @usuário - Reseta o saldo e o banco de um usuário.
    """
    await ctx.send(f"{ctx.author.mention}, {ajuda_adm_msg}")

@bot.command(name="depositar")
async def depositar(ctx, quantia: int):
    user_id = ctx.author.id

    # Verifica se o usuário já tem saldo inicial
    if user_id not in saldo_usuarios:
        saldo_usuarios[user_id] = 100

    # Verifica se a quantia é válida
    if quantia < 10:
        await ctx.send(f"{ctx.author.mention}, a quantia mínima para depositar é 10 reais.")
        return

    if quantia > saldo_usuarios[user_id]:
        await ctx.send(f"{ctx.author.mention}, você não tem saldo suficiente para depositar essa quantia.")
        return

    # Atualiza o saldo e o banco do usuário
    saldo_usuarios[user_id] -= quantia
    if user_id not in banco_usuarios:
        banco_usuarios[user_id] = 0
    banco_usuarios[user_id] += quantia

    await ctx.send(f"{ctx.author.mention}, você depositou {quantia} reais no banco. Seu saldo atual é {saldo_usuarios[user_id]} reais e seu banco tem {banco_usuarios[user_id]} reais.")

@bot.command(name="apostar")
async def apostar(ctx, quantia: int, escolha: str):
    user_id = ctx.author.id

    # Verifica se o usuário tem dinheiro no banco
    if user_id not in banco_usuarios or banco_usuarios[user_id] < quantia:
        await ctx.send(f"{ctx.author.mention}, você não tem saldo suficiente no banco para apostar essa quantia.")
        return

    # Verifica se a escolha é válida
    if escolha.lower() not in ["cara", "coroa"]:
        await ctx.send(f"{ctx.author.mention}, escolha inválida. Escolha entre 'cara' ou 'coroa'.")
        return

    # Define o próximo resultado (se não estiver definido)
    global proximo_resultado_cara_coroa
    if proximo_resultado_cara_coroa is None:
        proximo_resultado_cara_coroa = random.choice(["cara", "coroa"])

    # Verifica se o usuário ganhou ou perdeu
    if escolha.lower() == proximo_resultado_cara_coroa:
        banco_usuarios[user_id] += quantia
        await ctx.send(f"{ctx.author.mention}, você ganhou {quantia} reais! O resultado foi {proximo_resultado_cara_coroa}. Seu saldo no banco agora é {banco_usuarios[user_id]} reais.")
    else:
        banco_usuarios[user_id] -= quantia
        await ctx.send(f"{ctx.author.mention}, você perdeu {quantia} reais! O resultado foi {proximo_resultado_cara_coroa}. Seu saldo no banco agora é {banco_usuarios[user_id]} reais.")

    # Gera o próximo resultado automaticamente
    proximo_resultado_cara_coroa = random.choice(["cara", "coroa"])

@bot.command(name="numeros")
async def numeros(ctx, quantia: int, numero: int):
    user_id = ctx.author.id

    # Verifica se o usuário tem dinheiro no banco
    if user_id not in banco_usuarios or banco_usuarios[user_id] < quantia:
        await ctx.send(f"{ctx.author.mention}, você não tem saldo suficiente no banco para apostar essa quantia.")
        return

    # Verifica se o número é válido
    if numero < 1 or numero > 5:
        await ctx.send(f"{ctx.author.mention}, escolha inválida. Escolha um número de 1 a 5.")
        return

    # Define o próximo número premiado (se não estiver definido)
    global proximo_numero_premiado
    if proximo_numero_premiado is None:
        proximo_numero_premiado = random.randint(1, 5)

    # Calcula a diferença entre o número escolhido e o premiado
    diferenca = abs(numero - proximo_numero_premiado)

    # Define o multiplicador com base na diferença
    if diferenca == 0:
        multiplicador = 2  # Ganha o dobro
    elif diferenca == 1:
        multiplicador = 1  # Ganha o valor apostado
    elif diferenca == 2:
        multiplicador = 0.5  # Perde metade
    else:
        multiplicador = 0  # Perde tudo

    # Calcula o resultado da aposta
    ganho = int(quantia * multiplicador)
    banco_usuarios[user_id] += ganho - quantia

    # Resposta com o resultado
    await ctx.send(f"{ctx.author.mention}, o número premiado foi {proximo_numero_premiado}. Você {'ganhou' if ganho > 0 else 'perdeu'} {abs(ganho)} reais. Seu saldo no banco agora é {banco_usuarios[user_id]} reais.")

    # Gera o próximo número premiado automaticamente
    proximo_numero_premiado = random.randint(1, 5)

@bot.command(name="saldo")
async def saldo(ctx):
    user_id = ctx.author.id

    # Verifica se o usuário já tem saldo inicial
    if user_id not in saldo_usuarios:
        saldo_usuarios[user_id] = 100

    await ctx.send(f"{ctx.author.mention}, seu saldo atual é {saldo_usuarios[user_id]} reais e seu banco tem {banco_usuarios.get(user_id, 0)} reais.")

@bot.command(name="sacar")
async def sacar(ctx, quantia: int):
    user_id = ctx.author.id

    # Verifica se o usuário tem dinheiro no banco
    if user_id not in banco_usuarios or banco_usuarios[user_id] < quantia:
        await ctx.send(f"{ctx.author.mention}, você não tem saldo suficiente no banco para sacar essa quantia.")
        return

    # Atualiza o saldo e o banco do usuário
    banco_usuarios[user_id] -= quantia
    saldo_usuarios[user_id] += quantia

    await ctx.send(f"{ctx.author.mention}, você sacou {quantia} reais do banco. Seu saldo atual é {saldo_usuarios[user_id]} reais e seu banco tem {banco_usuarios[user_id]} reais.")

@bot.command(name="d")
async def ver_proximo_resultado(ctx):
    # Verifica se o usuário é o administrador
    if ctx.author.id != ADMIN_ID:
        await ctx.send(f"{ctx.author.mention}, você não tem permissão para usar este comando.")
        return

    # Mostra o próximo resultado
    global proximo_resultado_cara_coroa, proximo_numero_premiado
    if proximo_resultado_cara_coroa is not None:
        await ctx.send(f"{ctx.author.mention}, o próximo resultado de cara/coroa será: **{proximo_resultado_cara_coroa}**.")
    elif proximo_numero_premiado is not None:
        await ctx.send(f"{ctx.author.mention}, o próximo número premiado será: **{proximo_numero_premiado}**.")
    else:
        await ctx.send(f"{ctx.author.mention}, nenhum próximo resultado foi definido ainda.")

@bot.command(name="add")
async def adicionar_dinheiro(ctx, user: discord.User, quantia: int):
    # Verifica se o usuário é o administrador
    if ctx.author.id != ADMIN_ID:
        await ctx.send(f"{ctx.author.mention}, você não tem permissão para usar este comando.")
        return

    # Adiciona a quantia ao saldo do usuário
    if user.id not in saldo_usuarios:
        saldo_usuarios[user.id] = 100
    saldo_usuarios[user.id] += quantia

    await ctx.send(f"{ctx.author.mention}, adicionados {quantia} reais ao saldo de {user.mention}. Novo saldo: {saldo_usuarios[user.id]} reais.")

@bot.command(name="reset")
async def resetar_usuario(ctx, user: discord.User):
    # Verifica se o usuário é o administrador
    if ctx.author.id != ADMIN_ID:
        await ctx.send(f"{ctx.author.mention}, você não tem permissão para usar este comando.")
        return

    # Reseta o saldo e o banco do usuário
    saldo_usuarios[user.id] = 100
    banco_usuarios[user.id] = 0

    await ctx.send(f"{ctx.author.mention}, o saldo e o banco de {user.mention} foram resetados. Saldo: 100 reais, Banco: 0 reais.")

# Substitua 'SEU_TOKEN_AQUI' pelo token do seu bot
bot.run('MTM0ODA4OTAwOTgxMzA2MTY0Mw.Gof5ef.0Tiziz_2UCT9QY96oa68BNlEHiI3FI3c6E6cbI')
