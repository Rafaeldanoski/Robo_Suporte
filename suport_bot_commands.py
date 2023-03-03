########################### IMPORTS ################################################
import requests
import base64
import pandas as pd
from datetime import datetime, timedelta
import time
from bs4 import BeautifulSoup
import ast
import warnings
warnings.filterwarnings("ignore")

############################ API #################################################
wp_user = "rafael"
wp_password = open('python_api_password.txt').read()

wp_credentials = wp_user + ":" + wp_password
wp_token = base64.b64encode(wp_credentials.encode())
wp_header = {'Authorization': 'Basic ' + wp_token.decode('utf-8')}

api_url = 'https://asimov.academy/wp-json/wp/v2/comments?page=1&per_page=100'

response = requests.get(api_url)
pages_count = response.headers['X-WP-TotalPages']

def load_data():
    global df_pending_week, df_prod
    df_prod = pd.read_csv('df_prod.csv', sep=';').set_index("date")
    df_prod.index = pd.to_datetime(df_prod.index)

    resp_ids = [1, 694, 695, 2979, 232, 4127]
    parent_list = df_prod['parent'].unique()

    d = datetime(2023,2,14)
    df_pending_week = df_prod[(df_prod.index > d) & (~df_prod['id'].isin(parent_list)) & (~df_prod['author'].isin(resp_ids)) & (df_prod['id']!=999)]
    
################################ BOT DISCORD ####################################
# import hikari
import lightbulb

bot = lightbulb.BotApp(
    token=open('token.txt', 'r').read(), 
    default_enabled_guilds=(int(open('ds_channel_id.txt', 'r').read())))

############################### COMANDOS ################################################################
@bot.command
@lightbulb.command('msg_sup', 'Saudação Bot Suporte')
@lightbulb.implements(lightbulb.SlashCommand)
async def hello(ctx):
    await ctx.respond('*Its Alive!*')

#Comentários em aberto
@bot.command
@lightbulb.command('pending_msg', 'Comentários em aberto')
@lightbulb.implements(lightbulb.SlashCommand)
async def pending_msg(ctx):
    load_data()
    if len(df_pending_week) > 0:
        adriano = df_prod[df_prod['resp']=='<@671007727232745501>']['id'].to_list()
        juliano = df_prod[df_prod['resp']=='<@993487560431120464>']['id'].to_list()
        mateus = df_prod[df_prod['resp']=='<@343467764909998082>']['id'].to_list()
        rafael = df_prod[df_prod['resp']=='<@695370056787296410>']['id'].to_list()
        tadewald = df_prod[df_prod['resp']=='<@690175403876548673>']['id'].to_list()
        vanzelotti = df_prod[df_prod['resp']=='<@279056011233460224>']['id'].to_list()
        
        await ctx.respond(f" *Temos {len(df_pending_week)} Comentários em Aberto!* \n \
                            Python Starter: {len(df_pending_week[df_pending_week['trail']=='Python Starter'])} \n \
                            DIP: {len(df_pending_week[df_pending_week['trail']=='DIP'])} \n \
                            AUT: {len(df_pending_week[df_pending_week['trail']=='AUT'])} \n \
                            DSML: {len(df_pending_week[df_pending_week['trail']=='DSML'])} \n \
                            QUANT: {len(df_pending_week[df_pending_week['trail']=='QUANT'])} \n\n \
                            Adri: {len(df_pending_week[df_pending_week['id'].isin(adriano)])} \n \
                            Mateus: {len(df_pending_week[df_pending_week['id'].isin(mateus)])} \n \
                            Juli: {len(df_pending_week[df_pending_week['id'].isin(juliano)])} \n \
                            Rafa: {len(df_pending_week[df_pending_week['id'].isin(rafael)])} \n \
                            R. Tadewald: {len(df_pending_week[df_pending_week['id'].isin(tadewald)])} \n \
                            R. Vanzelotti: {len(df_pending_week[df_pending_week['id'].isin(vanzelotti)])} ")
        
    else:
        await ctx.respond(f" *Parabéns! Todos os comentários foram respondidos.*")

#Dump pending
@bot.command
@lightbulb.command('dump_pending', 'Todos os Comentários em aberto')
@lightbulb.implements(lightbulb.SlashCommand)
async def dump_pending(ctx):
    load_data()
    df_pending_week.sort_values(by='trail', inplace=True)
    for i in df_pending_week['id'].to_list():
        parsed_html = BeautifulSoup(ast.literal_eval(df_pending_week[df_pending_week['id']==i]['content'][0])['rendered'], features="lxml")
        await ctx.respond(f" {df_prod[df_prod['id']==i]['resp'][0]} \n \
                                    *Novo Comentário!* \n \
                                    Trilha: {df_pending_week[df_pending_week['id']==i]['trail'][0]} \n \
                                    Mensagem: {parsed_html.body.findAll('p')[0].text if len(parsed_html.body.findAll('p')) > 0 else ''} \n \
                                    {parsed_html.body.findAll('p')[1].text if len(parsed_html.body.findAll('p')) > 1 else ''} \n \
                                    Acesse --> {df_pending_week[df_pending_week['id']==i]['link'][0]} ")
        time.sleep(5)


#Dump my pending
@bot.command
@lightbulb.command('my_comments', 'Meus comentários em aberto')
@lightbulb.implements(lightbulb.SlashCommand)
async def dump_my_pending(ctx):
    load_data()
    resp = f"<@{ctx.user.id}>"
    df_prod_my_list = df_prod[df_prod['resp']==resp]['id'].to_list()
    if len(df_pending_week[df_pending_week['id'].isin(df_prod_my_list)]['id'].to_list()) > 0:
        for i in df_pending_week[df_pending_week['id'].isin(df_prod_my_list)]['id'].to_list():
            parsed_html = BeautifulSoup(ast.literal_eval(df_pending_week[df_pending_week['id']==i]['content'][0])['rendered'], features="lxml")
            await ctx.respond(f" <@{ctx.user.id}> *Novo Comentário!* \n \
                                        Trilha: {df_pending_week[df_pending_week['id']==i]['trail'][0]} \n \
                                        Mensagem: {parsed_html.body.findAll('p')[0].text if len(parsed_html.body.findAll('p')) > 0 else ''} \n \
                                        {parsed_html.body.findAll('p')[1].text if len(parsed_html.body.findAll('p')) > 1 else ''} \n \
                                        Acesse --> {df_pending_week[df_pending_week['id']==i]['link'][0]} ")
            time.sleep(5)
    else:
        await ctx.respond(f" *Parabéns <@{ctx.user.id}>! Todos os seus comentários foram respondidos.*")


bot.run()