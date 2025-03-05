// 类装饰器

// 这是工厂函数，返回值才是装饰器
function CustomClassDecorator(info: string): ClassDecorator {
    return (target: Function) => {
        // 非侵入式
        console.log(target) // [Function user]
        console.log(info) // 你好
    }
}

@CustomClassDecorator('你好')
class User {
    public name!: string

    constructor() {
        this.name = '马东锡'
    }
}

function AnimalDecorator<T extends {new(...args:any[]):{}}>(constructor:T ){
    let role = new constructor();
    console.log(JSON.stringify(role));
    return class extends constructor {
        name = "Peter"
        son = "kelis"
    }
}

@AnimalDecorator
class Role {
    public name!: string

    constructor() {
        this.name = '狗'
    }
}

let user = new User();
console.log(user.name)

let role = new Role();
console.log(role.name);