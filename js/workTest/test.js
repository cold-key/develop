function person(){
    var age = 18;
    function cat(){
        age++;
        console.log(age);
    }
    return cat;
}
console.log("1 ------ ");
person()();// 19
person()();// 19
console.log("2 ------ ");
let f = person();
f();
f();