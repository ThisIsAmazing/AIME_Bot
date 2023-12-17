#import statements
import discord
import mysql.connector
import random
import os

db_user = str(os.environ.get('DB_USER'))
db_host = str(os.environ.get('DB_HOST'))
db_pwd = str(os.environ.get('DB_PWD'))
db_name = str(os.environ.get('DB_NAME'))
bot_token = str(os.environ.get('BOT_TOKEN'))






#variable definition statements
testdifficulty = [3.5, 4, 4.5, 5, 5.5, 6, 6.5]
command = "Select problem from AIME where problemid={}"
randomcmd = "Select problem from AIME where id={}"
randomcmd2 = "Select problemid from AIME where id={}"
answercmd = "Select answer from AIME where problemid={}"
testcmd = "Select problemid from AIME where difficulty={difficulty} ORDER BY RAND() LIMIT {number};"
get_user_cmd = "INSERT INTO user_data(username,summoned,attempted,correct,incorrect,tests)VALUES('{}',0,0,0,0,0);"
update_summoned_cmd = "UPDATE user_data SET summoned = summoned + 1 WHERE username = '{}';"
update_attempted_cmd = "UPDATE user_data SET attempted = attempted + 1 WHERE username = '{}';"
update_correct_cmd = "UPDATE user_data SET correct = correct + 1 WHERE username = '{}';"
update_incorrect_cmd = "UPDATE user_data SET incorrect = incorrect + 1 WHERE username = '{}';"
update_tests_cmd = "UPDATE user_data SET tests = tests + 1 WHERE username = '{}';"
recieve_user_data = "Select summoned, attempted, correct, incorrect, tests from user_data where username='{}';"
file_template = "Problem Pictures/{}.png"
prefix = '!'
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    mydb = mysql.connector.connect(host=db_host, user=db_user, passwd=db_pwd, database=db_name)
    mycursor = mydb.cursor(buffered=True)
    if message.author == client.user:
        return

    try:
        await message.channel.send(file=discord.File(file_template.format(message.content)))
    except:
        pass
    else:
        mycursor.execute(update_summoned_cmd.format(message.author.name))
        mycursor.execute("commit;")

    await get_user(message)
    await problem(message)
    await answer(message)
    await help(message)
    await test(message)
    await receive_data(message)
    mydb.close()


async def problem(message):
    mydb = mysql.connector.connect(host=db_host, user=db_user, passwd=db_pwd, database=db_name)
    mycursor = mydb.cursor(buffered=True)
    messagecontent = message.content
    author = message.author.name
    if messagecontent == "!random":
        mycursor.execute(update_summoned_cmd.format(author))
        mycursor.execute("commit;")
        num = random.randint(1, 240)
        mycursor.execute(randomcmd2.format(num))
        myresult = mycursor.fetchall()
        for row in myresult:
            mycursor.execute(command.format(*row))
            myresult1 = mycursor.fetchall()
            i = 0
            for row1 in myresult1:
                i = i+1
                if i >= 2:
                    break
                await message.channel.send(*row1)
                await message.channel.send(file=discord.File(file_template.format(*row)))
    mydb.close()



async def test(message):
    mydb = mysql.connector.connect(host=db_host, user=db_user, passwd=db_pwd, database=db_name)
    mycursor = mydb.cursor(buffered=True)
    author = str(message.author.name)
    messagecontent = message.content
    if messagecontent == "!test":
        mycursor.execute(update_tests_cmd.format(author))
        mycursor.execute("commit;")
        for x in range(len(testdifficulty)):
            if(testdifficulty[x] == 6.5):
                difficultyCount = 3
            else:
                difficultyCount = 2
            mycursor.execute(testcmd.format(difficulty=testdifficulty[x], number=difficultyCount))
            myresult = mycursor.fetchall()
            for row in myresult:
                await message.channel.send(*row)
                await message.channel.send(file=discord.File(file_template.format(*row)))
    mydb.close()



async def answer(message):
    mydb = mysql.connector.connect(host=db_host, user=db_user, passwd=db_pwd, database=db_name)
    mycursor = mydb.cursor(buffered=True)
    author = str(message.author.name)
    messagecontent = message.content
    if messagecontent.startswith("!answer"):
        answer_form = messagecontent[8:].split()
        mycursor.execute(answercmd.format(int(answer_form[0])))
        myresult = mycursor.fetchall()
        j = 0
        for row in myresult:
            if int(answer_form[1]) == int(*row):
                j = j + 1
                if j >= 2:
                    break
                await message.channel.send("Correct!")
                mycursor.execute(update_attempted_cmd.format(author))
                mycursor.execute(update_correct_cmd.format(author))
                mycursor.execute("commit;")
            else:
                j = j + 1
                if j >= 2:
                    break
                await message.channel.send("Incorrect!")
                mycursor.execute(update_attempted_cmd.format(author))
                mycursor.execute(update_incorrect_cmd.format(author))
                mycursor.execute("commit;")
    mydb.close()


async def help(message):
    messagecontent = message.content
    if messagecontent.startswith("!help"):
        await message.channel.send(
            "Use this bot to fetch past American Invitational Mathematics Exam problems from 2022 to practice for the exam!")
        await message.channel.send("To select a specific problem, you must type in its problem id.")
        await message.channel.send(
            "The id is formed by getting the year of release(i.e 2022), the version(AIME I/II), and the problem number(i.e #13).")
        await message.channel.send(
            "If you want to find the the problem labeled 2022 AIME II Problem 7, then the id will simply be 202227. 2022 is the year of release, 2 is the version, and 7 is the problem number.")
        await message.channel.send(
            "If you want a random problem, simply type in **!random** and the bot will spew a randomly picked problem.")
        await message.channel.send(
            "If you want to check/find the answer to their problem, simply type in **!answer [problem id] [answer]**(with spaces) and the bot will reply by responding whether it is incorrect or correct.")
        await message.channel.send(
            "If you want the bot to generate a mock test for you to practice, simply type in **!test** and the bot will generate a random test that is composed of all the AIME problems.")
        await message.channel.send(
            "Lastly, if you want to check your statistics with problems, type in **!info** to see your statistics, which include the problems summoned/attempted/correct/incorrect/percentage and the amount of tests generated.")
        await message.channel.send("Please note for 2022 AIME II Problem #8, only 080 will be accepted as the correct answer.")
        await message.channel.send("Our team will keep coming up with more ideas for these bots, and be sure to check out our website at aimebot.thisisamazing.app!")


async def get_user(message):
    mydb = mysql.connector.connect(host=db_host, user=db_user, passwd=db_pwd, database=db_name)
    mycursor = mydb.cursor(buffered=True)
    author = str(message.author.name)
    try:
        mycursor.execute(get_user_cmd.format(author))
        mycursor.execute("commit;")
    except:
        pass
    mydb.close()

async def receive_data(message):
    mydb = mysql.connector.connect(host=db_host, user=db_user, passwd=db_pwd, database=db_name)
    mycursor = mydb.cursor(buffered=True)
    messagecontent = message.content
    author = message.author.name
    if messagecontent == "!info":
        user_data_statement = mycursor.execute(recieve_user_data.format(author))
        user_data_info = mycursor.fetchall()
        for row in user_data_info:
            if row[1] == 0:
                await message.channel.send("Problems Summoned: " + str(row[0]) +
                                           "\nProblems Attempted: " + str(row[1]) +
                                           "\nProblems Correct: " + str(row[2]) +
                                           "\nProblems Incorrect: " + str(row[3]) +
                                           "\nTests generated: " + str(row[4]))
            else:
                await message.channel.send("Problems Summoned: " + str(row[0]) +
                                           "\nProblems Attempted: " + str(row[1]) +
                                           "\nProblems Correct: " + str(row[2]) +
                                           "\nProblems Incorrect: " + str(row[3]) +
                                           "\nPercentage Correct: " + str(round(row[2] * 100 / row[1], 2)) +
                                           "\nTests generated: " + str(row[4]))

    mydb.close()





client.run(bot_token)