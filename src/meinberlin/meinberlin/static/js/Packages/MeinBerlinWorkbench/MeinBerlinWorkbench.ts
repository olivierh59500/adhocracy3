import AdhTopLevelState = require("../TopLevelState/TopLevelState");

export var meinBerlinWorkbenchDirective = () => {
    return {
        restrict: "E",
        templateUrl: "/static/js/Packages/MeinBerlinWorkbench/MeinBerlinWorkbench.html"
    };
};

export var moduleName = "adhMeinBerlinWorkbench";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhTopLevelState.moduleName
        ])
        // FIXME: This will probably require proper routing
        .config(["adhEmbedProvider", (adhEmbedProvider) => {
            adhEmbedProvider.embeddableDirectives.push("mein-berlin-workbench");
        }])
        .config(["adhTopLevelStateProvider", (adhTopLevelStateProvider : AdhTopLevelState.Provider) => {
            adhTopLevelStateProvider
                .when("mein_berlin_create", () : AdhTopLevelState.IAreaInput => {
                    return {
                        template: "<adh-mein-berlin-workbench></adh-mein-berlin-workbench>"
                    };
                });
        }])
        .directive("adhMeinBerlinWorkbench", ["adhConfig", meinBerlinWorkbenchDirective]);
};
