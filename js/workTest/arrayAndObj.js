function aResSampling(arr, m) {
    let result = new Array(m).fill(0).map((_, i) => ({ index: i, value: arr[i], weight: Math.pow(Math.random(),1/arr[i]) }));
    
    for (let i = m; i < arr.length; i++) {
        let w = Math.pow(Math.random(),1/arr[i]);
        let candidate = { index: i, value: arr[i], weight: w };
        
        let minWeightIndex = 0;
        for (let j = 1; j < m; j++) {
            if (result[j].weight < result[minWeightIndex].weight) {
                minWeightIndex = j;
            }
        }
        
        if (candidate.weight > result[minWeightIndex].weight) {
            result[minWeightIndex] = candidate;
        }
    }
    
    return result.map(item => item.value);
}

// 示例数组和权重
const values = [10, 1000000000000000, 30, 40, 50];
const m = 1; // 要随机选择的元素数量

// 调用函数并打印结果
console.log(aResSampling(values, m));