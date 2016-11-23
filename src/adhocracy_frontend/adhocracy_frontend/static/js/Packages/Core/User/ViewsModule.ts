/// <reference path="../../../../lib2/types/lodash.d.ts"/>

import * as _ from "lodash";

import * as AdhAngularHelpersModule from "../AngularHelpers/Module";
import * as AdhBadgeModule from "../Badge/Module";
import * as AdhEmbedModule from "../Embed/Module";
import * as AdhHttpModule from "../Http/Module";
import * as AdhLocaleModule from "../Locale/Module";
import * as AdhMovingColumnsModule from "../MovingColumns/Module";
import * as AdhNamesModule from "../Names/Module";
import * as AdhPermissionsModule from "../Permissions/Module";
import * as AdhResourceActionsModule from "../ResourceActions/Module";
import * as AdhResourceAreaModule from "../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../TopLevelState/Module";

import * as AdhCredentialsModule from "./CredentialsModule";
import * as AdhUserModule from "./Module";
import * as AdhImageModule from "../Image/Module";

import * as AdhHttp from "../Http/Http";
import * as AdhNames from "../Names/Names";
import * as AdhTopLevelState from "../TopLevelState/TopLevelState";

import * as AdhUserViews from "./Views";

import RIUser from "../../../Resources_/adhocracy_core/resources/principal/IUser";

export var moduleName = "adhUserViews";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAngularHelpersModule.moduleName,
            AdhBadgeModule.moduleName,
            AdhCredentialsModule.moduleName,
            AdhEmbedModule.moduleName,
            AdhLocaleModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhNamesModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhHttpModule.moduleName,
            AdhTopLevelStateModule.moduleName,
            AdhResourceActionsModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhUserModule.moduleName,
            AdhImageModule.moduleName
        ])
        .config(["adhTopLevelStateProvider", (adhTopLevelStateProvider : AdhTopLevelState.Provider) => {
            adhTopLevelStateProvider
                .when("login", () : AdhTopLevelState.IAreaInput => {
                    return {
                        templateUrl: "/static/js/templates/Login.html"
                    };
                })
                .when("password_reset", () : AdhTopLevelState.IAreaInput => {
                    return {
                        templateUrl: "/static/js/templates/PasswordReset.html",
                        reverse: (data) => {
                            return {
                                path: data["_path"],
                                search: {
                                    path: data["path"]
                                }
                            };
                        }
                    };
                })
                .when("create_password_reset", () : AdhTopLevelState.IAreaInput => {
                    return {
                        templateUrl: "/static/js/templates/CreatePasswordReset.html"
                    };
                })
                .when("register", ["adhHttp", (adhHttp : AdhHttp.Service) : AdhTopLevelState.IAreaInput => {
                    return {
                        templateUrl: "/static/js/templates/Register.html",
                        route: (path, search) => {
                            return adhHttp.options("/principals/users").then((options) => {
                                if (!options.POST) {
                                    throw 401;
                                } else {
                                    var data = _.clone(search);
                                    data["_path"] = path;
                                    return data;
                                }
                            });
                        }
                    };
                }])
                .when("activate", ["adhConfig", "adhUser", "adhDone", "$rootScope", "$location", AdhUserViews.activateArea]);
        }])
        .config(["adhResourceAreaProvider", AdhUserViews.registerRoutes()])
        .config(["adhNamesProvider", (adhNamesProvider : AdhNames.Provider) => {
            adhNamesProvider.names[RIUser.content_type] = "TR__RESOURCE_USER";
        }])
        .filter("adhTranslateUsername", ["translateFilter", AdhUserViews.translateUsernameFilter])
        .directive("adhListUsers", ["adhCredentials", "adhConfig", AdhUserViews.userListDirective])
        .directive("adhUserListItem", ["adhConfig", AdhUserViews.userListItemDirective])
        .directive("adhUserProfile", [
            "adhConfig",
            "adhCredentials",
            "adhHttp",
            "adhPermissions",
            "adhTopLevelState",
            "adhUser",
            "adhGetBadges",
            AdhUserViews.userProfileDirective])
        .directive("adhUserEdit", [
            "adhConfig",
            "adhHttp",
            "adhTopLevelState",
            "adhUser",
            "adhShowError",
            "adhSubmitIfValid",
            "adhResourceUrlFilter",
            "$location",
            AdhUserViews.userEditDirective])
        .directive("adhLogin", [
            "adhConfig",
            "adhUser",
            "adhTopLevelState",
            "adhEmbed",
            "adhPermissions",
            "adhShowError",
            "$window",
            AdhUserViews.loginDirective])
        .directive("adhPasswordReset", [
            "adhConfig", "adhHttp", "adhUser", "adhTopLevelState", "adhShowError", AdhUserViews.passwordResetDirective])
        .directive("adhCreatePasswordReset", [
            "adhConfig",
            "adhCredentials",
            "adhHttp",
            "adhUser",
            "adhTopLevelState",
            "adhEmbed",
            "adhShowError",
            AdhUserViews.createPasswordResetDirective])
        .directive("adhRegister", [
            "$sce",
            "$http",
            "adhConfig",
            "adhCredentials",
            "adhUser",
            "adhTopLevelState",
            "adhEmbed",
            "adhShowError",
            AdhUserViews.registerDirective])
        .directive("adhUserIndicator", [
            "adhConfig", "adhResourceArea", "adhTopLevelState", "adhPermissions", "$location", AdhUserViews.indicatorDirective])
        .directive("adhUserMeta", ["adhConfig", "adhResourceArea", "adhGetBadges", AdhUserViews.metaDirective])
        .directive("adhUserMessage", ["adhConfig", "adhHttp", AdhUserViews.userMessageDirective])
        .directive("adhUserDetailColumn", [
            "adhConfig", "adhPermissions", "adhTopLevelState", "$timeout", AdhUserViews.userDetailColumnDirective])
        .directive("adhUserEditColumn", ["adhConfig", "adhTopLevelState", AdhUserViews.userEditColumnDirective])
        .directive("adhUserProfileImage", ["adhHttp", "adhConfig", AdhUserViews.adhUserProfileImageDirective])
        .directive("adhUserProfileImageEdit", ["adhHttp", "adhPermissions", "adhConfig", AdhUserViews.adhUserProfileImageEditDirective])
        .directive("adhUserActivityOverview", ["adhConfig", "adhHttp", AdhUserViews.adhUserActivityOverviewDirective])
        .directive("adhHelpLink", ["adhConfig", AdhUserViews.adhHelpLinkDirective])
        .directive("adhUserWorkbench", ["adhConfig", "adhTopLevelState", AdhUserViews.workbenchDirective]);
};
