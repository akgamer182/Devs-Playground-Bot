import os
from random import randint
import discord
from dotenv import load_dotenv
from time import time
from discord.ext import commands
from discord.utils import get
import asyncio
from utils import escape_special_chars

#Load the environment file & get the guild that the bot is running on
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
IDEAS_CHANNEL_ID = int(os.getenv('IDEAS_CHANNEL'))

current_ideas = []
admins = []

#create the bot that will see all events
#intents are the events that the code will see
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    global IDEAS_CHANNEL
    global current_ideas
    global admins
    #load all ideas in the ideas file into the list
    with open('ideas.txt', 'r') as f:
        #the walrus operator (:=) allows you to assign a value to a variable and compare it to another value at the same time!
        while (line := f.readline()) != "":
            current_ideas.append(line[:-1])
    
    with open('admins.txt', 'r') as f:
        while (line := f.readline()) != "":
            admins.append(int(line[:-1]))
    
    IDEAS_CHANNEL = await bot.fetch_channel(IDEAS_CHANNEL_ID)
    print("Ready!")

@bot.command()
async def admin(ctx: commands.Context):
    global admins
    if ctx.message.author.id != 357298440650358804:
        await ctx.message.reply("you are not allowed to do this!")
    with open('admins.txt', 'a') as f:
        f.write(ctx.message.content.split()[1] + "\n")
    admins.append(int(ctx.message.content.split()[1]))
    await ctx.message.reply(f"Successfully made <@{ctx.message.content.split()[1]}> an administrator!")

@bot.command()
async def idea(ctx: commands.Context):
    #Anyone can submit an idea, so checking if the user is an admin is unnecessary
    global IDEAS_CHANNEL
    global current_ideas
    if len(ctx.message.content) <= len("!idea "):
        await ctx.message.reply("Please submit a valid idea!")
        return
    
    #Cutting out the command call to give only the idea
    #using the escape character (\) to avoid weird formatting from special characters
    idea = escape_special_chars(ctx.message.content.replace("!idea ", ""))
    await IDEAS_CHANNEL.send(f'idea #{len(current_ideas)+1}: \n<@{ctx.message.author.id}>: {idea}')    

@bot.command()
async def delete_idea(ctx: commands.Context):
    global IDEAS_CHANNEL
    global current_ideas
    global admins
    if not (ctx.author.id in admins):
        await ctx.message.reply("You are not allowed to do this!")
        return
    
    idea_num = ctx.message.content.replace("!delete_idea ", "")
    if not (idea_num.isnumeric() and int(idea_num) > 0 and int(idea_num) <= len(current_ideas)):
        await ctx.message.reply(f"Please enter a number between 1 and {len(current_ideas)}")
        return
    message = await IDEAS_CHANNEL.fetch_message(current_ideas[int(idea_num)-1])
    await message.delete()
    
    with open('ideas.txt', 'r') as f:
        newlines = f.readlines()
        newlines.remove(f'{current_ideas.pop(int(idea_num)-1)}\n')
    with open('ideas.txt', 'w') as f:
        f.write("".join(newlines))

    i = int(idea_num) - 1
    #decrease all suggestion nums after the deleted suggestion by 1 because i suck at coding lmao
    while i < len(current_ideas):
        message = await IDEAS_CHANNEL.fetch_message(current_ideas[i])
        new_content = f"idea #{i+1}\n" + message.content.split("\n", 1)[1]
        await message.edit(content=new_content)
        i+=1
    await ctx.message.reply(f"Successfully deleted idea {int(idea_num)}")

@bot.command()
async def clear_ideas(ctx: commands.Context):
    global IDEAS_CHANNEL
    global current_ideas
    global admins
    if not (ctx.author.id in admins):
        ctx.message.reply("You are not allowed to do this!")
        return
    
    current_ideas = []
    with open('ideas.txt', 'w') as f:
        #in write mode, f.write(str) will write over what is already there
        f.write("")
    if ctx != None:
        await ctx.message.reply("Successfully cleared ideas!")
        await IDEAS_CHANNEL.send("Ideas cleared!")

@bot.command()
async def finish_vote(ctx: commands.Context):
    global current_ideas
    global IDEAS_CHANNEL
    
    global admins
    if not (ctx.author.id in admins):
        ctx.message.reply("You are not allowed to do this!")
        return
    
    best_ratio = -1
    best_idea = None
    
    for message_id in current_ideas:
        current_message = await IDEAS_CHANNEL.fetch_message(message_id)

        upvotes = 0
        downvotes = 0

        for reaction in current_message.reactions:
            if str(reaction.emoji) == '✅':
                upvotes+=1
            elif str(reaction.emoji) == '❌':
                downvotes+=1
        #the bot adds 1 upvote and 1 downvote so we don't need to worry about division by 0
        if upvotes/downvotes > best_ratio:
            best_idea = current_message
            best_ratio = upvotes/downvotes
    await IDEAS_CHANNEL.send(f"The voting has been finished! \nChosen idea: \n{best_idea.content}")
    await clear_ideas(None)
        
        

@bot.event
async def on_message(message: discord.Message):
    global current_ideas
    #must be ran when you override on_message to ensure that commands are processed.
    await bot.process_commands(message)
    
    #If the bot sent a message beginning in 'idea #', append the message's id to the list.
    #This should be in the idea command, but i wasn't sure if it was possible to get the id of the sent message there
    if message.author.id == 1210735262137712650 and message.content[:6] == "idea #":
        await message.add_reaction('✅')
        await message.add_reaction('❌')
        current_ideas.append(message.id)
        with open('ideas.txt', 'a') as f:
            f.write(str(message.id) + "\n")

bot.run(TOKEN)