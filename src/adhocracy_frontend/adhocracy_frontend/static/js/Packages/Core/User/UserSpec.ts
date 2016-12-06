/// <reference path="../../../../lib2/types/jasmine.d.ts"/>

import * as q from "q";
import * as _ from "lodash";

import * as AdhUser from "./User";
import * as AdhCredentials from "./Credentials";


export var register = () => {
    describe("User", () => {
        describe("Service", () => {
            var adhCacheMock;
            var adhConfigMock;
            var adhHttpMock;
            var adhTrackingMock;
            var angularMock;
            var elementMock;
            var httpMock;
            var modernizrMock;
            var rootScopeMock;
            var timeoutMock;
            var windowMock;

            var adhUser;
            var adhCredentials;

            adhConfigMock = {
                rest_url: "mock"
            };


            beforeEach(() => {
                adhCacheMock = {
                    invalidate: (path) => undefined,
                    invalidateAll: () => undefined,
                    memoize: (path, subkey, closure) => closure()
                };

                adhTrackingMock = jasmine.createSpyObj("adhTrackingMock", ["trackPageView", "setLoginState", "setUserId"]);

                httpMock = jasmine.createSpyObj("httpMock", ["head", "post"]);
                httpMock.defaults = {
                    headers: {
                        common: {}
                    }
                };
                httpMock.head.and.returnValue(q.when({data: {}}));
                httpMock.post.and.returnValue(q.when({data: {}}));

                rootScopeMock = jasmine.createSpyObj("rootScope", ["$watch"]);

                windowMock = {
                    localStorage: jasmine.createSpyObj("localStorage", ["getItem", "setItem", "removeItem"])
                };
                windowMock.localStorage.getItem.and.returnValue(null);

                elementMock = jasmine.createSpyObj("element", ["on"]);
                angularMock = jasmine.createSpyObj("angular", ["element"]);
                angularMock.element.and.returnValue(elementMock);

                modernizrMock = {
                    localstorage: true
                };

                timeoutMock = jasmine.createSpy("$timeout");

                adhHttpMock = jasmine.createSpyObj("adhHttpMock", ["get", "post", "postRaw"]);
                adhHttpMock.post.and.returnValue(q.when({}));
                adhHttpMock.get.and.returnValue(q.when({
                    data: {
                        "adhocracy_core.sheets.principal.ICredentialsBasic": {}
                    }
                }));

                adhCredentials = new AdhCredentials.Service(
                    adhConfigMock, adhCacheMock, adhTrackingMock, modernizrMock, angularMock,
                    <any>q, httpMock, timeoutMock, rootScopeMock, windowMock);

                adhUser = new AdhUser.Service(adhHttpMock, adhCredentials, <any>q, rootScopeMock);
            });

            it("registers a handler on 'storage' DOM events", () => {
                expect(elementMock.on).toHaveBeenCalledWith("storage", jasmine.any(Function));
            });

            describe("updateSessionFromStorage", () => {
                beforeEach(() => {
                    spyOn(adhCredentials, "enableToken");
                    spyOn(adhCredentials, "deleteToken");
                });

                it("calls 'enableToken' if 'user-token' and 'user-path' exist in storage", (done) => {
                    var sessionValue = JSON.stringify({
                        "user-path": "huhu",
                        "user-token": "huhu"
                    });
                    (<any>adhCredentials).updateSessionFromStorage(sessionValue).then((success) => {
                        expect(adhCredentials.enableToken).toHaveBeenCalledWith("huhu", "huhu");
                        expect(success).toBe(true);
                        done();
                    });
                });

                it("calls 'deleteToken' if neither 'user-token' nor 'user-path' exist in storage", (done) => {
                    (<any>adhCredentials).updateSessionFromStorage(null).then((success) => {
                        expect(adhCredentials.deleteToken).toHaveBeenCalled();
                        expect(success).toBe(false);
                        done();
                    });
                    _.defer(() => {
                        expect(timeoutMock).toHaveBeenCalled();
                        var callback = timeoutMock.calls.mostRecent().args[0];
                        callback();
                    });
                });

                it("calls 'deleteToken' if the backend does not accept the user-token", (done) => {
                    httpMock.head.and.returnValue(q.reject({status: 400}));
                    var sessionValue = JSON.stringify({
                        "user-path": "huhu",
                        "user-token": "huhu"
                    });
                    (<any>adhCredentials).updateSessionFromStorage(sessionValue).then((success) => {
                        expect(adhCredentials.deleteToken).toHaveBeenCalled();
                        expect(success).toBe(false);
                        done();
                    });
                });
            });

            describe("login", () => {
                beforeEach(() => {
                    adhHttpMock.postRaw.and.returnValue(q.when({
                        data: {
                            status: "success",
                            user_path: "user1_path",
                            user_token: "user1_tok"
                        }
                    }));

                    expect(adhCredentials.loggedIn).toBe(undefined);
                    expect(adhUser.data).not.toBeDefined();
                });

                var testLogin = () => {
                    it("sets loggedIn to true", () => {
                        expect(adhCredentials.loggedIn).toBe(true);
                    });
                    // FIXME: this is async now
                    xit("sets data to the user resource", () => {
                        // FIXME: Use actual user schema
                        expect(adhUser.data).toBeDefined();
                    });
                    it("sets token to the session token", () => {
                        expect(adhCredentials.token).toBe("user1_tok");
                    });
                    it("sets default http headers for the http service", () => {
                        expect(httpMock.defaults.headers.common["X-User-Token"]).toBe("user1_tok");
                    });
                };

                describe("happy login flow with username and password", () => {
                    beforeEach((done) => {
                        adhUser.logIn("user1", "user1_pass").then(done);
                    });

                    testLogin();

                    it("requests the API endpoint /login_username", () => {
                        expect(adhHttpMock.postRaw).toHaveBeenCalledWith("/login_username", {
                            name: "user1",
                            password: "user1_pass"
                        });
                    });

                    it("stores user token and user path in localstorage", () => {
                        expect(windowMock.localStorage.setItem).toHaveBeenCalledWith("user-session", JSON.stringify({
                            "user-path": "user1_path",
                            "user-token": "user1_tok"
                        }));
                    });
                });

                describe("happy login flow with email and password", () => {
                    beforeEach((done) => {
                        adhUser.logIn("user1@somedomain", "user1_pass").then(done);
                    });

                    testLogin();

                    it("requests the API endpoint /login_email", () => {
                        expect(adhHttpMock.postRaw).toHaveBeenCalledWith("/login_email", {
                            email: "user1@somedomain",
                            password: "user1_pass"
                        });
                    });

                    it("stores user token and user path in localstorage", () => {
                        expect(windowMock.localStorage.setItem).toHaveBeenCalledWith("user-session", JSON.stringify({
                            "user-path": "user1_path",
                            "user-token": "user1_tok"
                        }));
                    });
                });

                describe("localstorage unavailable", () => {
                    beforeEach((done) => {
                        modernizrMock.localstorage = false;
                        adhUser.logIn("user1", "user1_pass").then(done);
                    });

                    testLogin();
                });

                describe("request fails", () => {
                    var _reason;

                    var logInErrorDetails = [
                        { name: "flurg", location: "grompf", description: "chrrgl" }
                    ];

                    var fullError = {
                        data: {
                            status: "",
                            errors: logInErrorDetails
                        }
                    };

                    beforeEach((done) => {
                        adhUser.adhHttp.postRaw.and.returnValue(q.reject(fullError));
                        adhUser.logIn("user1", "user1_wrong_pass").then(
                            done,
                            (reason) => {
                                _reason = reason;
                                done();
                            }
                        );
                    });

                    it("rejects the login attempt", () => {
                        expect(_reason).toBe(logInErrorDetails);
                        expect(adhCredentials.loggedIn).toBe(undefined);
                        expect(adhUser.data).not.toBeDefined();
                        expect(adhCredentials.token).not.toBeDefined();
                        expect(httpMock.defaults.headers.common["X-User-Token"]).not.toBeDefined();
                        expect(httpMock.defaults.headers.common["X-User-Path"]).not.toBeDefined();
                    });
                });
            });

            describe("logOut", () => {
                var testLogout = (_beforeEach : (done : () => void) => void) => {
                    beforeEach((done) => {
                        adhHttpMock.postRaw.and.returnValue(q.when({
                            data: {
                                status: "success",
                                user_path: "user1_path",
                                user_token: "user1_tok"
                            }
                        }));
                        adhUser.logIn("user1", "user1_pass").then(() => {
                            adhUser.logOut();
                            _beforeEach(done);
                        });
                    });

                    it("sets loggedIn to false", () => {
                        expect(adhCredentials.loggedIn).toBe(false);
                    });
                    it("unsets data on the user resource", () => {
                        expect(adhUser.data).not.toBeDefined();
                    });
                    it("unsets token", () => {
                        expect(adhCredentials.token).not.toBeDefined();
                    });
                    it("unsets default http headers for the http service", () => {
                        expect(httpMock.defaults.headers.common["X-User-Token"]).not.toBeDefined();
                    });
                };

                describe("localStorage available", () => {
                    testLogout((done) => {
                        done();
                    });

                    it("removes user token and user path from localstorage", () => {
                        expect(windowMock.localStorage.removeItem).toHaveBeenCalledWith("user-session");
                    });
                });

                describe("localStorage unavailable", () => {
                    testLogout((done) => {
                        modernizrMock.localstorage = false;
                        done();
                    });
                });
            });

            describe("register", () => {
                beforeEach((done) => {
                    adhUser.register("username", "email", "password", "passwordRepeat").then(done);
                });

                it("posts to '/principals/users/'", () => {
                    var args = adhHttpMock.post.calls.mostRecent().args;
                    expect(args[0]).toBe("/principals/users/");
                });
                it("posts a valid user resource", () => {
                    var data = adhHttpMock.post.calls.mostRecent().args[1].data;
                    expect(data["adhocracy_core.sheets.principal.IUserBasic"].name).toBe("username");
                    expect(data["adhocracy_core.sheets.principal.IUserExtended"].email).toBe("email");
                    expect(data["adhocracy_core.sheets.principal.IPasswordAuthentication"].password).toBe("password");
                });
            });

            describe("activate", () => {
                var threw : boolean;
                var activateUrl : string = "lYjaoXbEo3U/I";

                var myBeforeEach = (postRawResponse) => (done) => {
                    adhHttpMock.postRaw.and.callFake(() =>
                        q.when(postRawResponse));

                    adhUser.activate(activateUrl).then(
                        () => { threw = false; done(); },
                        () => { threw = true; done(); }
                    );
                };

                describe("(success case)", () => {
                    var postRawResponse = {
                        data: {
                            user_token: "user_token_8427",
                            user_path: "user_path_we7t"
                        }
                    };

                    beforeEach(myBeforeEach(postRawResponse));

                    it("does not throw when response is 'success'", () => {
                        expect(threw).toBe(false);
                    });
                    it("posts to '/activate_account' (using postRaw)", () => {
                        var args = adhHttpMock.postRaw.calls.mostRecent().args;
                        expect(args[0]).toBe("/activate_account");
                    });
                    it("posts its argument as activation URL", () => {
                        var args = adhHttpMock.postRaw.calls.mostRecent().args;
                        expect(args[1].hasOwnProperty("path")).toBe(true);
                        expect(args[1].path).toBe(activateUrl);
                    });
                    it("logs in user on success", () => {
                        expect(adhCredentials.userPath).toEqual(postRawResponse.data.user_path);
                        expect(httpMock.defaults.headers.common["X-User-Token"]).toEqual(postRawResponse.data.user_token);
                    });
                });

                describe("activate (failure case)", () => {
                    beforeEach(myBeforeEach("ef"));

                    it("throws when response is anything but 'success'", () => {
                        expect(threw).toBe(true);
                    });
                });
            });
        });
    });
};
