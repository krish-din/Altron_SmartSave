# -*- coding: utf-8 -*-
"""
Created on Sat Nov 09 18:24:47 2019

@author: cyril
"""
import json
import cherrypy
import cherrypy_cors
from pymongo import MongoClient


class houseService():

    def __init__(self):
        self.mongoClient = MongoClient('localhost:27017',
                                       username='admin',
                                       password='IDP',
                                       authSource='admin')

        self.mongoDB = self.mongoClient["Altron_HouseDetails"]

    def getTelUsers(self, houseID):

        query = {"HouseID": houseID}
        val = self.mongoDB["houseDetails"].find(query, {"_id": 0, "telUsers": 1})
        try:
            return (self._formJson("success", val.next()))
        except StopIteration:
            return (self._formJson("success", []))

    def getInfo(self, data):
        if data["by"] == "tel":
            filterBy = "telUsers"
        else:
            filterBy = "HouseID"

        query = {"{}".format(filterBy): data["input"]}
        val = self.mongoDB["houseDetails"].find(query, {"_id": 0})
        try:
            return (self._formJson("success", val.next()))
        except StopIteration:
            return (self._formJson("success", ""))

    def getHouseIDs(self):

        val = self.mongoDB["houseDetails"].distinct("HouseID")
        try:
            return (self._formJson("success", val))
        except StopIteration:
            return (self._formJson("success", ""))

    def getLimitsInfo(self, data):

        query = {"HouseID": data}
        val = self.mongoDB["houseDetails"].find(query, {"_id": 0, "plugLimit": 1, "tempLimit": 1, "pirLimit": 1})
        try:
            return (self._formJson("success", val.next()))
        except StopIteration:
            return (self._formJson("success", ""))

    def updateHouse(self, data):

        res = self.mongoDB["houseDetails"].update_one(
            {"HouseID": data["houseID"]},
            {"$set": {"catalogURL": data["catalogURL"],
                      "plugLimit": int(data["plugLimit"].encode()),
                      "tempLimit": int(data["tempLimit"].encode()),
                      "pirLimit": int(data["pirLimit"].encode())
                      }
             })
        if res.acknowledged:
            return (self._formJson("success", "Updated"))
        else:
            return (self._formJson("failed", "Failed to update House"))

    def addTelegramUser(self, data):
        for i in data["users"]:
            res = self.mongoDB["houseDetails"].update_one(
                {"HouseID": data["houseID"]},
                {"$push": {"telUsers": int(i.encode())}}
            )
        if res.acknowledged:
            return (self._formJson("success", "Updated"))
        else:
            return (self._formJson("failed", "fail to add user"))

    def addHouseDetails(self, data):

        val = self.mongoDB["houseDetails"].count_documents({"HouseID": data["houseID"]})

        if val:
            return (self._formJson("Failed", "HouseID exists"))
        else:
            res = self.mongoDB["houseDetails"].insert_one(
                {
                    "catalogURL": data["catalogURL"],
                    "deviceID": data["deviceID"],
                    "HouseID": data["houseID"],
                    "telUsers": [
                    ],
                    "plugLimit": int(data["plugLimit"].encode()),
                    "tempLimit": int(data["tempLimit"].encode()),
                    "pirLimit": int(data["pirLimit"].encode())
                }
            )
            if res.acknowledged:
                return (self._formJson("success", "Inserted"))
            else:
                return (self._formJson("failed", "fail to add user"))

    def removeHouse(self, data):
        myquery = {"HouseID": data["houseID"]}

        res = self.mongoDB["houseDetails"].delete_one(myquery)
        if res.acknowledged:

            return (self._formJson("success", "Deleted"))
        else:
            return (self._formJson("failed", "Failed to Remove user"))

    def _formJson(self, status, val):
        return (json.dumps({'Result': status, 'Output': val}))


class houseWebService(object):
    exposed = True

    def GET(self, *uri, **params):
        hseDtl = houseService()
        res = None
        if str(uri[0]) == "getTelUsers":
            res = hseDtl.getTelUsers(uri[1])

        elif str(uri[0]) == "getlimits":
            res = hseDtl.getLimitsInfo(uri[1])

        elif str(uri[0]) == "gethouseids":
            res = hseDtl.getHouseIDs()

        else:
            return hseDtl._formJson("Failed", "Wrong request")

        return (res)

    def POST(self, *uri, **params):
        hseDtl = houseService()
        res = None
        inputtext = json.loads(cherrypy.request.body.read())
        method = inputtext["call"]

        if method == "addHouse":
            res = hseDtl.addHouseDetails(inputtext["data"])

        elif method == "addTelUser":
            res = hseDtl.addTelegramUser(inputtext["data"])

        elif method == "updateHouse":
            res = hseDtl.updateHouse(inputtext["data"])

        elif method == "removeHouse":
            res = hseDtl.removeHouse(inputtext["data"])

        elif method == "getInfo":
            res = hseDtl.getInfo(inputtext["data"])


        else:
            return hseDtl._formJson("Failed", "Wrong request")

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
                [('Content-Type', 'application/json'), ]
        }
    }
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 9292,
    })
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)
    cherrypy.tree.mount(houseWebService(), '/houseservice', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
