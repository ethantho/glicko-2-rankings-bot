#bot.py
from __future__ import print_function
import os
import random
import discord
import asyncio
import json
import glicko2
import numpy as np
from random import randrange
from dotenv import load_dotenv
from discord.ext import tasks
from discord.ext import commands
from json import JSONEncoder

import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials



from google.oauth2 import service_account

def specificPlayerListIndex(name):
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='Superstars_OFF!a2:l1001').execute()
    values = result.get('values', [])
    for index, a in enumerate(values):
        if a[2] == name:
            return index
    return -1


def adjSpecificPlayerListIndex(name):
    adjResult = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='Adj_Elo_OFF!a2:l1001').execute()
    adjValues = result.get('values', [])
    for index, a in enumerate(values):
        if a[2] == name:
            return index
    return -1


SERVICE_ACCOUNT_FILE = 'keys.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)


# OLD SAMPLE_SPREADSHEET_ID = 'REDACTED'
SAMPLE_SPREADSHEET_ID = 'REDACTED'

service = build('sheets', 'v4', credentials = creds)


#call the sheets api
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='Superstars_OFF!a2:l1001').execute()
values = result.get('values', [])
adjResult = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='Adj_Elo_OFF!a2:l1001').execute()
adjValues = adjResult.get('values', [])

#print("Testing printing a player's entry")

coaksIndex = specificPlayerListIndex("LittleCoaks")
#print("Player LittleCoaks is at position " + str(coaksIndex))

#DONT SPECIFY LETTER OR PERCENT, ITS A FORMULA IN THE SHEET

#resource = {
#  "majorDimension": "ROWS",
 # "values": testEntry
#}

#request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='Superstars_OFF!a49', valueInputOption='USER_ENTERED', body= {"values":testEntry}).execute()

def sheetSort(playerList):
    return int(float(playerList[3]))


def updateLetters(allPlayersList):
    for i in allPlayersList:
        if(int(i[3]) < 900):
            i[0]='F'
        elif(int(i[3]) < 1000):
            i[0]='E'
        elif(int(i[3]) < 1100):
            i[0]='D'
        elif(int(i[3]) < 1200):
            i[0]='C'
        elif(int(i[3]) < 1300):
            i[0]='B'
        elif(int(i[3]) < 1400):
            i[0]='A'
        elif(int(i[3]) >= 1400):
            i[0]='S'


def updateOFFSheet(allPlayersList):
    allPlayersList.sort(key=sheetSort, reverse = True)
    updateLetters(allPlayersList)
    for i in allPlayersList:
        i[1] = (allPlayersList.index(i) + 1)
    for i in allPlayersList:
        wins = float(i[5])
        loses = float(i[6])
        total = wins + loses

        if(int(total) == 0):
            i[8] = "0"
        else:
            winPer = round((wins/total), 4) *100 
            i[8] = str(int(winPer)) + "%"
    request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='Superstars_OFF!a2', valueInputOption='USER_ENTERED', body= {"values":allPlayersList}).execute()


updateOFFSheet(values)

bot = commands.Bot(command_prefix="$")
#stipulations = Stipulations.readlines()

bot.remove_command("help")

#REDACTED = bot.get_user(REDACTED)
#Me = bot.get_user(REDACTED)

@bot.command()
async def profile(ctx, member:discord.Member = None):
    if member:
        await startStats(member)
        #service = build('sheets', 'v4', credentials = creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='Superstars_OFF!a2:l1001').execute()
        values = result.get('values', [])

        adjResult = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='Adj_Elo_OFF!a2:l1001').execute()
        adjValues = adjResult.get('values', [])

        memberIndex = specificPlayerListIndex(member.name)
        adjMemberIndex = adjSpecificPlayerListIndex(member.name)

        adjElo = adjValues[adjMemberIndex][2]
        rank = values[memberIndex][1]
        rating = values[memberIndex][3]
        wins = values[memberIndex][5]
        loses = values[memberIndex][6]
        winPercent = values[memberIndex][8]
        totalGames = values[memberIndex][9]

        em = discord.Embed(title = f"{member.name}'s stats",color = discord.Color.blue())
        em.add_field(name = "Rank", value = str(rank) , inline = True)
        em.add_field(name = "Adj. Elo", value = str(adjElo) , inline = True)
        em.add_field(name = "Wins", value = str(wins) , inline = True)
        em.add_field(name = "Loses", value = str(loses) , inline = True)
        em.add_field(name = "Win Percent", value = str(winPercent) , inline = True)
        em.add_field(name = "Loses", value = str(totalGames) , inline = True)
        await ctx.send(embed = em)
    else:
        em = discord.Embed(title = f"Please tag the user whose stats you are checking",color = discord.Color.orange())
        em.add_field(name = "Example:", value = "$sheetsProfile @exampleuser")
        await ctx.send(embed = em)


@bot.command()
async def topPlayers(ctx):
    adjResult = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='Adj_Elo_OFF!a2:l1001').execute()
    adjValues = adjResult.get('values', [])
    em = discord.Embed(title = f"Top Players",color = discord.Color.blue())
    for x in range(0,10):
        em.add_field(name = str(adjValues[x][3]), value = str(adjValues[x][2]) , inline = True)
    await ctx.send(embed = em)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


@bot.command()
async def rankedHelp(ctx):
    embed = discord.Embed(
        color = discord.Colour.orange()
    )

    embed.set_author(name='Help')

    embed.add_field(name='$rankedHelp', value = 'Shows this message', inline = False)

    embed.add_field(name='$profile @exampleuser', value = 'Shows the stats of the specified player', inline = False)

    embed.add_field(name='$submit <yourScore> <opponentScore> @opponent', value = 'Used by a player to submit the results of a match for approval with their opponent. Example: $submit 12 5 @exampleOpponent', inline = False)

    embed.add_field(name='$topPlayers', value = 'Displays the top 10 players, ranked by adjusted Elo', inline = False)

    embed.add_field(name='$forceSubmit <winScore> <loseScore> @winner @loser', value = 'ADMIN ONLY command to submit match results without the need for approval. $forceSubmit 10 5 @winner @loser', inline = False)

    embed.add_field(name='$penalty @exampleuser', value = "ADMIN ONLY command that subtracts 30 from a player's rating as a penalty", inline = False)

    await ctx.send(embed=embed)


@bot.command()
async def penalty(ctx, member:discord.Member = None):
    if member:
        role = discord.utils.get(ctx.guild.roles, name="Admin")
        if role in ctx.author.roles:
            await startStats(member)
            result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='Superstars_OFF!a2:l1001').execute()
            values = result.get('values', [])
            memberEntry = specificPlayerListIndex(member.name)
            oldRating = int(values[memberEntry][3])

            newRating = (oldRating- 30)
            values[memberEntry][3] = newRating
            updateOFFSheet(values)
            em = discord.Embed(title = f"Gave penalty -30 to {member.name}'s rating",color = discord.Color.red())
            em.add_field(name = "Old Rating", value = round((newRating+30)))
            em.add_field(name = "New Rating", value = round((newRating)))
            await ctx.send(embed = em)
        else:
            em = discord.Embed(title = f"Permission denied!",color = discord.Color.orange())
            em.add_field(name = "Requirements" , value = "You must have the role \"Admin\" to use this command")
            await ctx.send(embed = em)

    else:
        em = discord.Embed(title = f"Please tag the user to give the penalty to",color = discord.Color.orange())
        em.add_field(name = "Example:", value = "$penalty @exampleuser")
        await ctx.send(embed = em)


@bot.command()
async def submit(ctx, score1 = None, score2 = None, player2:discord.Member = None):
    if ((score1 and score2) and player2):
        player1 = ctx.author
        print(f"{player1.name} submitted match against {player2.name}. P1: {str(score1)} P2: {str(score2)}")
        if(int(score1) > int(score2)):
            print(f"Pre-approval Winner: {player1.name}")
                
        elif(int(score1) < int(score2)):
            print(f"Pre-approval Winner: {player2.name}")
        await startStats(player1)
        await startStats(player2)
        em = discord.Embed(title = f"{player2.name}, confirm these results by reacting to this message with ✅, or reject them with ❎",color = discord.Color.purple())
        em.add_field(name = f"{player1.name}'s score: ", value = score1)
        em.add_field(name = f"{player2.name}'s score:", value = score2)
        sentEmbed = await ctx.send(embed = em)
        
        await sentEmbed.add_reaction('✅')
        await sentEmbed.add_reaction('❎')

        def check(rctn, user):
             return (user.id == player2.id and str(rctn) == '✅') or ((user.id == player2.id or user.id == player1.id) and str(rctn) == '❎')

        try:
            rctn, user = await bot.wait_for('reaction_add', check = check, timeout = 180.0)

            if str(rctn) == '✅':
                em2 = discord.Embed(title = f"Confirmed match between {player1.name} and {player2.name}!",color = discord.Color.green())
                await ctx.send(embed = em2)

                if(int(score1) > int(score2)):
                    await glicko2RunSheetStats(player1.name, player2.name)
                    print(f"Winner: {player1.name}")
                
                elif(int(score1) < int(score2)):
                    await glicko2RunSheetStats(player2.name, player1.name)
                    print(f"Winner: {player2.name}")
                
                dmEmbed = discord.Embed(title = f"Results of match between {player1.name} and {player2.name}", color = discord.Color.blue())
                dmEmbed.add_field(name = f"{player1.name}'s score: ", value = score1)
                dmEmbed.add_field(name = f"{player2.name}'s score:", value = score2)
                LittleCoaks = bot.get_user(265263454556913666)
                channel = await LittleCoaks.create_dm()
                await channel.send(embed = dmEmbed)

            elif str(rctn) == '❎':
                em2 = discord.Embed(title = f"Rejected match between {player1.name} and {player2.name}!",color = discord.Color.red())

                await ctx.send(embed = em2)


        except asyncio.TimeoutError:
            await ctx.send("Sorry, you didn't react in time!")


            

        
    else:
        em = discord.Embed(title = f"Please specify your score, your opponents score, and tag your opponent",color = discord.Color.orange())
        em.add_field(name = "Example:", value = "$submit 12 5 @exampleuser")
        #em.add_field(name = "Note:", value = "This command should be run by the winner of the match", inline = False)
        await ctx.send(embed = em)


@bot.command()
async def forceSubmit(ctx, score1 = None, score2 = None, winner:discord.Member = None, loser:discord.Member = None):
    if ((score1 and score2) and (winner and loser)):
        await startStats(winner)
        await startStats(loser)
        role = discord.utils.get(ctx.guild.roles, name="Admin")
        if role in ctx.author.roles:
            em2 = discord.Embed(title = f"Confirmed match between {winner.name} and {loser.name}!",color = discord.Color.green())
            await ctx.send(embed = em2)
            await glicko2RunSheetStats(winner.name, loser.name)
            dmEmbed = discord.Embed(title = f"Results of match between {winner.name} and {loser.name}", color = discord.Color.blue())
            dmEmbed.add_field(name = f"{winner.name}'s score: ", value = score1)
            dmEmbed.add_field(name = f"{loser.name}'s score:", value = score2)
            LittleCoaks = bot.get_user(REDACTED)
            channel = await LittleCoaks.create_dm()
            await channel.send(embed = dmEmbed)
        else:
            em = discord.Embed(title = f"Permission denied!",color = discord.Color.orange())
            em.add_field(name = "Requirements" , value = "You must have the role \"Admin\" to use this command")
            await ctx.send(embed = em)

    else:
        em = discord.Embed(title = f"Please specify the winner's score, the loser's score, tag the winning player, and tag the losing player",color = discord.Color.orange())
        em.add_field(name = "Example:", value = "$forceSubmit 10 5 @winner @loser")
        await ctx.send(embed = em)


async def startStats(user):  #MAKES A NEW ENTRY FOR A USER NOT ALREADY ON SPREADSHEET
    
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='Superstars_OFF!a2:l1001').execute()

    values = result.get('values', []) 
    for i in values:
        if str(user.name) in i:
            return False
    
    testEntry = [None, '', user.name, '1200' , '', '0', '0','', None, '0', '350', '0.06']

    values.append(testEntry)
    updateOFFSheet(values)
    return True


async def getStatsData():
    with open("players.json" , "r") as f:
        users = json.load(f)

    return users


async def glicko2RunSheetStats(winner, loser):
    print(f"Running stats of {winner} and {loser}")
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range='Superstars_OFF!a2:l1001').execute()
    values = result.get('values', [])
    winnerEntry = specificPlayerListIndex(winner)
    loserEntry = specificPlayerListIndex(loser)

    winnerList = values[winnerEntry]
    loserList = values[loserEntry]

    winRat = float(winnerList[3])
    winRD = int(winnerList[10])
    winVol = float(winnerList[11])

    losRat = float(loserList[3])
    losRD = int(loserList[10])
    losVol = float(loserList[11])

    winner = glicko2.Player(winRat, winRD, winVol)
    loser = glicko2.Player(losRat, losRD, losVol)

    winner.update_player([losRat], [losRD], [1])
    loser.update_player([winRat], [winRD], [0])

    winnerList[3] = str(int(round(winner.rating)))
    winnerList[5] = str( int(winnerList[5]) + 1)
    winnerList[9] = str( int(winnerList[9]) + 1)
    winnerList[10] = str(int(winner.rd))
    winnerList[11] = str(round(winner.vol, 4))

    loserList[3] = str(int(round(loser.rating)))
    loserList[6] = str( int(loserList[6]) + 1)
    loserList[9] = str( int(loserList[9]) + 1)
    loserList[10] = str(int(loser.rd))
    loserList[11] = str(round(loser.vol,4))

    values[winnerEntry] = winnerList
    values[loserEntry] = loserList
    updateOFFSheet(values)


bot.run('REDACTED')
