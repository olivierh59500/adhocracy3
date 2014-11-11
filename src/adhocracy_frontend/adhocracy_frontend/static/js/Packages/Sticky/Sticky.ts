/// <reference path="../../_all.d.ts"/>

import Sticky = require("sticky");
console.log(Sticky);  // required to keep tsc from optimizing the import away.  :(

export var createDirective = () => {
    return {
        restrict: "A",
        link: (scope, element, attrs) => {
            var el = <any>$(element[0]);

            console.log(el);
            console.log(el.sticky);
            debugger;

            el.sticky({/*options*/});  // ...

            // var stick = new Sticky(document.querySelector(el), {});
        }
    };
};

export var moduleName = "sticky";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("sticky", [createDirective]);
};
