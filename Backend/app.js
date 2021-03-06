const express      = require('express');
const cors         = require('cors');
const authRequired = require('./auth');
const app          = express();
const config       = require('./config');
const userRouter   = require("./routes/user");
const logsRouter   = require("./routes/logs");
const bodyParser   = require('body-parser');
const client       = require('./connection.js');

// Create new elasticsearch index
client.indices.create({
  index: 'logss',
  body:{
    "mappings": {
      "Logs": {
          "properties":{
            "msgRefId":{"type":"text", "index": "not_analyzed"},
            "genUserId":{"type":"text", "index": "not_analyzed"},
            "boolPersonal":{"type":"boolean", "index": "not_analyzed"},
            "secUsername":{"type":"text", "index": "not_analyzed"},
            "title":{"type":"text", "analyzer": "english"},
            "amount":{"type":"double", "index": "analyzed"},
            "completeLog":{"type":"text", "analyzer": "english"},
            "category":{"type":"text", "index": "not_analyzed"}
          }
      }
    }
  }
},function(err,resp,status) {
    console.log("created index",resp);
});
 
// parse application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: false }));
 
// parse application/json
app.use(bodyParser.json());

// connect to mongodb
const mongoose     = require('mongoose');
mongoose.promise   = global.promise;
mongoose.connect(config.db.dbURI,{ useNewUrlParser: true }, function(err) {
  if(err)
  {
    throw err;
    process.exit(0);
  }

  console.log('connected to mongodb');
})
.catch((err) => {
  console.log("Could not connect to MongoDB: " + err);
});

/*
 * For local testing only!  Enables CORS for all domains
 */
app.use(cors());

// Auth MiddleWare
app.use(authRequired);

// Routes
app.use("/api/v1/user", userRouter);
app.use("/api/v1/logs", logsRouter);

// 404 on missing routes
app.get('/*', function(req, res, next){
    res.status(404).send("Route Not Found");
});

// Starting the server
app.listen(config['app']['port'], () => {
  console.log('Server Ready on port ' + config['app']['port']);
});