import json
from datetime import datetime, timedelta
from pymongo import MongoClient
from dateutil.relativedelta import relativedelta
from dateutil import rrule


class MongoDbClient(object):
    def __init__(self):
        self.mongoClient = MongoClient('localhost:27017')

        self.mongoDB = self.mongoClient["Altron_data"]

    # inserting into DB
    def insertSensorData(self, inputdata):
        if inputdata != "":
            inputdata["date"] = datetime.strptime(inputdata["date"], '%Y-%m-%dT%H:%M:%S.%f')
            print(inputdata)
            res = self.mongoDB["sensorData"].insert_one(inputdata);
            print(res.acknowledged)
            if res.acknowledged:
                reg_jsonres = {'Result': "Success", 'Message': "Inserted"}
            else:
                reg_jsonres = {'Result': "Failed", 'Message': "Insertion Failed"}
            print(reg_jsonres)
        else:
            reg_jsonres = {'Result': "Success", 'Message': "Nothing to Insert"}
        return json.dumps(reg_jsonres)

    # aggregating based on hour
    def getToday(self, filterBy, sensorType, sensor):
        hourCost = [0 for _ in range(24)]
        dt = datetime.combine(datetime.now().date(), datetime.min.time())
        if sensor == "all":
            filtercolumn = "sensorType"
            filterValue = sensorType
        else:
            filtercolumn = "sensorID"
            filterValue = sensor

        res = self.mongoDB["sensorData"].aggregate([
            {"$match": {'date': {"$gte": dt}
                , '{}'.format(filtercolumn): '{}'.format(filterValue)}}
            , {"$project": {'hour': {'$hour': '$date'}, '{}'.format(filterBy): 1, '_id': 0}}
            , {"$group": {"_id": "$hour", "consumption": {"$sum": "${}".format(filterBy)}}}
            , {"$sort": {"_id": 1}}
        ])

        if res:
            for i, j in enumerate(res):
                hourCost[j["_id"]] = j['consumption']

        return self._formJson("success", hourCost)

    # aggregating based on month
    def getMonth(self, filterBy, sensorType, sensor):
        if sensor == "all":
            filtercolumn = "sensorType"
            filterValue = sensorType
        else:
            filtercolumn = "sensorID"
            filterValue = sensor

        mon = datetime.now().month
        res = self.mongoDB["sensorData"].aggregate([
            {"$project": {'month': {'$month': "$date"}, '{}'.format(filtercolumn): 1, '{}'.format(filterBy): 1}},
            {"$match": {'month': mon
                , '{}'.format(filtercolumn): '{}'.format(filterValue)}},
            {"$project": {'consumptionCost': 1, '_id': 0}},
            {"$group": {"_id": "$month",
                        "consumptionCost": {"$sum": "${}".format(filterBy)}}}])

        try:

            consumption = res.next()['consumptionCost']
        except StopIteration:

            consumption = 0

        return self._formJson("success", consumption)

    # aggregating based on week
    def getWeek(self, filterBy, sensorType, sensor):
        if sensor == "all":
            filtercolumn = "sensorType"
            filterValue = sensorType
        else:
            filtercolumn = "sensorID"
            filterValue = sensor

        output = {}

        # weekstarts from Monday
        fromDate = datetime.combine(
            datetime.now().date() - timedelta(days=7)
            , datetime.min.time())

        for dt in rrule.rrule(rrule.DAILY,
                              dtstart=fromDate,
                              until=datetime.now()):
            output[dt.strftime('%d-%m-%Y')] = 0

        res = self.mongoDB["sensorData"].aggregate([
            {"$match": {'date':
                            {"$gte": fromDate,
                             "$lte": datetime.now()}
                , '{}'.format(filtercolumn): '{}'.format(filterValue)}}
            , {"$project": {'DOM': {'$dayOfMonth': '$date'},
                            'month': {'$month': '$date'},
                            'year': {'$year': '$date'},
                            '{}'.format(filterBy): 1, '_id': 0}}
            , {"$group": {"_id": {'month': '$month',
                                  'DOM': '$DOM',
                                  'year': '$year'},
                          "consumption": {"$sum": "${}".format(filterBy)}}}
            , {"$sort": {"_id.month": 1, "_id.DOM": -1, "_id.year": 1}}
        ])

        if res:
            for i, j in enumerate(res):
                strDate = "{}-{}-{}".format(str(j["_id"]["DOM"]).zfill(2), str(j["_id"]["month"]).zfill(2),
                                            j["_id"]["year"])
                output[strDate] = j['consumption']
        output = sorted(output.items(), key=lambda x: datetime.strptime(x[0], '%d-%m-%Y'))
        return self._formJson("success", output)

    # aggregating based on week
    def getWeekly(self, filterBy, sensorType, sensor):

        # weekstarts from Monday
        if sensor == "all":
            filtercolumn = "sensorType"
            filterValue = sensorType
        else:
            filtercolumn = "sensorID"
            filterValue = sensor

        output = [0, 0, 0]
        toDate = datetime.now()
        for k in range(3):
            cons = 0
            fromDate = datetime.combine(
                toDate - timedelta(days=7), datetime.min.time())

            res = self.mongoDB["sensorData"].aggregate([
                {"$match": {'date':
                                {"$gte": fromDate,
                                 "$lte": toDate}
                    , '{}'.format(filtercolumn): '{}'.format(filterValue)}}
                , {"$project": {'year': {'$year': '$date'},
                                '{}'.format(filterBy): 1, '_id': 0}}
                , {"$group": {"_id": "$year",
                              "consumption": {"$sum": "${}".format(filterBy)}}}
                , {"$sort": {"_id": 1}}
            ])

            if res:
                for i, j in enumerate(res):
                    cons += j['consumption']
                output[k] = cons
            toDate = fromDate
        return self._formJson("success", output)

    # aggregating based on month
    def getMonthly(self, filterBy, sensorType, sensor):
        if sensor == "all":
            filtercolumn = "sensorType"
            filterValue = sensorType
        else:
            filtercolumn = "sensorID"
            filterValue = sensor
        # weekstarts from Monday
        fromDate = datetime.combine(
            datetime.now() - relativedelta(months=+5),
            datetime.min.time()) - relativedelta(days=+datetime.now().day - 1)
        start, end = [fromDate, datetime.now()]
        total_months = lambda dt: dt.month + 12 * dt.year
        mlist = []
        for tot_m in xrange(total_months(start) - 1, total_months(end)):
            y, m = divmod(tot_m, 12)
            mlist.append(m + 1)
        query_res = []
        output = {i: 0 for i in mlist}
        res = self.mongoDB["sensorData"].aggregate([
            {"$project": {"_id": 0, "mth": {"$month": "$date"},
                          'date': 1,
                          '{}'.format(filtercolumn): 1,
                          "{}".format(filterBy): 1}},
            {"$match": {'date':
                            {"$gte": fromDate,
                             "$lte": datetime.now()}
                , '{}'.format(filtercolumn): '{}'.format(filterValue)}}
            , {"$group": {"_id": "$mth",
                          "consumption": {"$sum": "${}".format(filterBy)}}}
            , {"$sort": {"_id": 1}}
        ])

        if res:
            for i, j in enumerate(res):
                output[j["_id"]] = j['consumption']

        for i in mlist:
            query_res.append(output[i])
        return (self._formJson("success", query_res))

    def getSensorData(self, inputdata):

        res = self.mongoDB["sensorData"].find(inputdata, {"_id": 0})
        reg_jsonres = []

        for i in res:
            reg_jsonres.append(json.dumps(i))
        return (self._formJson("success", reg_jsonres))

    def _formJson(self, status, val):
        return (json.dumps({'Result': status, 'Output': val}))
