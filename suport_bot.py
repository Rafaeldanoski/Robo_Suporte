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

######################### DATASET #############################################
def load_data():
    df_prod = pd.read_csv('df_prod.csv', sep=';').set_index("date")
    df_prod.index = pd.to_datetime(df_prod.index)
    df_prod.sort_index(ascending=False, inplace=True)
    id_prod = df_prod['id'].to_list()

    resp_ids = [1, 694, 695, 2979, 232, 4127]
    parent_list = df_prod['parent'].unique()

    response = requests.get(api_url)
    response_json = response.json()

    global df_comments, df_pending, pages_count
    pages_count = response.headers['X-WP-TotalPages']
    df_comments = pd.DataFrame(response_json).set_index("date")
    df_comments.index = pd.to_datetime(df_comments.index)
    df_comments.sort_index(ascending=True, inplace=True)

    df_comments['groups'] = [df_comments['link'][x].split('/') for x in range(len(df_comments))]

    df_comments['course'] = ''
    df_comments['lesson'] = ''
    df_comments['topic'] = ''
    for i in range(len(df_comments)):
        df_comments['course'][i] = df_comments['groups'][i][4]
        try:
            df_comments['lesson'][i] = df_comments['groups'][i][6]
        except:
            df_comments['lesson'][i] = ''
        try:
            df_comments['topic'][i] = df_comments['groups'][i][8]
        except:
            df_comments['topic'][i] = ''

    dsml = ['machine-learning-ai-com-python', 'projetos-de-data-science']
    quant = ['trading-quantitativo']
    dip = ['dashboards-interativos-com-python','mybudget-acesso-livre','5-6-callbacks','4-5-o-metodo-update_layout','5-5-decorators','dashboards','projetos-dashboards']
    aut = ['automatizando-tarefas-com-python', 'web-scraping-extraindo-dados-da-web']

    resp_dip = ['<@343467764909998082>', '<@279056011233460224>']
    resp_aut = ['<@343467764909998082>', '<@279056011233460224>', '<@695370056787296410>', '<@671007727232745501>', '<@993487560431120464>']
    resp_dsml = ['<@695370056787296410>', '<@671007727232745501>', '<@993487560431120464>']
    resp_ps = ['<@695370056787296410>', '<@671007727232745501>', '<@993487560431120464>', '<@690175403876548673>']

    df_comments['trail'] = ''
    df_comments['resp'] = ''
    for i in range(len(df_comments)):
        if df_comments['course'][i] in dsml:
            df_comments['trail'][i] = 'DSML'
            if df_comments['parent'][i] == 0:
                last_resp = df_prod[(df_prod['parent']==0) & (df_prod['trail']=='DSML')]['resp'][0]
                try:
                    df_comments['resp'][i] = resp_dsml[(resp_dsml.index(last_resp))+1]
                except:
                    df_comments['resp'][i] = resp_dsml[0]
            else:
                try:
                    df_comments['resp'][i] = df_prod[df_prod['id']==df_comments['parent'][i]]['resp'][0]
                except:
                    df_comments['resp'][i] = resp_dsml[0]

        elif df_comments['course'][i] in quant:
            df_comments['trail'][i] = 'QUANT'
            df_comments['resp'][i] = '<@690175403876548673>'

        elif df_comments['course'][i] in dip:
            df_comments['trail'][i] = 'DIP'
            if df_comments['parent'][i] == 0:
                last_resp = df_prod[(df_prod['parent']==0) & (df_prod['trail']=='DIP')]['resp'][0]
                try:
                    df_comments['resp'][i] = resp_dip[(resp_dip.index(last_resp))+1]
                except:
                    df_comments['resp'][i] = resp_dip[0]
            else:
                try:
                    df_comments['resp'][i] = df_prod[df_prod['id']==df_comments['parent'][i]]['resp'][0]
                except:
                    df_comments['resp'][i] = resp_dip[0]

        elif df_comments['course'][i] in aut:
            df_comments['trail'][i] = 'AUT'
            if df_comments['parent'][i] == 0:
                last_resp = df_prod[(df_prod['parent']==0) & (df_prod['trail']=='AUT')]['resp'][0]
                try:
                    df_comments['resp'][i] = resp_aut[(resp_aut.index(last_resp))+1]
                except:
                    df_comments['resp'][i] = resp_aut[0]
            else:
                try:
                    df_comments['resp'][i] = df_prod[df_prod['id']==df_comments['parent'][i]]['resp'][0]
                except:
                    df_comments['resp'][i] = resp_aut[0]

        else:
            df_comments['trail'][i] = 'Python Starter'
            if df_comments['parent'][i] == 0:
                last_resp = df_prod[(df_prod['parent']==0) & (df_prod['trail']=='Python Starter')]['resp'][0]
                try:
                    df_comments['resp'][i] = resp_ps[(resp_ps.index(last_resp))+1]
                except:
                    df_comments['resp'][i] = resp_ps[0]
            else:
                try:
                    df_comments['resp'][i] = df_prod[df_prod['id']==df_comments['parent'][i]]['resp'][0]
                except:
                    df_comments['resp'][i] = resp_ps[0]

        if df_comments['id'][i] not in id_prod:
            df_prod = df_prod.append(df_comments[df_comments['id']==df_comments['id'][i]])
            df_prod.sort_index(ascending=False, inplace=True)
            parent_list = df_prod['parent'].unique()

    df_prod.sort_index(ascending=False, inplace=True)

    df_pending = df_prod[(~df_prod['id'].isin(parent_list)) & (~df_prod['author'].isin(resp_ids))]

    df_prod.to_csv('df_prod.csv', sep=';')

load_data()

comments = df_pending['id'].to_list()

################################# FULL DATASET ####################################
# df_comments_full = pd.DataFrame()
# for i in range(int(pages_count)):
#     api_url_full = 'https://asimov.academy/wp-json/wp/v2/comments?page='+str((i+1))+'&per_page=100'
#     response_full = requests.get(api_url_full)
#     response_json_full = response_full.json()
#     df_comments_page = pd.DataFrame(response_json_full).set_index("date")
#     df_comments_page.index = pd.to_datetime(df_comments_page.index)
#     df_comments_full = df_comments_full.append(df_comments_page)

# df_comments_full['groups'] = [df_comments_full['link'][x].split('/') for x in range(len(df_comments_full))]
# df_comments_full['course'] = ''
# df_comments_full['lesson'] = ''
# df_comments_full['topic'] = ''
# for i in range(len(df_comments_full)):
#     df_comments_full['course'][i] = df_comments_full['groups'][i][4]
#     try:
#         df_comments_full['lesson'][i] = df_comments_full['groups'][i][6]
#     except:
#         df_comments_full['lesson'][i] = ''
#     try:
#         df_comments_full['topic'][i] = df_comments_full['groups'][i][8]
#     except:
#         df_comments_full['topic'][i] = ''

# dsml = ['machine-learning-ai-com-python', 'projetos-de-data-science']
# quant = ['trading-quantitativo']
# dip = ['dashboards-interativos-com-python', 'mybudget-acesso-livre']

# df_comments_full['trail'] = ''
# for i in range(len(df_comments_full)):
#     if df_comments_full['course'][i] in dsml:
#         df_comments_full['trail'][i] = 'DSML'
#     elif df_comments_full['course'][i] in quant:
#         df_comments_full['trail'][i] = 'QUANT'
#     elif df_comments_full['course'][i] in dip:
#         df_comments_full['trail'][i] = 'DIP'
#     else:
#         df_comments_full['trail'][i] = 'Python Starter'

################################ BOT DISCORD ####################################
import hikari
import lightbulb

bot = lightbulb.BotApp(
    token=open('token.txt', 'r').read(), 
    default_enabled_guilds=(int(open('ds_channel_id.txt', 'r').read())))


@bot.listen(hikari.StartedEvent)
async def on_started(event):
    while True:
        load_data()
        for i in df_pending['id'].to_list():
            if i not in comments:
                channel = await bot.rest.fetch_channel('1069720089202544650')
                parsed_html = BeautifulSoup(df_pending[df_pending['id']==i]['content'][0]['rendered'], features="lxml")
                await channel.send(f" {df_pending[df_pending['id']==i]['resp'][0]} \n \
                                    *Novo Comentário!* \n \
                                    Trilha: {df_pending[df_pending['id']==i]['trail'][0]} \n \
                                    Mensagem: {parsed_html.body.findAll('p')[0].text if len(parsed_html.body.findAll('p')) > 0 else ''} \n \
                                    {parsed_html.body.findAll('p')[1].text if len(parsed_html.body.findAll('p')) > 1 else ''} \n \
                                    Acesse --> {df_pending[df_pending['id']==i]['link'][0]} ")
                comments.append(i)
            time.sleep(5)
        time.sleep(60)



bot.run()