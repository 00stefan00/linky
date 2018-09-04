from disco.bot import Bot, Plugin

from utils import jsonstorage
from utils.constants import Constants
from utils.migrationhelper import MigrationHelper
from utils.validation import Validator

import re
import pdb

class YTLinkyPlugin(Plugin):

    @Plugin.command('!ytvideochannel')
    def command_set_ytvideochannel(self, event):
        if not Validator(self).is_allowed(event):
            return
        if '#' in event.msg.content:
            value = re.sub("[^0-9]", " ", event.msg.content.split('#')[1]).split(' ')[0]
            if self.is_valid_server_channel_id(value):
                jsonstorage.add(self.get_server_id(event), Constants.yt_channel.fget(), value)
                event.msg.reply('Set {} as videochannel'.format(self.get_channel_name(value)))
            else:
                event.msg.reply('Channel-name not recognized')
        else:
            event.msg.reply('No channel detected')

    @Plugin.command('!ytsubscriptionlistshow')
    def command_set_ytsubscriptionlistshow(self, event):
        if not Validator(self).is_allowed(event):
            return
        subs = jsonstorage.get(self.get_server_id(event), Constants.yt_subs.fget())
        event.msg.reply("Youtube subscriptions: {}".format(subs.items()))

    @Plugin.command('!ytsubscriptionadd')
    def command_set_ytsubscriptionadd(self, event):
        if not Validator(self).is_allowed(event):
            return
        details = event.msg.content.split("!ytsubscriptionadd")[1].strip()
        name = details.split(" ")[0]
        yt_channel_id = details.split(" ")[1]
        
        if not self.has_youtube_subscription(self.get_server_id(event)):
            jsonstorage.initialize_dict(self.get_server_id(event), Constants.yt_subs.fget())

        jsonstorage.add_to_dict(self.get_server_id(event), Constants.yt_subs.fget(), name, yt_channel_id)
        event.msg.reply("Added to the subscriptions: {} with channel id: {}".format(name, yt_channel_id))

    @Plugin.command('!ytsubscriptionremove')
    def command_set_ytsubscriptionremove(self, event):
        if not Validator(self).is_allowed(event):
            return
        details = event.msg.content.split("!ytsubscriptionremove")[1].strip()
        name = details.split(" ")[0]
        jsonstorage.remove_from_dict(self.get_server_id(event), Constants.yt_subs.fget(), str(name))
        event.msg.reply("Removed from the subscriptions: {}".format(name))

    def has_youtube_subscription(self, server_id):
        try:
            blacklist = jsonstorage.get(server_id, Constants.yt_subs.fget())
            return True 
        except Exception:
            return False

    def has_youtube_post_channel(self, server_id):
        try:
            channel = jsonstorage.get(server_id, Constants.yt_channel.fget())
            return True
        except Exception:
            return False

    def get_server_id(self, event):
        return event._guild.id