import * as AdhAnonymize from "./Anonymize";


export var moduleName = "adhAnonymize";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("adhAnonymize", ["adhConfig", AdhAnonymize.anonymizeDirective]);
};
