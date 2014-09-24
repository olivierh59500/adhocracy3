/// <reference path="../../../lib/DefinitelyTyped/jasmine/jasmine.d.ts"/>
/// <reference path="../../../lib/DefinitelyTyped/modernizr/modernizr.d.ts"/>

import modernizr = require("modernizr");

import Config = require("../Config/Config");
import Http = require("../Http/Http");
import MetaApi = require("../MetaApi/MetaApi");
import PreliminaryNames = require("../PreliminaryNames/PreliminaryNames");
import WebSocket = require("./WebSocket");

import RIProposal = require("../../Resources_/adhocracy_sample/resources/proposal/IProposal");

export var register = (angular, config : Config.Type, meta_api) => {

    describe("WebSocket", () => {
        var preliminaryNames : PreliminaryNames;
        var metaApi : MetaApi.MetaApiQuery;
        var http : Http.Service<any>;
        var ws : WebSocket.IService;

        beforeEach(() => {
            preliminaryNames = new PreliminaryNames;
            metaApi = new MetaApi.MetaApiQuery(meta_api);
            http = (() => {
                var factory = ($http, $q, $timeout) : Http.Service<any> => {
                    return (
                        new Http.Service(
                            $http, $q, $timeout,
                            metaApi,
                            preliminaryNames,
                            config));
                };
                factory.$inject = ["$http", "$q", "$timeout"];
                return angular.injector(["ng"]).invoke(factory);
            })();
            ws = WebSocket.factory(<any>modernizr, config);
        });

        it("handles basic subscription to /adhocracy and update response nicely.", (done) => {
            ws.registerErrorHandler((msg) => {
                expect(JSON.stringify(msg, null, 2)).toEqual(false);
                done();
            });

            ws.register(config.rest_url + "/adhocracy/", (event) => {
                expect(event).toEqual("there should not be any event");
                done();
            });

            // keep posting indefinitely until we get a change
            // notification from the web socket.  (to rule out race
            // conditions between registration and post.)  (FIXME:
            // there should not be any race conditions.  but in order
            // to guarantee that, WebSocket needs to be changed
            // considerably.)
            var loop = () => {
                var resource = new RIProposal({
                    preliminaryNames : preliminaryNames,
                    name : "Against_Curtains_" + Math.random()
                });

                http.post(config.rest_url + "/adhocracy/", resource)
                    .then(
                        (response) => {
                            console.log("resource posted successfully.");
                            loop();
                        },
                        (msg) => {
                            expect(msg).toBe(false);
                        });
            };

            loop();
        });
    });
};
