/// <reference path="../../../../../lib2/types/angular.d.ts"/>

import * as AdhConfig from "../../../Core/Config/Config";
import * as AdhHttp from "../../../Core/Http/Http";
import * as AdhPreliminaryNames from "../../../Core/PreliminaryNames/PreliminaryNames";
import * as AdhProcess from "../../../Core/Process/Process";

import * as ResourcesBase from "../../ResourcesBase";

import RIProposal from "../../../../Resources_/adhocracy_meinberlin/resources/bplan/IProposal";
import RIProposalVersion from "../../../../Resources_/adhocracy_meinberlin/resources/bplan/IProposalVersion";
import * as SIProposal from "../../../../Resources_/adhocracy_meinberlin/sheets/bplan/IProposal";
import * as SIVersionable from "../../../../Resources_/adhocracy_core/sheets/versions/IVersionable";
import * as SIWorkflow from "../../../../Resources_/adhocracy_core/sheets/workflow/IWorkflowAssignment";

var pkgLocation = "/Meinberlin/Bplan/Proposal";


export interface IScope extends angular.IScope {
    path : string;
    data : {
        name : string;
        street : string;
        city : string;
        email : string;
        statement : string;
    };
    errors : any[];
    showError : Function;
    onSuccess? : Function;
    submit() : void;
    meinberlinProposalForm : any;
}


var postCreate = (
    adhHttp : AdhHttp.Service,
    adhPreliminaryNames : AdhPreliminaryNames.Service
) => (
    scope : IScope,
    poolPath : string
) : angular.IPromise<any> => {
    var proposal : ResourcesBase.IResource = {
        path: adhPreliminaryNames.nextPreliminary(),
        content_type: RIProposal.content_type,
        data: {},
    };
    proposal.parent = poolPath;

    var proposalVersion : ResourcesBase.IResource = {
        path: adhPreliminaryNames.nextPreliminary(),
        content_type: RIProposalVersion.content_type,
        data: {},
    };
    proposalVersion.parent = proposal.path;
    SIVersionable.set(proposalVersion, {
        follows: [proposal.first_version_path]
    });
    SIProposal.set(proposalVersion, {
        name: scope.data.name,
        street_number: scope.data.street,
        postal_code_city: scope.data.city,
        email: scope.data.email,
        statement: scope.data.statement
    });

    return adhHttp.deepPost([proposal, proposalVersion], {
        noCredentials: true
    });
};


export var createDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service,
    adhPreliminaryNames : AdhPreliminaryNames.Service,
    adhShowError,
    adhSubmitIfValid
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Create.html",
        scope: {
            path: "@",
            onSuccess: "=?"
        },
        link: (scope : IScope, element) => {
            scope.errors = [];
            scope.data = {
                name: "",
                street: "",
                city: "",
                email: "",
                statement: ""
            };
            scope.showError = adhShowError;

            scope.submit = () => {
                return adhSubmitIfValid(scope, element, scope.meinberlinProposalForm, () => {
                    return postCreate(adhHttp, adhPreliminaryNames)(scope, scope.path).then(() => {
                        if (typeof scope.onSuccess !== "undefined") {
                            scope.onSuccess();
                        }
                    });
                });
            };
        }
    };
};


export var embedDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Embed.html",
        scope: {
            path: "@"
        },
        link: (scope) => {
            scope.success = false;

            scope.showSuccess = () => {
                scope.success = true;
            };
            scope.showForm = () => {
                scope.success = false;
            };

            adhHttp.get(scope.path).then((resource) => {
                var sheet = SIWorkflow.get(resource);
                scope.currentPhase = sheet.workflow_state;
                scope.announceText = AdhProcess.getStateData(sheet, "announce").description;
                scope.frozenText = AdhProcess.getStateData(sheet, "frozen").description;
            });
        }
    };
};
