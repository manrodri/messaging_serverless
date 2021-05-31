'use strict';

const { uuid } = require('uuidv4');

var AWS = require('aws-sdk');

var dynamo = new AWS.DynamoDB();

exports.handler = function (event, context, callback) {
    var id =uuid();
    var users = event.users;
    users.push(event.cognitoUsername);
    var records = [];
    users.forEach(function(user) {
        records.push({
            PutRequest: {
                Item: {
                    ConversationId: {
                        S: id
                    },
                    Username: {
                        S: user
                    }
                }
            }
        });
    });

    dynamo.batchWriteItem({
        RequestItems: {
            'Chat-Conversations': records
        }
    }, function (err, data) {
        if(err === null) {
            callback(null, id);
        } else {
            callback(err);
        }
    });
};