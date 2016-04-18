import * as AdhEmbedModule from "../../Embed/Module";
import * as AdhHttpModule from "../../Http/Module";

import * as MyProposal from "./MyProposal";

export var moduleName = "adhMyPackageMyProposal";


export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhEmbedModule.moduleName,
            AdhHttpModule.moduleName,
        ])
        .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
            adhEmbedProvider.registerDirective("my-proposal-detail");
        }])
        .directive("adhMyProposalDetail", ["adhConfig", "adhHttp", MyProposal.detailDirective]);
};
