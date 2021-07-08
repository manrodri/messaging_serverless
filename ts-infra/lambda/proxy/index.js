'use strict';

var AWS = require('aws-sdk');

var S3 = new AWS.S3();

// why is this not in the remote?

var bucket = process.env.BUCKET_NAME || 'messages.soydecai.xyz';

exports.handler = function (event, context, callback) {

    console.log(event)

    const done = function (err, res) {
        callback(null, {
            statusCode: err ? '400' : '200',
            body: err ? JSON.stringify(err) : JSON.stringify(res),
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        });
    };

    var pathParameter = event.pathParameters.conversations;
    console.log(pathParameter)
    console.log(event.pathParameters)


    if (!event.pathParameters) {
        S3.getObject({
            Bucket: bucket,
            Key: 'data/conversations.json'
        }, function (err, data) {
            done(err, err ? null : JSON.parse(data.Body.toString()));
        });
    } else if (pathParameter) {

        S3.getObject({
            Bucket: bucket,
            Key: 'data/conversations/' + pathParameter + '.json'
        }, function (err, data) {
            done(err, err ? null : JSON.parse(data.Body.toString()));
        });
    } else {
        done('No cases hit');
    }
};