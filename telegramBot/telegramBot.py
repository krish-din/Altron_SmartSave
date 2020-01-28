import json
import paho.mqtt.client as MQTT
from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import CallbackQueryHandler
import logging

import requests

telBotUsers = {}
# Token
token = '868285920:AAG3yTL9-S0re013K_KbEF6AADbuAIG9ekQ'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def myOnConnect(paho_mqtt, userdata, flags, rc):
    print ("Connected to message broker with result code: " + str(rc))


def myOnMessageReceived(paho_mqtt, userdata, msg):
    broadcast(json.loads(msg.payload)['houseID'], json.loads(msg.payload)['value'])


def getBaseURL(chatID):
    # getting base house catalog API from server house details
    global telBotUsers
    systemFile = open("baseConfig.json")
    systemInfo = json.loads(systemFile.read())
    systemFile.close()
    baseURLReq = {
        "call": "getInfo",
        "data": {"by": "tel", "input": chatID}
    }
    baseURLInfo = json.loads(requests.post(systemInfo["houseDetailsURL"], json.dumps(baseURLReq)).text)

    if baseURLInfo["Result"] == "success":
        telBotUsers[chatID]["deviceID"] = baseURLInfo["Output"]["deviceID"]
        telBotUsers[chatID]["houseID"] = baseURLInfo["Output"]["HouseID"]
        telBotUsers[chatID]["catalogURL"] = baseURLInfo["Output"]["catalogURL"]
        print(telBotUsers)
        initiateSystem(chatID)


def initiateSystem(chatID):
    # checking for registered chatID's and getting device, service catalog url's
    global telBotUsers
    deviceID = telBotUsers[chatID]["deviceID"]
    getInfo = json.loads(requests.get(telBotUsers[chatID]["catalogURL"]
                                      + "/geturlinfo/"
                                      + telBotUsers[chatID]["houseID"] + '/'
                                      + telBotUsers[chatID]["deviceID"]).text)
    if getInfo["Result"] == "success":
        telBotUsers[chatID]["deviceURL"] = getInfo["Output"]["Devices"][deviceID]["DC"].encode()
        telBotUsers[chatID]["serviceURL"] = getInfo["Output"]["Devices"][deviceID]["SC"].encode()
        telBotUsers[chatID]["lastUpdates"].append(getInfo["Output"]["lastUpdate"].encode())
    getAPIs(chatID)
    # return(resAPIs)


def getAPIs(chatID):
    # storing house related APIs for every chat id
    global telBotUsers
    deviceID = telBotUsers[chatID]["deviceID"]
    houseID = telBotUsers[chatID]["houseID"]
    catalogURL = telBotUsers[chatID]["catalogURL"]
    getInfo = json.loads(requests.get(catalogURL + "/getsensorInfo/" + houseID + '/' + deviceID).text)
    if getInfo["Result"] == "success":
        sensorIDs = getInfo["Output"]["Devices"][deviceID]["Sensors"]

    getTelInfo = json.loads(requests.get(catalogURL + "/gettelusers/" + houseID).text)
    if getTelInfo["Result"] == "success":
        telBotUsers[chatID]["telUsers"] = getTelInfo["Output"]["Tel_Users"]

    devReq = {
        "call": "getDeviceName",
        "houseID": houseID,
        "deviceID": deviceID,
        "data": sensorIDs
    }
    devReqResp = json.loads(requests.post(telBotUsers[chatID]["deviceURL"], json.dumps(devReq)).text)

    if devReqResp["Result"] == "success":
        telBotUsers[chatID]["sensors"] = devReqResp["Output"]

    servReq = {
        "call": "getService",
        "houseID": houseID,
        "deviceID": deviceID,
        "data": ["sensorStatusAPI", "DataCollection", "last_update"]
    }
    serviceResp = json.loads(requests.post(telBotUsers[chatID]["serviceURL"], json.dumps(servReq)).text)
    if serviceResp["Result"] == "success":
        telBotUsers[chatID]["sensorStatusAPI"] = serviceResp["Output"]["sensorStatusAPI"]["API"]
        telBotUsers[chatID]["sensorDataAPI"] = serviceResp["Output"]["DataCollection"]["DataInsertAPI"]
        telBotUsers[chatID]["lastUpdates"].append(serviceResp["Output"]["last_update"])
    # return (baseURLs)


# bot functions
def start(update, context):
    global telBotUsers
    """Send Welcome message, get chat_id and store it in resource catalog"""
    update.message.reply_text('Welcome to SmartPlug, a bot to manage your plugs.')
    chat_id = update.message.chat_id
    update.message.reply_text('Your Chat ID:{}'.format(chat_id))
    update.message.reply_text("To get status updates please add your chat id in the website preferences section")
    register(chat_id)
    # storing house related details for every chat id
    telBotUsers[chat_id] = {"lastUpdates": [], "initial": True}


def help(update, context):
    """Send Help message to user"""

    text = 'This bot helps you manage the plugs easily on Telegram:\n\n' \
           'To get status updates register your chat id in the website' \
           'type /status check plug status\n' \
           'type /stats to check plug statistics\n' \
           'type /scheduler to schedule a task\n' \
           'type /switch {plug_id} {On/Off} to switch On/Off a plug' \
           'type /stop to exit'
    update.message.reply_text(text)


def status(update, context):
    """query on plugs' status"""
    """
    state = check_status()

    if state[0]['status'] == 1:
        text1 = 'Turn Off Plug 1'
    else:
        text1 = 'Turn on Plug 1'

    if state[1]['status'] == 1:
        text1 = 'Turn Off Plug 2'
    else:
        text1 = 'Turn on Plug 2'
    """
    global telBotUsers
    chatID = update.message.chat_id

    if chatID in telBotUsers:
        pass
    else:
        update.message.reply_text("User chat id not registered")
        return

    if telBotUsers[chatID]["initial"]:
        print(telBotUsers)
        getBaseURL(chatID)
        telBotUsers[chatID]["initial"] = False

    if checkConfigUpdates(chatID):
        initiateSystem(chatID)
        statusURL = telBotUsers[chatID]["sensorStatusAPI"]
        sensors = telBotUsers[chatID]["sensors"]
        telUsers = telBotUsers[chatID]["telUsers"]
    else:
        statusURL = telBotUsers[chatID]["sensorStatusAPI"]
        sensors = telBotUsers[chatID]["sensors"]
        telUsers = telBotUsers[chatID]["telUsers"]

    if chatID in telUsers:
        keyboard = []
        text = ""
        for i in sensors.keys():
            if 'plug' in i.encode():
                curStatusInfo = json.loads(requests.get(statusURL + "/getstatus/" + i.encode()).text)
                curStatus = curStatusInfo["Output"]
                text = text + "{}:{} ".format(i.encode(), ["On" if curStatus else "Off"][0])
                dispText = "Turn {} {}".format(["Off" if curStatus else "On"][0], i.encode())
                text1 = "Turn {} {}:{}".format(["Off" if curStatus else "On"][0], i.encode(), chatID)
                keyboard.append([InlineKeyboardButton(dispText, callback_data=text1)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text, reply_markup=reply_markup)




def stats(update, context):
    """ask for criterion then query"""
    global telBotUsers
    chatID = update.message.chat_id

    if chatID in telBotUsers:
        pass
    else:
        update.message.reply_text("User chat id not registered")
        return

    if telBotUsers[chatID]["initial"]:
        getBaseURL(chatID)
        telBotUsers[chatID]["initial"] = False

    if checkConfigUpdates(chatID):
        initiateSystem(chatID)
        telUsers = telBotUsers[chatID]["telUsers"]
    else:
        telUsers = telBotUsers[chatID]["telUsers"]

    if chatID in telUsers:
        keyboard = [[InlineKeyboardButton("by day", callback_data='day:{}'.format(chatID)),
                     InlineKeyboardButton("by week", callback_data='week:{}'.format(chatID)),
                     InlineKeyboardButton("by month", callback_data='month:{}'.format(chatID))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please choose the criterion:', reply_markup=reply_markup)
    else:
        update.message.reply_text("User chat id not registered")


def scheduler(update, context):
    """ask for criterion then query"""
    global telBotUsers
    chatID = update.message.chat_id

    if chatID in telBotUsers:
        pass
    else:
        update.message.reply_text("User chat id not registered")
        return

    if telBotUsers[chatID]["initial"]:
        getBaseURL(chatID)
        telBotUsers[chatID]["initial"] = False

    if checkConfigUpdates(chatID):
        initiateSystem(chatID)
        sensors = telBotUsers[chatID]["sensors"]
        telUsers = telBotUsers[chatID]["telUsers"]
    else:
        sensors = telBotUsers[chatID]["sensors"]
        telUsers = telBotUsers[chatID]["telUsers"]

    if chatID in telUsers:
        keyboard = []
        text = ""
        for i in sensors.keys():
            if 'plug' in i.encode():
                text1 = "{}".format(i.encode())
                keyboard.append([InlineKeyboardButton(text1, callback_data="Schedule {}:{}".format(text1, chatID))])

        # keyboard = [[InlineKeyboardButton("Plug 1", callback_data='Plug1'),
        #              InlineKeyboardButton("Plug 2", callback_data='Plug2')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please choose the plug:', reply_markup=reply_markup)
    else:
        update.message.reply_text("User chat id not registered")


def switch(update, context):
    global telBotUsers
    chatID = update.message.chat_id

    if chatID in telBotUsers:
        pass
    else:
        update.message.reply_text("User chat id not registered")
        return

    if telBotUsers[chatID]["initial"]:
        getBaseURL(chatID)
        telBotUsers[chatID]["initial"] = False

    if checkConfigUpdates(chatID):
        initiateSystem(chatID)
        telUsers = telBotUsers[chatID]["telUsers"]
    else:
        telUsers = telBotUsers[chatID]["telUsers"]

    if chatID in telUsers:
        try:
            _id, _status = context.args[0], context.args[1]
            if _id and _status:
                _paho_mqtt.publish('house/' + str(telBotUsers[chatID]["houseID"]) + '/plugwise/' + _id + '/action',
                                   json.dumps({"Appliance_Name": telBotUsers[chatID]["sensors"][_id], "value": _status}),
                                   2)
                update.message.reply_text('Successfully switched {} Plug {}'.format(_status, _id))
        except:
            update.message.reply_text('Use /switch {plug_id} {On/Off} to perform the switch')
    else:
        update.message.reply_text("User chat id not registered")


def button(update, context):
    query = update.callback_query
    text = query_reply(query.data)
    query.edit_message_text(text)


def unknown(update, context):
    help(update, context)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def stop(update, context):
    """Bye, delete chat_id"""
    chat_id = update.message.chat_id
    delete(chat_id)
    update.message.reply_text('Bye')


# helper functions
def register(_id):
    # register chat_id in resource datalog
    print("chat id: ", _id)


def delete(_id):
    # deregister chat_id in resource datalog
    print("chat id: ", _id)


def switch_off(plug_id):
    # publish
    print("switch off ", plug_id)


def broadcast(houseID, msg):
    systemFile = open("baseConfig.json")
    systemInfo = json.loads(systemFile.read())
    systemFile.close()
    getTelUsers = json.loads(requests.get(systemInfo["houseDetailsURL"]
                                          + "/getTelUsers/"
                                          + houseID).text)
    if getTelUsers["Result"] == "success":
        telUsers = getTelUsers["Output"]["telUsers"]
    else:
        telUsers = []
    try:
        for i in telUsers:
            updater.bot.send_message(i, msg, 'Markdown')
    except:
        pass
    # return "Plug 1 consumption too high.\nYou can switch it off using command /switch {plug_id}"


def checkConfigUpdates(chatID):
    global telBotUsers

    getCatUpdate = json.loads(requests.get(telBotUsers[chatID]["catalogURL"] + "/getlastupdate/"
                                           + telBotUsers[chatID]["houseID"]).text)
    catUpdate = getCatUpdate["Output"]["lastUpdate"]

    getserUpdate = json.loads(requests.get(telBotUsers[chatID]["serviceURL"]
                                           + telBotUsers[chatID]["houseID"] + "/"
                                           + telBotUsers[chatID]["deviceID"] + "/last_update").text)
    serUpdate = getserUpdate["Output"]

    if (catUpdate != telBotUsers[chatID]["lastUpdates"][0]) \
            or (serUpdate != telBotUsers[chatID]["lastUpdates"][1]):
        print("restarting")
        # tl.stop()
        return 1
    else:
        return 0


def check_status():
    # contact rc to get sensorStatusAPI address
    # get the value by requests

    # status = requests.get(url + '/' + plug_id)
    # result = {"id": plug_id, "status": status}

    result = [{"id": 1, "status": 1}, {"id": 2, "output": 0}]
    return result


def query_reply(inputData):
    global telBotUsers
    s, chatID = inputData.split(":")[0], int(inputData.split(":")[1].encode())
    if s == 'day':
        return 'Stats by day {}'.format(":".join(telBotUsers[chatID]["deviceURL"].split(":", 2)[:2])
                                        + ":7000/dashboard_24hours.html")
    elif s == 'week':
        return 'Stats by week {}'.format(":".join(telBotUsers[chatID]["deviceURL"].split(":", 2)[:2])
                                         + ":7000/dashboard_7days.html")
    elif s == 'month':
        return 'Stats by month {}'.format(":".join(telBotUsers[chatID]["deviceURL"].split(":", 2)[:2])
                                          + ":7000/dashboard_6months.html")
    elif 'Schedule' in s:
        plug_id = s.split()[1]
        _paho_mqtt.publish('house/' + str(telBotUsers[chatID]["houseID"]) + '/'
                           + str(telBotUsers[chatID]["deviceID"]) + '/plugs/schedule',
                           json.dumps({"Appliance_Name": telBotUsers[chatID]["sensors"][plug_id], "value": plug_id}), 2)
        return 'Successfully schedule the task on {}'.format(s)
    elif 'Turn Off' in s:
        plug_id = s.split()[2]
        _paho_mqtt.publish('house/' + str(telBotUsers[chatID]["houseID"]) + '/plugwise/' + plug_id + '/action',
                           json.dumps({"Appliance_Name": telBotUsers[chatID]["sensors"][plug_id], "value": "Off"}), 2)

        return 'Successfully switched off {}'.format(plug_id)
    elif 'Turn On' in s:
        plug_id = s.split()[2]
        _paho_mqtt.publish('house/' + str(telBotUsers[chatID]["houseID"]) + '/plugwise/' + plug_id + '/action',
                           json.dumps({"Appliance_Name": telBotUsers[chatID]["sensors"][plug_id], "value": "On"}), 2)
        return 'Successfully switched on {}'.format(plug_id)


def main():
    global updater
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("scheduler", scheduler))
    dp.add_handler(CommandHandler("switch", switch))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler("stop", stop))

    # on unknown commands - return help message
    dp.add_handler(MessageHandler(Filters.command, unknown))

    # on noncommand i.e message - return help message
    dp.add_handler(MessageHandler(Filters.text, help))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    try:
        _paho_mqtt = MQTT.Client("PlugWise_ActionUpdate", False)
        _paho_mqtt.on_connect = myOnConnect
        _paho_mqtt.connect("mqtt.eclipse.org", 1883)
        _paho_mqtt.loop_start()
        _paho_mqtt.subscribe('altron/centralcontroller/telegram/messages', 2)
    except:
        print("Error connecting to MQTT Broker.")
        pass
    main()
