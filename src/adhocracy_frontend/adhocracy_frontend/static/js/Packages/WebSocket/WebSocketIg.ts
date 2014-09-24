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
        var resource : RIProposal;

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
            resource = new RIProposal({
                preliminaryNames : preliminaryNames,
                name : "Against_Curtains_" + Math.random()
            });
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

            http.post(config.rest_url + "/adhocracy/", resource)
                .then(
                    (response) => {
                        console.log("resource posted successfully.");
                    },
                    (msg) => {
                        expect(msg).toBe(false);
                    });
        });
    });
};
