import json
import time
import numpy as np
import paho.mqtt.client as PahoMQTT
import requests
from datetime import datetime
from calendar import monthrange
import operator


class MyMQTT:
    def __init__(self, name, broker, port, notifier, houseID):
        self.broker = broker
        self.port = port
        self.notifier = notifier
        self.houseID = houseID
        self._paho_mqtt = PahoMQTT.Client(name, False)
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        pass

    def myOnMessageReceived(self, paho_mqtt, userdata, msg):
        self.notifier.notify(msg.topic, msg.payload)

    def myPublish(self, plug_id, pw_name, data, topic=""):
        if not topic:
            pw_topic = 'house/' + str(self.houseID) + '/plugwise/' + plug_id + '/action'
            js = {"Appliance_Name": pw_name, "value": data}
        else:
            pw_topic = topic
            js = {"houseID": pw_name, "value": data}
        self._paho_mqtt.publish(pw_topic, json.dumps(js), 2)

    def mySubscribe(self, topic, qos=2):
        self._paho_mqtt.subscribe(topic, qos)

    def myUnSubscribe(self, topic):
        self._paho_mqtt.unsubscribe(topic)

    def start(self):
        print(self.port)
        self._paho_mqtt.connect(self.broker, int(self.port))
        self._paho_mqtt.loop_start()

    def stop(self):
        self._paho_mqtt.disconnect()
        self._paho_mqtt.loop_stop()


class CentralController:

    def __init__(self):
        self.systemFile = open("baseConfig.json")
        self.systemInfo = json.loads(self.systemFile.read())
        self.systemFile.close()
        self.device_search = 'all'
        self.mqttStatus = 0
        self.restartSystem = 0
        self.deviceToDelete = []
        self.initial = 1
        self.deletedDeviceReadings = {}
        self.deviceToAdd = []
        self.curDevices = []
        self.sortedExpectedHourCost = {}
        self.switchedoffPlugs = {}
        self.scheduledPlugs = []
        self.initSystem()

    # getting Device and Service URL's from resource catalog
    def initSystem(self):
        self.deviceID = self.systemInfo["deviceID"]
        self.catalogURL = self.systemInfo["catalogURL"]
        getInfo = json.loads(requests.get(self.catalogURL + "/getinfo/" + self.deviceID).text)
        if getInfo["Result"] == "success":
            info = getInfo["Output"]
            self.catalog_Sensors = info["Devices"][self.deviceID]["Sensors"]
            self.houseID = info["HouseID"].encode()
            self.dcUrl = info["Devices"][self.deviceID]["DC"].encode()
            self.scUrl = info["Devices"][self.deviceID]["SC"].encode()
        else:
            print("System Initialisation Failed due to Resource Catalog Issues")
            time.sleep(60)
            self.initSystem()

        # storing last update Date to restart the system
        getUpdate = json.loads(requests.get(self.catalogURL + "/getlastupdate/" + self.houseID).text)
        if getUpdate["Result"] == "success":
            self.catalog_lastUpdate = getUpdate["Output"]["lastUpdate"]

        # getting all the system details
        self.deviceConfigurations()
        self.serviceConfigurations()
        self.startSystem()
        self.checkCatalogRegister()
        self.unsubscribeToTopics()
        self.subscribeToTopics()
        if self.restartSystem:
            self.restartSystem = 0
            self.decisionMaking()

    def deviceConfigurations(self):
        # Getting all sensor Details
        device_details = json.loads(requests.get(self.dcUrl
                                                 + self.houseID + "/"
                                                 + self.deviceID + "/"
                                                 + self.device_search).text)

        if device_details["Result"] == "success":
            # if restart get updated sensors
            if self.restartSystem:
                self.new_sensor_details = device_details["Output"]["Plugs"]["installedPlugs"]
                self.new_sensor_details.extend(device_details["Output"]["T-Sensors"]["installedT-Sensors"])
                self.new_sensor_details.extend(device_details["Output"]["M-Sensors"]["installedM-Sensors"])

            else:
                self.plug_details = device_details["Output"]["Plugs"]["installedPlugs"]
                self.tempSensors = device_details["Output"]["T-Sensors"]["installedT-Sensors"]
                self.pidSensors = device_details["Output"]["M-Sensors"]["installedM-Sensors"]
                self.curDevices.extend([i["ID"] for i in self.plug_details])
                self.curDevices.extend([i["ID"] for i in self.tempSensors])
                self.curDevices.extend([i["ID"] for i in self.pidSensors])
        else:
            print("Couldnt recover device details")
            time.sleep(60)
            self.deviceConfigurations()

        getDevUpdate = json.loads(requests.get(self.dcUrl
                                               + self.houseID + "/"
                                               + self.deviceID + "/getlastupdate").text)
        self.device_lastUpdate = getDevUpdate["Output"]

    def checkCatalogRegister(self):
        # checking device registration in catalog
        for i in self.curDevices:
            if i not in self.catalog_Sensors:
                print("device not registered in Resource Catalog. Registering now..")
                reg_device = {
                    "call": "adddevices",
                    "HouseID": self.houseID,
                    "data": {"type": "Sensors", "deviceID": self.deviceID, "values": [i["ID"]]}
                }
                json.loads(requests.post(self.catalogURL, reg_device).text)

    def serviceConfigurations(self):
        # getting all Service Details
        try:
            serviceDetails = json.loads(requests.get(self.scUrl
                                                     + self.houseID + "/"
                                                     + self.deviceID + "/all").text)
            if serviceDetails["Result"] == "success":
                self.mqtt_broker = serviceDetails["Output"]["MQTT"]["mqtt_broker"]
                self.mqtt_port = serviceDetails["Output"]["MQTT"]["mqtt_port"]
                self.telmqtt_broker = serviceDetails["Output"]["TelegramMQTT"]["mqtt_broker"]
                self.telmqtt_port = serviceDetails["Output"]["TelegramMQTT"]["mqtt_port"]
                self.MonthlyCap = serviceDetails["Output"]["Threshold"]["MonthlyCap"]
                self.desiredTemperature = serviceDetails["Output"]["Threshold"]["Temperature"]
                self.sensorDataAPI = serviceDetails["Output"]["DataCollection"]["DataInsertAPI"]
                self.costAPIDetails = serviceDetails["Output"]["Cost"]
                self.plugFrequency = serviceDetails["Output"]["Plugs"]["Frequency"]
                self.tempFrequency = serviceDetails["Output"]["T-Sensors"]["Frequency"]
                self.sensorStatusAPI = serviceDetails["Output"]["sensorStatusAPI"]["API"]
                self.service_lastUpdate = serviceDetails["Output"]["last_update"]
            else:
                print("Service details request failed")
                time.sleep(60)
                self.serviceConfigurations()
        except requests.exceptions.ConnectionError as e:
            print("Connection Failed with {}".format(e))
            time.sleep(120)
            self.serviceConfigurations()

    # starting the system
    def startSystem(self):
        if self.restartSystem:
            print("restarting")
            sensorsIDs = [i["ID"] for i in self.new_sensor_details]
            if self.agg_sensor_readings:
                # add, delete and update sensor details
                delta = list(set(sensorsIDs).symmetric_difference(set(self.agg_sensor_readings.keys())))
                for j in delta:
                    if j in self.agg_sensor_readings.keys():
                        print("removing sensor:{}".format(j))
                        self.deviceToDelete.append(j)
                    else:
                        print("adding sensors:{}".format(j))
                        self.agg_sensor_readings[j] = []
                        if 'plug' in j:
                            self.proj_plug_readings[j] = []
                        self.deviceToAdd.append(j)
                        for i in self.new_sensor_details:
                            if i["ID"] == j:
                                # appending for sensor addition
                                _, _ = self.identifySensorType(j, 'A', i)

                if not delta:
                    self.plug_details = [i for i in self.new_sensor_details if 'plug' in i['ID']]
                    self.tempSensors = [i for i in self.new_sensor_details if 'temp' in i['ID']]
                    self.pidSensors = [i for i in self.new_sensor_details if 'PIR' in i['ID']]

            else:
                self.agg_sensor_readings = {i["ID"]: [] for i in self.new_sensor_details}
                self.proj_plug_readings = {i["ID"]: [] for i in self.new_sensor_details if 'plug' in i['ID']}
            self.clearAggregatedReadings()
        else:
            self.agg_sensor_readings = {i: [] for i in self.curDevices}
            self.proj_plug_readings = {i["ID"]: [] for i in self.plug_details}

        # starting myMQTT for local and global brokers
        self.myMqtt = MyMQTT("centralController", self.mqtt_broker, self.mqtt_port, self, self.houseID)
        self.myMqtt.start()
        self.telMqtt = MyMQTT("TelegramMQTT", self.telmqtt_broker, self.telmqtt_port, self, self.houseID)
        self.telMqtt.start()

    # clearing aggregated readings
    def clearAggregatedReadings(self):
        for idx, i in enumerate(self.deviceToDelete):
            # deleting sensor
            _, _ = self.identifySensorType(i, 'D')
            self.deviceToDelete.pop(idx)

    # identifying sensor for appending new sensors, deleting sensors data
    def identifySensorType(self, name, role='', data=''):
        # A- Append data, D - deleting sensor details/ collected data
        if 'plug' in name:
            sen = "plugwise"
            top = "aggregated_pwr"
            if role == 'A':
                self.plug_details.append(data)
            elif role == 'D':
                [self.plug_details.pop(idx) for idx, i in enumerate(self.plug_details) if i["ID"] == name]
                self.proj_plug_readings.pop(name, None)
                self.agg_sensor_readings.pop(name, None)
        elif 'temp' in name:
            sen = "temperature"
            top = "aggregated_temp"
            if role == 'A':
                self.tempSensors.append(data)
            elif role == "D":
                self.deletedDeviceReadings[name] = {
                    'data': np.mean(self.agg_sensor_readings[name]),
                    'room': [i['Room'] for i in self.tempSensors if i["ID"] == name][0],
                    'expiryTime': int(time.time()) + 60 * 60
                }
                [self.tempSensors.pop(idx) for idx, i in enumerate(self.tempSensors) if i["ID"] == name]
                self.agg_sensor_readings.pop(name, None)
        else:
            sen = "pid"
            top = "presence"
            if role == 'A':
                self.pidSensors.append(data)
            elif role == "D":
                self.deletedDeviceReadings[name] = {
                    'data': np.mean(self.agg_sensor_readings[name]),
                    'room': [i['Room'] for i in self.pidSensors if i["ID"] == name][0],
                    'expiryTime': int(time.time()) + 60 * 60
                }
                [self.pidSensors.pop(idx) for idx, i in enumerate(self.pidSensors) if i["ID"] == name]
                self.agg_sensor_readings.pop(name, None)
        return sen, top

    # subscribing topics
    def subscribeToTopics(self):
        for i in self.deviceToAdd:
            sen, top = self.identifySensorType(i)
            topic = 'house/{}/{}/{}/{}'.format(self.houseID, sen, i, top)
            self.myMqtt.mySubscribe(topic)
        for i in self.curDevices:
            sen, top = self.identifySensorType(i)
            topic = 'house/{}/{}/{}/{}'.format(self.houseID, sen, i, top)
            self.myMqtt.mySubscribe(topic)
        telegramTopic = 'house/{}/{}/plugs/schedule'.format(self.houseID, self.deviceID)
        self.telMqtt.mySubscribe(telegramTopic)

    # un-subscribing deleted topics
    def unsubscribeToTopics(self):
        for i in self.deviceToDelete:
            sen, top = self.identifySensorType(i)
            topic = 'house/{}/{}/{}/{}'.format(self.houseID, sen, i, top)
            self.myMqtt.myUnSubscribe(topic)

    def notify(self, topic, msg):
        try:
            dev = topic.split("/")[3]
            print(topic, msg)
            # scheduling plugs based on topic
            if 'schedule' in topic:
                self.scheduledPlugs.append(str((json.loads(msg)['value'])))
                self.scheduledPlugs = list(set(self.scheduledPlugs))
                print("Scheduled Plugs:{}".format(self.scheduledPlugs))
            else:
                if 'plugwise' in topic:
                    if len(self.proj_plug_readings[dev]) == (60 / self.plugFrequency):
                        self.proj_plug_readings[dev].pop(0)
                    var = [self.agg_sensor_readings[dev].pop(0) if len(self.agg_sensor_readings[dev]) else 0]
                    self.proj_plug_readings[dev].append(float((json.loads(msg)['value'])))
                elif 'temperature' in topic and len(self.agg_sensor_readings[dev]) == (60 / self.tempFrequency):
                    self.agg_sensor_readings[dev].pop(0)
                elif 'presence' in topic and len(self.agg_sensor_readings[dev]) == 1:
                    self.agg_sensor_readings[dev].pop(0)

                self.agg_sensor_readings[dev].append(float((json.loads(msg)['value'])))
            # print(self.agg_sensor_readings)
        except KeyError:
            print("Yet to add the sensor")

    # checking for updates in the system
    def checkConfigUpdates(self):
        getCatUpdate = json.loads(requests.get(self.catalogURL + "/getlastupdate/" + self.houseID).text)
        catUpdate = getCatUpdate["Output"]["lastUpdate"]
        getDevUpdate = json.loads(requests.get(self.dcUrl
                                               + self.houseID + "/"
                                               + self.deviceID + "/getlastupdate").text)
        devUpdate = getDevUpdate["Output"]
        getserUpdate = json.loads(requests.get(self.scUrl
                                               + self.houseID + "/"
                                               + self.deviceID + "/last_update").text)
        serUpdate = getserUpdate["Output"]

        if (catUpdate != self.catalog_lastUpdate) \
                or (devUpdate != self.device_lastUpdate) \
                or (serUpdate != self.service_lastUpdate):
            print("restarting")
            self.restartSystem = 1
            # tl.stop()
            self.initSystem()

    # getting current hour cost for calculating current consumption cost
    def getHourCost(self):
        costDetails = json.loads(requests.get(
            self.costAPIDetails["CostAPI"] + "feeds.json?api_key=" + self.costAPIDetails["read_key"]).text)["feeds"]
        cost = 1
        hour = datetime.now().hour
        for i in costDetails:
            x = [int(j.encode()) for j in i['field2'].split('-')]
            if x[0] > x[1] and (x[0] <= hour <= 23 or 0 <= hour <= x[1]):
                cost = float(i['field3'].encode())
                break
            elif x[0] <= hour <= x[1]:
                cost = float(i['field3'].encode())
                break
        return cost

    # getting current Hour Cap Limit based on remaining month limit
    def findCapLimit(self):
        monthData = json.loads(requests.get(self.sensorDataAPI + "/getmonth?data=cost&type=Plugs&ID=all").text)
        monthConsumption = monthData["Output"]
        remainingDays = monthrange(datetime.now().year, datetime.now().month)[1] - datetime.now().day
        dayCap = float((self.MonthlyCap - monthConsumption)) / remainingDays
        dayData = json.loads(requests.get(self.sensorDataAPI + "/gettoday?data=cost&type=Plugs&ID=all").text)
        dayConsumption = float(sum(dayData["Output"]))
        return dayCap - dayConsumption

    # finding whether current room temperature requires to switch on / off heating appliances based on desired
    # temperature
    def heatingAppliances(self, curSensor):
        tempSensor = [j["data"] for j in self.deletedDeviceReadings
                      if curSensor["Room"] == j["Room"] and time.time() < j["expiryTime"]]

        tempSensor = [j["ID"] for j in self.tempSensors if curSensor["Room"] == j["Room"]]
        if not len(tempSensor) or not self.agg_sensor_readings[tempSensor[0]]:
            return "No Temperature Sensor Values"
        elif self.desiredTemperature + 1 > np.mean(
                self.agg_sensor_readings[tempSensor[0]]) > self.desiredTemperature - 1:
            return 'off'
        elif np.mean(self.agg_sensor_readings[tempSensor[0]]) < self.desiredTemperature:
            return "on"

    # finding whether any presence in a particular room and return 1 or 0
    def presenceAppliances(self, curSensor):
        pidSensor = [j["data"] for j in self.deletedDeviceReadings
                     if curSensor["Room"] == j["Room"] and time.time() < j["expiryTime"]]
        pidSensor = [j["ID"] for j in self.pidSensors if curSensor["Room"] == j["Room"]]
        pidSensor = int(self.agg_sensor_readings[pidSensor[0]][0]) if len(pidSensor) > 0 else 0
        return pidSensor

    # deciding whether to switch on or off the plugs
    def decisionMaking(self):
        while not self.restartSystem:
            self.checkConfigUpdates()
            # getting current day cap
            currentDayCap = self.findCapLimit()
            expectedHourCost = {}
            currentHourCap = currentDayCap / (24 - datetime.now().hour)
            # calculating projected consumption cost based on moving average plug readings
            for idx, plug in enumerate(self.proj_plug_readings):
                if self.proj_plug_readings[plug] and len(self.agg_sensor_readings[plug]):
                    self.agg_sensor_readings[plug].pop(0)
                    expectedHourCost[plug] = np.mean(self.proj_plug_readings[plug]) * self.getHourCost()

            # controlling plugs based on current day cap
            if currentDayCap > 0 and expectedHourCost:
                totalHourCost = sum(expectedHourCost.values())
                self.sortedExpectedHourCost = sorted(expectedHourCost.items(), key=operator.itemgetter(1))
                print("CurrentDayCap:{},CurrentHourCap:{},ExpectedCost:{}".format(currentDayCap, currentHourCap,
                                                                                  totalHourCost))
                if totalHourCost > currentHourCap:
                    for i in self.sortedExpectedHourCost:
                        if int(i[1]) > 0:
                            try:
                                curSensor = [k for k in self.plug_details if k["ID"] == i[0]][0]
                            except IndexError:
                                print("No such plug available in plug_details")
                                self.checkConfigUpdates()
                                break
                            if curSensor["Control"]:
                                # heating appliances requires temperature data to switch off/on
                                if "Heating" in curSensor["Name"]:
                                    response = self.heatingAppliances(curSensor)
                                    if response == "off":
                                        self.myMqtt.myPublish(curSensor['ID'], curSensor['Name'], 'Off')
                                        totalHourCost = totalHourCost - i[1]
                                    elif response == 'on':
                                        print("required")
                                    else:
                                        print("Couldn't find temperature sensor, heating consuming - {}.switch off if not \
                                                needed".format(i[1]))
                                else:
                                    print("Off due to high consumption cost")
                                    self.myMqtt.myPublish(curSensor['ID'], curSensor['Name'], 'Off')
                                    totalHourCost = totalHourCost - i[1]
                                    # storing switched off plugs to switch on later
                                    self.switchedoffPlugs[curSensor['ID']] = {"Sensor": curSensor,
                                                                              "expectedCost":
                                                                                  (expectedHourCost[curSensor['ID']]
                                                                                   / self.getHourCost())}
                            else:
                                # if control is 0, then send message about the current status
                                self.myMqtt.myPublish("", "",
                                                      "{} cannot be controlled".format(curSensor['Name']),
                                                      topic='house/' + self.houseID + '/' + self.deviceID
                                                            + '/messages/telegram')
                                print("Can't Control: {}".format(curSensor["Name"]))

                            if totalHourCost < currentHourCap:
                                break

                    if totalHourCost > currentHourCap:
                        self.telMqtt.myPublish("", self.houseID, "Exceeded Daily Cap.",
                                               topic='altron/centralcontroller/telegram/messages')
                else:
                    # switching on the scheduled plugs based on current consumption
                    if len(self.scheduledPlugs):
                        for idx, k in enumerate(self.scheduledPlugs):
                            try:
                                curSensor = [i for i in self.plug_details if i['ID'] == k][0]
                                self.myMqtt.myPublish(curSensor['ID'], curSensor['Name'], 'On')
                            except IndexError:
                                print("No such sensor")
                            self.scheduledPlugs.pop(idx)
                    else:
                        # restarting switched off plugs based on current consumption
                        restarted = []
                        for i in self.switchedoffPlugs:
                            curSensor = self.switchedoffPlugs[i]["Sensor"]
                            print("Checking switched Off Plugs")
                            if totalHourCost + (
                                    self.switchedoffPlugs[i]["expectedCost"] * self.getHourCost()) < currentHourCap:
                                restarted.append(i)
                                if curSensor["Restart"]:
                                    # restarting presence needed appliances only there is user presence
                                    if curSensor["Presence"]:
                                        if self.presenceAppliances(curSensor):
                                            print("Switching on switched off plug:{}".format(curSensor["Name"]))
                                            self.myMqtt.myPublish(curSensor['ID'], curSensor['Name'], 'On')
                                    else:
                                        print("Switching on switched off plug:{}".format(curSensor["Name"]))
                                        self.myMqtt.myPublish(curSensor['ID'], curSensor['Name'], 'On')
                                else:
                                    self.myMqtt.myPublish("", "",
                                                          "{} can be switched on based on current "
                                                          "consumption".format(curSensor['Name']),
                                                          topic='house/' + self.houseID + '/' + self.deviceID
                                                                + '/messages/telegram')

                        for k in restarted:
                            self.switchedoffPlugs.pop(k, None)
            else:
                if currentDayCap <= 0:
                    self.telMqtt.myPublish("", self.houseID, "Exceeded Monthly Cap.Please update the limit in website",
                                           topic='altron/centralcontroller/telegram/messages')
                    print("send message already exceeded monthly cap limit update to auto-control the system")

            # check for heater in appliances.. switch on if temperature goes low; switch off if temp high
            for k in self.plug_details:
                res = json.loads(requests.get(self.sensorStatusAPI + "/getstatus/{}".format(k["ID"])).text)[
                    "Output"]
                if "Heating" in k["Name"] and not self.initial:
                    resp = self.heatingAppliances(k)
                    print("temperature decision:{}".format(resp))
                    if res:
                        if resp == "off":
                            print("Switching off heater based on desired temperature:{}".format(k["Name"]))
                            self.myMqtt.myPublish(k['ID'], k['Name'], 'Off')
                    else:
                        if resp == 'on':
                            self.myMqtt.myPublish(k['ID'], k['Name'], 'On')

            # presense needed appliances will be switched on/off based on current presence
            getSwtichedOnPlugs = json.loads(requests.get(self.sensorStatusAPI + "/getstatus/onplugs").text)
            swtichedOnPlugs = getSwtichedOnPlugs["Output"]
            for i in swtichedOnPlugs:
                if not self.initial:
                    try:
                        curSensor = [k for k in self.plug_details if k["ID"] == i][0]
                        pidSensor = self.presenceAppliances(curSensor)
                        print("checking presence needed appliances:{}".format(pidSensor))
                        if curSensor["Presence"] and not pidSensor:
                            if curSensor["Control"]:
                                print("Off due to not presence")
                                self.myMqtt.myPublish(curSensor['ID'], curSensor['Name'], 'Off')
                                self.switchedoffPlugs[curSensor['ID']] = {"Sensor": curSensor,
                                                                          "expectedCost": np.mean(
                                                                              self.proj_plug_readings[curSensor['ID']])}
                            else:
                                print("Presence not detected. switch off")
                    except IndexError:
                        print("No such sensor ON")

            # delete expired data
            for i in self.deletedDeviceReadings:
                if time.time() >= i["expiryTime"]:
                    self.deletedDeviceReadings.pop(i, None)

            self.initial = 0
            time.sleep(120)


if __name__ == "__main__":
    controller = CentralController()
    controller.decisionMaking()
#
