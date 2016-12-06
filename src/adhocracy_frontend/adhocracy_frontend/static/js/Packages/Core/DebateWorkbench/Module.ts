import * as AdhAbuseModule from "../Abuse/Module";
import * as AdhCommentModule from "../Comment/Module";
import * as AdhDocumentModule from "../Document/Module";
import * as AdhEmbedModule from "../Embed/Module";
import * as AdhHttpModule from "../Http/Module";
import * as AdhMovingColumnsModule from "../MovingColumns/Module";
import * as AdhPermissionsModule from "../Permissions/Module";
import * as AdhResourceActionsModule from "../ResourceActions/Module";
import * as AdhResourceAreaModule from "../ResourceArea/Module";
import * as AdhTopLevelStateModule from "../TopLevelState/Module";

import * as DebateWorkbench from "./DebateWorkbench";


export var moduleName = "adhDebateWorkbench";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhAbuseModule.moduleName,
            AdhCommentModule.moduleName,
            AdhDocumentModule.moduleName,
            AdhEmbedModule.moduleName,
            AdhHttpModule.moduleName,
            AdhMovingColumnsModule.moduleName,
            AdhPermissionsModule.moduleName,
            AdhResourceActionsModule.moduleName,
            AdhResourceAreaModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .directive("adhDebateWorkbench", ["adhConfig", "adhTopLevelState", DebateWorkbench.debateWorkbenchDirective])
        .directive("adhDocumentDetailColumn", [
            "adhConfig", "adhPermissions", "adhTopLevelState", DebateWorkbench.documentDetailColumnDirective])
        .directive("adhDocumentCreateColumn", [
            "adhConfig", "adhTopLevelState", DebateWorkbench.documentCreateColumnDirective])
        .directive("adhDocumentEditColumn", [
            "adhConfig", "adhTopLevelState", DebateWorkbench.documentEditColumnDirective])
        .directive("adhDebateProcessDetailColumn", [
            "adhConfig", "adhEmbed", "adhHttp", "adhPermissions", "adhTopLevelState", DebateWorkbench.processDetailColumnDirective])
        .directive("adhDebateAddDocumentButton", [
            "adhConfig", "adhHttp", "adhPermissions", "adhTopLevelState", DebateWorkbench.addDocumentButtonDirective])
        .directive("adhDebateProcessDetailAnnounceColumn", [
            "adhConfig",
            "adhEmbed",
            "adhHttp",
            "adhPermissions",
            "adhTopLevelState",
            DebateWorkbench.processDetailAnnounceColumnDirective
        ]);
};
