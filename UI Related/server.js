var bodyParser = require('body-parser');
// var urlencodedParser = bodyParser.urlencoded({extended:false});
var cookieParser = require('cookie-parser');
var session1 = require('express-session');
const express = require('express');
const app = express();
const path = require('path');
const axios = require('axios');
const assert = require('assert');
app.set('views','./views');
app.set('view engine', 'ejs');
app.use(cookieParser());
app.use(bodyParser.urlencoded({ extended: false }));
// initialize express-session to allow us track the logged-in user across sessions.
app.use(session1({
    key: 'user_sid',
    secret: 'somerandonstuffs',
    resave: false,
    saveUninitialized: false,
    cookie: {
        expires: 600000
    }
}));
app.set('adminUser', 0);
app.use((req, res, next) => {
    
    if (req.cookies.user_sid && !req.session.user ) {
        res.clearCookie('user_sid');        
    }
    next();
});


// middleware function to check for logged-in users
var sessionChecker = (req, res, next) => {	
    var adminUser = app.get('adminUser')        
    if (req.session.user && req.cookies.user_sid && (req.originalUrl!="/houseDetails.html" && req.originalUrl!="/adminindex.html") && adminUser!=1) {        
        res.sendFile(__dirname + '\\app\\'+req.originalUrl);        
    }
    else if (req.session.user && req.cookies.user_sid && (req.originalUrl==="/houseDetails.html" || req.originalUrl==="/adminindex.html") && adminUser===1){
        res.sendFile(__dirname + '\\app\\'+req.originalUrl);
    }
     else {
        next();
    }    
};

app.get('/', sessionChecker, (req, res) => {
    res.redirect('/login');
});

app.get('/index.html', sessionChecker, (req, res) => {    
    res.redirect('/login');
});
app.get('/tablelist.html', sessionChecker, (req, res) => {    
    res.redirect('/login');
});
app.get('/dashboard_24hours.html', sessionChecker, (req, res) => {    
    res.redirect('/login');
});
app.get('/dashboard_7days.html', sessionChecker, (req, res) => {    
    res.redirect('/login');
});
app.get('/dashboard_3weeks.html', sessionChecker, (req, res) => {    
    res.redirect('/login');
});
app.get('/dashboard_6months.html', sessionChecker, (req, res) => {    
    res.redirect('/login');
});

app.get('/costdashboard_24hours.html', sessionChecker, (req, res) => {    
    res.redirect('/login');
});
app.get('/costdashboard_7days.html', sessionChecker, (req, res) => {    
    res.redirect('/login');
});
app.get('/costdashboard_3weeks.html', sessionChecker, (req, res) => {    
    res.redirect('/login');
});
app.get('/costdashboard_6months.html', sessionChecker, (req, res) => {    
    res.redirect('/login');
});
app.get('/houseDetails.html', sessionChecker, (req, res) => {    
    res.redirect('/login');
});
app.get('/adminindex.html', sessionChecker, (req, res) => {    
    res.redirect('/login');
});
app.get('/login', (req, res) => {  
    if (req.cookies.user_sid && req.session.user ) {
        res.clearCookie('user_sid');        
    }      
    res.sendFile(__dirname + '\\app\\login.html');
});

app.use(express.static(path.join(__dirname, 'app')));

app.route('/login')
    .get(sessionChecker, (req, res) => {
        console.log("login")
        res.sendFile(__dirname + '/app/login.html');
    })
    .post((req, postres) => {
        data = JSON.stringify({
            "call":"getInfo",
            "data":{"name":req.body.inputEmail,"password":req.body.inputPassword}
        })
        const  headers= {
            'Content-Type': 'application/json',
            'Content-Length': data.length
          }
          

        axios.post('http://127.0.0.1:9191/loginservice', data,{
            headers: headers
          })
        .then((res) => {            
            const user = res.data.Output
            if (user === "") {
                postres.redirect('/login');
            
            } 
            else 
            {
                req.session.user = user.name;
                
                
                if (user.admin){
                    app.set('adminUser', 1);
                    const adminData = {}
                    adminData["tsURL"] = user["tsURL"]
                    adminData["tsKeys"] = user["tsKeys"]
                    adminData["admin"] = user["admin"]
                    adminData["ip"] = app.get("serverip")
                    app.set('adminData', adminData);
                    postres.redirect('/adminindex');
                }
                else
                {
                    app.set('adminUser', 0);
                    const houseData =JSON.stringify(
                    {
                        "call":"getInfo",
                        "data":{"by":"houseID","input":user.HouseID}
                    })
                    
                    axios.post('http://127.0.0.1:9292/houseservice', houseData,{
                            headers: headers
                        })
                        .then((res) => {
                            const respdata = res.data.Output
                            if (respdata === "") {                                
                                postres.redirect('/login');
                            
                            } else {
                                const data = {};
                                data["catalogURL"] = respdata["catalogURL"]
                                data["HouseID"] = respdata["HouseID"]
                                data["deviceID"] = respdata["deviceID"]
                                data["ip"] = app.get("serverip")
                                app.set('data', data);                                
                                postres.redirect('/index');
                            }
                        })
                        .catch((error) => {
                            console.error(error)
                        })            
                }
            }
        })
        .catch((error) => {
            console.error(error)
        })
});

app.get('/index', (req, res) => {
    var user = app.get('data')
    
    if (req.session.user && req.cookies.user_sid) {         
        res.render(__dirname + '/views/index.ejs',{user:user});
    } else {
        res.redirect('/login');
    }
});

app.get('/adminindex', (req, res) => {
    if (app.get('adminUser') ===1){
    var adminData = app.get('adminData')
    axios.get('http://127.0.0.1:9191/loginservice/gethousecount')
    .then(response => {
        houses = response.data.Output
        console.log(houses)
        if (houses.length){
            adminData.Count = houses.length;
            adminData.houseIDs = [houses];
            if (req.session.user && req.cookies.user_sid && adminData.admin) {                       
                res.render(__dirname + '/views/adminindex.ejs',{adminData:adminData});
            } else {
                res.redirect('/login');
            }
        }
        else{
            adminData.Count = 0;
            adminData.houseIDs = [];
            if (req.session.user && req.cookies.user_sid && adminData.admin) {                        
                res.render(__dirname + '/views/adminindex.ejs',{adminData:adminData});
            } else {
                res.redirect('/login');
            }
        }
        
    })
    .catch(error => {
        console.log(error);
    });   }
    else{
        res.redirect('/login');
    } 
});

app.get('/dashboard', (req, res) => {
    console.log(req.originalUrl)
    if (req.session.user && req.cookies.user_sid && (app.get('adminUser') ===0) ) {         
        res.render(__dirname + '/app/index.html');
    } else {
        res.redirect('/login');
    }
});

app.get('/logout', (req, res) => {
    if (req.session.user && req.cookies.user_sid) {
        res.clearCookie('user_sid');
        res.redirect('/');
    } else {
        res.redirect('/login');
    }
});

'use strict';

var os = require('os');
var ifaces = os.networkInterfaces();

Object.keys(ifaces).forEach(function (ifname) {
  var alias = 0;

  ifaces[ifname].forEach(function (iface) {
    if ('IPv4' !== iface.family || iface.internal !== false) {
      // skip over internal (i.e. 127.0.0.1) and non-ipv4 addresses
      return;
    }
    if (ifname === "VirtualBox Host-Only Network"){
        console.log(ifname, iface.address);  
        app.set('serverip',  iface.address);
    }
    // if (alias >= 1 )  {
    //   // this single interface has multiple ipv4 addresses
    // //   console.log(ifname + ':' + alias, iface.address);
    // } else {
    //   // this interface has only one ipv4 adress
    //   console.log(ifname, iface.address);
    // }
    ++alias;
  });
});
const server = app.listen(7000, () => {
  console.log(`Express running → PORT ${server.address().port}`);
}); 


