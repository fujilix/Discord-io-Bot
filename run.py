import discord
import requests
import os
import re
import subprocess
import time

#定義
async def standby():
    await client.change_presence(activity=discord.Game(name='コマンド待機中'))

# 自分のBotのアクセストークンに置き換えてください
TOKEN = '########TOKEN########'
removebgapikey = '########TOKEN########'

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

    if message.content == '/help':
        await message.channel.send('/pic /kiri')

    if message.content == '/cleanup':
        if message.author.guild_permissions.administrator:
            await message.channel.purge()
            await message.channel.send('Clean up!')
            time.sleep(5)
            await message.channel.purge()

        else:
            await message.channel.send('Permission Error')

    if  message.content.startswith('/pic'):
            await message.channel.send('Speed or Quality')
            await client.change_presence(activity=discord.Game(name='Image Processing...'))

            file_name = message.attachments[0].filename
            url = message.attachments[0].url
            print(file_name)
            print(url)
            path = ("image/") + file_name
            outpath = ("image/") + ("output") + file_name
            response = requests.get(url)
            image = response.content
            with open(path, "wb") as aaa:
                aaa.write(image)
            input_image = path
            command = ["waifu2x-caffe-cui.exe", "-force_cudnn 1", "-m noise_scale", "-n 3", "-t 1","--model_dir models/anime_style_art_rgb","-i",input_image,"-o", outpath, "-crop_size 128"]
            await message.channel.send('Processing...')
            subprocess.call(command)
            await message.channel.send(file=discord.File(outpath))



    if message.content.startswith('/cut'):
            await client.change_presence(activity=discord.Game(name='Processing...'))
            file_name = message.attachments[0].filename
            url = message.attachments[0].url
            print(file_name)
            print(url)
            path = ("image/") + file_name
            outpath = ("image/remove/") + ("output") + file_name
            response = requests.get(url)
            image = response.content
            await message.channel.send('Processing...')
            with open(path, "wb") as aaa:
                aaa.write(image)

            print(path)

            response = requests.post(
                'https://api.remove.bg/v1.0/removebg',
                files={'image_file': open(path, 'rb')},
                data={'size': 'auto'},
                headers={'X-Api-Key': removebgapikey},
            )
            await message.channel.send('Processing')
            if response.status_code == requests.codes.ok:

                with open(outpath, 'wb') as out:
                    out.write(response.content)
                    await message.channel.send(file=discord.File(outpath))

            else:
                await message.channel.send('Error Please Check Remove.bg')
                print("Error:", response.status_code, response.text)

client.run(TOKEN)
