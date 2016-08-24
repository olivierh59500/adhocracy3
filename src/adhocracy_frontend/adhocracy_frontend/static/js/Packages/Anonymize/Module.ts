import * as AdhUserModule from "../User/Module";

import * as AdhAnonymize from "./Anonymize";


export var moduleName = "adhAnonymize";

export var register = (angular) => {
    angular
        .module(moduleName, [
			AdhUserModule.moduleName
		])
        .directive("adhAnonymize", ["adhConfig", "adhUser", "$q", AdhAnonymize.anonymizeDirective]);
};
