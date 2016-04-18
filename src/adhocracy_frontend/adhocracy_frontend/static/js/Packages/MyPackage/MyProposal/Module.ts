import * as AdhHttpModule from "../../Http/Module";

import * as MyProposal from "./MyProposal";

export var moduleName = "adhMyPackageMyProposal";


export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhHttpModule.moduleName,
        ])
        .directive("adhMyProposalDetail", ["adhConfig", "adhHttp", MyProposal.detailDirective]);
};
