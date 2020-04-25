'use strict';
const AWS = require('aws-sdk');
const Alexa = require("alexa-sdk");
const lambda = new AWS.Lambda();
const dynamoDb = new AWS.DynamoDB.DocumentClient();
const uuid = require('uuid');

exports.handler = function(event, context, callback) {
    const alexa = Alexa.handler(event, context);
    alexa.appId = "amzn1.ask.skill.c536fe5b-7418-4fef-a8c5-ec7db07afaaa";
    alexa.registerHandlers(handlers);
    alexa.execute();
};


const handlers = {
    'LaunchRequest': function() {
        this.emit('Prompt');
    },
    'Unhandled': function() {
        this.emit('AMAZON.HelpIntent');
    },
    'AddExpense': function() {

        var amount = this.event.request.intent.slots.Amount.value;
        var category = this.event.request.intent.slots.Category.value;
        var userId = this.event.context.System.user.userId;

        if ((typeof(amount) != "undefined") || (typeof(category) != "undefined")) {

            console.log("\n\nLoading handler\n\n");

            const dynamodbParams = {
                TableName: process.env.DYNAMODB_TABLE_EXPENSES,
                Item: {
                    id: uuid.v4(),
                    userId: userId,
                    amount: amount,
                    category: category,
                    createdAt: timestamp,
                    updatedAt: timestamp,
                },
            };

            const params = {
                TableName: process.env.DYNAMODB_TABLE_EXPENSES,
                FilterExpression: 'category = :this_category',
                ExpressionAttributeValues: {
                    ':this_category': category
                }
            };

            console.log('Attempting to get expense', params);

            dynamoDb.scan(params).promise()
                .then(data => {
                    console.log('Got expense: ' + JSON.stringify(data), params);

                    const self = this;
                    const item = data.Items[0];
                    if (!item) {
                        dynamoDb.put(dynamodbParams).promise()
                            .then(data => {
                                console.log('Expense added: ', dynamodbParams);
                                this.emit(':ask', 'Añadidos' + amount + ' euros en la tarifa ' + category + '. Puedes comprobar un gasto, eliminarlo o actualizarlo. Tú eliges.');
                            })
                            .catch(err => {
                                console.error(err);
                                this.emit(':tell', 'Jiuston, tenemos un problema');
                            });

                    } else {
                        this.emit(':ask', 'Ya existe un precio para ' + category + ', tal vez te gustaría actualizar el precio')
                    }
                })
        }
    },
    'GetExpense': function() {

        var category = this.event.request.intent.slots.Category.value;

        if ((typeof(category) != "undefined")) {

            console.log("\n\nLoading handler\n\n");

            const params = {
                TableName: process.env.DYNAMODB_TABLE_EXPENSES,
                FilterExpression: 'category = :this_category',
                ExpressionAttributeValues: {
                    ':this_category': category
                }
            };

            console.log('Attempting to get expense', params);
            const self = this;
            dynamoDb.scan(params, function(err, data) {
                const item = data.Items[0];
                if (!item) {
                    self.emit(':ask', 'Lo siento, no puedo encontrar esa tarifa ahora.');
                }
                if (item) {
                    console.log("DEBUG:  Getitem worked. ");
                    self.emit(':ask', 'La hora más económica es a las' + data.Items[0].hour + 'con un precio de tan solo ' + data.Items[0].amount + 'céntimos de euro.');
                }
            });

        } else {
            this.emit('NoMatch')
        }
    },
    'DeleteExpense': function() {

        var category = this.event.request.intent.slots.Category.value;
        const {
            userId
        } = this.event.session.user;
        console.log(userId)
        console.log(category)

        if ((typeof(category) != "undefined")) {

            console.log("\n\nLoading handler\n\n");

            const params = {
                TableName: process.env.DYNAMODB_TABLE_EXPENSES,
                FilterExpression: 'category = :this_category',
                ExpressionAttributeValues: {
                    ':this_category': category
                }
            };

            console.log('Attempting to get expense', params);

            dynamoDb.scan(params).promise()
                .then(data => {
                    console.log('Got expense: ' + JSON.stringify(data), params);

                    const self = this;
                    const item = data.Items[0];
                    if (!item) {
                        self.emit(':ask', 'Lo siento, no podemos borrar ese precio porque no existe. Inténtelo de nuevo.');
                    }

                    if (item) {
                        console.log('Attempting to delete data', data);
                        const newparams = {
                            TableName: process.env.DYNAMODB_TABLE_EXPENSES,
                            Key: {
                                id: data.Items[0].id,
                                createdAt: data.Items[0].createdAt
                            }
                        };
                        console.log(newparams)
                        dynamoDb.delete(newparams, function(err, data) {
                            if (err) {
                                console.error("Unable to read item. Error JSON:", JSON.stringify(err, null, 2));
                                self.emit(':tell', '¡Ups, creo que algo ha ido mal!');
                            } else {
                                console.log("DEBUG:  deleteItem worked. ");
                                self.emit(':ask', 'Por lo tanto, he eliminado el precio con la categoría ' + category + ' . ¿Quieres hacer algo más?');


                            }
                        });
                    }
                })
        }
    },
    'UpdateExpense': function() {

        var category = this.event.request.intent.slots.Category.value;
        var amount = this.event.request.intent.slots.Amount.value;

        console.log(category)
        console.log(amount)

        if ((typeof(category) != "undefined") || (typeof(amount) != "undefined")) {

            console.log("\n\nLoading handler\n\n");

            const params = {
                TableName: process.env.DYNAMODB_TABLE_EXPENSES,
                FilterExpression: 'category = :this_category',
                ExpressionAttributeValues: {
                    ':this_category': category
                }
            };

            console.log('Attempting to get expense', params);

            dynamoDb.scan(params).promise()
                .then(data => {
                    console.log('Got expense: ' + JSON.stringify(data), params);

                    const self = this;
                    let newamount;
                    const item = data.Items[0];
                    if (!item) {
                        self.emit(':ask', 'Lo siento, no puedo actualizar ese precio porque no existe. Inténtelo de nuevo.');
                    }

                    if (item) {
                        console.log('Attempting to update data', data);
                        newamount = parseInt(amount, 10) + parseInt(data.Items[0].amount, 10)
                        console.log(newamount)
                        const newparams = {
                            TableName: process.env.DYNAMODB_TABLE_EXPENSES,
                            Key: {
                                id: data.Items[0].id,
                                createdAt: data.Items[0].createdAt
                            },
                            UpdateExpression: "set amount = :newamount",
                            ExpressionAttributeValues: {
                                ":newamount": newamount,
                            },
                            ReturnValues: "UPDATED_NEW"
                        };
                        console.log(newparams)
                        dynamoDb.update(newparams, function(err, data) {
                            if (err) {
                                console.error("Unable to read item. Error JSON:", JSON.stringify(err, null, 2));
                                self.emit(':tell', '¡Algo ha ido mal!');
                            } else {
                                console.log("DEBUG:  updateItem worked. ");
                                self.emit(':ask', 'Los precios para la tarifa ' + category + ' han sido actualizados' + newamount + ' . ¿Quieres hacer algo más?');


                            }
                        });
                    }
                })
        }
    },
    'AMAZON.YesIntent': function() {
        this.emit('Prompt');
    },
    'AMAZON.NoIntent': function() {
        this.emit('AMAZON.StopIntent');
    },
    'Prompt': function() {
        this.emit(':ask', '¡Bienvenido a mi tarifa económica!. Estoy aquí para ayudarte a ahorrar con la carga de tu coche eléctrico! Dime cómo te puedo ayudar', 'Por favor, ¿puedes repetirlo de nuevo?');
    },
    'PromptGet': function() {
        this.emit(':ask', 'Por favor, dime qué tarifa te gustaría comprobar', 'Por favor, ¿puedes repetirlo de nuevo?');
    },
    'NoMatch': function() {
        this.emit(':ask', 'Lo siento, no pude entenderte.', 'Por favor, ¿puedes repetirlo de nuevo?');
    },
    'AMAZON.HelpIntent': function() {
        const speechOutput = 'Necesito que me digas el precio y la tarifa';
        const reprompt = 'Saluda, para escuchar mi voz.';

        this.response.speak(speechOutput).listen(reprompt);
        this.emit(':responseReady');
    },
    'AMAZON.CancelIntent': function() {
        this.response.speak('¡Adiós y gracias por confiar en mi para ahorrar tu tarifa de la luz!');
        this.emit(':responseReady');
    },
    'AMAZON.StopIntent': function() {
        this.response.speak('¡Nos vemos pronto, y gracias por confiar en mi para ahorrar tu tarifa de la luz!');
        this.emit(':responseReady');
    }
};