import discord
from CommandHandler import CommandExecutor, NameScan
from ConfigHandler import ConfigManager

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

        if message.content.startswith('!sb'):
            commandExecutor = CommandExecutor(config, configManager, scanner)
            await commandExecutor.command_processing(message)

    async def on_member_join(self, member):
        if config.getboolean('Settings', 'auto_kick'):
            await scanner.scan_single_name(member.guild, member)

    async def on_member_update(self, before, after):
        # Make sure there is a nickname for this event
        if after.nick == None:
            return
        # Make sure the nickname changed to something new
        if before.nick == after.nick:
            return

        print("Member updated for " + str(before.nick) + " to " + after.nick)

        if config.getboolean('Settings', 'name_change_protection'):
            await scanner.nickname_scanner(before, after)


# init client
client = SentryBot()

configManager = ConfigManager()
config = configManager.config
scanner = NameScan(config)
token = config.get('Settings', 'token')

if token == 'default':
    token = input("Please input token:")
    config['Settings']['token'] = token
    configManager.save_config()

# establish client information and run
client.run(token)
