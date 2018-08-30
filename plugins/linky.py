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
            value = event.msg.content.split('#')[1]
            # todo: check if channel exists self.bot.client.state.channels.values()     
            jsonstorage.add(self.get_server_id(event), Constants.listen_channel, value)
        else:
            event.msg.reply('No channel detected')

    @Plugin.command('!responsechannel')
    def command_set_responsechannel(self, event):
        if '#' in event.msg.content:
            value = event.msg.content.split('#')[1]
            # todo: check if channel exists self.bot.client.state.channels.values()     
            jsonstorage.add(self.get_server_id(event), Constants.response_channel, value)
        else:
            event.msg.reply('No channel detected')

    @Plugin.listen('MessageCreate')
    def on_message_create(self, event):
        self.initialize(event)

        if self.is_bot(event):
            return

        msg = event.message.content
        channel = event.raw_data['message']['channel_id']
        channels = self.bot.client.state.channels.values()  

        if self.has_responsechannel(self.get_server_id(event)):
            response_channel = self.bot.client.state.channels.get(jsonstorage.get(self.get_server_id(event), Constants.response_channel))

            # TODO check if response channel exists in serverchannels
            for url in self.get_urls(msg):
                response_channel.send_message(url)
        else:
            event.reply("No responsechannel has been set")

    def get_server_id(self, event):
        return event._guild.id

    def get_urls(self, msg):
        urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', msg)
        return urls

    def is_bot(self, event):
        return (self.bot.client.state.me.id == int(event.raw_data['message']['author']['id']))

    def has_listenchannel(self, server_id):
        try:
            channel = jsonstorage.get(server_id, Constants.listen_channel)
            return True
        except Exception:
            return False

    def has_responsechannel(self, server_id):
        try:
            channel = jsonstorage.get(server_id, Constants.response_channel)
            return True
        except Exception:
            return False
