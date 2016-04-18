/// <reference path="../../../../lib2/types/angular.d.ts"/>

import * as AdhConfig from "../../Config/Config";
import * as AdhHttp from "../../Http/Http";

import * as SIDescription from "../../../Resources_/adhocracy_core/sheets/description/IDescription";
import * as SITitle from "../../../Resources_/adhocracy_core/sheets/title/ITitle";

var pkgLocation = "/MyPackage/MyProposal";


export interface IScope extends angular.IScope {
    data : {
        title : string;
        description : string;
    };
}


var bindPath = (
    adhHttp : AdhHttp.Service<any>
) => (
    scope : IScope,
    pathKey : string = "path"
) => {
    scope.$watch(pathKey, (path : string) => {
        if (path) {
            adhHttp.get(path).then((resource) => {
                scope.data = {
                    title: resource.data[SITitle.nick].title,
                    description: resource.data[SIDescription.nick].description,
                };
            });
        }
    });
};


export var detailDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Detail.html",
        scope: {
            path: "@"
        },
        link: (scope : IScope) => {
            bindPath(adhHttp)(scope);
        }
    };
};
