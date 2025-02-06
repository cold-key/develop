const {MathUtil} = require('./MathUtil');
const {CircleCollider} = require('./Collider');

let MathUtilObj = new MathUtil();

class CollisionDetection{
    colliderTypeEnum;
    constructor(){
        this.colliderTypeEnum = {
            rect:1,
            circle:2,
            polygon:3,
            sector:4
        }
    }

    detect(collider1,collider2){
        let collider1Type = this.getColliderType(collider1);
        let collider2Type = this.getColliderType(collider2);

        let detectFunction = null;
        switch(true){
            case collider1Type === this.colliderTypeEnum.circle && collider2Type === this.colliderTypeEnum.circle:
                detectFunction = this.circleToCircle;
                break;
            case collider1Type === this.colliderTypeEnum.circle && collider2Type === this.colliderTypeEnum.rect:
                detectFunction = this.circleToRect;
                break;
            case collider1Type === this.colliderTypeEnum.circle && collider2Type === this.colliderTypeEnum.polygon:
                detectFunction = this.circleToPolygon;
                break;
            case collider1Type === this.colliderTypeEnum.circle && collider2Type === this.colliderTypeEnum.sector:
                detectFunction = this.circleToSector;
                break;
            case collider1Type === this.colliderTypeEnum.rect && collider2Type === this.colliderTypeEnum.rect:
                detectFunction = this.rectToRect;
                break;
            case collider1Type === this.colliderTypeEnum.rect && collider2Type === this.colliderTypeEnum.polygon:
                detectFunction = this.rectToPolygon;
                break;
            case collider1Type === this.colliderTypeEnum.rect && collider2Type === this.colliderTypeEnum.sector:
                detectFunction = this.rectToSector;
                break;
            case collider1Type === this.colliderTypeEnum.polygon && collider2Type === this.colliderTypeEnum.polygon:
                detectFunction = this.polygonToPolygon;
                break;
            case collider1Type === this.colliderTypeEnum.polygon && collider2Type === this.colliderTypeEnum.sector:
                detectFunction = this.polygonToPolygon;
                break;
            case collider1Type === this.colliderTypeEnum.sector && collider2Type === this.colliderTypeEnum.sector:
                detectFunction = this.sectorToSector;
                break;
        }

        let isCollision = detectFunction(collider1,collider2);
        return isCollision;
    }

    getColliderType(collider1){
        if(collider1 instanceof RectCollider){
            return this.colliderTypeEnum.rect;
        }else if(collider1 instanceof CircleCollider){
            return this.colliderTypeEnum.circle;
        }else if(collider1 instanceof PolygonCollider){
            return this.colliderTypeEnum.polygon;
        }else if(collider1 instanceof SectorCollider){
            return this.colliderTypeEnum.sector;
        }
    }

    circleToCircle(collider1,collider2){
        let point1 = collider1.getPoint();
        let r1 = collider1.getR();
        let point2 = collider2.getPoint();
        let r2 = collider2.getR();
        let distance = MathUtilObj.pointToPointDistance(point1,point2);
        let isCollision = distance < r1+r2; 
        return isCollision;
    }

    circleToRect(collider1,collider2){
        return this.circleToPolygon(collider1,collider2);
    }

    circleToPolygon(collider1,collider2){
        let circleCenterPoint = collider1.getPoint();
        let r = collider1.getR();
        let polygonPointList = collider2.getPointList();
        if(circleCenterPoint.isInPolygon(polygonPointList)){
            return true;
        }
        for(let i = 0; i < polygonPointList.length; i++){
            let j = (i + 1) % polygonPointList.length;
            let point1 = polygonPointList[i];
            let point2 = polygonPointList[j];
            let tempLine = new Line(point1,point2,1);
            let distance = MathUtilObj.pointToLineDistance(circleCenterPoint,tempLine);
            if(distance <= r){
                return true;
            }
        }
        return false;
    }

    circleToSector(collider1,collider2){
        let circlePoint = collider1.getPoint();
        let circleR = collider1.getR();
        let sectorPoint = collider2.getPoint();
        let r = collider2.getR();
        let circleCollider = new CircleCollider(sectorPoint,r);
        if(!this.circleToCircle(collider1,circleCollider)){
            return false;
        }
        let lineList = collider2.getLineList();
        for(let i = 0; i < lineList.length;i++){
            let tempLine = lineList[i];
            if(tempLine.getPointToLineDistance(circlePoint) <= circleR){
                return true;
            }
        }
        return false;
    }

    rectToRect(collider1,collider2){
        let lineList1 = collider1.getLineList();
        let lineList2 = collider2.getLineList();
        let isCollision = this.lineListToLineList(lineList1,lineList2);
        if(!isCollision){
            //
        }
        return isCollision;
    }

    rectToPolygon(collider1,collider2){
        return false;
    }

    rectToSector(collider1,collider2){
        return false;
    }

    polygonToPolygon(collider1,collider2){
        let pointList1 = collider1.getPointList();
        let lineList1 = collider1.getLineList();
        let pointList2 = collider2.getPointList();
        let lineList2 = collider2.getLineList();
        if(this.lineListToLineList(lineList1,lineList2)){
            return true;
        }
        for(let i = 0;i < pointList1.length;i++){
            let tempPoint = pointList1[i];
            if(tempPoint.isInPolygon(pointList2)){
                return true;
            }
        }
        for(let i = 0;i < pointList2.length;i++){
            let tempPoint = pointList2[i];
            if(tempPoint.isInPolygon(pointList1)){
                return true;
            }
        }
        return false;
    }

    polygonToSector(collider1,collider2){
        return false;
    }

    sectorToSector(collider1,collider2){
        return false;
    }

    lineListToLineList(lineList1,lineList2){
        for(let i = 0; i < lineList1.length; i++){
            let line1 = lineList1[i];
            for(let j = 0; j < lineList2.length;j++){
                let line2 = lineList1[j];
                let isIntersect = line1.isIntersectTwoLine(line2);
                if(isIntersect){
                    return true;
                }
            }
        }
        return false;
    }
}