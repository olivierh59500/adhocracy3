/// <reference path="../../../../lib2/types/angular.d.ts"/>
/// <reference path="../../../../lib2/types/lodash.d.ts"/>

import * as _ from "lodash";

import * as AdhConfig from "../Config/Config";
import * as AdhCredentials from "../User/Credentials";
import * as AdhHttp from "../Http/Http";
import * as AdhListing from "../Listing/Listing";
import * as AdhPermissions from "../Permissions/Permissions";
import * as AdhPreliminaryNames from "../PreliminaryNames/PreliminaryNames";
import * as AdhUtil from "../Util/Util";

import * as ResourcesBase from "../../ResourcesBase";

import RIBadgeAssignment from "../../../Resources_/adhocracy_core/resources/badge/IBadgeAssignment";
import * as SIBadge from "../../../Resources_/adhocracy_core/sheets/badge/IBadge";
import * as SIBadgeable from "../../../Resources_/adhocracy_core/sheets/badge/IBadgeable";
import * as SIBadgeAssignment from "../../../Resources_/adhocracy_core/sheets/badge/IBadgeAssignment";
import * as SIDescription from "../../../Resources_/adhocracy_core/sheets/description/IDescription";
import * as SIName from "../../../Resources_/adhocracy_core/sheets/name/IName";
import * as SIPool from "../../../Resources_/adhocracy_core/sheets/pool/IPool";
import * as SITitle from "../../../Resources_/adhocracy_core/sheets/title/ITitle";

var pkgLocation = "/Core/Badge";

export interface IBadgeAssignment {
    title : string;
    description : string;
    name : string;
    path : string;
    badgePath : string;
}

export interface IGetBadgeAssignments {
    (resource : ResourcesBase.IResource) : angular.IPromise<IBadgeAssignment[]>;
}

export interface IBadge {
    name : string;
    title? : string;
    path : string;
    groups? : string[];
}

export interface IBadgeGroup {
    name : string;
    title : string;
    path : string;
}

var extractBadge = (badge) : IBadge => {
    return {
        name: SIName.get(badge).name,
        title: SITitle.get(badge).title,
        path: badge.path,
        groups: SIBadge.get(badge).groups
    };
};

var extractGroup = (group) : IBadgeGroup => {
    return {
        name: SIName.get(group).name,
        title: SITitle.get(group).title,
        path: group.path
    };
};

var collectBadgesByGroup = (groupPaths, badges) => {
    var badgesByGroup = {};
    _.forEach(groupPaths, (groupPath) => {
        badgesByGroup[groupPath] = [];
        _.forOwn(badges, (badge) => {
            if (_.includes(badge.groups, groupPath)) {
                badgesByGroup[groupPath].push(badge);
            }
        });
    });
    return badgesByGroup;
};

var createBadgeFacets = (badgeGroups, badges) : AdhListing.IFacetItem[] => {
    var groupPaths = _.map(badgeGroups, "path");
    var badgesByGroup = collectBadgesByGroup(groupPaths, badges);
    return _.map(badgeGroups, (group : any) => {
        return {
            key: "badge",
            name: group.title,
            items: _.map(badgesByGroup[group.path], (badge : any) => {
                return {
                    key: badge.name,
                    name: badge.title
                };
            })
        };
    });
};

export var getBadgeFacets = (
    adhHttp : AdhHttp.Service,
    $q : angular.IQService
) => (
    path : string
) : angular.IPromise<AdhListing.IFacetItem[]> => {
    var httpMap = (paths : string[], fn) : angular.IPromise<any[]> => {
        return $q.all(_.map(paths, (path) => {
            return adhHttp.get(path).then(fn);
        }));
    };

    var params = {
        elements: "content",
        depth: 4,
        content_type: SIBadge.nick
    };

    return adhHttp.get(path, params).then((response) => {
        var badgePaths = <string[]>_.map(SIPool.get(response).elements, "path");
        return httpMap(badgePaths, extractBadge).then((badges) => {
            var groupPaths = _.union.apply(_, _.map(badges, "groups"));
            return httpMap(groupPaths, extractGroup).then((badgeGroups) => {
                return createBadgeFacets(badgeGroups, badges);
            });
        });
    });
};

export var getBadgesFactory = (
    adhHttp : AdhHttp.Service,
    $q : angular.IQService
) : IGetBadgeAssignments => (
    resource : ResourcesBase.IResource,
    includeParent? : boolean
) : angular.IPromise<IBadgeAssignment[]> => {
    if (typeof includeParent === "undefined") {
        includeParent = !!resource.content_type.match(/Version$/);
    }

    var assignmentPaths = SIBadgeable.get(resource).assignments;

    var getBadge = (assignmentPath : string) => {
        return adhHttp.get(assignmentPath).then((assignment : ResourcesBase.IResource) => {
            var badgePath = SIBadgeAssignment.get(assignment).badge;
            return adhHttp.get(badgePath).then((badge) => {
                return {
                    title: SITitle.get(badge).title,
                    name: SIName.get(badge).name,
                    description: SIDescription.get(assignment).description,
                    path: assignmentPath,
                    badgePath: badgePath
                };
            });
        });
    };

    if (includeParent) {
        var parentPath = AdhUtil.parentPath(resource.path);

        return adhHttp.get(parentPath).then((parentResource) => {
            var parentAssignments = SIBadgeable.get(parentResource).assignments;
            assignmentPaths = assignmentPaths.concat(parentAssignments);
            return $q.all(_.map(assignmentPaths, getBadge));
        });
    } else {
        return $q.all(_.map(assignmentPaths, getBadge));
    }
};

export var getAssignableBadgePaths = (rawOptions) : string[] => {
    var requestBodyOptions : {content_type : string}[] = AdhUtil.deepPluck(rawOptions, [
        "data", "POST", "request_body"
    ]);

    var assignableBadgeOptions = _.find(
        requestBodyOptions,
        (body) => body.content_type === RIBadgeAssignment.content_type);

    return AdhUtil.deepPluck(assignableBadgeOptions, [
        "data", SIBadgeAssignment.nick, "badge"
    ]);
};

var bindPath = (
    adhHttp : AdhHttp.Service,
    adhPermissions : AdhPermissions.Service,
    $q : angular.IQService
) => (
    scope
) : void => {
    scope.data = {
        badge: "",
        description: ""
    };

    var getAssignableBadges = (rawOptions) : angular.IPromise<any> => {
        if (!rawOptions) {
            return $q.when();
        }

        var assignableBadgePaths : string[] = getAssignableBadgePaths(rawOptions);

        return $q.all(_.map(assignableBadgePaths, (b) => adhHttp.get(b).then(extractBadge))).then((badges : any) => {
            scope.badges = _.keyBy(badges, "path");
            var groupPaths : string[]  = _.union.apply(_, _.map(badges, "groups"));
            return $q.all(_.map(groupPaths, (g) => adhHttp.get(g))).then((result) => {
                scope.badgeGroups = _.keyBy(_.map(result, extractGroup), "path");
                scope.badgesByGroup = collectBadgesByGroup(groupPaths, badges);
            });
        });
    };

    adhPermissions.bindScope(scope, scope.poolPath, "rawOptions", {importOptions: false});
    scope.$watch("rawOptions", getAssignableBadges);
};


export var badgeAssignment = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhPermissions : AdhPermissions.Service,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    $q : angular.IQService,
    adhCredentials : AdhCredentials.Service,
    adhGetBadges
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Assignment.html",
        scope: {
            modals: "=",
            path: "@",
            showDescription: "=?"
        },
        link: (scope) => {
            scope.badgeablePath = scope.path;
            scope.data = {};

            adhHttp.get(scope.path).then((proposal) => {
                scope.poolPath = SIBadgeable.get(proposal).post_pool;

                return adhGetBadges(proposal).then((assignments : IBadgeAssignment[]) => {

                    bindPath(adhHttp, adhPermissions, $q)(scope);

                    adhHttp.get(scope.badgeablePath).then((proposal) => {
                        scope.poolPath = SIBadgeable.get(proposal).post_pool;

                        scope.assignments = _.keyBy(assignments, "badgePath");
                        // The following object only contains the current assignments. In order to render the badge
                        // assignment UI, Assignment.html iterates over the available badges, though,
                        // and gives them the value checkboxes[badgePath], which is parsed to false when undefined.
                        scope.checkboxes = _.mapValues(scope.assignments, (v) => true);
                    });

                    scope.submit = () => {
                        adhHttp.withTransaction((transaction) => {
                            _.forOwn(scope.checkboxes, (checked, badgePath) => {
                                var assignmentExisted = scope.assignments.hasOwnProperty(badgePath);
                                if (checked && !assignmentExisted) {
                                    var assignment : ResourcesBase.IResource = {
                                        path: adhPreliminaryNames.nextPreliminary(),
                                        content_type: RIBadgeAssignment.content_type,
                                        data: {},
                                    };
                                    SIBadgeAssignment.set(assignment, {
                                        badge: badgePath,
                                        object: scope.badgeablePath,
                                        subject: adhCredentials.userPath
                                    });
                                    transaction.post(scope.poolPath, assignment);
                                } else if (!checked && assignmentExisted) {
                                    transaction.delete(scope.assignments[badgePath].path);
                                }
                            });

                            return transaction.commit()
                                .then((responses) => {
                                    scope.modals.hideModal("badges");
                                    scope.modals.alert("TR__BADGE_ASSIGNMENT_UPDATED", "success");
                                }, (response) => {
                                    scope.serverError = response[0].description;
                                });
                        });
                    };

                    scope.cancel = () => {
                        scope.modals.hideModal("badges");
                    };
                });
            });

        }
    };
};
