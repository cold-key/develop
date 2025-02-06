// let constant = require("../base/Constant.js")

class Point{
    x;
    y;

    constructor(x,y){
        this.x = x;
        this.y = y;
    }

    getX(){
        return this.x;
    }
    getY(){
        return this.y;
    }
    getToPointDistance(point1){
        let x1 = point1.getX();
        let y1 = point1.getY();
        let x2 = this.x;
        let y2 = this.y;
        return Math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2));
    }

    isInPolygon(pointList){
        let isIn = false;
        for(let i = 0; i < pointList.length; i++){
            let j = (i + 1) % pointList.length;
            let point1 = pointList[i];
            let xi = point1.getX();
            let yi = point1.getY();
            let point2 = pointList[j];
            let xj = point2.getX();
            let yj = point2.getY();
            let isIntersect = (this.y > yi !== this.y > yj) && (this.x < (xj - xi) * (y - yi) / (yj - yi) + xi)
            if(isIntersect){
                isIn = !isIn;
            }
        }
        return isIn;
    }
}

class Line{
    point1;
    point2;
    type; //  1 : 线段 2：直线 3：射线
    
    k;
    b;

    constructor(point1,point2,type){
        this.point1 = point1;
        this.point2 = point2;
        this.type = type;

        this.k = (point1.getY() - point2.getY()) / (point1.getX() - point2.getX());
        this.b = point1.getY() - this.k * point1.getX();
    }

    // angle [0,360)
    constructor(startPoint,r,angle){
        let tansformedAngle = 0;
        if(angle < 0){
            tansformedAngle = 180 + angle
        }
        if(angle > 180){
            tansformedAngle = angle - 180;
        }
        let k = Math.tan(tansformedAngle);
        let b = startPoint.getY() - k * startPoint.getX();
        this.k = k;
        this.b = b;

        let point2X = startPoint.getX() + Math.cos(tansformedAngle) * r;
        let point2Y = startPoint.getY() + Math.sin(tansformedAngle) * r;

        this.point1 = startPoint;
        this.point2 = new Point(point2X,point2Y);
        this.type = 1;
    }

    getK(){
        return this.k;
    }

    getB(){
        return this.b;
    }

    isPointInLine(point){
        let pointY = point.getY();
        let pointX = point.getX();
        if(pointY !== this.k * pointX + this.b){
            return false;
        }
        if(this.type === 1){
            let minX = this.point1.getX() < this.point2.getX() ? this.point1.getX() : this.point2.getX();
            let maxX = this.point1.getX() > this.point2.getX() ? this.point1.getX() : this.point2.getX();
            if(pointX <= maxX && pointX >= minX){
                return true;
            }
        }else if (this.type === 2){
            return true;
        }else if(this.type === 3){
            if(this.point1.getX() < this.point2.getX()){
                return this.point1.getX() < pointX;
            }else{
                return this.point1.getX() > pointX;
            }
        }
        return false;
    }

    getPointToLineDistance(point){
        let pointX = point.getX();
        let pointY = point.getY();
        let distance = 0;
        if(this.type === 2){
            distance = Math.abs(this.k * pointX - pointY + this.b) / Math.sqrt(this.k * this.k + 1);
        }else if(this.type === 1){
            let point1Distance = point.getToPointDistance(this.point1);
            let point2Distance = point.getToPointDistance(this.point2);
            distance = point1Distance < point2Distance ? point1Distance : point2Distance;
        }else if(this.type === 3){
            // todo
        }

        return distance;
    }

    getIntersectionWithLine(otherLine){
        let k1 = this.getK();
        let b1 = this.getB();
        let k2 = otherLine.getK();
        let b2 = otherLine.getB();

        let x = (b2 - b1) / (k1 - k2);
        let y = (k1 * b2 - b1 * k1 - b2 * k2 + b1 * k2) / (k1 - l2);

        return new Point(x,y);
    }

    isIntersectTwoLine(otherLine){
        if(this.getK() === otherLine.getK()){
            if(this.getB() === otherLine.getB()){
                return true;
            }else{
                return false;
            }
        }else{
            let intersecrPoint = this.getIntersectionWithLine(otherLine);
            return this.isPointInLine(intersecrPoint);
        }
    }

    // 小角:(0,90)
    getAngleWithLine(otherLine){
        let k1 = this.k;
        let k2 = otherLine.getK();

        let angle = (180/Math.PI) * Math.atan(Math.abs((k1-k2)/(1+k1*k2)));
        return angle;
    }
}
class MathUtil{

    constructor(){

    }

    pointToPointDistance(point1,point2){
        let x1 = point1.getX();
        let y1 = point1.getY();
        let x2 = point2.getX();
        let y2 = point2.getY();
        return Math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2));
    }

    pointToLineDistance(point,line){
        return line.getPointToLineDistance(point);
    }
}

module.export = {
    Point,
    Line,
    MathUtil
}