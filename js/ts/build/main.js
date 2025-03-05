var __runInitializers = (this && this.__runInitializers) || function (thisArg, initializers, value) {
    var useValue = arguments.length > 2;
    for (var i = 0; i < initializers.length; i++) {
        value = useValue ? initializers[i].call(thisArg, value) : initializers[i].call(thisArg);
    }
    return useValue ? value : void 0;
};
var __esDecorate = (this && this.__esDecorate) || function (ctor, descriptorIn, decorators, contextIn, initializers, extraInitializers) {
    function accept(f) { if (f !== void 0 && typeof f !== "function") throw new TypeError("Function expected"); return f; }
    var kind = contextIn.kind, key = kind === "getter" ? "get" : kind === "setter" ? "set" : "value";
    var target = !descriptorIn && ctor ? contextIn["static"] ? ctor : ctor.prototype : null;
    var descriptor = descriptorIn || (target ? Object.getOwnPropertyDescriptor(target, contextIn.name) : {});
    var _, done = false;
    for (var i = decorators.length - 1; i >= 0; i--) {
        var context = {};
        for (var p in contextIn) context[p] = p === "access" ? {} : contextIn[p];
        for (var p in contextIn.access) context.access[p] = contextIn.access[p];
        context.addInitializer = function (f) { if (done) throw new TypeError("Cannot add initializers after decoration has completed"); extraInitializers.push(accept(f || null)); };
        var result = (0, decorators[i])(kind === "accessor" ? { get: descriptor.get, set: descriptor.set } : descriptor[key], context);
        if (kind === "accessor") {
            if (result === void 0) continue;
            if (result === null || typeof result !== "object") throw new TypeError("Object expected");
            if (_ = accept(result.get)) descriptor.get = _;
            if (_ = accept(result.set)) descriptor.set = _;
            if (_ = accept(result.init)) initializers.unshift(_);
        }
        else if (_ = accept(result)) {
            if (kind === "field") initializers.unshift(_);
            else descriptor[key] = _;
        }
    }
    if (target) Object.defineProperty(target, contextIn.name, descriptor);
    done = true;
};
var __setFunctionName = (this && this.__setFunctionName) || function (f, name, prefix) {
    if (typeof name === "symbol") name = name.description ? "[".concat(name.description, "]") : "";
    return Object.defineProperty(f, "name", { configurable: true, value: prefix ? "".concat(prefix, " ", name) : name });
};
function sayIntroduce(originalMethod, context) {
    return function () {
        originalMethod.call(this);
        if (Introduce[this.name]) {
            console.log(Introduce[this.name]);
        }
    };
}
function constructorLogger(originalConstructor) {
    console.log("constructor...");
    return originalConstructor;
}
let People = (() => {
    let _classDecorators = [constructorLogger];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    let _instanceExtraInitializers = [];
    let _sayHelloByPeople_decorators;
    var People = _classThis = class {
        constructor(name, age) {
            this.name = __runInitializers(this, _instanceExtraInitializers);
            this.name = name;
            this.age = age;
        }
        getName() {
            return this.name;
        }
        sayHelloByPeople() {
            console.log("People sayHello");
            // console.log(`Hello, my name is ${this.name}`);
        }
    };
    __setFunctionName(_classThis, "People");
    (() => {
        const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
        _sayHelloByPeople_decorators = [sayIntroduce];
        __esDecorate(_classThis, null, _sayHelloByPeople_decorators, { kind: "method", name: "sayHelloByPeople", static: false, private: false, access: { has: obj => "sayHelloByPeople" in obj, get: obj => obj.sayHelloByPeople }, metadata: _metadata }, null, _instanceExtraInitializers);
        __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
        People = _classThis = _classDescriptor.value;
        if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        __runInitializers(_classThis, _classExtraInitializers);
    })();
    return People = _classThis;
})();
let Animal = (() => {
    let _classDecorators = [constructorLogger];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    let _instanceExtraInitializers = [];
    let _sayHelloByAnimal_decorators;
    var Animal = _classThis = class {
        constructor(name) {
            this.name = __runInitializers(this, _instanceExtraInitializers);
            this.name = name;
        }
        getName() {
            return this.name;
        }
        sayHelloByAnimal() {
            console.log("Animal sayHello");
            // console.log(`wangwang, wang wang wang ${this.name}`);
        }
    };
    __setFunctionName(_classThis, "Animal");
    (() => {
        const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
        _sayHelloByAnimal_decorators = [sayIntroduce];
        __esDecorate(_classThis, null, _sayHelloByAnimal_decorators, { kind: "method", name: "sayHelloByAnimal", static: false, private: false, access: { has: obj => "sayHelloByAnimal" in obj, get: obj => obj.sayHelloByAnimal }, metadata: _metadata }, null, _instanceExtraInitializers);
        __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
        Animal = _classThis = _classDescriptor.value;
        if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        __runInitializers(_classThis, _classExtraInitializers);
    })();
    return Animal = _classThis;
})();
const Introduce = {
    Kobe: "manba out",
    Dog: "wanwanwanwanwanwan"
};
let Kobe = new People("Kobe", 30);
// Kobe.sayHelloByPeople();
let Dog = new Animal("Dog");
// Dog.sayHelloByAnimal();
