import json
import time
from serial import SerialException
import paho.mqtt.client as MQTT
import requests
from pyW215.pyW215 import SmartPlug, ON, OFF
import plugwise as pw
import sys, glob, serial

# MQTT broker
class MyMQTT:
    def __init__(self, name, broker, port, notifier, houseID):
        self.broker = broker
        self.port = port
        self.notifier = notifier
        self.houseID = houseID
        self._paho_mqtt = MQTT.Client(name, False)
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        pass
        # print ("Connected to message broker with result code: " + str(rc))

    def myOnMessageReceived(self, paho_mqtt, userdata, msg):
        self.notifier.notify(msg.topic, msg.payload)

    # publishing MQTT message
    def myPublish(self, plug_id, pw_name, pw_data):
        pw_topic = 'house/' + str(self.houseID) + '/plugwise/' + plug_id + '/rwpower'
        js = {"Appliance_Name": pw_name, "value": pw_data}
        print(js)
        self._paho_mqtt.publish(pw_topic, json.dumps(js), 2)

    def mySubscribe(self, topicSub, qos=2):
        self._paho_mqtt.subscribe(topicSub, qos)

    def start(self):
        print(self.port)
        self._paho_mqtt.connect(self.broker, int(self.port))
        self._paho_mqtt.loop_start()

    def stop(self):
        self._paho_mqtt.disconnect()
        self._paho_mqtt.loop_stop()


class pwDataCollector:
    # Initialising the system
    def __init__(self):
        self.systemFile = open("baseConfig.json")
        self.systemInfo = json.loads(self.systemFile.read())
        self.systemFile.close()
        self.dc_searchby = 'sensors'
        self.device_search = 'Plugs'
        self.mqttStatus = 0
        self.restartSystem = 0
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
        self.initializePlugs()
        self.startSystem()
        self.checkCatalogRegister()
        self.subscribeToTopics()
        if self.restartSystem:
            time.sleep(2)
            print("restarted")
            self.restartSystem = 0
            self.collect_data()

    def serial_ports(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    # getting plug details
    def deviceConfigurations(self):
        # Device Details
        self.device_details = json.loads(requests.get(self.dcUrl
                                                      + self.houseID + "/"
                                                      + self.deviceID + "/"
                                                      + self.dc_searchby + "/"
                                                      + self.device_search).text)
        if self.device_details["Result"] == "success":
            self.plug_details = self.device_details["Output"]["installed{}".format(self.device_search)]
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
        for i in self.plug_details:
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
            "data": ["MQTT", "TelegramMQTT", "last_update", "sensorStatusAPI"]
        }
        serviceResp = json.loads(requests.post(self.scUrl, json.dumps(servReq)).text)

        if serviceResp["Result"] == "success":
            self.mqtt_broker = serviceResp["Output"]["MQTT"]["mqtt_broker"]
            self.mqtt_port = serviceResp["Output"]["MQTT"]["mqtt_port"]
            self.telmqtt_broker = serviceResp["Output"]["TelegramMQTT"]["mqtt_broker"]
            self.telmqtt_port = serviceResp["Output"]["TelegramMQTT"]["mqtt_port"]
            self.service_lastUpdate = serviceResp["Output"]["last_update"]
            self.sensorStatusAPI = serviceResp["Output"]["sensorStatusAPI"]["API"]
        else:
            print("couldnt recover service details. Trying again")
            time.sleep(60)
            self.serviceConfigurations()

    # initialising plugs with MAC and IP address
    def initializePlugs(self, plug={}):
        if plug:
            self.plugs.pop(plug["ID"], None)
            if plug["brand"] == "PW":
                self.plugs[plug["ID"]] = pw.Circle(plug['Mac'].encode(), pw.Stick(port='COM7'))
                self.updateSensorStatus(plug["ID"], [1 if self.plugs[plug["ID"]].get_info() == "ON" else 0][0])
            elif plug["brand"] == "DL":
                address, pwd = plug['Mac'].encode().split(":")
                self.plugs[plug["ID"]] = SmartPlug(address, pwd)
                self.updateSensorStatus(plug["ID"], [1 if self.plugs[plug["ID"]].state == "ON" else 0][0])
        else:
            self.plugs = {}
            try:
                ports = self.serial_ports()
                if isinstance(ports[0], serial.serialposix.Serial):
                    pw_port = pw.Stick(port=ports[0].port)
                else:
                    pw_port = pw.Stick(port=ports[0])
            except SerialException:
                print("couldnot connect to port")
            for i in self.plug_details:
                if i["brand"] == "PW":
                    self.plugs[i["ID"]] = pw.Circle(i['Mac'].encode(), pw_port)
                    self.updateSensorStatus(i["ID"], [1 if self.plugs[i["ID"]].get_info() == "ON" else 0][0])
                elif i["brand"] == "DL":
                    address, pwd = i['Mac'].encode().split(":")
                    self.plugs[i["ID"]] = SmartPlug(address, pwd)
                    self.updateSensorStatus(i["ID"], [1 if self.plugs[i["ID"]].state == "ON" else 0][0])
            print("Initialised Plugs")

    # starting the data collection
    def startSystem(self):
        self.plug_readings = [[] for i in range(len(self.plug_details))]
        self.agg_plug_readings = [[] for i in range(len(self.plug_details))]

        self.myMqtt = MyMQTT("PlugWise_Reader", self.mqtt_broker, self.mqtt_port, self, self.houseID)
        self.myMqtt.start()
        self.telMqtt = MyMQTT("TelegramMQTT", self.telmqtt_broker, self.telmqtt_port, self, self.houseID)
        self.telMqtt.start()

    # subscribing to topics
    def subscribeToTopics(self):
        for i in range(len(self.plug_details)):
            self.topicRawPwr = 'house/' + str(self.houseID) + '/plugwise/' + self.plug_details[i]['ID'] + '/action'
            print(self.topicRawPwr)
            self.myMqtt.mySubscribe(self.topicRawPwr)
            self.telMqtt.mySubscribe(self.topicRawPwr)

    # getting subscribed data
    def notify(self, topic, msg):
        plug_ID = topic.split("/")[3]
        print(topic, msg)
        if self.plugs[plug_ID]:
            command = json.loads(msg)["value"].encode()
            plugBrand = filter(lambda plug: plug['ID'] == plug_ID, self.plug_details)[0]["brand"]
            if command == "On":
                if plugBrand == "PW":
                    self.plugs[plug_ID].switch_on()
                elif plugBrand == "DL":
                    self.plugs[plug_ID].state = ON

                self.updateSensorStatus(plug_ID, 1)
            else:
                if plugBrand == "PW":
                    self.plugs[plug_ID].switch_off()
                elif plugBrand == "DL":
                    self.plugs[plug_ID].state = OFF
                self.updateSensorStatus(plug_ID, 0)

    # updating plug status in status json file
    def updateSensorStatus(self, plug_ID, status):
        updateStatus = json.dumps({
            "call": "updateSensor",
            "data": {"sensorID": plug_ID, "status": status}
        })

        resp = json.loads(requests.post(self.sensorStatusAPI, updateStatus).text)

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
            # tl.stop()
            self.initSystem()

    # collecting data from plugs and publishing data to aggregator
    def collect_data(self):
        plugInactivity = [0 for i in range(len(self.plug_details))]
        inActivityCheckCounter = 0
        while not self.restartSystem:
            inActivityCheckCounter += 1
            self.checkConfigUpdates()
            for i in range(len(self.plug_details)):
                if self.plug_details[i]["active"]:
                    try:
                        if self.plug_details[i]["brand"] == "PW":
                            power = self.plugs[self.plug_details[i]['ID']].get_power_usage()
                        elif self.plug_details[i]["brand"] == "DL":
                            power = self.plugs[self.plug_details[i]['ID']].current_consumption
                            power = [power - 0.07 if power != "N/A" else power][0]
                        else:
                            power = "N/A"

                        if power != "N/A":
                            self.myMqtt.myPublish(
                                self.plug_details[i]['ID'],
                                self.plug_details[i]['Name'],
                                power)
                            plugInactivity[i] = 0
                        else:
                            raise Exception
                    except:
                        print ("Plug is not active:" + self.plug_details[i]['ID'])
                        plugInactivity[i] = plugInactivity[i] + 1
                        if plugInactivity[i] > 3:
                            self.plug_details[i]["active"] = 0
                            # update in device catalog
                            inactiveData = {
                                "call": "updateDevices",
                                "houseID": self.houseID,
                                "deviceID": self.deviceID,
                                "catalogURL": self.catalogURL,
                                "data": {"sensor": self.device_search,
                                         "sensorID": self.plug_details[i]['ID'],
                                         "properties": {"active": 0}}
                            }
                            requests.post(self.dcUrl, json.dumps(inactiveData))
                    time.sleep(1)
            # checking inactive plugs current status
            if inActivityCheckCounter >= 5:
                print("checking Inactive")
                inActivityCheckCounter = 0
                inActivePlugs = filter(lambda curPlug: curPlug['active'] == 0, self.plug_details)
                for plug in inActivePlugs:
                    self.initializePlugs(plug)
                    state = None
                    try:
                        if plug["brand"] == "PW":
                            state = self.plugs[plug['ID']].get_info()
                        elif plug["brand"] == "DL":
                            print(self.plugs[plug['ID']])
                            state = self.plugs[plug['ID']].state
                        if state is not None and state != "unknown":
                            # update in device catalog
                            activeData = {
                                "call": "updateDevices",
                                "houseID": self.houseID,
                                "deviceID": self.deviceID,
                                "catalogURL": self.catalogURL,
                                "data": {"sensor": self.device_search,
                                         "sensorID": plug['ID'],
                                         "properties": {"active": 1}}
                            }
                            requests.post(self.dcUrl, json.dumps(activeData))
                    except Exception as e:
                        print e
            time.sleep(60)


if __name__ == '__main__':
    collect = pwDataCollector()
    collect.collect_data()
