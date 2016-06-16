import * as AdhConfig from "../Config/Config";
import * as AdhHttp from "../Http/Http";
import * as AdhProcess from "../Process/Process";

var pkgLocation = "/Abuse";


export var reportAbuseDirective = (adhHttp : AdhHttp.Service<any>, adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Abuse.html",
        scope: {
            url: "@"  // frontend URL
        },
        require: "^adhColumn",
        link: (scope, element, attrs, column : AdhProcess.ColumnController) => {
            scope.netiquette_url = adhConfig.netiquette_url;
            scope.submit = () => {
                return adhHttp.postRaw(adhConfig.rest_url + "/report_abuse", {
                    url: scope.url,
                    remark: scope.remark
                }).then(() => {
                    column.hideOverlay("abuse");
                    column.alert("TR__REPORT_ABUSE_STATUS_OK", "success");
                }, () => {
                    // FIXME
                });
            };

            scope.cancel = () => {
                column.hideOverlay("abuse");
            };
        }
    };
};

