import discord
import requests
import os
import re
import subprocess
import time
import configparser
import sys
import asyncio

config = configparser.ConfigParser()

if os.path.isfile('Token.ini'):
    print('設定ファイルが存在します')
    config.read('Token.ini')

    #Config Check
    if config['TOKEN']['discord-bot-token'] == 'TOKEN HERE' or config['DIR']['waifu2x-dir'] == 'waifu2xのディレクトリを指定':
        print('トークンまたはディレクトリを指定してください')
        time.sleep(3)
        sys.exit()
    else:
      TOKEN = config['TOKEN']['discord-bot-token']
      removebgapikey = config['TOKEN']['remove.bg-token']
      waifu2x_dir = config['DIR']['waifu2x-dir']

      if not os.path.exists(waifu2x_dir + '/image'):
          print("処理後のフォルダを作成します。")
          os.mkdir(waifu2x_dir + '/image')
          os.mkdir(waifu2x_dir + '/image/output')
          os.mkdir(waifu2x_dir + '/image/remove')

      else:
          print("処理後のフォルダが存在します。")

      #waifu2x check
      if os.path.isfile(waifu2x_dir + '/waifu2x-caffe-cui.exe'):
          print('waifu2x Ready')
          waifu_ready = 1
      else:
          print('waifu2xがありません。ディレクトリ指定をし直すか、waifu2x-caffeをダウンロードしてください。')
          print('/pic機能がロックされます')
          waifu_ready = 0


else:
    print('設定ファイルが無いため生成します')
    config['TOKEN'] = {
        'discord-bot-token' : 'TOKEN HERE',
        'remove.bg-token' : 'TOKEN HERE'
    }
    config['DIR'] = {
        'waifu2x-dir' : 'waifu2xのディレクトリを指定',
    }

    with open('Token.ini', 'w') as file:
        config.write(file)
    print('設定ファイルにトークンを記入てください')
    time.sleep(3)
    sys.exit( )

# 接続に必要なオブジェクトを生成
client = discord.Client()

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')
# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return

    if message.content =='/ems':
        await message.channel.send('see you!')
        await client.logout()
        print('ログアウト')

    if message.content == '/help':
        await message.channel.send('/pic : waifu2xを使用して画像を高画質化します')
        await message.channel.send('/cut : remove.bgのapiを使用して画像を切り抜きます')

    if message.content == '/cleanup':
        if message.author.guild_permissions.administrator:
            await message.channel.purge(limit=None)
            await message.channel.send('Clean up!')
            await asyncio.sleep(5)
            await message.channel.purge()

        else:
            await message.channel.send('Permission Error')

    if  message.content.startswith('/pic'):
            if waifu_ready == 1:

                file_name = message.attachments[0].filename
                url = message.attachments[0].url
                print(file_name)
                print(url)
                path = waifu2x_dir + ("/image/") + file_name
                outpath = waifu2x_dir + ("/image/") + ("output/") + file_name
                response = requests.get(url)
                image = response.content
                with open(path, "wb") as aaa:
                    aaa.write(image)
                input_image = path
                modeldirect = waifu2x_dir + ("/models/anime_style_art_rgb")
                waifu2x_start = waifu2x_dir + ('/waifu2x-caffe-cui.exe')
                command = [waifu2x_start, "-force_cudnn 1", "-m noise_scale", "-n 3", "-t 1","--model_dir ",modeldirect,"-i",input_image,"-o", outpath,"-crop_size 128"]
                print (command)
                await message.channel.send('Processing...')
                subprocess.call(command)
                await message.channel.send(file=discord.File(outpath))
            else:
                print('waifu2xが正しくインストールされていません。')
                await message.channel.send('waifu2xがインストールされていない、または不正なディレクトリ指定です。bot管理者にお知らせください。')
                await message.channel.send('debug : [waifu2x_dir] = ' + waifu2x_dir)

    if message.content.startswith('/cut'):
            await message.channel.send('Processing...')
            file_name = message.attachments[0].filename
            url = message.attachments[0].url
            print(file_name)
            print(url)
            path = waifu2x_dir + ("/image/") + file_name
            outpath = waifu2x_dir + ("/image/remove/") + file_name
            response = requests.get(url)
            image = response.content
            with open(path, "wb") as aaa:
                aaa.write(image)
            print(path)
            response = requests.post(
                'https://api.remove.bg/v1.0/removebg',
                files={'image_file': open(path, 'rb')},
                data={'size': 'auto'},
                headers={'X-Api-Key': removebgapikey},
            )

            if response.status_code == requests.codes.ok:

                with open(outpath, 'wb') as out:
                    out.write(response.content)
                await message.channel.send(file=discord.File(outpath))
            else:
                await message.channel.send('Error Please Check Remove.bg')
                print("Error:", response.status_code, response.text)

client.run(TOKEN)
