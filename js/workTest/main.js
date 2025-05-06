


let a = [2,9,6,8,10,7,1,3,5];

a.sort((a,b)=>{
    return a - b;
})

let result = -1;

if(a[0] !== 1){
    result = 1;
}else{
    for(let i = 0; i < a.length - 1;i++){
        if(a[i] + 1 !== a[i+1]){
            result = a[i] + 1;
            break;
        }
    }
    
    if(result === -1){
        result = a.length + 1;
    }
}

console.log(result);
