from disco.bot import Bot, Plugin

from utils import jsonstorage
from utils.constants import Constants
from utils.migrationhelper import MigrationHelper

import re
import pdb

class LinkyPlugin(Plugin):
    def initialize(self, event):
        migrationhelper = MigrationHelper(self.get_server_id(event))
        migrationhelper.check_for_updates()

    @Plugin.command('!help')
    def help(self, event):
        helptext = "``` \n"
        helptext += "!help output: \n"
        helptext +=" \n"
        helptext += "@linky !urlinputchannel #channelname | to set which channel should be scanned for URLS \n"
        helptext += "@linky !urloutputchannel #channelname | to set which channel should be used to output scanned URLS \n"
        helptext += "@linky !adminonlycontrol true/false | to allow or disallow non-admin members of the discord to use @linky !commands \n"
        helptext +=" @linky !domainblacklistadd <name> <url> | will set a certain domain to not be posted in the outputchannel\n"
        helptext +=" @linky !domainblacklistremove <name> | will remove a certain domain that is grouped with that name from the blacklist \n"
        helptext +=" @linky !domainblacklistshow | will show the current blacklist \n"
        helptext += "```"
        event.msg.reply(helptext)

    @Plugin.command('!adminonlycontrol')
    def command_set_adminonlycontrol(self, event):
        if not self.is_allowed(event):
            return
        value = event.msg.content.split('!adminonlycontrol')[1].lower().strip()
        if value in ['true', 'false']:
            jsonstorage.add(self.get_server_id(event), Constants.adminonlycontrol.fget(), value)
            event.msg.reply('Admin-only-control set to: {}'.format(value))
        else:
            event.msg.reply('Received: {}, only accepts true/false'.format(value))

    @Plugin.command('!urlinputchannel')
    def command_set_urlinputchannel(self, event):
        if not self.is_allowed(event):
            return
        if '#' in event.msg.content:
            value = re.sub("[^0-9]", " ", event.msg.content.split('#')[1]).split(' ')[0]
            if self.is_valid_server_channel_id(value):
                jsonstorage.add(self.get_server_id(event), Constants.url_input_channel.fget(), value)
                event.msg.reply('Listening to channel: {}'.format(self.get_channel_name(value)))
            else:
                event.msg.reply('Channel-name not recognized')
        else:
            event.msg.reply('No channel detected')

    @Plugin.command('!urloutputchannel')
    def command_set_urloutputchannel(self, event):
        if not self.is_allowed(event):
            return
        if '#' in event.msg.content:
            value = re.sub("[^0-9]", " ", event.msg.content.split('#')[1]).split(' ')[0]
            if self.is_valid_server_channel_id(value):
                jsonstorage.add(self.get_server_id(event), Constants.url_output_channel.fget(), value)
                event.msg.reply('Set {} as outputchannel'.format(self.get_channel_name(value)))
            else:
                event.msg.reply('Channel-name not recognized')
        else:
            event.msg.reply('No channel detected')

    @Plugin.command('!domainblacklistshow')
    def command_set_domainblacklistshow(self, event):
        if not self.is_allowed(event):
            return
        blacklist = jsonstorage.get(self.get_server_id(event), Constants.blacklisted_domains.fget())
        event.msg.reply("Blacklist: {}".format(blacklist.items()))

    @Plugin.command('!domainblacklistadd')
    def command_set_domainblacklistadd(self, event):
        if not self.is_allowed(event):
            return
        details = event.msg.content.split("!domainblacklistadd")[1].strip()
        name = details.split(" ")[0]
        urls = self.get_urls(details.split(" ")[1])
        if (len(urls) < 1):
            event.msg.reply("No URL found")
            return
        if not self.has_blacklisted_domains(self.get_server_id(event)):
            jsonstorage.initialize_dict(self.get_server_id(event), Constants.blacklisted_domains.fget())
        url = self.get_stripped_domain(urls[0])
        jsonstorage.add_to_dict(self.get_server_id(event), Constants.blacklisted_domains.fget(), name, url)
        event.msg.reply("Added to the blacklist: {} with domain: {}".format(name, url))

    @Plugin.command('!domainblacklistremove')
    def command_set_domainblacklistremove(self, event):
        if not self.is_allowed(event):
            return
        details = event.msg.content.split("!domainblacklistremove")[1].strip()
        name = details.split(" ")[0]
        jsonstorage.remove_from_dict(self.get_server_id(event), Constants.blacklisted_domains.fget(), str(name))
        event.msg.reply("Removed from the blacklist: {}".format(name))

    @Plugin.listen('MessageCreate')
    def on_message_create(self, event):
        self.initialize(event)

        if self.is_bot(event):
            return
        if self.has_inputchannel(self.get_server_id(event)):
            url_input_channel_id = jsonstorage.get(self.get_server_id(event), Constants.url_input_channel.fget())
            if event.raw_data['message']['channel_id'] != url_input_channel_id:
                return

        urls = self.get_urls(event.message.content)
        # Return if there are no valid URLS found
        if len(urls) < 1:
            return
        if self.has_outputchannel(self.get_server_id(event)):
            url_output_channel_id = int(jsonstorage.get(self.get_server_id(event), Constants.url_output_channel.fget()))
            url_output_channel = self.bot.client.state.channels.get(url_output_channel_id)
            if self.is_valid_server_channel_id(url_output_channel_id):
                for url in urls:
                    if not self.url_is_blacklisted(self.get_server_id(event), url):
                        url_output_channel.send_message(url)
        else:
            event.reply("No outputchannel has been set")

    def get_server_id(self, event):
        return event._guild.id

    def get_urls(self, msg):
        urls = re.findall(r'(https?://\S+)', msg)
        return urls

    def url_is_blacklisted(self, server_id, url):
        blacklist = jsonstorage.get(server_id, Constants.blacklisted_domains.fget()).items()
        for entry in blacklist:
            if self.get_stripped_domain(entry[1]) == self.get_stripped_domain(url):
                return True
        return False

    def get_stripped_domain(self, url):
        return url.split("//")[-1].split("/")[0].split("www.")[1]   

    def get_server_channel_list(self):
        return self.bot.client.state.channels.values()

    def is_valid_server_channel_id(self, channel_id):
        return (next((channel for channel in self.get_server_channel_list() if channel.id == int(channel_id)), None) is not None)

    def get_channel_name(self, channel_id):
        for channel in self.get_server_channel_list():
            if channel.id == int(channel_id):
                return '#{}'.format(channel.name)
        return ''

    def is_bot(self, event):
        return (self.bot.client.state.me.id == int(event.raw_data['message']['author']['id']))

    def is_allowed(self, event):
        if self.is_admin_only_control(self.get_server_id(event)) and not self.is_admin(event):
            event.msg.reply('Sorry, you lack the required permissions to program my behaviour')
            return False
        return True

    def is_admin(self, event):
        return event.member.permissions.to_dict()['administrator']

    def is_admin_only_control(self, server_id):
        try:
            value = jsonstorage.get(server_id, Constants.adminonlycontrol.fget())
        except:
            value = None
        if value in ['True', 'true']:
            return True
        else:
            return False

    def has_inputchannel(self, server_id):
        try:
            channel = jsonstorage.get(server_id, Constants.url_input_channel.fget())
            return True
        except Exception:
            return False

    def has_outputchannel(self, server_id):
        try:
            channel = jsonstorage.get(server_id, Constants.url_output_channel.fget())
            return True
        except Exception:
            return False

    def has_blacklisted_domains(self, server_id):
        try:
            blacklist = jsonstorage.get(server_id, Constants.blacklisted_domains.fget())
            return True 
        except Exception:
            return False