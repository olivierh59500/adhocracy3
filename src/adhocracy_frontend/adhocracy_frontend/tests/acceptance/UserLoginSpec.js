"use strict";

var UserPages = require("./UserPages.js");
var fs = require("fs");
var _ = require("lodash");
var shared = require("./shared");

/*describe("user registration", function() {
    xit("can register - broken due to issue #583 (duplicate tpc_begin)", function() {
        UserPages.register("u1", "u1@example.com", "password1");
        UserPages.logout();
        UserPages.login("u1", "password1");
        expect(UserPages.isLoggedIn()).toBe(true);
    });

    it("cannot register with wrong password repeat", function() {
        var page = new UserPages.RegisterPage().get();
        page.fill("u2", "u2@example.com", "password2", "password3");
        expect(page.submitButton.isEnabled()).toBe(false);
    });
});*/

xdescribe("user login", function() {
    it("can login with username", function() {
        UserPages.login(UserPages.participantName, UserPages.participantPassword);
        expect(UserPages.isLoggedIn()).toBe(true);
        UserPages.logout();
    });

    it("can login with email", function() {
        UserPages.login(UserPages.participantEmail, UserPages.participantPassword);
        expect(UserPages.isLoggedIn()).toBe(true);
        UserPages.logout();
    });

    it("cannot login with wrong name", function() {
        UserPages.login("noexist", "password1");
        expect(UserPages.isLoggedIn()).toBe(false);
    });

    it("cannot login with wrong password", function() {
        UserPages.login("participant", "password1");
        expect(UserPages.isLoggedIn()).toBe(false);
    });

    it("cannot login with short password", function() {
        var page = new UserPages.LoginPage().get();
        page.loginInput.sendKeys("abc");
        page.passwordInput.sendKeys("abc");
        page.submitButton.click();
        expect(element(by.css(".form-error")).getText()).toContain("Short");
    });

    /*it("login is persistent", function() {
        UserPages.login(UserPages.participantName, UserPages.participantPassword);
        expect(UserPages.isLoggedIn()).toBe(true);
        browser.refresh();
        browser.waitForAngular();
        expect(UserPages.isLoggedIn()).toBe(true);
        UserPages.logout();
    });*/
});

describe("user password reset", function() {
    it("email is sent to user", function() {
        var mailsBeforeMessaging = fs.readdirSync(browser.params.mail.queue_path + "/new");

        var page = new UserPages.ResetPasswordCreatePage().get();
        page.fill(UserPages.participantEmail);
        expect(element(by.css(".login-success")).getText()).toContain("SPAM");

        var flow = browser.controlFlow();
        flow.execute(function() {
            var mailsAfterMessaging = fs.readdirSync(browser.params.mail.queue_path + "/new");
            expect(mailsAfterMessaging.length).toEqual(mailsBeforeMessaging.length + 1);
        });
    });

    it("error displayed if the email is not associated to an user", function() {
        var page = new UserPages.ResetPasswordCreatePage().get();
        page.fill("abc@xy.de");
        expect(element(by.css(".form-error")).getText()).toContain("No user");
    });

    it("recover access with the link contained in the email", function(){
        var mailsBeforeMessaging = fs.readdirSync(browser.params.mail.queue_path + "/new");
        var page = new UserPages.ResetPasswordCreatePage().get();
        var resetUrl = "";

        console.log(1);
        page.fill(UserPages.participantEmail);

        console.log(2);
        var flow = browser.controlFlow();
        console.log(3);
        flow.execute(function() {
            console.log(4);
            var mailsAfterMessaging = fs.readdirSync(browser.params.mail.queue_path + "/new");
            console.log(5);
            var newMails = _.difference(mailsAfterMessaging, mailsBeforeMessaging);
            console.log(6);
            var mailpath = browser.params.mail.queue_path + "/new/" + newMails[0];

            console.log(7);
            shared.parseEmail(mailpath, function(mail) {
                // console.log('email=', mail);
                console.log(8);
                expect(mail.subject).toContain("Reset Password");
                console.log(9);
                expect(mail.to[0].address).toContain("participant");
                console.log(10);
                resetUrl = mail.text.split("\n\n")[4];
            });
        });

        console.log(11);
        browser.driver.wait(function() {
            console.log(12);
            return resetUrl != "";
        }).then(function() {
            console.log(resetUrl);
            console.log(13);
            browser.getCurrentUrl().then(function() {console.log(arguments)});
            browser.driver.get(resetUrl);
            browser.driver.getPageSource().then(function() {console.log(arguments)});
            var resetPage = new UserPages.ResetPasswordPage().get(resetUrl);
            console.log(14);
            resetPage.fill('new password');

            // After changing the password the user is logged in
            //expect(UserPages.isLoggedIn()).toBe(true);

            // and can now login with the new password
            console.log(15);
            UserPages.logout();
            console.log(16);
            UserPages.login(UserPages.participantEmail, 'new password');
            console.log(17);
            expect(true);
            //expect(UserPages.isLoggedIn()).toBe(true);
            console.log(18);
        });
    });
});
