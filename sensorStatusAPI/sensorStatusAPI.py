import json
from datetime import datetime
import time
import cherrypy_cors
import cherrypy
import requests
import paho.mqtt.client as MQTT

mqttStarted = False


class MyMQTT:
    def __init__(self, broker, port, houseID):
        self.broker = broker
        self.port = port
        self.houseID = houseID
        self._paho_mqtt = MQTT.Client("PlugWise_ActionUpdate", False)
        self._paho_mqtt.on_connect = self.myOnConnect

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print ("Connected to message broker with result code: " + str(rc))

    def on_disconnect(self):
        self._paho_mqtt.loop_stop()

    def myPublish(self, plug_id, pw_name, pw_data):
        pw_topic = 'house/' + str(self.houseID) + '/plugwise/' + plug_id + '/action'

        js = {"Appliance_Name": pw_name, "value": pw_data}
        print(pw_topic, js)
        self._paho_mqtt.publish(pw_topic, json.dumps(js), 2)

    def start(self):
        print(self.port)
        self._paho_mqtt.connect(self.broker, int(self.port))
        self._paho_mqtt.loop_start()

    def stop(self):
        self._paho_mqtt.disconnect()


class sensorStatus():

    def __init__(self):
        self.devicefile = open("sensorStatus.json")
        self.sensorStatus = json.loads(self.devicefile.read())
        self.devicefile.close()
        self.systemFile = open("baseConfig.json")
        self.systemInfo = json.loads(self.systemFile.read())
        self.systemFile.close()

    def getServiceURL(self):
        global mqttStarted
        self.deviceID = self.systemInfo["deviceID"]
        self.catalogURL = self.systemInfo["catalogURL"]
        self.getInfo = json.loads(requests.get(self.catalogURL + "/getinfo/" + self.deviceID).text)
        if self.getInfo["Result"] == "success":
            self.info = self.getInfo["Output"]
            self.houseID = self.info["HouseID"].encode()
            self.scUrl = self.info["Devices"][self.deviceID]["SC"].encode()

        servReq = {
            "call": "getService",
            "houseID": self.houseID,
            "deviceID": self.deviceID,
            "data": ["MQTT"]
        }
        serviceResp = json.loads(requests.post(self.scUrl, json.dumps(servReq)).text)

        if serviceResp["Result"] == "success":
            self.mqtt_broker = serviceResp["Output"]["MQTT"]["mqtt_broker"]
            self.mqtt_port = serviceResp["Output"]["MQTT"]["mqtt_port"]

        self.myMqtt = MyMQTT(self.mqtt_broker, self.mqtt_port, self.houseID)
        if mqttStarted:
            print("stopped")
            self.myMqtt.stop()
            time.sleep(1)
            self.myMqtt.start()
        else:
            print("started")
            mqttStarted = True
            self.myMqtt.start()

    def getStatus(self, sensorID):
        res = None
        if sensorID == "onplugs":
            res = [i for i in self.sensorStatus
                   if self.sensorStatus[i] == 1 and 'plug' in i]
            return (self._formJson("success", res))

        elif sensorID == "offplugs":
            res = [i for i in self.sensorStatus
                   if self.sensorStatus[i] == 0 and 'plug' in i]
            return (self._formJson("success", res))
        else:
            try:
                res = self.sensorStatus[sensorID]
                return (self._formJson("success", res))
            except:
                return (self._formJson("failed", "No such Sensor"))

    def addSensor(self, data):

        try:
            sensorID = data["sensorID"]

            allow = [1 for i in self.sensorStatus.keys() if i == sensorID]

            if not len(allow):

                updateTime = str(datetime.now()).rsplit(':', 1)[0]
                self.sensorStatus["last_update"] = updateTime
                self.sensorStatus[sensorID] = 0
                with open('sensorStatus.json', 'w') as f:
                    f.write(json.dumps(self.sensorStatus))
                    f.close()
            else:
                return (self._formJson("Failed", "Same ID exists"))

            return (self._formJson("success", "Sensor Added"))

        except:
            return (self._formJson("failed", "Failed to Add"))

    def updateSensorweb(self, data):
        self.getServiceURL()
        sensorID = data["sensorID"]
        sensorName = data["sensorName"]
        print(data["status"])
        self.myMqtt.myPublish(sensorID, sensorName, data["status"])
        #        self.myMqtt.stop()
        return (self._formJson("success", "mqttpublish"))

    def updateSensor(self, data):
        try:
            sensorID = data["sensorID"]

            allow = [1 for i in self.sensorStatus.keys() if i == sensorID]

            if len((allow)):
                updateTime = str(datetime.now()).rsplit(':', 1)[0]
                self.sensorStatus["last_update"] = updateTime
                self.sensorStatus[sensorID] = data["status"]
                with open('sensorStatus.json', 'w') as f:
                    f.write(json.dumps(self.sensorStatus))
                    f.close()
                output = "Device updated"
            else:
                return (self._formJson("Failed", "Keys didnt match"))

            return (self._formJson("success", output))

        except:
            return (self._formJson("failed", "Failed to Add"))

    def deleteSensor(self, data):

        try:
            sensorID = data["sensorID"]
            updateTime = str(datetime.now()).rsplit(':', 1)[0]
            self.sensorStatus["last_update"] = updateTime
            self.sensorStatus.pop(sensorID)
            with open('sensorStatus.json', 'w') as f:
                f.write(json.dumps(self.sensorStatus))
                f.close()

            return (self._formJson("success", "Sensor Deleted"))

        except:
            return (self._formJson("failed", "No such Sensor"))

    def _formJson(self, status, val):
        return (json.dumps({'Result': status, 'Output': val}))


class sensorStatusWebService(object):
    exposed = True

    def GET(self, *uri, **params):
        #        return (str(len(params)))
        senStatus = sensorStatus()
        try:
            call = uri[0]

            if call == "getstatus" and len(uri) == 2:
                response = senStatus.getStatus(uri[1])

            else:
                response = (sensorStatus._formJson("failed", "Not a valid request"))

            return (response)
        except:
            return (sensorStatus._formJson("failed", "exception occured"))

    def POST(self, *uri, **params):

        senStatus = sensorStatus()
        res = None
        inputtext = json.loads(cherrypy.request.body.read())
        method = inputtext["call"]

        if method == "addSensor":
            res = senStatus.addSensor(inputtext["data"])

        elif method == "updateSensor":
            res = senStatus.updateSensor(inputtext["data"])

        elif method == "updateSensorWeb":
            print(inputtext)
            res = senStatus.updateSensorweb(inputtext["data"])

        elif method == "deleteSensor":
            res = senStatus.deleteSensor(inputtext["data"])

        else:
            return senStatus._formJson("Failed", "Wrong request")

        return (res)

    def PUT(self, *uri, **params):
        pass

    def DELETE(self):
        pass


def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"


if __name__ == '__main__':
    cherrypy_cors.install()
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.CORS.on': True,
            'cors.expose.on': True,
            'tools.response_headers.headers':
                [('Content-Type', 'application/json')]
        }
    }
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8286,
    })
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)
    cherrypy.tree.mount(sensorStatusWebService(), '/sensorstatus', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
