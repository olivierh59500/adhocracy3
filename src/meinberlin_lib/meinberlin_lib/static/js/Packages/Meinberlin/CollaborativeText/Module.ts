import * as AdhDocumentModule from "../../Core/Document/Module";
import * as AdhIdeaCollectionModule from "../../Core/IdeaCollection/Module";
import * as AdhNamesModule from "../../Core/Names/Module";
import * as AdhProcessModule from "../../Core/Process/Module";
import * as AdhResourceAreaModule from "../../Core/ResourceArea/Module";

import * as AdhDocument from "../../Core/Document/Document";
import * as AdhIdeaCollectionWorkbench from "../../Core/IdeaCollection/Workbench/Workbench";
import * as AdhNames from "../../Core/Names/Names";
import * as AdhProcess from "../../Core/Process/Process";
import * as AdhResourceArea from "../../Core/ResourceArea/ResourceArea";

import RIDocument from "../../../Resources_/adhocracy_core/resources/document/IDocument";
import RIDocumentVersion from "../../../Resources_/adhocracy_core/resources/document/IDocumentVersion";
import RICollaborativeTextProcess from "../../../Resources_/adhocracy_meinberlin/resources/collaborative_text/IProcess";

export var moduleName = "adhMeinberlinCollaborativeText";

export var register = (angular) => {
    var processType = RICollaborativeTextProcess.content_type;

    angular
        .module(moduleName, [
            AdhDocumentModule.moduleName,
            AdhIdeaCollectionModule.moduleName,
            AdhNamesModule.moduleName,
            AdhProcessModule.moduleName,
            AdhResourceAreaModule.moduleName,
        ])
        .config(["adhResourceAreaProvider", "adhConfig", (adhResourceAreaProvider: AdhResourceArea.Provider, adhConfig) => {
            AdhIdeaCollectionWorkbench.registerCommonRoutesFactory(
                RICollaborativeTextProcess, RIDocument, RIDocumentVersion)()(adhResourceAreaProvider);
            AdhIdeaCollectionWorkbench.registerDocumentRoutesFactory(
                RICollaborativeTextProcess, RIDocument, RIDocumentVersion)()(adhResourceAreaProvider);

            var processHeaderSlot = adhConfig.pkg_path + AdhIdeaCollectionWorkbench.pkgLocation + "/AddDocumentSlot.html";
            adhResourceAreaProvider.processHeaderSlots[processType] = processHeaderSlot;
        }])
        .config(["adhConfig", "adhProcessProvider", (adhConfig, adhProcessProvider : AdhProcess.Provider) => {
            adhProcessProvider.templates[processType] =
                "<adh-idea-collection-workbench data-process-properties=\"processProperties\">" +
                "</adh-idea-collection-workbench>";
            adhProcessProvider.setProperties(processType, {
                createSlot: adhConfig.pkg_path + AdhDocument.pkgLocation + "/CreateSlot.html",
                detailSlot: adhConfig.pkg_path + AdhDocument.pkgLocation + "/DetailSlot.html",
                editSlot: adhConfig.pkg_path + AdhDocument.pkgLocation + "/EditSlot.html",
                hasCommentColumn: true,
                hasImage: true,
                itemClass: RIDocument,
                versionClass: RIDocumentVersion
            });
        }])
        .config(["adhNamesProvider", (adhNamesProvider : AdhNames.Provider) => {
            adhNamesProvider.names[processType] = "TR__RESOURCE_COLLABORATIVE_TEXT_EDITING";
        }]);
};