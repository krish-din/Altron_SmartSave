import json
import time
from datetime import datetime
import numpy as np
import paho.mqtt.client as PahoMQTT
import requests


class MyMQTT:
    def __init__(self, broker, port, notifier, houseID):
        self.broker = broker
        self.port = port
        self.notifier = notifier
        self.houseID = houseID
        self._paho_mqtt = PahoMQTT.Client("PlugWise_Aggregator", False)
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        pass
        # print ("Connected to message broker with result code: " + str(rc))

    def myOnMessageReceived(self, paho_mqtt, userdata, msg):
        self.notifier.notify(msg.topic, msg.payload)

    def myPublish(self, plug_id, pw_name, pw_data):
        pw_topic = 'house/' + str(self.houseID) + '/plugwise/' + plug_id + '/aggregated_pwr'
        js = {"Appliance_Name": pw_name, "value": pw_data}
        print(pw_topic)
        print(js)
        self._paho_mqtt.publish(pw_topic, json.dumps(js), 2)

    def mySubscribe(self, topicRawPwr, qos=2):
        self._paho_mqtt.subscribe(topicRawPwr, qos)

    def myUnSubscribe(self, topic):
        self._paho_mqtt.unsubscribe(topic)

    def start(self):
        print(self.port)
        self._paho_mqtt.connect(self.broker, int(self.port))
        self._paho_mqtt.loop_start()

    def stop(self):
        self._paho_mqtt.disconnect()
        self._paho_mqtt.loop_stop()


class pwDataAggregator:
    def __init__(self):
        self.systemFile = open("baseConfig.json")
        self.systemInfo = json.loads(self.systemFile.read())
        self.systemFile.close()
        self.dc_searchby = 'sensors'
        self.device_search = 'Plugs'
        self.mqttStatus = 0
        self.restartSystem = 0
        self.plugstodelete = {}
        self.plugstoadd = []
        self.startTime = int(time.time())
        self.initSystem()

    # getting Device and Service URL's from resource catalog
    def initSystem(self):
        self.deviceID = self.systemInfo["deviceID"]
        self.catalogURL = self.systemInfo["catalogURL"]
        self.getInfo = json.loads(requests.get(self.catalogURL + "/getinfo/" + self.deviceID).text)
        if self.getInfo["Result"] == "success":
            self.info = self.getInfo["Output"]
            self.houseID = self.info["HouseID"].encode()
            self.dcUrl = self.info["Devices"][self.deviceID]["DC"].encode()
            self.scUrl = self.info["Devices"][self.deviceID]["SC"].encode()
        else:
            print("System Initialisation Failed due to Resource Catalog Issues")
            time.sleep(60)
            self.initSystem()

        # storing last update Date to restart the system
        self.getUpdate = json.loads(requests.get(self.catalogURL + "/getlastupdate/" + self.houseID).text)
        if self.getUpdate["Result"] == "success":
            self.catalog_lastUpdate = self.getUpdate["Output"]["lastUpdate"]

        self.deviceConfigurations()
        self.serviceConfigurations()
        self.startSystem()
        self.checkCatalogRegister()
        self.unsubscribeToTopics()
        self.subscribeToTopics()
        if self.restartSystem:
            print("restarted")
            self.restartSystem = 0
            self.aggregate_Data()

    # getting plug details
    def deviceConfigurations(self):
        # Device Details
        self.device_details = json.loads(requests.get(self.dcUrl
                                                      + self.houseID + "/"
                                                      + self.deviceID + "/"
                                                      + self.dc_searchby + "/"
                                                      + self.device_search).text)
        if self.device_details["Result"] == "success":
            if self.restartSystem:
                self.new_plug_details = self.device_details["Output"]["installed{}".format(self.device_search)]
            else:
                self.plug_details = self.device_details["Output"]["installed{}".format(self.device_search)]

        else:
            print("Couldnt recover device details")
            time.sleep(60)
            self.deviceConfigurations()
        getDevUpdate = json.loads(requests.get(self.dcUrl
                                               + self.houseID + "/"
                                               + self.deviceID + "/getlastupdate").text)
        self.device_lastUpdate = getDevUpdate["Output"]

    # getting user service details
    def serviceConfigurations(self):
        # Service Details
        servReq = {
            "call": "getService",
            "houseID": self.houseID,
            "deviceID": self.deviceID,
            "data": ["MQTT", "last_update", "DataCollection", "Cost", self.device_search]
        }
        serviceResp = json.loads(requests.post(self.scUrl, json.dumps(servReq)).text)

        if serviceResp["Result"] == "success":
            self.mqtt_broker = serviceResp["Output"]["MQTT"]["mqtt_broker"]
            self.mqtt_port = serviceResp["Output"]["MQTT"]["mqtt_port"]
            self.service_lastUpdate = serviceResp["Output"]["last_update"]
            self.frequency = serviceResp["Output"][self.device_search]["Frequency"]
            self.insertDataAPI = serviceResp["Output"]["DataCollection"]
            self.costAPIDetails = serviceResp["Output"]["Cost"]
        else:
            print("couldnt recover service details. Trying again")
            time.sleep(60)
            self.serviceConfigurations()

    # starting the data aggregation
    def startSystem(self):
        # getting updates of the system
        if self.restartSystem:
            print("restarting")
            plugIDs = [i["ID"] for i in self.new_plug_details]
            if self.plug_readings:
                delta = list(set(plugIDs).symmetric_difference(set(self.plug_readings.keys())))
                # addition or deletion of plugs
                for j in delta:
                    if j in self.plug_readings.keys():
                        print("removing plugs{}".format(j))
                        self.plugstodelete[j] = [i["Name"] for idx, i in enumerate(self.plug_details) if i["ID"] == j][
                            0]
                        [self.plug_details.pop(idx) for idx, i in enumerate(self.plug_details) if i["ID"] == j]
                    else:
                        print("adding plugs{}".format(j))
                        self.plug_readings[j] = []
                        self.agg_plug_readings[j] = []
                        self.plugstoadd.append(j)
                        [self.plug_details.append(i) for i in self.new_plug_details if i["ID"] == j]

                if not delta:
                    self.plug_details = self.new_plug_details

            else:
                self.plug_readings = {i["ID"]: [] for i in self.new_plug_details}
                self.agg_plug_readings = {i["ID"]: [] for i in self.new_plug_details}
            self.clearAggregatedReadings()
        else:
            self.plug_readings = {i["ID"]: [] for i in self.plug_details}
            self.plugReadingTime = {i["ID"]: [] for i in self.plug_details}
            self.agg_plug_readings = {i["ID"]: [] for i in self.plug_details}

        self.myMqtt = MyMQTT(self.mqtt_broker, self.mqtt_port, self, self.houseID)
        self.myMqtt.start()

    def checkCatalogRegister(self):
        # checking device registration in catalog
        for i in self.plug_details:
            if i['ID'] not in self.info["Devices"][self.deviceID]["Sensors"]:
                print("device not registered in Resource Catalog. Registering now..")
                reg_device = {
                    "call": "adddevices",
                    "HouseID": self.houseID,
                    "data": {"type": "Sensors", "deviceID": self.deviceID, "values": [i["ID"]]}
                }
                requests.post(self.catalogURL, reg_device)

    # susbcribing to topics
    def subscribeToTopics(self):
        for i in self.plugstoadd:
            self.topicRawPwr = 'house/' + str(self.houseID) + '/plugwise/' + i + '/rwpower'
            self.myMqtt.mySubscribe(self.topicRawPwr)
        for i in range(len(self.plug_details)):
            self.topicRawPwr = 'house/' + str(self.houseID) + '/plugwise/' + self.plug_details[i]['ID'] + '/rwpower'
            self.myMqtt.mySubscribe(self.topicRawPwr)

    # unsubscribing to deleted plug topics
    def unsubscribeToTopics(self):
        for i in self.plugstodelete.keys():
            self.topicRawPwr = 'house/' + str(self.houseID) + '/plugwise/' + i + '/rwpower'
            self.myMqtt.myUnSubscribe(self.topicRawPwr)

    # clearing data collected by deleted plugs
    def clearAggregatedReadings(self):
        for idx, plugs in enumerate(self.plugstodelete.keys()):
            print("Clearing Readings")
            if not len(self.agg_plug_readings[plugs]):
                self.agg_plug_readings[plugs].append(self.plugReadingTime[plugs][0])
            self.agg_plug_readings[plugs].append(
                np.mean(self.plug_readings[plugs][1:]))
            self.plug_readings.pop(plugs, None)
            self.plugReadingTime.pop(plugs, None)
            dt = self.agg_plug_readings[plugs][0]
            oneHourAvg = np.mean(self.agg_plug_readings[plugs][1:])
            sensorData = json.dumps({
                "call": "insert",
                "data": {
                    "date": dt.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                    "sensorType": self.device_search,
                    "sensorID": plugs,
                    "sensorName": self.plugstodelete[plugs],
                    "sensorData": oneHourAvg * (len(self.agg_plug_readings[plugs][1:]) * self.frequency) / 60,
                    "avgtime": 60,
                    "consumptionCost": oneHourAvg * self.getHourCost(dt)
                }
            })
            requests.post(self.insertDataAPI["DataInsertAPI"], sensorData)
            self.agg_plug_readings.pop(plugs, None)
            self.plugstodelete.pop(plugs, None)

    def notify(self, topic, msg):
        try:
            plug_ID = topic.split("/")[3]
            self.plug_readings[plug_ID].append(float((json.loads(msg)['value'])))
            self.plugReadingTime[plug_ID].append(datetime.now())
        except KeyError:
            print("Yet to add the plug")

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
            self.initSystem()

    # getting current hour cost from thingspeak
    def getHourCost(self, dt):
        costDetails = json.loads(requests.get(
            self.costAPIDetails["CostAPI"] + "feeds.json?api_key=" + self.costAPIDetails["read_key"]).text)["feeds"]
        cost = 1
        hour = dt.hour
        for i in costDetails:
            x = [int(j.encode()) for j in i['field2'].split('-')]
            if x[0] > x[1] and (x[0] <= hour <= 23 or 0 <= hour <= x[1]):
                cost = float(i['field3'].encode())
                break
            elif x[0] <= hour <= x[1]:
                cost = float(i['field3'].encode())
                break
        return cost

    # collect plugs power consumption and aggregating them over one hour
    def aggregate_Data(self):
        while not self.restartSystem:
            self.checkConfigUpdates()
            for idx, plugs in enumerate(self.plug_details):
                print("{} readings Length:{}".format(plugs["ID"], len(self.plug_readings[plugs["ID"]])))
                if len(self.plug_readings[plugs["ID"]]) >= self.frequency:
                    if not len(self.agg_plug_readings[plugs["ID"]]):
                        self.agg_plug_readings[plugs["ID"]].append(self.plugReadingTime[plugs["ID"]][0])
                    self.agg_plug_readings[plugs["ID"]].append(
                        np.mean(self.plug_readings[plugs["ID"]][:self.frequency]))
                    self.myMqtt.myPublish(plugs["ID"], plugs['Name'],
                                          np.mean(self.plug_readings[plugs["ID"]][:self.frequency]))
                    del self.plug_readings[plugs["ID"]][:self.frequency]
                    del self.plugReadingTime[plugs["ID"]][:self.frequency]
                    print(self.agg_plug_readings[plugs["ID"]])
                    if len(self.agg_plug_readings[plugs["ID"]]) == (60 / self.frequency) + 1:
                        print("inserting into DB")
                        dt = self.agg_plug_readings[plugs["ID"]][0]
                        oneHourAvg = np.mean(self.agg_plug_readings[plugs["ID"]][1:])
                        sensorData = json.dumps({
                            "call": "insert",
                            "data": {
                                "date": dt.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                                "sensorType": self.device_search,
                                "sensorID": plugs["ID"],
                                "sensorName": plugs["Name"],
                                "sensorData": oneHourAvg,
                                "avgtime": 60,
                                "consumptionCost": oneHourAvg * self.getHourCost(dt)
                            }
                        })
                        requests.post(self.insertDataAPI["DataInsertAPI"], sensorData)
                        del self.agg_plug_readings[plugs["ID"]][:]
            time.sleep(120)


if __name__ == "__main__":
    aggregate = pwDataAggregator()
    aggregate.aggregate_Data()
#
