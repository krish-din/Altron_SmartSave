# -*- coding: utf-8 -*-
"""
Created on Sat Nov 09 18:24:47 2019

@author: cyril
"""
from datetime import datetime
import json
import cherrypy
import cherrypy_cors
from pymongo import MongoClient


class loginSer():

    def __init__(self):
        self.mongoClient = MongoClient('localhost:27017',
                                       username='admin',
                                       password='IDP',
                                       authSource='admin')

        self.mongoDB = self.mongoClient["Altron"]

    def getHouseCount(self):
        val = self.mongoDB["login"].find({"admin": 0}, {"_id": 0, "HouseID": 1})
        houses = []
        for i in val:
            houses.append(i["HouseID"])
        try:
            return (self._formJson("success", houses))
        except StopIteration:
            return (self._formJson("success", ""))

    def getInfo(self, data):
        val = self.mongoDB["login"].find({"name": data["name"], "pasw": data["password"]}
                                         , {"_id": 0, "pasw": 0})
        try:
            return (self._formJson("success", val.next()))
        except StopIteration:
            return (self._formJson("success", ""))

    def updateUser(self, users):
        val = self.mongoDB["login"].count_documents({"name": users["name"]})

        if val:
            res = self.mongoDB["login"].update_one(
                {"name": users["name"]},
                {"$set": {"pasw": users["paswd"]}})
            if res.acknowledged:
                return (self._formJson("success", "Updated"))
            else:
                return (self._formJson("failed", "failed to update password"))

        else:
            return (self._formJson("Failed", "No such user exists"))

    def addWebUser(self, users):

        val = self.mongoDB["login"].count_documents({"$or": [{"name": users["name"]}, {"HouseID": users["houseID"]}]})

        if val:
            return (self._formJson("Failed", "HouseID/EmailID exists"))
        else:
            res = self.mongoDB["login"].insert_one(
                {"name": users["name"],
                 "pasw": users["paswd"],
                 "tsURL": "",
                 "tsKeys": "",
                 "HouseID": users["houseID"],
                 "admin": 0}
            )
            if res.acknowledged:
                return (self._formJson("success", "Inserted"))
            else:
                return (self._formJson("failed", "fail to add user"))

    def removeWebUser(self, users):
        myquery = {"name": users["name"]}

        res = self.mongoDB["catalog"].delete_one(myquery)
        if res.acknowledged:

            return (self._formJson("success", "Deleted"))
        else:
            return (self._formJson("failed", "Failed to Remove user"))

    def _formJson(self, status, val):
        return (json.dumps({'Result': status, 'Output': val}))


class loginWebService(object):
    exposed = True

    def GET(self, *uri, **params):
        lgnSer = loginSer()
        res = None
        if str(uri[0]) == "gethousecount":
            res = lgnSer.getHouseCount()
        else:
            return lgnSer._formJson("Failed", "Wrong request")

        return (res)

    def POST(self, *uri, **params):
        lgnSer = loginSer()
        res = None
        inputtext = json.loads(cherrypy.request.body.read())
        method = inputtext["call"].encode()
        print(method)
        if method == "addUser":
            res = lgnSer.addWebUser(inputtext["Users"])

        elif method == "updateUser":
            res = lgnSer.updateUser(inputtext["Users"])

        elif method == "removeUser":
            res = lgnSer.removeWebUser(inputtext["Users"])

        elif method == "getInfo":
            res = lgnSer.getInfo(inputtext["data"])

        else:
            return lgnSer._formJson("Failed", "Wrong request")

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
        'server.socket_port': 9191,
    })
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)
    cherrypy.tree.mount(loginWebService(), '/loginservice', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
