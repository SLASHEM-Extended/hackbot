#!/usr/bin/env python3

import json
import os
import re
import socket
import sys
import threading
import random
import ssl
import socket
from time import sleep, time, ctime
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

threaddone = False

# TODO Replace all this stuff (wrapped in "#{" and "#}") with JSON (In progress)
bigdictofstuff = {}
configfilename = "botinfo.json"
try:
    with open(configfilename, "r") as configfile:
        bigdictofstuff = json.load(configfile)
except FileNotFoundError:
    print('Error: config file "{}" not found.  Exiting.'.format(jsonfilename))

# Initialize values from the config file.  None of this is actually used (yet).

servername = bigdictofstuff["server"]
serverport = bigdictofstuff["port"]
nick = bigdictofstuff["botnick"]
masters = bigdictofstuff["masters"]
voiced = bigdictofstuff["voiced"]
autoopped = bigdictofstuff["autoopped"]
chans = bigdictofstuff["chans"]
ircrealname = bigdictofstuff["realname"]
ircident = bigdictofstuff["ident"]
telldict = bigdictofstuff["telldict"]
printingstuff = bigdictofstuff["printingstuff"]
usergreetings = bigdictofstuff["greetings"]

games = bigdictofstuff["games"]


#{
slexlog = open("/slashem/games/slex-1.8.6/slexdir/logfile", "r")
nhlog = open("/slashem/games/nethack/nethackdir/logfile", "r")
slashemlog = open("/slashem/games/slashemlogfile", "r")
with open("/slashem/games/slex-1.7.6/slexdir/logfile", "r") as slex, open("/slashem/games/nethack/nethackdir/logfile", "r") as nh, open("/slashem/games/slashemlogfile") as slashem:
    slexlinenums = len(slex.read().split("\n"))
    nhlinenums = len(nh.read().split("\n"))
    slashemlinenums = len(slashem.read().split("\n"))


HOST, PORT, NICK = "irc.freenode.net", 6697, "MozillaBot"
CHANS = ("#em.slashem.me", "#slashem", "#slashemextended")

opped = True
REALNAME = "SPEZ SPEZ SPEZ SPEZ"
IDENT = "cuckbot"
#}
PINOQUERIES = ("@?", "@u?", "@v?", "@V?", "@u+?", "@s?", "@g?", "@l?", "@le?", "@lt?", "@b?", "@d?", "!trump", "!potus")
readbuffer = ""
printingstuff = True


def updateconfigfile():
#{
    print("updating configuration file")
    # local
    bigdictofstuff = {}

    # All dose are global referenced as read-only
    bigdictofstuff["server"] = servername
    bigdictofstuff["port"] = serverport
    bigdictofstuff["botnick"] = nick
    bigdictofstuff["masters"] = masters
    bigdictofstuff["voiced"] = voiced
    bigdictofstuff["chans"] = chans
    bigdictofstuff["realname"] = ircrealname
    bigdictofstuff["ident"] = ircident
    bigdictofstuff["telldict"] = telldict
    bigdictofstuff["printingstuff"] = printingstuff
    bigdictofstuff["greetings"] = usergreetings
    bigdictofstuff["autoopped"] = autoopped

    bigdictofstuff["games"] = games
    with open(configfilename, "w") as configfile:
        json.dump(bigdictofstuff, configfile, sort_keys=True, indent=4)
    print("done!  configuration is {}".format(bigdictofstuff))
#}


# Slash'EM format is as follows.  NH is the same but without conduct:
# version.version.version points deathdnum(?) deathlev maxlvl curHP maxHP death(?) endtime(YYYYMMDD) starttime(YYYYMMDD) UID role race gen align name,reason "Conduct="...
def parselogfileline(line):
#{
    ver2game = {"7": "S007", "7SL": "SLethe", "8": "S008", "6": "slex", "0": "nh"}
    log = {}

    # Split by " " OR ","
    line = re.split(r"[, ]+", line)
    print("line is {}, therefore message is {}".format(line, line[16:]))
    version = line[0].split(".")
    log["version"] = "".join(version)
    log["versionmajor"] = version[0]
    log["versionminor"] = version[1]
    log["patchlevel"] = version[2]
    log["score"] = int(line[1])
    log["deathdnum"] = line[2]
    log["diedlevel"] = line[3]
    log["maxxlvl"] = line[4]
    log["curhp"] = line[5]
    log["maxhp"] = line[6]
    log["deaths"] = line[7]
    log["enddate"] = line[8]
    log["startdate"] = line[9]
    log["role"] = line[11]
    log["race"] = line[12]
    log["gender"] = line[13]
    log["align"] = line[14]
    log["name"] = line[15]
    if ver2game[log["patchlevel"]] == "nh":
        log["reason"] = " ".join(line[16:])
    else:
        log["reason"] = " ".join(line[16:-1])
    print("Reason was {}".format(log["reason"]))
    print(log)
    reason = "[{}] {} ({} {} {} {}), {} points, {}".format(ver2game[log["patchlevel"]], log['name'], log['role'],log['race'], log['gender'], log['align'], log['score'], log['reason'])

    print(reason)
    if log["score"] > 10:
        for i in CHANS:
            sendmsg(reason, i)
#}


# Format is
#def parsexlogfileline(line):
#{


def es(number):
#{
    if number > 1:
        return "s"
    else:
        return ""
#}


def finishemoff():
#{
    for i in range(slexlinenums):
        slexlog.readline()
    for i in range(nhlinenums):
        nhlog.readline()
    for i in range(slashemlinenums):
        slashemlog.readline()
#}


def checkformore():
#{
    while not threaddone:
        slexline = slexlog.readline()
        nhline = nhlog.readline()
        slashemline = slashemlog.readline()
        if slexline:
            parselogfileline(slexline)
        if slashemline:
            parselogfileline(slashemline)
        if nhline:
            parselogfileline(nhline)
        if ((not slexline) and (not nhline) and (not slashemline)):
            sleep(.1)
#}


#{
def send(text):
    s.send(bytes(text+"\r\n", "UTF-8"))
    print("> {}".format(text))

def joinchan(chan):
    send("JOIN {}".format(chan))

def sendmsg(msg,chan):
    send("PRIVMSG {} :{}".format(chan,msg))

def reply(msg,dictofstuff):
    if list(dictofstuff["target"])[0] == "#":
        sendmsg(msg, dictofstuff["target"])
    else:
        sendmsg(msg, dictofstuff["nick"])

def voice(nick,chan):
    send("MODE {} +v {}".format(chan,nick))

def op(nick,chan):
    if opped:
        send("MODE {} +o {}".format(chan,nick))
    else:
        send("PRIVMSG ChanServ :OP {} {}".format(chan,nick))

def devoice(nick,chan):
    send("MODE {} -v {}".format(chan,nick))

def deop(nick, chan):
    send("MODE {} -o {}".format(chan,nick))

def topicset(topic, chan):
    send("TOPIC {} :{}".format(chan,topic))

def kick(nick, reason, chan):
    send("KICK {} {} :{}".format(chan,nick,reason))

def ban(nick, chan):
    send("MODE {} +b {}".format(chan,nick))

def unban(nick, chan):
    send("MODE {} -b {}".format(chan,nick))

def part(chan,reason):
    if reason:
        send('PART {} :"{}"'.format(chan,reason))
    else:
        send("PART {}".format(chan))

def quit(reason):
    global threaddone
    threaddone = True
    send("QUIT {}".format(reason))
    print("< {}".format(s.recv(2048).decode("UTF-8")))
    s.shutdown(socket.SHUT_RD)
    s.close()


def whois(nick):
    send("WHOIS {}\r\n".format(nick))
    f = s.recv(128).decode("UTF-8").split("\r\n")
    g = s.recv(128).decode("UTF-8").split("\r\n")
    return (f,g)
#}


# XXX replace this with twisted
def connect():
#{
    global s
    s = socket.socket()
    s = context.wrap_socket(s, server_hostname=HOST)
    s.connect((HOST, PORT))
    send("NICK {}\r\n".format(NICK))
    send("USER {} {} bla :{}\r\n".format(IDENT,HOST,REALNAME))

    sendmsg("IDENTIFY {} {}".format(NICK, input("Requesting password for {} at {}:{} (echoed): ".format(NICK, HOST, PORT))), "NickServ")
    for i in CHANS:
        joinchan(i)
        waitfornames()
    sendmsg("So thou thought I wouldst copy the other robot, fool", "#em.slashem.me")
#    sendmsg("The DDOSes seem to be over", "#em.slashem.me")
    threading.Thread(target=pingcheck).start()
#}


# Not really a descriptive name, but whatever.  Checks for server PINGs and
# then passes the input to functions that do useful stuff with it.
def pingcheck():
#{
    global threaddone
    threaddone = False
    while not threaddone:
        readbuffer = s.recv(2048).decode("UTF-8")
        readbuffer = readbuffer.strip('\r\n')
        readbuffer = readbuffer.split()
        if readbuffer[0] == "PING":
            send("PONG {}\r\n".format(readbuffer[1]))
            print("PINGPONG")
        else:
            print(u"< {}".format(" ".join(readbuffer)))
            parseircinput(readbuffer)
    s.shutdown(socket.SHUT_RD)
    s.close()
#}


## Begin IRC stuff

# Parses input from the IRC server into a dict, does some preliminary parsing,
# then passes the dict off to other, smarter functions.
def parseircinput(ircinput):
#{
    global telldict
    global opped
    # If we got an error, abort
    if ircinput[1] in ("401", "403", "421", "441", "442", "482"):
        print("{}: {}".format(ircinput[1],"".join(list(" ".join(ircinput[4:]))[1:])))
        return

    if " ".join(ircinput[-2:]) == "-o {}".format(NICK):
        opped = False
    elif " ".join(ircinput[-2:]) == "+o {}".format(NICK):
        opped = True
    # TODO make this better and more streamlined
    dictofstuff = {}
    nickconnect = ircinput[0]
    nickconnect = list(nickconnect)
    del nickconnect[0]
    nickconnect = ''.join(nickconnect)
    nickconnect = nickconnect.split("!")
    dictofstuff["nick"] = nickconnect[0]
    connect = nickconnect[1]
    connect = connect.split("@")
    dictofstuff["connectserver"] = connect[1]
    dictofstuff["connectuser"] = connect[0]
    connect, nickconnect = "", ""
    dictofstuff["type"] = ircinput[1]
    dictofstuff["target"] = ircinput[2]
    del ircinput[0]
    del ircinput[0]
    del ircinput[0]
    if len(ircinput) >= 1:
        msg = list(' '.join(ircinput))
        del msg[0]
        dictofstuff["msg"] = ''.join(msg)
    else:
        dictofstuff["msg"] = " | "
    print(dictofstuff)

    if dictofstuff["msg"].lower().find("mozilla") != -1:
        if random.randrange(2):
            reply("Mozilla?  Fuck Mozilla!", dictofstuff)
        else:
            reply("Long live XUL!", dictofstuff)

    if dictofstuff["msg"][0] == "!":
        handleircinput(dictofstuff)

    if dictofstuff["nick"].lower() in telldict and not (dictofstuff["type"] in ("QUIT", "PART", "NICK")):
        handlemsgs(dictofstuff["nick"], dictofstuff["target"])

    # They're joining and they're either from the server "znc.dank.ninja" or
    # their nick (lowercase) is in voiced[]
    if (dictofstuff["connectserver"] == "znc.dank.ninja" or dictofstuff["nick"].lower() in voiced) and dictofstuff["type"] == "JOIN" and dictofstuff["target"] == "#em.slashem.me":
        voice(dictofstuff["nick"], "#em.slashem.me")

    # If they're one of our masters, we gotta do what they say!
    if dictofstuff["nick"].lower() in masters:
        if dictofstuff["type"] == "JOIN" and dictofstuff["target"] == "#em.slashem.me":
            op(dictofstuff["nick"], "#em.slashem.me")
            sendmsg("Welcome, oh master", "#em.slashem.me")
        if list(dictofstuff["msg"])[0] == "!":
            mastercommands(dictofstuff["msg"])

    if dictofstuff["nick"].lower() in autoopped and dictofstuff["type"] == "JOIN" and dictofstuff["target"] == "#em.slashem.me":
        op(dictofstuff["nick"], "#em.slashem.me")

    if dictofstuff["nick"].lower() in usergreetings and dictofstuff["type"] == "JOIN":
        reply(usergreetings[dictofstuff["nick"].lower()], dictofstuff)
    


    # If their message is in PINOQUERIES[], query pinobot and reply back
    for i in PINOQUERIES:
        if dictofstuff["msg"].startswith(i) and dictofstuff["target"] in ("#em.slashem.me", "#ascension.run"):
            sendmsg(dictofstuff["msg"], "Pinobot")
            reply(" ".join(s.recv(2048).decode("UTF-8").strip("\r\n").split()[3:])[1:], dictofstuff)
#}


def handleircinput(dictofstuff):
#{
    global telldict
    global usergreetings

    # If, say, the user says "!say foo bar baz", command will be "say" and
    # commandtext will be "foo bar baz"
    command = "".join(list(dictofstuff["msg"].split()[0])[1:])
    commandtext = " ".join(dictofstuff["msg"].split()[1:])

    # Their have messages and they're doing something such that they will
    # continue to be in the channel
    if dictofstuff["nick"].lower() in telldict and not (dictofstuff["type"] in ("QUIT", "PART")) and len(command.split()) > 2:
        handlemsgs(dictofstuff["nick"], dictofstuff["target"])

    if command == "topic":
        topicset(commandtext, "#em.slashem.me")
    if command == "ping":
        reply("pong!", dictofstuff)

    if commandtext.lower().find("mozilla") != -1:
        reply("Fuck Mozilla!", dictofstuff)

    if command == "greeting":
            if commandtext:
                usergreetings[dictofstuff["nick"].lower()] = commandtext
                updateconfigfile()
                reply("Successfully set greeting for {} to \"{}\"".format(dictofstuff["nick"], commandtext), dictofstuff)
            elif dictofstuff["nick"].lower() in usergreetings and not commandtext:
                reply("{}: your greeting is currently set to \"{}\"".format(dictofstuff["nick"], usergreetings[dictofstuff["nick"].lower()]), dictofstuff)
            elif not commandtext:
                reply("{}: you do not currently have a greeting.  LAME!".format(dictofstuff["nick"]), dictofstuff)

    # Use their nick as default for user-queries that if they didn't provide a
    # user
    if command in ("user", "slashemrc", "slexrc", "nethackrc", "save") and not commandtext:
        commandtext = dictofstuff["nick"]

    if command == "user" and os.path.exists("/slashem/dgldir/userdata/{}".format(commandtext)):
        reply("https://em.slashem.me/userdata/{}".format(commandtext), dictofstuff)
    elif command == "user":
        reply('No such user: "{}"'.format(commandtext), dictofstuff)

    if command == "slashemrc" and os.path.exists("/slashem/dgldir/userdata/{0}/{0}.slashemrc".format(commandtext)):
        reply("https://em.slashem.me/userdata/{0}/{0}.slashemrc".format(commandtext), dictofstuff)
    elif command == "slashemrc":
        reply("I couldn't find that...", dictofstuff)

    if command == "nethackrc" and os.path.exists("/slashem/dgldir/userdata/{0}/nethack/{0}.nh360rc".format(commandtext)):
        reply("https://em.slashem.me/userdata/{0}/nethack/{0}.nh360rc".format(commandtext), dictofstuff)
    elif command == "nethackrc":
        reply("I couldn't find that...", dictofstuff)

    if command == "slexrc" and os.path.exists("/slashem/dgldir/userdata/{0}/slex/{0}.slexrc".format(commandtext)):
        reply("https://em.slashem.me/userdata/{0}/slex/{0}.slexrc".format(commandtext), dictofstuff)
    elif command == "slexrc":
        reply("I couldn't find that...", dictofstuff)

    if command == "save" and os.path.exists("/slashem/games/slex-1.7.6/slexdir/1003{}".format(commandtext)):
        reply("{} has a save file, last modified {}.".format(commandtext, " ".join(ctime(os.path.getmtime("/slashem/games/slex-1.7.6/slexdir/1003{}".format(commandtext))).split()[:3])), dictofstuff)
    elif command == "save":
        reply("{} does not have a save file".format(commandtext), dictofstuff)

    if command == "tell":
        tellfromnick = dictofstuff["nick"]
        telltonick = commandtext.split()[0]
        tellmsg = " ".join(commandtext.split()[1:])
        tellattime = time()
        if telltonick.lower() != tellfromnick.lower():
            try:
                telldict[telltonick.lower()]
            except KeyError:
                telldict[telltonick.lower()] = []
            telldict[telltonick.lower()].append({"fromnick": tellfromnick,
                                                 "msg": tellmsg,
                                                 "time": int(tellattime)})
            reply("I'll get that, {}.".format(dictofstuff["nick"]), dictofstuff)
            print(telldict)
            updateconfigfile()
        else:
            reply("{}: tell yourself!".format(dictofstuff["nick"]), dictofstuff)

    elif command == "rng":
        if commandtext.find("|") != -1:
            reply("The RNG says: {}".format(random.choice(commandtext.split("|"))), dictofstuff)
        else:
            reply(random.choice(commandtext.split()), dictofstuff)

    elif command == "roulette" and dictofstuff["target"] == "#em.slashem.me":
        gunslot = random.randrange(3)
        print("gun is at {}".format(gunslot))
        if gunslot:
            reply("{}: *click*".format(dictofstuff["nick"]), dictofstuff)
        else:
            kick(dictofstuff["nick"], "BANG!", "#em.slashem.me")
#}


def mastercommands(commandtext):
#{
    global voiced
    global autoopped
    # Strip out the leading "!"
    command = "".join(list(commandtext.split()[0].lower())[1:])
    # Strip out the leading !${command}
    commandtextstr = " ".join(commandtext.split()[1:])
    commandtext = commandtextstr.split()

    if command == "kick":
        kickednick = commandtext[0]
        reason = " ".join(commandtext[1:])
        kick(kickednick, reason, "#em.slashem.me")
    elif command == "ban":
        for i in commandtext:
            ban("{}!*@*".format(i), "#em.slashem.me")

    elif command == "unban":
        for i in commandtext:
            unban("{}!*@*".format(i), "#em.slashem.me")

    elif command == "kickban":
        kick(commandtext[0], commandtext[1:], "#em.slashem.me")
        ban("{}!*@*".format(commandtext[0]), "#em.slashem.me")

    elif command == "command":
        send(commandtextstr)
    elif command == "op":
        for i in commandtext:
            op(i, "#em.slashem.me")
    elif command == "voice":
        for i in commandtext:
            voice(i, "#em.slashem.me")
    elif command == "deop":
        for i in commandtext:
            deop(i, "#em.slashem.me")
    elif command == "devoice":
        for i in commandtext:
            devoice(i, "#em.slashem.me")
    elif command == "autoop":
        for i in commandtext:
            autoopped.append(i)
        updateconfigfile()
    elif command == "autovoice":
        for i in commandtext:
            voiced.append(i)
        updateconfigfile()
    elif command == "deautoop":
        for i in commandtext:
            try:
                del autoopped[autoopped.index(i)]
            except ValueError:
                reply("{} is not currently autoopped.  u mad?".format(i), dictofstuff)
    elif command == "deautovoice":
        for i in commandtext:
            try:
                del voiced[voiced.index(i)]
            except ValueError:
                reply("{} is not currently autovoiced.  u mad?".format(i), dictofstuff)

    elif command == "rejoin":
        for i in CHANS:
            part(i, False)
            joinchan(i)
            waitfornames()
    elif command == "join":
        for i in commandtext:
            joinchan(i)
            waitfornames()
    elif command == "part":
        if commandtext[1:]:
            parttext = " ".join(commandtext[1:])
        else:
            parttext = False

        part(commandtext[0], parttext)
    elif command == "reconnect":
        quit("")
        global threaddone
        threaddone = True
        connect()
    elif command == "quit":
        if commandtext:
            quit(commandtext)
        else:
            quit("")
        sys.exit(0)
#}


# Handle the recieving of messages that have been !telled them by another user.
def handlemsgs(tonick, channel):
#{
    print("handlemsgs() was called")
    global telldict
    tomsgs = telldict[tonick.lower()]
    if printingstuff:
        print(tomsgs)

    # Clear their msg pool
    del telldict[tonick.lower()]
    print(telldict)

    # Yes this is hacky, but it isn't my fault that python lacks
    # blah : blah ? blah
    if len(tomsgs) > 1:
        sendmsg("{}: you have {} new messages, most recent from {}.".format(tonick,len(tomsgs), tomsgs[-1]["fromnick"]), channel)
    else:
        sendmsg("{}: you have 1 new message from {}.".format(tonick, tomsgs[0]["fromnick"]), channel)
    for i in tomsgs:
        if len(tomsgs) > 1:
            # \x02 == bold/endbold
            sendmsg('\x02{}\x02 said "{}"'.format(i["fromnick"],i["msg"]), channel)
        else:
            sendmsg('{} said "{}"'.format(i["fromnick"],i["msg"]), channel)
    updateconfigfile()
#}
def waitfornames():
#{
    done = False
    while not done:
        readbuffer = s.recv(2048).decode("UTF-8").strip("\r\n")
        print(u"<> {}".format(readbuffer))
        if readbuffer.find(":End of /NAMES list.") != -1:
            done = True
            print("Got names")
#}

connect()
finishemoff()
print("Finished them off")
checkformore()
