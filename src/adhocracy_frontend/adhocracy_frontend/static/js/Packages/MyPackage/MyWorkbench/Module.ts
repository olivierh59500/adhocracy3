import * as AdhMovingColumnsModule from "../../MovingColumns/Module";
import * as AdhTopLevelStateModule from "../../TopLevelState/Module";

import * as MyWorkbench from "./MyWorkbench";

export var moduleName = "adhMyPackageMyWorkbench";


export var register = (angular) => {
    angular
        .module(moduleName, [
            AdhMovingColumnsModule.moduleName,
            AdhTopLevelStateModule.moduleName
        ])
        .directive("adhMyWorkbench", ["adhConfig", "adhTopLevelState", MyWorkbench.workbenchDirective])
        .directive("adhMyWorkbenchProposalDetailColumn", ["adhConfig", MyWorkbench.proposalDetailColumnDirective])
        .directive("adhMyWorkbenchProposalCreateColumn", ["adhConfig", MyWorkbench.proposalCreateColumnDirective])
        .directive("adhMyWorkbenchProposalListingColumn", ["adhConfig", MyWorkbench.proposalListingColumnDirective]);
};
