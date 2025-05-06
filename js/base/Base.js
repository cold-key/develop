// console.log("test");

// let arr1 = [1,3,5,7,9,0,0,0,0,0];
// let arr2 = [2,4,6,8,10];

// let rightIndex = 9;

// let oneIndex = 4;
// let twoIndex = 4;

// while(oneIndex >=0 && twoIndex >= 0){
//     if(arr1[oneIndex] > arr2[twoIndex]){
//         arr1[rightIndex] = arr1[oneIndex];
//         rightIndex--;
//         oneIndex--;
//     }else{
//         arr1[rightIndex] = arr2[twoIndex];
//         rightIndex--;
//         twoIndex--;
//     }
// }
// while(twoIndex >= 0){
//     arr1[rightIndex] = arr2[twoIndex];
//     rightIndex--;
//     twoIndex--;
// }

// console.log(JSON.stringify(arr1));

// // let totalLength = arr1.length + arr2.length;

// // 插入排序的思路

// // for(let i = 0; i < arr2.length; i++){
// //     arr1[arr1.length] = arr1[arr1.length - 1];
// //     for(let j = arr1.length - 2; j >= 0; j++){
// //         if(arr1[j] > arr2[i]){
// //             arr1[j] = arr1[j-1];
// //         }else{
// //             arr1[j] = arr2[i];
// //             break;
// //         }
// //     }
// // }


// let a = [1,0,1,2,3,4,98,39,23,34,5,234];




// let p = new Promise((resolve, reject)=>{
//     console.log("start");
//     setTimeout(()=>{
//         resolve();
//     },1000)
// });
// p.then(()=>{
//     console.log("success");
// }).then(()=>{
//     setTimeout(()=>{
//         console.log("success 1000 ms");
//     },1000)
// });