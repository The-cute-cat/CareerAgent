"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
Object.defineProperty(exports, "__esModule", { value: true });
var vue_router_1 = require("vue-router");
var HelloWorld_vue_1 = require("./components/HelloWorld.vue");
var __VLS_ctx = __assign(__assign({}, {}), {});
var __VLS_components;
var __VLS_intrinsics;
var __VLS_directives;
/** @type {__VLS_StyleScopedClasses['router-link-exact-active']} */ ;
/** @type {__VLS_StyleScopedClasses['logo']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.header, __VLS_intrinsics.header)({});
__VLS_asFunctionalElement1(__VLS_intrinsics.img)(__assign(__assign({ alt: "Vue logo" }, { class: "logo" }), { src: "@/assets/logo.svg", width: "125", height: "125" }));
/** @type {__VLS_StyleScopedClasses['logo']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)(__assign({ class: "wrapper" }));
/** @type {__VLS_StyleScopedClasses['wrapper']} */ ;
var __VLS_0 = HelloWorld_vue_1.default;
// @ts-ignore
var __VLS_1 = __VLS_asFunctionalComponent1(__VLS_0, new __VLS_0({
    msg: "You did it!",
}));
var __VLS_2 = __VLS_1.apply(void 0, __spreadArray([{
        msg: "You did it!",
    }], __VLS_functionalComponentArgsRest(__VLS_1), false));
__VLS_asFunctionalElement1(__VLS_intrinsics.nav, __VLS_intrinsics.nav)({});
var __VLS_5;
/** @ts-ignore @type {typeof __VLS_components.RouterLink | typeof __VLS_components.RouterLink} */
vue_router_1.RouterLink;
// @ts-ignore
var __VLS_6 = __VLS_asFunctionalComponent1(__VLS_5, new __VLS_5({
    to: "/",
}));
var __VLS_7 = __VLS_6.apply(void 0, __spreadArray([{
        to: "/",
    }], __VLS_functionalComponentArgsRest(__VLS_6), false));
var __VLS_10 = __VLS_8.slots.default;
var __VLS_8;
var __VLS_11;
/** @ts-ignore @type {typeof __VLS_components.RouterLink | typeof __VLS_components.RouterLink} */
vue_router_1.RouterLink;
// @ts-ignore
var __VLS_12 = __VLS_asFunctionalComponent1(__VLS_11, new __VLS_11({
    to: "/about",
}));
var __VLS_13 = __VLS_12.apply(void 0, __spreadArray([{
        to: "/about",
    }], __VLS_functionalComponentArgsRest(__VLS_12), false));
var __VLS_16 = __VLS_14.slots.default;
var __VLS_14;
var __VLS_17;
/** @ts-ignore @type {typeof __VLS_components.RouterView} */
vue_router_1.RouterView;
// @ts-ignore
var __VLS_18 = __VLS_asFunctionalComponent1(__VLS_17, new __VLS_17({}));
var __VLS_19 = __VLS_18.apply(void 0, __spreadArray([{}], __VLS_functionalComponentArgsRest(__VLS_18), false));
var __VLS_export = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({});
exports.default = {};
