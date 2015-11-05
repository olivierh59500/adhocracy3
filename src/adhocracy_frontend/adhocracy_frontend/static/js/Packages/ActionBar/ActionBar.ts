import * as AdhConfig from "../Config/Config";
import * as AdhTopLevelState from "../TopLevelState/TopLevelState";

var pkgLocation = "/ActionBar";

export var cancelDirective = (
        adhTopLevelState : AdhTopLevelState.Service,
        adhConfig : AdhConfig.IService,
        adhResourceUrl) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Cancel.html",
        scope: {
            path: "@"
        },
        link: (scope, element, attrs) => {
            console.log("xx");
            var url = adhResourceUrl(scope.path);
            adhTopLevelState.goToCameFrom(url);
        }
    };
};

