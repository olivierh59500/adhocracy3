/// <reference path="../../../../lib2/types/angular.d.ts"/>

import * as AdhConfig from "../Config/Config";
import * as AdhEmbed from "../Embed/Embed";
import * as AdhHttp from "../Http/Http";
import * as AdhPermissions from "../Permissions/Permissions";
import * as AdhProcess from "../Process/Process";
import * as AdhResourceArea from "../ResourceArea/ResourceArea";
import * as AdhTopLevelState from "../TopLevelState/TopLevelState";
import * as AdhUtil from "../Util/Util";

import * as ResourcesBase from "../../../ResourcesBase";

import RIComment from "../../../Resources_/adhocracy_core/resources/comment/IComment";
import RICommentVersion from "../../../Resources_/adhocracy_core/resources/comment/ICommentVersion";
import RIDocument from "../../../Resources_/adhocracy_core/resources/document/IDocument";
import RIDocumentVersion from "../../../Resources_/adhocracy_core/resources/document/IDocumentVersion";
import RIParagraph from "../../../Resources_/adhocracy_core/resources/paragraph/IParagraph";
import RIParagraphVersion from "../../../Resources_/adhocracy_core/resources/paragraph/IParagraphVersion";

import * as SIComment from "../../../Resources_/adhocracy_core/sheets/comment/IComment";
import * as SIDescription from "../../../Resources_/adhocracy_core/sheets/description/IDescription";
import * as SIImageReference from "../../../Resources_/adhocracy_core/sheets/image/IImageReference";
import * as SIParagraph from "../../../Resources_/adhocracy_core/sheets/document/IParagraph";
import * as SITitle from "../../../Resources_/adhocracy_core/sheets/title/ITitle";
import * as SIWorkflow from "../../../Resources_/adhocracy_core/sheets/workflow/IWorkflowAssignment";

export var pkgLocation = "/Core/DebateWorkbench";


export var debateWorkbenchDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Workbench.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("view", scope));
        }
    };
};


export var documentDetailColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhPermissions : AdhPermissions.Service,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/DocumentDetailColumn.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
            scope.$on("$destroy", adhTopLevelState.bind("documentUrl", scope));
            adhPermissions.bindScope(scope, () => scope.documentUrl && AdhUtil.parentPath(scope.documentUrl), "proposalItemOptions");
        }
    };
};

export var documentCreateColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/DocumentCreateColumn.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
        }
    };
};

export var documentEditColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/DocumentEditColumn.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
            scope.$on("$destroy", adhTopLevelState.bind("documentUrl", scope));
        }
    };
};

export var processDetailColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhEmbed : AdhEmbed.Service,
    adhHttp : AdhHttp.Service,
    adhPermissions : AdhPermissions.Service,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ProcessDetailColumn.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
            scope.data = {};
            scope.$watch("processUrl", (value : string) => {
                if (value) {
                    adhHttp.get(value).then((resource) => {
                        var workflow = SIWorkflow.get(resource);
                        scope.data.picture = (SIImageReference.get(resource) || {}).picture;
                        scope.data.title = SITitle.get(resource).title;
                        scope.data.participationStartDate = AdhProcess.getStateData(workflow, "participate").start_date;
                        scope.data.participationEndDate = AdhProcess.getStateData(workflow, "evaluate").start_date;
                        scope.data.shortDescription = SIDescription.get(resource).short_description;
                    });
                }
            });
            adhPermissions.bindScope(scope, () => scope.processUrl, "processOptions");
            var context = adhEmbed.getContext();
            scope.hasResourceHeader = (context === "");
        }
    };
};

export var addDocumentButtonDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhPermissions : AdhPermissions.Service,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/AddDocumentButton.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
            adhPermissions.bindScope(scope, () => scope.processUrl, "processOptions");

            scope.setCameFrom = () => {
                adhTopLevelState.setCameFrom();
            };
        }
    };
};

export var processDetailAnnounceColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhEmbed : AdhEmbed.Service,
    adhHttp : AdhHttp.Service,
    adhPermissions : AdhPermissions.Service,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    var directive = processDetailColumnDirective(adhConfig, adhEmbed, adhHttp, adhPermissions, adhTopLevelState);
    directive.templateUrl = adhConfig.pkg_path + pkgLocation + "/ProcessDetailAnnounceColumn.html";
    return directive;
};


export var registerRoutes = (
    processType : ResourcesBase.IResourceClass,
    context : string = ""
) => (adhResourceAreaProvider : AdhResourceArea.Provider) => {
    adhResourceAreaProvider
        .default(processType, "", processType.content_type, context, {
            space: "content",
            movingColumns: "is-show-hide-hide"
        })
        .default(processType, "create_document", processType.content_type, context, {
            space: "content",
            movingColumns: "is-show-hide-hide"
        })
        .specific(processType, "create_document", processType.content_type, context, [
            "adhHttp", (adhHttp : AdhHttp.Service) => (resource) => {
                return adhHttp.options(resource.path).then((options : AdhHttp.IOptions) => {
                    if (!options.POST) {
                        throw 401;
                    } else {
                        return {};
                    }
                });
            }])
        .defaultVersionable(RIDocument, RIDocumentVersion, "", processType.content_type, context, {
            space: "content",
            movingColumns: "is-show-show-hide"
        })
        .specificVersionable(RIDocument, RIDocumentVersion, "", processType.content_type, context, [
            () => (item : ResourcesBase.IResource, version : ResourcesBase.IResource) => {
                return {
                    documentUrl: version.path
                };
            }])
        .defaultVersionable(RIDocument, RIDocumentVersion, "edit", processType.content_type, context, {
            space: "content",
            movingColumns: "is-show-show-hide"
        })
        .specificVersionable(RIDocument, RIDocumentVersion, "edit", processType.content_type, context, [
            "adhHttp", (adhHttp : AdhHttp.Service) => (item : ResourcesBase.IResource, version : ResourcesBase.IResource) => {
                return adhHttp.options(item.path).then((options : AdhHttp.IOptions) => {
                    if (!options.POST) {
                        throw 401;
                    } else {
                        return {
                            documentUrl: version.path
                        };
                    }
                });
            }])
        .defaultVersionable(RIParagraph, RIParagraphVersion, "comments", processType.content_type, context, {
            space: "content",
            movingColumns: "is-collapse-show-show"
        })
        .specificVersionable(RIParagraph, RIParagraphVersion, "comments", processType.content_type, context, [
            () => (item : ResourcesBase.IResource, version : ResourcesBase.IResource) => {
                var documentUrl = _.last(_.sortBy(SIParagraph.get(version).documents));
                return {
                    commentableUrl: version.path,
                    commentCloseUrl: documentUrl,
                    documentUrl: documentUrl
                };
            }])
        .defaultVersionable(RIComment, RICommentVersion, "", processType.content_type, context, {
            space: "content",
            movingColumns: "is-collapse-show-show"
        })
        .specificVersionable(RIComment, RICommentVersion, "", processType.content_type, context, ["adhHttp", "$q", (
            adhHttp : AdhHttp.Service,
            $q : angular.IQService
        ) => {
            var getCommentableUrl = (resource) : angular.IPromise<any> => {
                if (resource.content_type !== RICommentVersion.content_type) {
                    return $q.when(resource);
                } else {
                    var url = SIComment.get(resource).refers_to;
                    return adhHttp.get(url).then(getCommentableUrl);
                }
            };

            return (item : ResourcesBase.IResource, version : ResourcesBase.IResource) => {
                return getCommentableUrl(version).then((commentable) => {
                    var documentUrl = _.last(_.sortBy(SIParagraph.get(commentable).documents));
                    return {
                        commentableUrl: commentable.path,
                        commentCloseUrl: documentUrl,
                        documentUrl: documentUrl
                    };
                });
            };
        }]);
};
