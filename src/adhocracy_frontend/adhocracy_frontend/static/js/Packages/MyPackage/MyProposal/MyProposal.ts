import * as SIDescription from "../../../Resources_/adhocracy_core/sheets/description/IDescription";
import * as SITitle from "../../../Resources_/adhocracy_core/sheets/title/ITitle";

var pkgLocation = "/MyPackage/MyProposal";


var bindPath = (
    adhHttp
) => (
    scope,
    pathKey = "path"
) => {
    var path = scope[pathKey];
    adhHttp.get(path).then((resource) => {
        scope.data = {
            title: resource.data[SITitle.nick].title,
            description: resource.data[SIDescription.nick].description,
        };
    });
};


export var detailDirective = (
    adhConfig,
    adhHttp
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {
            path: "@"
        },
        link: (scope) => {
            bindPath(adhHttp)(scope);
        }
    };
};
