from disco.bot import Bot, Plugin

from utils import jsonstorage
from utils.constants import Constants

import re
import pdb

class LinkyPlugin(Plugin):
    def initialize(self, event):
        pass

    @Plugin.command('!help')
    def help(self, event):
        helptext = "``` \n"
        helptext += "!help output: \n"
        helptext += "@linky !urlinputchannel #channelname to set which channel should be scanned for URLS \n"
        helptext += "@linky !urloutputchannel #channelname to set which channel should be used to output scanned URLS \n"

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
            	jsonstorage.add(self.get_server_id(event), Constants.listen_channel.fget(), value)
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
                jsonstorage.add(self.get_server_id(event), Constants.response_channel.fget(), value)
                event.msg.reply('Set {} as outputchannel'.format(self.get_channel_name(value)))
            else:
                event.msg.reply('Channel-name not recognized')
        else:
            event.msg.reply('No channel detected')

    @Plugin.listen('MessageCreate')
    def on_message_create(self, event):
        self.initialize(event)

        if self.is_bot(event):
            return
        if self.has_listenchannel(self.get_server_id(event)):
            listen_channel_id = jsonstorage.get(self.get_server_id(event), Constants.listen_channel.fget())
            if event.raw_data['message']['channel_id'] != listen_channel_id:
                return

	urls = self.get_urls(event.message.content)
	# Return if there are no valid URLS found
	if len(urls) < 1:
            return
        if self.has_responsechannel(self.get_server_id(event)):
            response_channel_id = int(jsonstorage.get(self.get_server_id(event), Constants.response_channel.fget()))
            response_channel = self.bot.client.state.channels.get(response_channel_id)
            if self.is_valid_server_channel_id(response_channel_id):
                for url in urls:
                    response_channel.send_message(url)
        else:
            event.reply("No responsechannel has been set")

    def get_server_id(self, event):
        return event._guild.id

    def get_urls(self, msg):
        urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', msg)
        return urls

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

    def has_listenchannel(self, server_id):
        try:
            channel = jsonstorage.get(server_id, Constants.listen_channel.fget())
            return True
        except Exception:
            return False

    def has_responsechannel(self, server_id):
        try:
            channel = jsonstorage.get(server_id, Constants.response_channel.fget())
            return True
        except Exception:
            return False
