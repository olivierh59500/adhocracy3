/// <reference path="../../../lib2/types/angular.d.ts"/>

import * as AdhConfig from "../Config/Config";
import * as AdhHttp from "../Http/Http";
import * as AdhPermissions from "../Permissions/Permissions";
import * as AdhUtil from "../Util/Util";
import * as AdhTopLevelState from "../TopLevelState/TopLevelState";

import * as SIName from "../../Resources_/adhocracy_core/sheets/name/IName";
import * as SIWorkflow from "../../Resources_/adhocracy_core/sheets/workflow/IWorkflowAssignment";
import RIProcess from "../../Resources_/adhocracy_core/resources/process/IProcess";

var pkgLocation = "/Process";


// mirrors adhocracy_core.sheets.workflow.StateData
export interface IStateData {
    name : string;
    description : string;
    start_date : string;
}

export var getStateData = (sheet : SIWorkflow.Sheet, name : string) : IStateData => {
    for (var i = 0; i < sheet.state_data.length; i++) {
        if (sheet.state_data[i].name === name) {
            return sheet.state_data[i];
        }
    }
    return {
        name: null,
        description: null,
        start_date: null
    };
};


export class Provider implements angular.IServiceProvider {
    public templates : {[processType : string]: string};
    public $get;

    constructor () {
        this.templates = {};

        this.$get = ["$injector", ($injector) => {
            return new Service(this, $injector);
        }];
    }
}

export class Service {
    constructor(
        private provider : Provider,
        private $injector : angular.auto.IInjectorService
    ) {}

    public getTemplate(processType : string) : string {
        if (!this.provider.templates.hasOwnProperty(processType)) {
            throw "No template for process type \"" + processType + "\" has been configured.";
        }
        return this.provider.templates[processType];
    }
}

export var workflowSwitchDirective = (
    adhConfig : AdhConfig.IService,
    adhHttp : AdhHttp.Service<any>,
    adhPermissions : AdhPermissions.Service,
    $window : angular.IWindowService
) => {
    return {
        restrict: "E",
        templateUrl: adhConfig.pkg_path + pkgLocation + "/WorkflowSwitch.html",
        scope: {
            path: "@"
        },
        transclude: true,
        link: (scope) => {

            adhPermissions.bindScope(scope, scope.path, "rawOptions", {importOptions: false});
            scope.$watch("rawOptions", (rawOptions) => {
                scope.availableStates = AdhUtil.deepPluck(rawOptions, [
                    "data", "PUT", "request_body", "data", SIWorkflow.nick, "workflow_state"]);
            });

            adhHttp.get(scope.path).then((process) => {
                scope.workflowState = process.data[SIWorkflow.nick].workflow_state;
            });

            scope.switchState = (newState) => {
                adhHttp.get(scope.path).then((process) => {
                    process.data[SIWorkflow.nick] = {
                        workflow_state: newState
                    };
                    process.data[SIName.nick] = undefined;
                    adhHttp.put(scope.path, process).then((response) => {
                        $window.alert("Switched to process state " + newState + ". Page reloading...");
                        $window.parent.location.reload();
                    });
                });
            };

        }
    };
};

export var processViewDirective = (
    adhTopLevelState : AdhTopLevelState.Service,
    adhProcess : Service,
    $compile : angular.ICompileService
) => {
    return {
        restrict: "E",
        link: (scope, element) => {
            adhTopLevelState.on("processType", (processType) => {
                if (processType) {
                    var template = adhProcess.getTemplate(processType);
                    element.html(template);
                    $compile(element.contents())(scope);
                }
            });
        }
    };
};

export var listItemDirective = () => {
    return {
        restrict: "E",
        scope: {
            path: "@"
        },
        template: "<a data-ng-href=\"{{ path | adhResourceUrl }}\">{{path}}</a>"
    };
};

export var listingDirective = (adhConfig : AdhConfig.IService) => {
    return {
        restrict: "E",
        scope: {},
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Listing.html",
        link: (scope) => {
            scope.contentType = RIProcess.content_type;
            scope.params = {
                depth: "all"
            };
        }
    };
};

/**
 * Column directive
 *
 * Every column should be wrapped in an instance of this
 * directive.  It provides common functionality, e.g. alerts and
 * overlays via a controller that can be required by subelements.
 *
 * Subelements can inject template code with the following transclusionIds
 * (see AdhInject):
 *
 * -   body
 * -   menu
 * -   collapsed
 * -   overlays
 */
export interface IColumnScope extends angular.IScope {
    // the controller with interfaces for alerts, overlays, ...
    ctrl: ColumnController;

    // an object that can be used to share data between different parts of the column.
    shared;

    // key of the currently active overlay or undefined
    overlay: string;

    // private
    _alerts: {
        [id: number]: {
            message: string;
            mode: string;
        }
    };
}

export class ColumnController {
    private lastId: number;

    constructor(
        protected adhTopLevelState: AdhTopLevelState.Service,
        protected $timeout: angular.ITimeoutService,
        public $scope: IColumnScope,
        protected $element: angular.IAugmentedJQuery
    ) {
        $scope.ctrl = this;
        $scope._alerts = {};
        $scope.shared = {};

        this.lastId = 0;
    }

    public focus(): void {
        var index = this.$element.index();
        this.adhTopLevelState.set("focus", index);
    }

    public clear(): void {
        this.$scope._alerts = {};
        this.$scope.overlay = undefined;
    }

    public alert(message: string, mode: string = "info", duration: number = 3000): void {
        var id = this.lastId++;
        this.$timeout(() => this.removeAlert(id), duration);

        this.$scope._alerts[id] = {
            message: message,
            mode: mode
        };
    }

    public removeAlert(id: number): void {
        delete this.$scope._alerts[id];
    }

    public showOverlay(key: string): void {
        this.$scope.overlay = key;
    }

    public hideOverlay(key?: string): void {
        if (typeof key === "undefined" || this.$scope.overlay === key) {
            this.$scope.overlay = undefined;
        }
    }

    public toggleOverlay(key: string, condition?: boolean): void {
        if (condition || (typeof condition === "undefined" && this.$scope.overlay !== key)) {
            this.$scope.overlay = key;
        } else if (this.$scope.overlay === key) {
            this.$scope.overlay = undefined;
        }
    }

    public $broadcast(name: string, ...args: any[]) {
        return this.$scope.$broadcast.apply(this.$scope, arguments);
    }

    /**
     * Bind variables from topLevelState and clear this column whenever one of them changes.
     */
    public bindVariablesAndClear(scope, keys: string[]): void {
        var self: ColumnController = this;

        // NOTE: column directives are typically injected mutliple times
        // with different transcludionIds. But we want to trigger clear() only once.
        var clear = () => {
            if (scope.transclusionId === "body") {
                self.clear();
            }
        };

        clear();

        keys.forEach((key: string) => {
            scope.$on("$destroy", self.adhTopLevelState.on(key, (value) => {
                scope[key] = value;
                clear();
            }));
        });
    }
}


export var columnDirective = (adhConfig: AdhConfig.IService) => {
    return {
        restrict: "E",
        scope: true,
        replace: true,
        transclude: true,
        templateUrl: adhConfig.pkg_path + pkgLocation + "/Column.html",
        controller: ["adhTopLevelState", "$timeout", "$scope", "$element", ColumnController]
    };
};
