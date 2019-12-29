import discord
from better_profanity import profanity
from ConfigHandler import ConfigManager, ExceptionsManager


class CommandExecutor:

    def __init__(self, globalConfig, globalConfigManager, globalScanner):
        self.config = globalConfig
        self.configManager = globalConfigManager
        self.scanner = globalScanner

    async def command_processing(self, message):
        # Get log output channel from config
        logchannel = self.config.getint('Settings', 'channel')

        # Establish permissions of the command sender
        permissions = message.author.permissions_in(message.channel)

        if not permissions.manage_nicknames:
            await message.channel.send("You don't have permission to use commands for this bot")
            return
        # End Permissions

        # Send help wall-o-text
        if message.content.startswith('!sbhelp'):
            await message.channel.send("```Welcome to SentryBot designed by Black Ace of the ProsperCraft Network \n"
                                       "\n"
                                       "This help menu should get you get started and teach you what you need to know to use this bot effectively. "
                                       "Command structure is designed for easy logging of activity within a channel but having a log output channel is not required, the bot will simply run silently if no channel is set as the logging channel. "
                                       "All activity is audited by discord anyway so it is up to you to use a text channel. Log output uses spoiler text to prevent over the shoulder incidents with children of adult staff members.\n"
                                       "\n"
                                       "Why kick and not ban? Just to answer this foreseeable question. Discord has 2 names associated with an account per server. The account name and the server nick name. It is possible to change both of these. "
                                       "The default kick message actually contains a link showing how to do that (check your default.ini config if you changed your message already) in the interest of not having to unban people every other day, "
                                       "I felt it was easier to have the system kick them until their name is appropriate. So I designed it to be able to do just that.\n"
                                       "\n"
                                       "What if I want to add more words? This bot will be packaged with a manual wordlist called simply default_words.txt, simply add whatever words you want to add to that list of words. "
                                       "The system pulls out one word per line when it starts up so make sure to restart the bot and you should be just fine.\n"
                                       "\n"
                                       "Who has permission to use these commands? The permission associated with this bot is the Manage Nicknames permission. Anyone with that permission can use the bot commands. "
                                       "I figure if they are allowed to change peoples nicknames, they are probably allowed to interact with a bot like this.\n"
                                       "```")
            await message.channel.send("```Commands: \n"
                                       "\n"
                                       "!sbhere: Sets the current channel this command is run in as the log output channel\n"
                                       "\n"
                                       "!sbclear: Clears the log output channel (sets it as -1 on the config side)\n"
                                       "\n"
                                       "!sbtoggle <Options:--auto-kick|--nickname-prot>: Toggles functionality to auto kick new joins with vulgar names, and protection for nickname changes per server\n"
                                       "\n"
                                       "!sbmessage <Options:-k|-w>: Sets the message to be displayed in a DM to the user when they are kicked, or publicly when they join the server, does not display welcome message if the user has a bad name. Welcome message functionality should be disabled in other bots for this to be effective. \n"
                                       "\n"
                                       "!sbstatus: Displays setting information of the bot\n"
                                       "\n"
                                       "!sbscan <Optional:-k>: A manual scan for all current members of the server. Will output to the current channel the command is used in if no log channel is set, will NOT output at all if one is set. You can run this command without any options to simply scan for bad names or add the -k to kick every player it finds. Also displays what was detected."
                                       "```")
            await message.channel.send("```Contacting the author: \n"
                                       "Any requests for features or help should be directed to Black Ace#8725 via discord or emailed to me at the1blackace21@gmail.com\n"
                                       "I do not check my email frequently however so discord really is the better option.```")

        # Set log channel setting
        if message.content.startswith('!sbhere'):
            self.config['Settings']['channel'] = str(message.channel.id)
            self.configManager.save_config()
            await message.channel.send('Log channel output set to here, commands will also now only be accepted here.')
            return

        # Clear log channel setting
        if message.content.startswith('!sbclear'):
            self.config['Settings']['channel'] = str(-1)
            self.configManager.save_config()
            await message.channel.send('Log channel output cleared, using any channel for commands.')
            return

        # Commands beyond this point will not output if a channel is set and the command is run in the wrong channel
        if message.channel.id != logchannel and logchannel != -1:
            print('Not proper channel, no output.')
            return

        # Toggle options for autokick and nickname protection
        if message.content.startswith('!sbtoggle'):
            # Handle toggle for auto kick
            if '--auto-kick' in message.content:
                current = self.config.getboolean('Settings', 'auto_kick')
                self.config['Settings']['auto_kick'] = str(not current)
                self.configManager.save_config()
                await message.channel.send('Auto kick has been ' + ('enabled' if not current else 'disabled'))

            # Handle toggle for nickname protection
            if '--nickname-prot' in message.content:
                current = self.config.getboolean('Settings', 'name_change_protection')
                self.config['Settings']['name_change_protection'] = str(not current)
                self.configManager.save_config()
                await message.channel.send('Auto kick has been ' + ('enabled' if not current else 'disabled'))

        # Change messages content
        if message.content.startswith('!sbmessage '):
            commandmessage = message.content.replace('!sbmessage ', '')
            if commandmessage.startswith('-k '):
                kick_message = commandmessage.replace('-k ', '')
                self.config['Settings']['kick_message'] = kick_message
                self.configManager.save_config()
                await message.channel.send('__**Kick Message Changed to:**__ ' + kick_message)

            if commandmessage.startswith('-w '):
                welcome_message = commandmessage.replace('-w ', '')
                self.config['Settings']['welcome_message'] = welcome_message
                self.configManager.save_config()
                await message.channel.send('__**Welcome Message Changed to:**__ ' + welcome_message)

        # Handle status display
        if message.content.startswith('!sbstatus'):
            auto_kick_mode = self.config.getboolean('Settings', 'auto_kick')
            name_change_prot = self.config.getboolean('Settings', 'name_change_protection')
            kick_message = self.config.get('Settings', 'kick_message')
            welcome_message = self.config.get('Settings', 'welcome_message')
            await message.channel.send('Hello {0.author.mention}, I am online \n'.format(message) +
                                       'Auto Kick Mode: ' + str(auto_kick_mode) + '\n' +
                                       'Name Change Protection: ' + str(name_change_prot) + '\n' +
                                       'Kick Message: ' + kick_message + '\n' +
                                       'Welcome Message: ' + welcome_message)
            return

        # Handle manual scan
        if message.content.startswith('!sbscan'):
            await message.channel.send('{0.author.mention} Initiating name scan...'.format(message))
            kick_mode = False
            if '-k' in message.content:
                kick_mode = True
            scan_results = await self.scanner.scan_account_names(message.guild, kick_mode)
            for k, v in scan_results.items():
                await message.channel.send('Found improper name, ' + '||' + v + '||' + ' Obfuscated: ||' +
                                           profanity.censor(v) + '||' + (' - Player Kicked' if kick_mode else ' - No Action Taken'))
                if kick_mode:
                    guild = message.guild
                    guild.kick(guild.get_member(k), self.config.get('Settings', 'kick_message'))
            await message.channel.send('Scan Complete! Found ' + str(len(scan_results)) + ' bad user names.')

        # Handle exception command
        if message.content.startswith('!sbexception'):
            if message.content.startswith('!sbexception '):
                content = message.content.replace('!sbexception ', '')
                if content.startswith('--add_exempt '):
                    toadd = content.replace('--add_exempt ', '')
                    exceptionsManager.add_exception('exempt', toadd)
                    await message.channel.send('User name ' + toadd + " has been added to the exceptions list and will be ignored during scans.")
                    return

                if content.startswith('--add_restricted '):
                    toadd = content.replace('--add_restricted ', '')
                    exceptionsManager.add_exception('restricted', toadd)
                    await message.channel.send('User name ||' + toadd + '|| has been added to the restricted list and will be kicked automatically on join. This is effectively a name ban.')
                    return

                if content.startswith('--remove_exempt '):
                    toremove = content.replace('--remove_exempt ', '')
                    if exceptionsManager.contains('exempt', toremove):
                        exceptionsManager.remove_exception('exempt', toremove)
                        await message.channel.send('User name ' + toremove + ' has been removed from the exceptions list and will no longer be ignored during scans.')
                    else:
                        await message.channel.send('User name ' + toremove + ' not found on the exceptions list. !sbexception --list for a full list.')
                    return

                if content.startswith('--remove_restricted '):
                    toremove = content.replace('--remove_restricted ', '')
                    if exceptionsManager.contains('restricted', toremove):
                        exceptionsManager.remove_exception('restricted', toremove)
                        await message.channel.send('User name ||' + toremove + '|| has been removed from the restricted list and will no longer be kicked automatically.')
                    else:
                        await message.channel.send('User name ' + toremove + ' not found on the restricted list. !sbexception --list for a full list.')
                    return

                if '--list' in message.content:
                    list = exceptionsManager.get_exceptions()
                    if not list:
                        await message.channel.send('Nothing to list in exceptions. Use !sbexception without any arguments to get usage information.')
                    for k, v in list.items():
                        await message.channel.send('```List: ' + k + '```')
                        list_message = '> '
                        if not v:
                            list_message = list_message + '> No names listed'
                        else:
                            for value in v:
                                if k == 'restricted':
                                    list_message = list_message + '||' + value + '||\n'
                                else:
                                    list_message = list_message + value + '\n'
                        await message.channel.send(list_message)
                    return

            await message.channel.send('```Help menu for command !sbexception```\n'
                                       '> !sbexception --add_exempt <name>\n'
                                       'This command will add exceptions to be ignored by the name scanner.\n'
                                       '> !sbexception --remove_exempt <name>\n'
                                       'This command will remove exceptions to be ignored by the name scanner\n'
                                       '> !sbexception --add_restricted <name>\n'
                                       'This command will add restricted names that will always be blacklisted by the scanner.\n'
                                       '> !sbexception --remove_restricted <name>\n'
                                       'This command will remove restricted names from the blacklist\n'
                                       '> !sbexception --list\n'
                                       'This command will list all names in either list.')




class NameScan:

    def __init__(self, globalConfig):
        self.config = globalConfig
        self.default_words = open('default_words.txt').read().splitlines()
        profanity.load_censor_words(self.default_words)

    async def scan_account_names(self, guild, kick_mode):
        members = guild.members
        results = {}
        for member in members:
            if exceptionsManager.contains('exempt', member.name):
                continue
            if profanity.contains_profanity(member.name) or exceptionsManager.contains('restricted', member.name):
                results[member.id] = member.name
                if kick_mode:
                    await guild.kick(member, reason=self.config.get('Settings', 'kick_message'))
        return results

    async def scan_single_name(self, guild, member):
        if exceptionsManager.contains('exempt', member.name):
            return
        if profanity.contains_profanity(member.name) or exceptionsManager.contains('restricted', member.name):
            log_channel = self.config.getint('Settings', 'channel')
            if log_channel != -1:
                await guild.get_channel(log_channel).send('User ||' + member.name + '|| has been kicked from the server.')
            await guild.kick(member, reason=self.config.get('Settings', 'kick_message'))

    async def nickname_scanner(self, before, after):
        if exceptionsManager.contains('exempt', after.nick):
            return
        if profanity.contains_profanity(after.nick) or exceptionsManager.contains('restricted', after.nick):
            log_channel = self.config.getint('Settings', 'channel')
            if log_channel != -1:
                await after.guild.get_channel(log_channel).send('User ||' + before.name + '|| tried to change nickname to ||' + after.nick + '|| - action blocked.')
            # Send Message
            await after.send('The server ' + after.guild.name + ' detected that you tried to set a vulgar nickname. This action has been blocked. Please contact an administator if you feel this is an error.')
            # Handle name edit back to previous value
            try:
                await after.edit(reason='Automated Protection', nick=before.nick)
            except(discord.Forbidden):
                print("Could not change nickname")
                if log_channel != -1:
                    await after.guild.get_channel(log_channel).send('Error, can not change nickname')

exceptionsManager = ExceptionsManager()
exceptions = exceptionsManager.get_exceptions()