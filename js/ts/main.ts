function sayIntroduce(originalMethod: any, context: ClassMethodDecoratorContext) {
    return function(){
        originalMethod.call(this);
        if(Introduce[this.name]){
            console.log(Introduce[this.name]);
        }
    }
}

function constructorLogger(originalConstructor: any) {
    console.log("constructor...");
    return originalConstructor;  
}

@constructorLogger
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
    sayHelloByPeople(){
        console.log("People sayHello");
        // console.log(`Hello, my name is ${this.name}`);
    }
}

@constructorLogger
class Animal{
    private name:string;
    constructor(name:string){
        this.name = name;
    }

    getName(){
        return this.name;
    }

    @sayIntroduce
    sayHelloByAnimal(){
        console.log("Animal sayHello");
        // console.log(`wangwang, wang wang wang ${this.name}`);
    }
}

const Introduce = {
    Kobe : "manba out",
    Dog : "wanwanwanwanwanwan"
}

let Kobe = new People("Kobe",30);
// Kobe.sayHelloByPeople();

let Dog = new Animal("Dog");
// Dog.sayHelloByAnimal();