class BaseClass {
    public x : number;
    private y : number;
    protected z : number;

    constructor(x : number = 0, y : number = 0, z : number = 0){
        this.x = x;
        this.y = y;
        this.z = z;
        console.log("BaseClass constructor");
    }

    getX(){
        return this.x;
    }

    setX(x : number){
        this.x = x;
    }

    getY(){
        return this.y;
    }

    setY(y : number){
        this.y = y;
    }

    getZ(){
        return this.z;
    }

    setZ(z : number){
        this.z = z;
    }

    toString(){
        return this.x + "," + this.y + "," + this.z;
    }
}

class SubClass extends BaseClass {
    private key : string;

    constructor(x : number = 0, y : number = 0, z : number = 0, key : string = ""){
        super(x,y,z);
        this.key = key;
        console.log("SubClass constructor");
    }

    getKey(){
        return this.key;
    }

    setKey(key : string){
        this.key = key;
    }

    test(){
        
    }

    toString(){
        return super.toString();
    }
}

interface IPrint {
    print(): void;
}

abstract class AbstractClass {
    abstract test(): void;
}

class SubAbstractClass extends AbstractClass implements IPrint {
    print(): void {
        console.log("SubAbstractClass print");
    }

    test(): void {
        console.log("SubAbstractClass test");
    }
}

function main(): void {
    // let sub = new SubClass(1,2,3, "key");
    // console.log(sub.toString());

    let subAbstract = new SubAbstractClass();
    subAbstract.print();
    subAbstract.test();
}

main();

export { main };