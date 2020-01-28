# -*- coding: utf-8 -*-
"""
Created on Sun Nov 10 04:01:43 2019

@author: cyril
"""
import json
from datetime import datetime
import cherrypy_cors
import cherrypy
import requests


class Devices:
    def __init__(self):
        self.devicefile = open("devices.json")
        self.devices = json.loads(self.devicefile.read())
        self.devicefile.close()

    def getDevice(self, houseID, deviceID, filterType, deviceFilter=''):
        res = None
        if filterType == "all":
            res = self.devices[houseID][deviceID]

        elif filterType == "getlastupdate":
            res = self.devices[houseID][deviceID]["last_update"]

        elif filterType == "sensors" and deviceFilter:
            try:
                res = self.devices[houseID][deviceID][deviceFilter]
            except:
                res = "No such device type"

        elif filterType == "ID" and deviceFilter:
            res1 = self.devices[houseID][deviceID]
            for i in res1.keys():
                for j in (res1[i]["installed{}".format(i)]):
                    if j["ID"] == deviceFilter:
                        res = j
        else:
            return self._formJson("failed", None)

        if res:
            return self._formJson("success", res)
        else:
            return self._formJson("success", "device not found")

    def getDeviceName(self, houseID, deviceID, sensorIDs):
        curSensors = []
        for i in self.devices[houseID][deviceID].keys():
            if i.encode() != "last_update":
                for j in (self.devices[houseID][deviceID][i]["installed{}".format(i)]):
                    curSensors.append(j)
        res = {}
        for i in sensorIDs:
            for j in curSensors:
                if i == j["ID"]:
                    res[i] = j["Name"].encode()
        if res:
            return self._formJson("success", res)
        else:
            return self._formJson("success", "device not found")

    def addDevice(self, houseID, deviceID, catalogURL, statusURL, data):
        try:
            sensorType = data["sensor"]
            deviceInfo = data["properties"]

            res = self.devices[houseID][deviceID][sensorType]["installed{}".format(sensorType)]

            req = json.loads(
                requests.get(catalogURL + "/getserverurl/" + houseID)
                    .text)
            if req["Result"] == "success":
                serverURL = req["Output"]["serverURL"]

            req = json.loads(
                requests.get(serverURL + "/getlimits/" + houseID)
                    .text)
            if req["Result"] == "success":
                sensorLimit = req["Output"] \
                    ["{}Limit".format(deviceInfo["ID"].split("_")[0].lower())]

            limitExceeded = [0 if sensorLimit > len(res) else 1][0]

            if limitExceeded:
                return (self._formJson("Failed",
                                       "Maximum allowed {} added".format(sensorType)))

            req = json.loads(
                requests.get(catalogURL + "/getkeys/" + houseID + "/" + sensorType)
                    .text)
            if req["Result"] == "success":
                sensorKeys = req["Output"]["SensorKeys"][sensorType]
            # adding if all sensor keys are available
            allow = [1 for i in res
                     if (i["ID"] != deviceInfo["ID"]
                         and sensorKeys[-1] in deviceInfo["ID"]
                         and i["Name"] != deviceInfo["Name"])]

            keysCheck = [1 for i in sensorKeys[:-1] if (i in deviceInfo.keys())]

            if len(res) == sum(allow) and \
                    sum(keysCheck) == len(sensorKeys) - 1:

                self.devices[houseID][deviceID][sensorType]["installed{}".format(sensorType)].append(deviceInfo)
                cat_data = json.dumps({
                    "call": "adddevices",
                    "HouseID": houseID,
                    "data": {"type": "Sensors",
                             "deviceID": deviceID,
                             "values": [deviceInfo["ID"]]}
                })

                json.loads(requests.post(catalogURL, cat_data).text)

                status_data = json.dumps({
                    "call": "addSensor",
                    "data": {"sensorID": deviceInfo["ID"]}
                })
                json.loads(requests.post(statusURL, status_data).text)

                updateTime = str(datetime.now()).rsplit(':', 1)[0]
                self.devices[houseID][deviceID]["last_update"] = updateTime
                self.devices[houseID][deviceID][sensorType]["last_update"] = updateTime
                with open('devices.json', 'w') as f:
                    f.write(json.dumps(self.devices))
                    f.close()
            else:
                return (self._formJson("Failed",
                                       "Same ID or Name exists/ not all keys are there"))

            return self._formJson("success", "Device Added")

        except:
            return self._formJson("failed", "Failed to Add")

    def updateDevice(self, houseID, deviceID, catalogURL, data):
        try:
            sensorType = data["sensor"]
            sensorID = data["sensorID"]
            deviceInfo = data["properties"]

            res = self.devices[houseID][deviceID][sensorType]["installed{}".format(sensorType)]

            req = json.loads(requests.get(catalogURL + "/getkeys/" + houseID + "/" + sensorType).text)
            # updating based on sensor keys
            if req["Result"] == "success":
                sensorKeys = req["Output"]["SensorKeys"][sensorType]

            allow = [1 for i in list(deviceInfo.keys()) if (i in sensorKeys[:-1])]

            nameCheck = 1

            if "Name" in deviceInfo.keys():
                for i in res:
                    if i["Name"] == deviceInfo["Name"] and i["ID"] != sensorID:
                        nameCheck = 0

            if "ID" in deviceInfo.keys():
                return self._formJson("failed", "can't Update Sensor ID")

            if len(deviceInfo.keys()) == sum(allow) and nameCheck:
                for i, j in enumerate(res):
                    if j["ID"] == sensorID:
                        for k in deviceInfo.keys():
                            self.devices[houseID][deviceID][sensorType] \
                                ["installed{}".format(sensorType)][i][k] = deviceInfo[k]
                        output = "Device updated"
                        updateTime = str(datetime.now()).rsplit(':', 1)[0]
                        self.devices[houseID][deviceID]["last_update"] = updateTime
                        self.devices[houseID][deviceID][sensorType]["last_update"] = updateTime
                        break
                    else:
                        output = "Device not found"
            else:
                return self._formJson("Failed", "Keys didn't match/Same name exists")

            with open('devices.json', 'w') as f:
                f.write(json.dumps(self.devices))
                f.close()
            return self._formJson("success", output)

        except:
            return self._formJson("failed", "Failed to Add")

    def deleteDevice(self, houseID, deviceID, catalogURL, statusURL, data):
        try:
            sensorType = data["sensor"]
            sensorID = data["sensorID"]
            #            catalogURL = data["catalogURL"]

            res = self.devices[houseID][deviceID][sensorType]["installed{}".format(sensorType)]
            #            print(res)
            for i, j in enumerate(res):
                #                print(j["ID"])
                if j["ID"] == sensorID:
                    self.devices[houseID][deviceID][sensorType]["installed{}".format(sensorType)].pop(i)

                    cat_data = json.dumps({
                        "call": "remdevices",
                        "HouseID": houseID,
                        "data": {"type": "Sensors",
                                 "deviceID": deviceID,
                                 "values": [j["ID"]]}
                    })
                    json.loads(requests.post(catalogURL, cat_data).text)

                    status_data = json.dumps({
                        "call": "deleteSensor",
                        "data": {"sensorID": j["ID"]}
                    })
                    json.loads(requests.post(statusURL, status_data).text)

                    updateTime = str(datetime.now()).rsplit(':', 1)[0]
                    self.devices[houseID][deviceID]["last_update"] = updateTime
                    self.devices[houseID][deviceID][sensorType]["last_update"] = updateTime
                    with open('devices.json', 'w') as f:
                        f.write(json.dumps(self.devices))
                        f.close()
                    return self._formJson("success", "Device deleted")

            return self._formJson("Failed", "No such Device ")
        except:
            return self._formJson("failed", "Failed to delete")

    def _formJson(self, status, val):
        return json.dumps({'Result': status, 'Output': val})


class DeviceCatalogWebService(object):
    exposed = True

    def GET(self, *uri, **params):
        dev = Devices()
        try:
            houseID = uri[0]
            deviceID = uri[1]
            filtertype = uri[2]

            if filtertype == "all" or filtertype == "getlastupdate":
                response = dev.getDevice(houseID, deviceID, filtertype)

            elif (filtertype == "ID" or filtertype == "sensors") and uri[3]:
                response = dev.getDevice(houseID, deviceID, filtertype, uri[3])

            else:
                response = (dev._formJson("failed", "Not a valid request"))

            return response
        except:
            return dev._formJson("failed", "exception occured")

    def POST(self):
        dev = Devices()
        res = None
        inputtext = json.loads(cherrypy.request.body.read())
        method = inputtext["call"]
        houseID = inputtext["houseID"]
        deviceID = inputtext["deviceID"]

        if method == "addDevice":

            res = dev.addDevice(houseID, deviceID,
                                inputtext["catalogURL"],
                                inputtext["statusURL"],
                                inputtext["data"])

        elif method == "updateDevices":
            res = dev.updateDevice(houseID, deviceID,
                                   inputtext["catalogURL"], inputtext["data"])

        elif method == "getDeviceName":
            res = dev.getDeviceName(houseID, deviceID,
                                    inputtext["data"])

        elif method == "removeDevice":
            res = dev.deleteDevice(houseID, deviceID,
                                   inputtext["catalogURL"],
                                   inputtext["statusURL"]
                                   , inputtext["data"])
        else:
            return dev._formJson("Failed", "Wrong request")

        return res

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
        'server.socket_port': 8282,
    })
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)
    cherrypy.tree.mount(DeviceCatalogWebService(), '/devicecatalog', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
