import * as AdhConfig from "../Config/Config";
import * as AdhUser from "../User/User";

var pkgLocation = "/Anonymize";

export var getAnonymizeDefault = (
    adhUser : AdhUser.Service
) => {
    return adhUser.ready.then(() => {
        return adhUser.data.anonymize;
    });
};

export var getAnonymizeOptional = (
    $q : angular.IQService
) => {
    return $q.when(true);
    // scope.isOptional = rawOptions.data[verb].request_headers.hasOwnProperty("X-Anonymize");
};

export var anonymizeDirective = (
    adhConfig : AdhConfig.IService,
    adhUser : AdhUser.Service,
    $q : angular.IQService
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
                scope.data = {};
                scope.data.model = false;
                scope.isOptional = false;

                $q.all([
                    getAnonymizeDefault(adhUser),
                    getAnonymizeOptional($q)
                ]).then((args) => {
                    scope.data.model = args[0];
                    scope.isOptional = args[1];
                });

                scope.$watch("data.model", (model) => {
                    scope.model = model;
                });
            }
        }
    };
};
