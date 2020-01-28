import json
import time
import numpy as np
import paho.mqtt.client as MQTT
import requests
from gpiozero import MotionSensor

class MyMQTT:
    def __init__(self, broker, port, notifier, houseID):
        self.broker = broker
        self.port = port
        self.notifier = notifier
        self.houseID = houseID
        self._paho_mqtt = MQTT.Client("readPID", False)
        self._paho_mqtt.on_connect = self.myOnConnect

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        pass
        # print ("Connected to message broker with result code: " + str(rc))

    def myPublish(self, dev_ID, name, data):
        pw_topic = 'house/' + str(self.houseID) + '/pid/' + dev_ID + '/presence'
        js = {"PID": name, "value": data}
        print(js)
        self._paho_mqtt.publish(pw_topic, json.dumps(js), 2)

    def start(self):
        print(self.port)
        self._paho_mqtt.connect(self.broker, int(self.port))
        self._paho_mqtt.loop_start()

    def stop(self):
        self._paho_mqtt.disconnect()
        self._paho_mqtt.loop_stop()


class pidDataCollector:

    def __init__(self):
        self.systemFile = open("baseConfig.json")
        self.systemInfo = json.loads(self.systemFile.read())
        self.systemFile.close()
        self.dc_searchby = 'sensors'
        self.device_search = 'M-Sensors'
        self.mqttStatus = 0
        self.restartSystem = 0
        self.pidtodelete = {}
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

        self.getUpdate = json.loads(requests.get(self.catalogURL + "/getlastupdate/" + self.houseID).text)
        if self.getUpdate["Result"] == "success":
            self.catalog_lastUpdate = self.getUpdate["Output"]["lastUpdate"]

        self.deviceConfigurations()
        self.serviceConfigurations()
        self.initializeMotionSensors()
        self.startSystem()
        self.checkCatalogRegister()
        if self.restartSystem:
            print("restarted")
            self.restartSystem = 0
            self.collect_data()

    def deviceConfigurations(self):
        # Device Details
        self.device_details = json.loads(requests.get(self.dcUrl
                                                      + self.houseID + "/"
                                                      + self.deviceID + "/"
                                                      + self.dc_searchby + "/"
                                                      + self.device_search).text)
        if self.device_details["Result"] == "success":
            if self.restartSystem:
                self.newpidSensors = self.device_details["Output"]["installed{}".format(self.device_search)]
            else:
                self.pidSensors = self.device_details["Output"]["installed{}".format(self.device_search)]

            self.device_lastUpdate = self.device_details["Output"]["last_update"]
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
        for i in self.pidSensors:
            if i['ID'] not in self.info["Devices"][self.deviceID]["Sensors"]:
                print("device not registered in Resource Catalog. Registering now..")
                reg_device = {
                    "call": "adddevices",
                    "HouseID": self.houseID,
                    "data": {"type": "Sensors", "deviceID": self.deviceID, "values": [i["ID"]]}
                }
                requests.post(self.catalogURL, reg_device)

    def serviceConfigurations(self):
        # Service Details
        servReq = {
            "call": "getService",
            "houseID": self.houseID,
            "deviceID": self.deviceID,
            "data": ["MQTT", "last_update", "sensorStatusAPI", self.device_search]
        }
        serviceResp = json.loads(requests.post(self.scUrl, json.dumps(servReq)).text)

        if serviceResp["Result"] == "success":
            self.mqtt_broker = serviceResp["Output"]["MQTT"]["mqtt_broker"]
            self.mqtt_port = serviceResp["Output"]["MQTT"]["mqtt_port"]
            self.service_lastUpdate = serviceResp["Output"]["last_update"]
            self.frequency = serviceResp["Output"][self.device_search]["Frequency"]
            self.sensorStatusAPI = serviceResp["Output"]["sensorStatusAPI"]["API"]
        else:
            print("couldnt recover service details. Trying again")
            time.sleep(60)
            self.serviceConfigurations()

    # initializing motion sensor objects
    def initializeMotionSensors(self):
        self.pirSensors = {}
        for i in self.pidSensors:
            self.pirSensors[i["ID"]] = MotionSensor(i["GPIO"])
        print("Initialised PIRs")

    def startSystem(self):
        # checking for restart due to updates
        if self.restartSystem:
            print("restarting")
            PIDs = [i["ID"] for i in self.newpidSensors]
            if self.pidReadings:
                #  add, delete, update  of sensors
                delta = list(set(PIDs).symmetric_difference(set(self.pidReadings.keys())))
                for j in delta:
                    if j in self.pidReadings.keys():
                        print("removing PID:{}".format(j))
                        self.pidtodelete[j] = [i["Name"] for i in self.pidSensors if i["ID"] == j]
                        [self.pidSensors.pop(idx) for idx, i in enumerate(self.pidSensors) if i["ID"] == j]
                    else:
                        print("adding PID:{}".format(j))
                        self.pidReadings[j] = []
                        [self.pidSensors.append(i) for i in self.newpidSensors if i["ID"] == j]
                if not delta:
                    self.pidSensors = self.newpidSensors
            else:
                self.pidReadings = {i["ID"]: [] for i in self.newpidSensors}
            self.clearAggregatedReadings()
        else:
            self.pidReadings = {i["ID"]: [] for i in self.pidSensors}

        if not self.mqttStatus:
            self.myMqtt = MyMQTT(self.mqtt_broker, self.mqtt_port, self, self.houseID)
            self.myMqtt.start()
            self.mqttStatus = 1

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

    # clearing deleted motion sensor data
    def clearAggregatedReadings(self):
        for idx, pid in enumerate(self.pidtodelete.keys()):
            print("Clearing Readings")
            if sum(self.pidReadings[pid]) == 0:
                self.myMqtt.myPublish(
                    pid,  # id
                    self.pidtodelete[pid],  # name
                    "0")
            else:
                self.myMqtt.myPublish(
                    pid,  # id
                    self.pidtodelete[pid],  # name
                    "1")
            self.pidReadings.pop(pid, None)
            self.pidtodelete.pop(pid, None)

    # updating current sensor status for UI
    def updateSensorStatus(self, motionID, status):
        updateStatus = json.dumps({
            "call": "updateSensor",
            "data": {"sensorID": motionID, "status": status}
        })

        resp = json.loads(requests.post(self.sensorStatusAPI, updateStatus).text)

    # collecting pid sensor data
    def collect_data(self):
        pidInactivity = [0 for i in range(len(self.pidSensors))]
        inActivityCheckCounter = 0
        while not self.restartSystem:
            inActivityCheckCounter += 1
            self.checkConfigUpdates()
            for idx, j in enumerate(self.pidSensors):
                try:
                    pidInactivity[idx] = 0
                    # getting current presence
                    self.pidReadings[j["ID"]].append([1 if self.pirSensors[j["ID"]].motion_detected else 0][0])
                    # publishing pid data if length reaches current frequency
                    if (len(self.pidReadings[j["ID"]])) == ((60 * self.frequency) / 30):
                        # taking mean value of presence instead of 1 or 0 due to pir sensor capability
                        if np.mean(self.pidReadings[j["ID"]]) < 0.1:
                            self.myMqtt.myPublish(
                                j['ID'],
                                j['Name'],
                                "0")
                            self.updateSensorStatus(j["ID"], 0)
                        else:
                            self.myMqtt.myPublish(
                                j['ID'],
                                j['Name'],
                                "1")
                            self.updateSensorStatus(j["ID"], 1)
                        del self.pidReadings[j["ID"]][:]
                except:
                    # if inactive update the sensor as inactive
                    if pidInactivity[idx] > 3:
                        j["active"] = 0
                        # update in device catalog
                        inactiveData = {
                            "call": "updateDevices",
                            "houseID": self.houseID,
                            "deviceID": self.deviceID,
                            "catalogURL": self.catalogURL,
                            "data": {"sensor": self.device_search,
                                     "sensorID": j['ID'],
                                     "properties": {"active": 0}}
                        }
                        requests.post(self.dcUrl, json.dumps(inactiveData))
                    print ("Motion Sensor:" + j['ID'] + " not Active")

            # checking inactive sensors current status
            if inActivityCheckCounter >= 5:
                print("checking Inactive")
                inActivityCheckCounter = 0
                inActivePID = filter(lambda curPID: curPID['active'] == 0, self.pidSensors)
                for pid in inActivePID:
                    motion = None
                    try:
                        motion = self.pirSensors[pid["ID"]].motion_detected
                        if motion is not None:
                            # update in device catalog
                            activeData = {
                                "call": "updateDevices",
                                "houseID": self.houseID,
                                "deviceID": self.deviceID,
                                "catalogURL": self.catalogURL,
                                "data": {"sensor": self.device_search,
                                         "sensorID": pid['ID'],
                                         "properties": {"active": 1}}
                            }
                            requests.post(self.dcUrl, json.dumps(activeData))
                    except:
                        pass
            time.sleep(30)


if __name__ == '__main__':
    collect = pidDataCollector()
    collect.collect_data()
