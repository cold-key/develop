class Map{
    constructor(row,col,map){
        this.row = row;
        this.col = col;
        this.map = map;

        this.directionArray = [[0,-1],[1,0],[0,1],[-1,0]];
    }

    buildRandomMap(row,col){
        let map = [];
        for(let i = 0; i < row;i++){
            let colArray = [];
            for(let j = 0; j < col; j++){
                let value = Math.floor(Math.random() * 1.4);
                let point = new Point(j,i);
                colArray.push({value:value,point:point});
            }
            map.push(colArray);
        }
        this.row = row;
        this.col = col;
        this.map = map;
    }

    getPointByPostion(x,y){
        if(x < 0 || x >= this.col || y < 0 || y >= this.row){
            return null;
        }else{
            return this.map[y][x];
        }
    }

    getAroundPointList(x,y){
        let pointList = [];
        for(let i = 0; i < this.directionArray.length; i++){
            let nextX = x + this.directionArray[i][0];
            let nextY = y + this.directionArray[i][1];
            if(nextX < 0 || nextX >= this.col || nextY < 0 || nextY >= this.row){
                continue;
            }else{
                let tempPoint = this.getPointByPostion(nextX,nextY);
                pointList.push(tempPoint);
            }
        }
        return pointList;
    }

    showMap(){
        for(let i = 0; i < row;i++){
            let colStr = "";
            for(let j = 0; j < col; j++){
                let value = this.map[i][j].value;
                colStr += value+" ";
            }
            console.log(colStr);
        }
    }
}

class Point{
    constructor(x,y){
        this.x = x;
        this.y = y;

        this.gValue = 0;
        this.hValue = 0;
        this.fValue = 0;

        this.parentPoint = null;

        this.distanceFunc = function(pointA , pointB){
            let ax = pointA.getX();
            let bx = pointB.getX();
            let ay = pointA.getY();
            let by = pointB.getY();
            return Math.sqrt( (ax - bx) * (ax - bx) + (ay - by) * (ay - by));
        }
    }

    getParentPoint(){
        return this.parentPoint;
    }

    setParentPoint(point){
        this.parentPoint = point;
    }

    getX(){
        return this.x;
    }

    getY(){
        return this.y;
    }

    getG(){
        return this.gValue;
    }

    setG(g){
        this.gValue = g;
    }

    getH(){
        return this.hValue;
    }

    setH(h){
        this.hValue = h;
    }

    getF(){
        return this.gValue + this.hValue;
    }

    setComputeDistanceWay(func){
        if(func){
            this.distanceFunc = func;
        }
    }

    getDistanceToOtherPoint(OtherPoint){
        return this.distanceFunc(this,OtherPoint);
    }
}

function AStar(map,startPoint,endPoint){
    let openQueue = [];
    let openMap = {};
    let closeMap = {};
    let isSearchSuccess = false;

    let pathEndPoint = null;

    openQueue.push(startPoint);
    while(openQueue.length > 0){
        let minPoint = openQueue.shift();
        let x = minPoint.point.getX();
        let y = minPoint.point.getY();
        let key = x + "-" + y
        console.log("minPoint:"+key);
        let aroundPointList = map.getAroundPointList(x,y);
        for(let i = 0; i < aroundPointList.length; i++){
            let temp = aroundPointList[i];
            let value = temp.value;
            let aroundPoint = temp.point;

            if(aroundPoint.x === endPoint.point.x && aroundPoint.y === endPoint.point.y){
                isSearchSuccess = true;
                break;
            }

            let aroundPointKey = aroundPoint.x + "-" + aroundPoint.y;
            console.log("aroundPointKey:"+aroundPointKey);
            if(value === 1 || closeMap[aroundPointKey]){
                console.log("skip");
                continue;
            }
            aroundPoint.setG(minPoint.point.getG() + 1);
            aroundPoint.setH(aroundPoint.getDistanceToOtherPoint(endPoint.point));
            aroundPoint.setParentPoint(minPoint.point);

            if(!openMap[aroundPointKey]){
                openQueue.push(temp);
                openMap[aroundPointKey] = true;
            }
        
        }
        closeMap[key] = true;

        openQueue.sort((a,b)=>{
            return a.point.getF() - b.point.getF();
        })

        if(isSearchSuccess){
            pathEndPoint = minPoint.point;
            break;
        }
    }

    let pathNodeList = [];
    if(!isSearchSuccess && openQueue.length === 0){
        return pathNodeList
    }else{
        while(pathEndPoint.getParentPoint()){
            pathNodeList.unshift(pathEndPoint);
            pathEndPoint = pathEndPoint.getParentPoint();
        }
        return pathNodeList;
    }
}

function main(){
    let mapObj = new Map();
    mapObj.buildRandomMap(60,60);
    // console.log(mapObj.map);
    mapObj.map[0][0].value = 0;
    mapObj.map[59][59].value = 0;

    let startPoint = new Point(0,0);
    let endPoint = new Point(59,59);
    let path = AStar(mapObj, mapObj.map[0][0],mapObj.map[59][59]);
    // console.log(path);
    for(let i = 0; i < path.length;i++){
        console.log(path[i].x + "," + path[i].y);
    }

}

main();

