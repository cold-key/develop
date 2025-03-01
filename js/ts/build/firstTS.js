"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.main = main;
class BaseClass {
    constructor(x = 0, y = 0, z = 0) {
        this.x = x;
        this.y = y;
        this.z = z;
        console.log("BaseClass constructor");
    }
    getX() {
        return this.x;
    }
    setX(x) {
        this.x = x;
    }
    getY() {
        return this.y;
    }
    setY(y) {
        this.y = y;
    }
    getZ() {
        return this.z;
    }
    setZ(z) {
        this.z = z;
    }
    toString() {
        return this.x + "," + this.y + "," + this.z;
    }
}
class SubClass extends BaseClass {
    constructor(x = 0, y = 0, z = 0, key = "") {
        super(x, y, z);
        this.key = key;
        console.log("SubClass constructor");
    }
    getKey() {
        return this.key;
    }
    setKey(key) {
        this.key = key;
    }
    test() {
    }
    toString() {
        return super.toString();
    }
}
class AbstractClass {
}
class SubAbstractClass extends AbstractClass {
    print() {
        console.log("SubAbstractClass print");
    }
    test() {
        console.log("SubAbstractClass test");
    }
}
function main() {
    // let sub = new SubClass(1,2,3, "key");
    // console.log(sub.toString());
    let subAbstract = new SubAbstractClass();
    subAbstract.print();
    subAbstract.test();
}
main();
