class People{
    name:string;
    age:number;
    constructor(name:string,age:number){
        this.name = name;
        this.age = age;
    }

    getName(){
        return this.name;
    }

    @sayIntroduce
    sayHello(){
        console.log(`Hello, my name is ${this.name}`);
    }
}

const Introduce = {
    Kobe : "manba out",
}

function sayIntroduce(originalMethod: any, context: ClassMethodDecoratorContext) {
    // console.log(context);
    return function(){
        originalMethod.call(this);
        if(Introduce[this.name]){
            console.log(Introduce[this.name]);
        }
    }
}

let Kobe = new People("Kobe",30);
Kobe.sayHello();
