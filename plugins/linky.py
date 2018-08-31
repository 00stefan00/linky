from disco.bot import Bot, Plugin

from utils import jsonstorage
from utils.constants import Constants

import re
import pdb
# python -m disco.cli --config config.json
# https://discordapp.com/oauth2/authorize?&client_id=484777422638546955&scope=bot&permissions=220224

class LinkyPlugin(Plugin):
    def initialize(self, event):
        pass

    @Plugin.command('!listenchannel')
    def command_set_listenchannel(self, event):
        if '#' in event.msg.content:
            value = event.msg.content.split('#')[1][:-1]
            if self.is_valid_server_channel_id(value):
            	jsonstorage.add(self.get_server_id(event), Constants.listen_channel.fget(), value)
            	event.msg.reply('Listening to channel: {}'.format(self.get_channel_name(value)))
            else:
                event.msg.reply('Channel-name not recognized')
        else:
            event.msg.reply('No channel detected')

    @Plugin.command('!responsechannel')
    def command_set_responsechannel(self, event):
        if '#' in event.msg.content:
            value = event.msg.content.split('#')[1][:-1]
            if self.is_valid_server_channel_id(value):
                jsonstorage.add(self.get_server_id(event), Constants.response_channel.fget(), value)
                event.msg.reply('Set {} as responsechannel'.format(self.get_channel_name(value)))
            else:
                event.msg.reply('Channel-name not recognized')
        else:
            event.msg.reply('No channel detected')

    @Plugin.listen('MessageCreate')
    def on_message_create(self, event):
        self.initialize(event)

        if self.is_bot(event):
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
