# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 13:31:20 2019

@author: cyril
"""

import json
import sensorData as sd
import cherrypy_cors
import cherrypy


class sensorDataWebService(object):
    exposed = True

    def GET(self, *uri, **params):
        op1 = sd.MongoDbClient()
        call = uri[0]
        data = params["data"]
        sensorType = params["type"]
        sensorID = params["ID"]
        if data == "sensor":
            filterBy = "sensorData"
        elif data == "cost":
            filterBy = "consumptionCost"
        if call == "gettoday":
            response = op1.getToday(filterBy, sensorType, sensorID)
        elif call == "getmonth":
            response = op1.getMonth(filterBy, sensorType, sensorID)
        elif call == "getweek":
            response = op1.getWeek(filterBy, sensorType, sensorID)
        elif call == "getweekly":
            response = op1.getWeekly(filterBy, sensorType, sensorID)
        elif call == "getmonthly":
            response = op1.getMonthly(filterBy, sensorType, sensorID)
        else:
            response = json.dumps({'Result': "Failed", 'Output': "Wrong Request"})
        return (response)

    def POST(self):
        op1 = sd.MongoDbClient()
        response = None
        inputtext = json.loads(cherrypy.request.body.read())
        try:
            if inputtext["call"] == "insert":
                print(inputtext["data"])
                response = op1.insertSensorData(inputtext["data"])

            else:
                response = json.dumps({'Result': "Failed", 'Output': "Wrong Request"})
        except:
            response = json.dumps({'Result': "Failed", 'Output': "Request Failed"})

        return (response)

    def PUT(self):
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
        'server.socket_port': 8284,
    })
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)
    cherrypy.tree.mount(sensorDataWebService(), '/sensordata', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
