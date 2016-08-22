import * as AdhConfig from "../Config/Config";

var pkgLocation = "/Anonymize";


export var anonymizeDirective = (
    adhConfig : AdhConfig.IService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Anonymize.html",
        scope: {
            options: "=",
            model: "=",
        },
        link: (scope) => {
            scope.isEnabled = adhConfig.anonymize_enabled;

            if (scope.isEnabled) {
                // FIXME: live
                // scope.isOptional = rawOptions.data[verb].request_headers.hasOwnProperty("X-Anonymize");

                scope.data = {};

                scope.$watch("isOptional", (isOptional) => {
                    // scope.data.model = isOptional ? adhUser.anonymize : false;
                });

                scope.$watch("data.model", (model) => {
                    scope.model = model;
                });
            }
        }
    };
};
