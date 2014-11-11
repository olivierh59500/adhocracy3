/// <reference path="../../_all.d.ts"/>

import sticky = require("sticky");

export var createDirective = () => {
    return {
        restrict: "A",
        link: (scope, element, attrs) => {
            var el = element[0];
            var stick = new sticky.Sticky(document.querySelector(el), {});
        }
    };
};

export var moduleName = "sticky";

export var register = (angular) => {
    angular
        .module(moduleName, [])
        .directive("sticky", [createDirective]);
};
