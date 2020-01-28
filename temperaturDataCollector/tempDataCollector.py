import json
import time
import Adafruit_DHT as dht
import paho.mqtt.client as MQTT
import requests


class MyMQTT:
    def __init__(self, broker, port, notifier, houseID):
        self.broker = broker
        self.port = port
        self.notifier = notifier
        self.houseID = houseID
        self._paho_mqtt = MQTT.Client("Readtemperature", False)
        self._paho_mqtt.on_connect = self.myOnConnect

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        pass
        # print ("Connected to message broker with result code: " + str(rc))

    def myPublish(self, plug_id, name, data):
        pw_topic = 'house/' + str(self.houseID) + '/temperature/'+plug_id+'/rwTmp'
        # print(pw_topic)
        js = {"Temperature": name, "value": data}
        print(js)
        self._paho_mqtt.publish(pw_topic, json.dumps(js), 2)

    def start(self):
        print(self.port)
        self._paho_mqtt.connect(self.broker, int(self.port))
        self._paho_mqtt.loop_start()

    def stop(self):
        self._paho_mqtt.disconnect()
        self._paho_mqtt.loop_stop()


class tempDataCollector:
    def __init__(self):
        self.systemFile = open("baseConfig.json")
        self.systemInfo = json.loads(self.systemFile.read())
        self.systemFile.close()
        self.dc_searchby = 'sensors'
        self.device_search = 'T-Sensors'
        self.mqttStatus = 0
        self.restartSystem = 0
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
        if self.restartSystem:
            print("restarted")
            self.restartSystem = 0
            self.collect_data()

    # getting temperature sensor details
    def deviceConfigurations(self):
        # Device Details
        self.device_details = json.loads(requests.get(self.dcUrl
                                                      + self.houseID + "/"
                                                      + self.deviceID + "/"
                                                      + self.dc_searchby + "/"
                                                      + self.device_search).text)
        if self.device_details["Result"] == "success":
            self.tempSensors = self.device_details["Output"]["installed{}".format(self.device_search)]

        else:
            print("Couldnt recover device details")
            time.sleep(60)
            self.deviceConfigurations()

        getDevUpdate = json.loads(requests.get(self.dcUrl
                                               + self.houseID + "/"
                                               + self.deviceID + "/getlastupdate").text)
        self.device_lastUpdate = getDevUpdate["Output"]

        # checking device registration in catalog
        for i in self.tempSensors:
            if i['ID'] not in self.info["Devices"][self.deviceID]["Sensors"]:
                print("device not registered in Resource Catalog. Registering now..")
                reg_device = {
                    "call": "adddevices",
                    "HouseID": self.houseID,
                    "data": {"type": "Sensors", "deviceID": self.deviceID, "values": [i["ID"]]}
                }
                requests.post(self.catalogURL, reg_device)

    # getting user service details
    def serviceConfigurations(self):
        # Service Details
        servReq = {
            "call": "getService",
            "houseID": self.houseID,
            "deviceID": self.deviceID,
            "data": ["MQTT", "last_update"]
        }
        serviceResp = json.loads(requests.post(self.scUrl, json.dumps(servReq)).text)

        if serviceResp["Result"] == "success":
            self.mqtt_broker = serviceResp["Output"]["MQTT"]["mqtt_broker"]
            self.mqtt_port = serviceResp["Output"]["MQTT"]["mqtt_port"]
            self.service_lastUpdate = serviceResp["Output"]["last_update"]
        else:
            print("couldnt recover service details. Trying again")
            time.sleep(60)
            self.serviceConfigurations()

    # start collecting temperature data
    def startSystem(self):
        self.myMqtt = MyMQTT(self.mqtt_broker, self.mqtt_port, self, self.houseID)
        self.myMqtt.start()

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
            self.restartSystem = 1
            self.initSystem()

    # collecting temperature data from DHT11
    def collect_data(self):
        tempInactivity = [0 for i in range(len(self.tempSensors))]
        inActivityCheckCounter = 0
        while not self.restartSystem:
            inActivityCheckCounter += 1
            self.checkConfigUpdates()
            for idx, i in enumerate(self.tempSensors):
                try:
                    tempInactivity[idx] = 0
                    humidity, temperature = dht.read_retry(11, i['GPIO'])
                    self.myMqtt.myPublish(
                        i['ID'],
                        i['Name'],
                        temperature)
                except:
                    tempInactivity[idx] = tempInactivity[idx] + 1
                    if tempInactivity[idx] > 3:
                        i["active"] = 0
                        # update in device catalog
                        inactiveData = {
                            "call": "updateDevices",
                            "houseID": self.houseID,
                            "deviceID": self.deviceID,
                            "catalogURL": self.catalogURL,
                            "data": {"sensor": self.device_search,
                                     "sensorID": i['ID'],
                                     "properties": {"active": 0}}
                        }
                        requests.post(self.dcUrl, json.dumps(inactiveData))
                    print ("Temperature Sensor:" + i['ID'] + " not Active")

            # checking inactive sensors current status
            if inActivityCheckCounter >= 5:
                print("checking Inactive")
                inActivityCheckCounter = 0
                inActiveTemp = filter(lambda curtemp: curtemp['active'] == 0, self.tempSensors)
                for temp in inActiveTemp:
                    power = None
                    try:
                        humidity, temperature = dht.read_retry(11, temp['GPIO'])
                        if temperature is not None:
                            # update in device catalog
                            activeData = {
                                "call": "updateDevices",
                                "houseID": self.houseID,
                                "deviceID": self.deviceID,
                                "catalogURL": self.catalogURL,
                                "data": {"sensor": self.device_search,
                                         "sensorID": temp['ID'],
                                         "properties": {"active": 1}}
                            }
                            requests.post(self.dcUrl, json.dumps(activeData))
                    except:
                        pass
            time.sleep(60)


if __name__ == '__main__':
    collect = tempDataCollector()
    collect.collect_data()
