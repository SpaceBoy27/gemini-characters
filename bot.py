#init
import pathlib
import textwrap
import discord

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown

with open('.conf') as c:
    conf = c.read()

def get_config(param):
    startIndex = conf.find(param + ': ')
    startIndex = startIndex + len(param + ': ')
    endIndex = conf.find('\n', startIndex)
    return conf[startIndex:endIndex]

#config
intents = discord.Intents.default()
intents.message_content = True

definition = get_config('definition')

username = get_config('username')

apiKey = get_config('api_key')

discordToken = get_config('discord_token')

model = genai.GenerativeModel('gemini-pro')
genai.configure(api_key=apiKey)


#main
response = ''
def get_reply(message):

  print("\n" + "get memory")
  with open('.mem') as m:
      mem = m.read()

  if(len(mem)>10000):
      print("\n" + "summarizing memory, this may take a while")
      summary_prompt = "Please summarize the following conversation: " + "\n" + mem
      summary = model.generate_content(summary_prompt)

      print(mem) #debug in case all is lost

      mem = summary.text + "\n" + "[user]: " + message[3]
  else:
      mem = mem + "\n" + "[user]: " + message[3]

  print("\n" + "querying API")
  prompt = "Please take the role of the following character definition: " + definition + "\n" + "The user's name is " + username + "\n" + "Your current memories include the following, where you are [AI] and the user is [user]: " + "\n" + mem + "\n" + "Please reply to the following message, which is written by the user unless otherwise specified. Please do not add [AI] or any other user tag to the beginning of your message, as that will be done by the program." + "\n" + message
  reply = model.generate_content(prompt)

  mem = mem + "\n" + "[AI]:" + reply.text

  print("\n" + "updating memory")
  with open('.mem', 'w') as m:
      m.write(mem)

  print("response: " + reply.text)
  return reply.text
  

#discord
import discord


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith('--'):
            userMessage = message.content[3]
            chatMessage = get_reply(message.content)
            await message.channel.send(chatMessage)

client = MyClient(intents=intents)
client.run(discordToken)
