import discord
from discord.utils import get
from replit import db
import keep_alive
import os
from profanity_filter import ProfanityFilter
from termcolor import colored
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

print(colored("Initializing profanity filter...", 'yellow'))
pf = ProfanityFilter()
print(colored("Done initializing! Time to go!", "green"))
prefix = "."
myid = os.environ["MYID"]
token = os.environ['TOKEN']

keep_alive.keep_alive()
def addUserToWarnings(id, name):
  if(id in db):
    db[id] += 1
    if db[str(id)] != 3:
      print("User: " + name + ' with ID: ' + id + " is already in database so instead we are adding to variable")
  else:
    db[id] = 1
def has_numbers(inputString):
  return any(char.isdigit() for char in inputString)
  
client = discord.Client()

@client.event
async def on_ready():
  print(colored("Logged into Discord as " + client.user.name + "#" + client.user.discriminator, "blue"))
  
@client.event
async def on_message(message):
    if message.author == client.user:
      return
    print(pf.censor('Message from {0.author}: {0.content}'.format(message)))
    if 'ㅤ' in message.content:
      print('Message contained an empty symbol!')
    if not pf.is_clean(message.content):
        user = await client.fetch_user(message.author.id)
        await user.send("Your message was removed due to vulgar launguage.")
        addUserToWarnings(str(message.author.id), message.author.name)
        
        if db[str(message.author.id)] == 3 :
            await user.send("Three strikes and you're out! ⚾️ You have been banned from *" + message.guild.name + "* permanently! Think carefully next time before breaking rules!")
            await message.guild.ban(message.author, reason="Vulgar language")
            aaronId = await client.fetch_user(myid)
            await aaronId.send("User: **" + user.name + "** was banned from server: " + message.guild.name + ".")
            #reset warnings
            db[str(message.author.id)] = 0
            print(("User: **" + user.name + "** was banned from server: " + message.guild.name + "."))
            return
        await user.send("You have " + str(db[str(message.author.id)]) + " warnings. " + str(3 - db[str(message.author.id)]) + " more warnings and you will be banned from the server *" + message.guild.name + "*.")
        print(message.author.name + " has " + str(db[str(message.author.id)]) + " warnings.")
        await message.delete()
        return
      
    if message.content.startswith(prefix):
      sent = message.content.replace(prefix, '')
      if sent == "react":
        def check(reaction, user):  # Our check for the reaction
          return user == message.author  # We check that only the authors reaction counts

        whatwesent = await message.channel.send("Please react to the message!")  # Message to react to
        await whatwesent.add_reaction("✅")
        await whatwesent.add_reaction("<:redcross:989321217335001148>")
        reaction = await client.wait_for("reaction_add", check=check)  # Wait for a reaction
        reactionemoji = str(reaction[0])
        if reactionemoji == "<:redcross:989321217335001148>":
          await whatwesent.edit(content="NO!")
        if reactionemoji == "✅":
          await whatwesent.edit(content="YES!")
        await message.delete()
        if reactionemoji != "✅" or reactionemoji != "<:redcross:989321217335001148>":
          return
      if sent.startswith("purge"):
        if message.author.guild_permissions.administrator:
          if not has_numbers(sent):
            await message.channel.send("You cannot purge an empty amount of messages!")
            return
          print("Purging " + sent.replace("purge ", "") + " messages")
          await message.channel.purge(limit = int(sent.replace("purge ", "")) + 1)
        else:
          await message.channel.send("You do not have sufficient permissions to perform this command.")
      if sent == 'help':
            embed = discord.Embed(
              title='Commands',
              description = "A list of all the commands currently implemented into RebootBot.",
              color = 0xFFD04F
            )
            embed.set_thumbnail(
              url="https://childadolescentpsych.cumc.columbia.edu/sites/default/files/styles/555x315/public/HelpFriend-HelpSign-613244854%20555x315.jpg?itok=IzH1dmRK"
            )
            embed.set_author(
              name = "RebootTech",
              url = "https://www.youtube.com/channel/UCClxU4y-qthx3w5hMEzrSSg",
              icon_url = "https://i.ibb.co/LR5VHFg/Logo-1.png"
            )
            embed.add_field(
              name="ㅤ", 
              value="---------------------------------------", 
              inline=False
            )
            embed.add_field(
              name="USER COMMANDS", 
              value="---------------------------------------", 
              inline=False
            )
            embed.add_field(
              name="!help", 
              value="Use this command if you forgot RebootBot's commands!", 
              inline=False
            )
            embed.add_field(
              name="!bio", 
              value="Sends an about page message.", 
              inline=False
            )
            embed.add_field(
              name="!server", 
              value="Tells you what server your message was sent in.", 
              inline=False
            )
            embed.add_field(
              name="!whoami", 
              value="Tells you whether you are an admin or a normal person.", 
              inline=False
            )
            embed.add_field(
              name="!react", 
              value="The bot sends a message that you react to. Choose one!", 
              inline=False
            )
            embed.add_field(
              name="ㅤ", 
              value="---------------------------------------", 
              inline=False
            )
            embed.add_field(
              name="ADMIN COMMANDS", 
              value="---------------------------------------", 
              inline=False
            )
            embed.add_field(
              name="!clearwarnings ```@NAME```", 
              value="Clears any number of warnings of the mentioned user. Sets user's database warning value to ***0*** **NEEDS ADMIN PERMISSIONS TO WORK**", 
              inline=False
            )
            embed.add_field(
              name="!ban ```@NAME```", 
              value="Bans the user you mentioned. **NEEDS ADMIN PERMISSIONS TO WORK**", 
              inline=False
            )
            embed.add_field(
              name="!kick ```@NAME```", 
              value="Kicks the user you mentioned. **NEEDS ADMIN PERMISSIONS TO WORK**", 
              inline=False
            )
            embed.add_field(
              name="!purge ```NUMBER```", 
              value="Purges ```NUMBER``` amount of messages from the channel the message was sent in.", 
              inline=False
            )
            embed.set_footer(
              text="Commands and command names are subject to change. If a command you know is not working, try !help to see an updated list of commands."
            )
            await message.channel.send(embed = embed)
      if sent == 'whoami':
        if message.author.guild_permissions.administrator:
          await message.channel.send("you are big boy admin")
        else:
          await message.channel.send("you normal peasant!")
      if sent.startswith('ban'):
            if message.author.guild_permissions.administrator:
              a = message.content
              a = a.replace("<","")
              a = a.replace(">","")
              a = a.replace("@","")
              a = a.replace("!ban ", '')
              a = a.replace("!", '')
              user = await client.fetch_user(a)
              await message.guild.ban(user)
              await message.reply('User: **' + user.name + "** was banned sucessfully.", mention_author = False)
      if sent.startswith('kick'):
            if message.author.guild_permissions.administrator:
              a = message.content
              a = a.replace("<","")
              a = a.replace(">","")
              a = a.replace("@","")
              a = a.replace("!kick ", '')
              a = a.replace("!", '')
              user = await client.fetch_user(a)
              await message.guild.kick(user)
              await message.reply('User: **' + user.name + "** was kicked sucessfully.", mention_author = False)
          #lock sensitive interactions to people with admin perms
      if sent.startswith('clearwarnings'):
            if message.author.guild_permissions.administrator:
              a = message.content
              a = a.replace("<","")
              a = a.replace(">","")
              a = a.replace("@","")
              a = a.replace(prefix + "clearwarnings ", '')
              a = a.replace(prefix, '')
            print("warnings cleared.")
            db[str(a)] = 0
            user = await client.fetch_user(a)
            await message.channel.send(f"<@{a}>'s warnings were cleared. They now have " + str(db[str(a)]) + " warnings.")
      if sent == 'dm':
                user = await client.fetch_user(message.author.id)
                await user.send("test dm")
      if sent == 'server':
              await message.channel.send('Message was sent in ' + message.guild.name)
      if sent == 'bio':
                await message.channel.send(
                    "Hello! I'm RebootBot! Nice to meet you! I am a utility bot designed and programmed by Aaron W., known online as AW_Dev."
                )
      if sent == 'mention':
              author_name = message.author.id
              await message.channel.send(f"<@{author_name}> is your name.")
      if sent == 'embed':
            embed = discord.Embed(
              title='Test Embed',
              description = "This is a test embed.",
              color = 0x61D48D
            )
            embed.set_author(
              name = message.author.name,
              url = "https://aw-dev.itch.io",
              icon_url = message.author.avatar_url
            )
            embed.add_field(name="Field 1 Title", value="This is the value for field 1. This is NOT an inline field.", inline=False)
            await message.channel.send(embed = embed)
client.run(token)