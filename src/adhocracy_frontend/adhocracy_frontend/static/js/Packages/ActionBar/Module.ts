import * as AdhTopLevelStateModule from "../TopLevelState/Module";

import * as AdhActionBar from "./ActionBar";


export var moduleName = "adhActionBar";

export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhTopLevelStateModule.moduleName
        ])
        .directive("adhCancel", ["adhTopLevelState", "adhConfig", AdhActionBar.cancelDirective]);
};
