/// <reference path="../../../../lib2/types/angular.d.ts"/>

import * as AdhConfig from "../Config/Config";
import * as AdhHttp from "../Http/Http";
import * as AdhPermissions from "../Permissions/Permissions";
import * as AdhResourceArea from "../ResourceArea/ResourceArea";
import * as AdhTopLevelState from "../TopLevelState/TopLevelState";
import * as AdhUtil from "../Util/Util";

import * as ResourcesBase from "../../ResourcesBase";

import RIComment from "../../../Resources_/adhocracy_core/resources/comment/IComment";
import RICommentVersion from "../../../Resources_/adhocracy_core/resources/comment/ICommentVersion";
import RIParagraph from "../../../Resources_/adhocracy_core/resources/paragraph/IParagraph";
import RIParagraphVersion from "../../../Resources_/adhocracy_core/resources/paragraph/IParagraphVersion";
import * as SIComment from "../../../Resources_/adhocracy_core/sheets/comment/IComment";
import * as SIParagraph from "../../../Resources_/adhocracy_core/sheets/document/IParagraph";
import * as SIWorkflow from "../../../Resources_/adhocracy_core/sheets/workflow/IWorkflowAssignment";

export var pkgLocation = "/Core/Workbench";


export var workbenchDirective = (
    adhTopLevelState : AdhTopLevelState.Service,
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Workbench.html",
        scope: {
            processProperties: "="
        },
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("view", scope));
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
            scope.$on("$destroy", adhTopLevelState.bind("contentType", scope));
            scope.$watch("processUrl", (processUrl) => {
                if (processUrl) {
                    adhHttp.get(processUrl).then((resource) => {
                        scope.currentPhase = SIWorkflow.get(resource).workflow_state;
                    });
                }
            });
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

export var proposalDetailColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ProposalDetailColumn.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
            scope.$on("$destroy", adhTopLevelState.bind("proposalUrl", scope));
        }
    };
};

export var proposalCreateColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ProposalCreateColumn.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
        }
    };
};

export var proposalEditColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ProposalEditColumn.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
            scope.$on("$destroy", adhTopLevelState.bind("proposalUrl", scope));
        }
    };
};

export var imageColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service,
    adhResourceUrl,
    adhParentPath
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/ImageColumn.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
            scope.$on("$destroy", adhTopLevelState.bind("proposalUrl", scope));
            scope.goBack = () => {
                var url = adhResourceUrl(adhParentPath(scope.proposalUrl));
                adhTopLevelState.goToCameFrom(url);
            };
        }
    };
};

export var detailColumnDirective = (
    adhConfig : AdhConfig.IService,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/DetailColumn.html",
        link: (scope) => {
            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
        }
    };
};

var addResourceButtonFactory = (
    targetView : string,
    label : string
) => (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhPermissions : AdhPermissions.Service,
    adhTopLevelState : AdhTopLevelState.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/AddProposalButton.html",
        link: (scope) => {
            scope.targetView = targetView;
            scope.label = label;

            scope.$on("$destroy", adhTopLevelState.bind("processUrl", scope));
            adhPermissions.bindScope(scope, () => scope.processUrl, "processOptions");
            adhHttp.get(scope.processUrl).then((process) => {
                var workflow = SIWorkflow.get(process).workflow;
                scope.workflowAllowsCreate = (workflow !== "debate" && workflow !== "debate_private" && workflow !== "stadtforum");
            });

            scope.setCameFrom = () => {
                adhTopLevelState.setCameFrom();
            };
        }
    };
};

export var addDocumentButtonDirective = addResourceButtonFactory("create_document", "TR__ADD_DOCUMENT");
export var addProposalButtonDirective = addResourceButtonFactory("create_proposal", "TR__IDEA_COLLECTION_PARTICIPATE");


export var registerCommonRoutesFactory = (
    ideaCollection,
    itemType,
    versionType
) => (
    context : string = ""
) => (
    adhResourceAreaProvider : AdhResourceArea.Provider
) => {
    adhResourceAreaProvider
        .default(ideaCollection, "", ideaCollection.content_type, context, {
            space: "content",
            movingColumns: "is-show-hide-hide"
        })
        .default(ideaCollection, "edit", ideaCollection.content_type, context, {
            space: "content",
            movingColumns: "is-show-hide-hide"
        })
        .specific(ideaCollection, "edit", ideaCollection.content_type, context, [
            "adhHttp", (adhHttp : AdhHttp.Service) => (resource) => {
                return adhHttp.options(resource.path).then((options : AdhHttp.IOptions) => {
                    if (!options.PUT) {
                        throw 401;
                    } else {
                        return {};
                    }
                });
            }])
        .defaultVersionable(itemType, versionType, "", ideaCollection.content_type, context, {
            space: "content",
            movingColumns: "is-show-show-hide"
        })
        .defaultVersionable(itemType, versionType, "edit", ideaCollection.content_type, context, {
            space: "content",
            movingColumns: "is-show-show-hide"
        });
};

export var registerDocumentRoutesFactory = (
    ideaCollection,
    itemType,
    versionType,
    hasCommentColumn : boolean = true
) => (
    context : string = ""
) => (
    adhResourceAreaProvider : AdhResourceArea.Provider
) => {
    adhResourceAreaProvider
        .default(ideaCollection, "create_document", ideaCollection.content_type, context, {
            space: "content",
            movingColumns: "is-show-show-hide"
        })
        .specific(ideaCollection, "create_document", ideaCollection.content_type, context, [
            "adhHttp", (adhHttp : AdhHttp.Service) => (resource) => {
                return adhHttp.options(resource.path).then((options : AdhHttp.IOptions) => {
                    if (!options.POST) {
                        throw 401;
                    } else {
                        return {};
                    }
                });
            }])
        .specificVersionable(itemType, versionType, "", ideaCollection.content_type, context, [
            () => (item : ResourcesBase.IResource, version : ResourcesBase.IResource) => {
                return {
                    documentUrl: version.path
                };
            }])
        .specificVersionable(itemType, versionType, "edit", ideaCollection.content_type, context, [
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
            }]);

    if (hasCommentColumn) {
        adhResourceAreaProvider
            .defaultVersionable(RIParagraph, RIParagraphVersion, "comments", ideaCollection.content_type, context, {
                space: "content",
                movingColumns: "is-collapse-show-show"
            })
            .specificVersionable(RIParagraph, RIParagraphVersion, "comments", ideaCollection.content_type, context, [
                () => (item : ResourcesBase.IResource, version : ResourcesBase.IResource) => {
                    var documentUrl = _.last(_.sortBy(SIParagraph.get(version).documents));
                    return {
                        commentableUrl: version.path,
                        commentCloseUrl: documentUrl,
                        documentUrl: documentUrl
                    };
                }])
            .defaultVersionable(RIComment, RICommentVersion, "", ideaCollection.content_type, context, {
                space: "content",
                movingColumns: "is-collapse-show-show"
            })
            .specificVersionable(RIComment, RICommentVersion, "", ideaCollection.content_type, context, ["adhHttp", "$q", (
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
    }
};

export var registerProposalRoutesFactory = (
    ideaCollection,
    itemType,
    versionType,
    hasCommentColumn : boolean = true
) => (
    context : string = ""
) => (
    adhResourceAreaProvider : AdhResourceArea.Provider
) => {
    adhResourceAreaProvider
        .default(ideaCollection, "create_proposal", ideaCollection.content_type, context, {
            space: "content",
            movingColumns: "is-show-show-hide"
        })
        .specific(ideaCollection, "create_proposal", ideaCollection.content_type, context, [
            "adhHttp", (adhHttp : AdhHttp.Service) => (resource) => {
                return adhHttp.options(resource.path).then((options : AdhHttp.IOptions) => {
                    if (!options.POST) {
                        throw 401;
                    } else {
                        return {};
                    }
                });
            }])
        .specificVersionable(itemType, versionType, "", ideaCollection.content_type, context, [
            () => (item, version) => {
                return {
                    proposalUrl: version.path
                };
            }])
        .specificVersionable(itemType, versionType, "edit", ideaCollection.content_type, context, [
            "adhHttp", (adhHttp : AdhHttp.Service) => (item, version) => {
                return adhHttp.options(item.path).then((options : AdhHttp.IOptions) => {
                    if (!options.POST) {
                        throw 401;
                    } else {
                        return {
                            proposalUrl: version.path
                        };
                    }
                });
            }])
        .defaultVersionable(itemType, versionType, "image", ideaCollection.content_type, context, {
            space: "content",
            movingColumns: "is-show-show-hide"
        })
        .specificVersionable(itemType, versionType, "image", ideaCollection.content_type, context, [
            "adhHttp", (adhHttp : AdhHttp.Service) => (item, version) => {
                return adhHttp.options(item.path).then((options : AdhHttp.IOptions) => {
                    if (!options.POST) {
                        throw 401;
                    } else {
                        return {
                            proposalUrl: version.path
                        };
                    }
                });
            }]);

    if (hasCommentColumn) {
        adhResourceAreaProvider
            .defaultVersionable(itemType, versionType, "comments", ideaCollection.content_type, context, {
                space: "content",
                movingColumns: "is-collapse-show-show"
            })
            .specificVersionable(itemType, versionType, "comments", ideaCollection.content_type, context, [
                () => (item, version) => {
                    return {
                        commentableUrl: version.path,
                        commentCloseUrl: version.path,
                        proposalUrl: version.path
                    };
                }])
            .defaultVersionable(RIComment, RICommentVersion, "", ideaCollection.content_type, context, {
                space: "content",
                movingColumns: "is-collapse-show-show"
            })
            .specificVersionable(RIComment, RICommentVersion, "", ideaCollection.content_type, context, ["adhHttp", "$q", (
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
                        return {
                            commentableUrl: commentable.path,
                            commentCloseUrl: commentable.path,
                            proposalUrl: commentable.path
                        };
                    });
                };
            }]);
    }
};