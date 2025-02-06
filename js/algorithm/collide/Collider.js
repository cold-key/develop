const {Point,Line,MathUtil} = require('./MathUtil');

class Collider{
    constructor(){
        //
    }

}

// 无旋转的矩形碰撞体
class RectCollider extends Collider{
    point;
    width;
    height;
    pointList;
    lineList;
    constructor(point,width,height){
        this.point = point;
        this.width = width;
        this.height = height;
        this.lineList = [];
        this.buildPointList();
    }

    buildLineList(){
        let angle = this.endAngle - this.startAngle;
        let lineNum = Math.floor(angle / this.minAngle);
        for(let i = 0;i <= lineNum;i++){
            let tempAngle = i*this.minAngle + this.startAngle;
            let tempLine = new Line(this.point,this.r,tempAngle);
            this.lineList.push(tempLine);
        }
    }

    buildPointList(){
        this.pointList = []
        this.pointList.push(this.point);
        let upPoint = new Point(this.point.getX(),this.point.getY()+this.height);
        let rightPoint = new Point(this.point.getX()+this.width,this.point.getY());
        let rightAndUpPoint = new Point(this.point.getX()+this.width,this.point.getY()+this.height);
        this.pointList.push(upPoint);
        this.pointList.push(rightAndUpPoint);
        this.pointList.push(rightPoint);
    }

    getPoint(){
        return this.point;
    }

    getWidth(){
        return this.width;
    }

    getHeight(){
        return this.height;
    }

    getPointList(){
        return this.pointList;
    }

    getLineList(){
        return this.lineList;
    }
}

class CircleCollider extends Collider{
    point;
    r;
    constructor(point,r){
        this.point = point;
        this.r = r;
    }

    getPoint(){
        return this.point;
    }

    getR(){
        return this.r;
    }
}

class PolygonCollider extends Collider{
    pointList;
    lineList;
    constructor(pointList){
        this.pointList = pointList;
        this.lineList = [];
        this.buildLineList();
    }

    getPointList(){
        return this.pointList;
    }

    getLineList(){
        return this.lineList;
    }

    buildLineList(){
        for(let i = 0; i < this.pointList.length; i++){
            let j = (i + 1) % this.pointList.length;
            let point1 = this.pointList[i];
            let point2 = this.pointList[j];
            let tempLine = new Line(point1,point2,1);
            this.lineList.push(tempLine);
        }
    }
}

class SectorCollider extends Collider{
    point; // 发射点
    r;
    startAngle; // 起始角一定小于结束角
    endAngle;
    lineList;
    constructor(point,r,startAngle,endAngle){
        this.point = point;
        this.r = r;
        this.startAngle = startAngle;
        this.endAngle = endAngle;

        this.minAngle = 10;

        this.buildLineList();
    }

    standardizeAngle(){
        
    }

    getPoint(){
        return this.point;
    }

    getR(){
        return this.r;
    }

    getLineList(){
        return this.lineList;
    }

    buildLineList(){
        let angle = this.endAngle - this.startAngle;
        let lineNum = Math.floor(angle / this.minAngle);
        for(let i = 0;i <= lineNum;i++){
            let tempAngle = i*this.minAngle + this.startAngle;
            let tempLine = new Line(this.point,this.r,tempAngle);
            this.lineList.push(tempLine);
        }
    }
}