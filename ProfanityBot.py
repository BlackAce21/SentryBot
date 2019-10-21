import discord
import json
from better_profanity import profanity
from ConfigHandler import ConfigManager, ExceptionsManager


class NameScan:

    def __init__(self):
        self.default_words = open('default_words.txt').read().splitlines()

    def scan_account_names(self, guild):
        members = guild.members
        results = {}
        profanity.load_censor_words(self.default_words)
        for member in members:
            if member.name in exceptions['exempt']:
                continue
            if profanity.contains_profanity(member.name) or member.name in exceptions['restricted']:
                results[member.id] = member.name
        return results


class SentryBot(discord.Client):

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!sbhere'):
            config['Settings']['channel'] = message.channel.id
            await message.channel.send('Channel output set to here.')

        if message.channel.id != config['Settings']['channel'] and config['Settings']['channel'] != -1:
            return

        if message.content.startswith('!sbsettings'):
            return

        if message.content.startswith('!sbhello'):
            await message.channel.send('Hello {0.author.mention}'.format(message))

        if message.content.startswith('!sbscan'):
            await message.channel.send('{0.author.mention} Initiating name scan...'.format(message))
            scan_results = scanner.scan_account_names(message.guild)
            for k, v in scan_results.items():
                await message.channel.send('Found improper name, ' + '||' + v + '||' + ' Obfuscated: ||' +
                                           profanity.censor(v) + '||' + ' - No Action Taken')
            await message.channel.send('Scan Complete! Found ' + str(len(scan_results)) + ' bad user names.')

        if message.content.startswith('!sbcreatelist'):
            members = message.guild.members
            await message.channel.send('Pulling member list information...')
            data = {}
            for member in members:
                data[member.id] = []
                data[member.id].append({
                    'name': member.name,
                    'display_name': member.display_name
                })

            with open('members.json', 'w') as outfile:
                json.dump(data, outfile)
            await message.channel.send('Member list dumped to JSON')


# init config and exception
configManager = ConfigManager()
config = configManager.get_config()

exceptionsManager = ExceptionsManager()
exceptions = exceptionsManager.get_exceptions()

# init scanner and client
scanner = NameScan()
client = SentryBot()

# establish client information and run
client.run()
