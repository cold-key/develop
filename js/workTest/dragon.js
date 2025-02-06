// 追踪子弹
function logicBulletTrack(){
    // 龙测试代码
    this.bulletMoveNode.angle = 0;

    if(!this.longBodyBoneList){
        let startStr = "long2";
        this.longBodySectionLength = 0;
        this.longBodyMoveDistance = 0;
        this.longBodyBoneList = []; // 龙身bone数组
        this.longBonePosList = []; // 龙身世界坐标数组
        this.longBodyTarPosList = []; // 龙身目标世界坐标数组

        let spine = cc.find("pioneerSkill_long/s/long",this.bulletMoveNode).getComponent(sp.Skeleton);
        spine.updateWorldTransform();
        let bone = spine.findBone(startStr);
        this.longBodyBoneList.push(bone);


        let pos = cc.v2(bone.x,bone.y);
        let worldPos = this.node.convertToWorldSpaceAR(pos);
        this.longBonePosList.push(worldPos);

        // aft.Logger.error("初始化bone身体世界坐标系数组");

        for(let i = 'b'.charCodeAt(0);i <= 'o'.charCodeAt(0); i++){
            let bone = spine.findBone(startStr+String.fromCharCode(i));
            this.longBodyBoneList.push(bone);

            let pos = cc.v2(bone.x,bone.y);
            let worldPos = this.node.convertToWorldSpaceAR(pos);
            this.longBonePosList.push(worldPos);

        }

        let pos1 = this.longBonePosList[0];
        let pos2 = this.longBonePosList[1];
        this.longBodySectionLength = aft.Utils.getDistance(pos1,pos2);

        this.longBodyTarPosList = [];
        this.longBodyTarPosList.push(null);

        for(let i = 0 ;i < this.longBonePosList.length; i++){
            let tarPos = this.longBonePosList[i];
            this.longBodyTarPosList.push(cc.v2(tarPos.x ,tarPos.y));
        }

        // aft.Logger.error("龙每节的长度" + this.longBodySectionLength);
    }

    // aft.Logger.error("世界坐标" + this.node.convertToWorldSpaceAR(cc.v2(0,0)));



    // if(!this.curUpdateDegree){
    //     this.curUpdateDegree = 12;
    // }
    // if(!this.tarObj || !this.tarObj.isAlive()){
    //     this.changeTrackTarget();
    //     return;
    // }
    //
    // let curPos = this.node.getPosition();
    // let tarPos = this.tarObj.getShootTarPos(0);
    // let tarDegree = aft.Utils.getDegree(curPos, tarPos);
    //
    // let degree1 = this.curTrackDegree;
    // let degree2 = tarDegree;
    // let degreeDistance = aft.Utils.getDegreeDistance(degree1, degree2);
    //
    // let maxDifference = 3;
    //
    // // 正常判断 根据角度大小 判断方向
    // if(degreeDistance == Math.abs(degree1 - degree2)){
    //
    // }
    // // 说明实际夹角小 但0-359 两个数值差距比较大
    // else{
    //     if(degree1 > 180){
    //         degree1 -= 360;
    //     }
    //     if(degree2 > 180){
    //         degree2 -= 360;
    //     }
    // }
    // if(degree1 > degree2){
    //     degree1 -= this.curUpdateDegree;
    //     if(degree1 < (degree2 - maxDifference)){
    //         degree1 = degree2 - maxDifference;
    //     }
    // }else{
    //     degree1 += this.curUpdateDegree;
    //     if(degree1 > (degree2 + maxDifference)){
    //         degree1 = degree2 + maxDifference;
    //     }
    // }
    // this.curTrackDegree = degree1;
    // if(this.curTrackDegree < 0){
    //     this.curTrackDegree += 360;
    // }
    //
    // let offset = aft.Utils.getOffsetByRotationAndDistance(this.curTrackDegree, this.speed / 60);
    // let nextPos = cc.v2(curPos.x + offset.x, curPos.y + offset.y);
    // this.node.setPosition(nextPos);
    //
    // if(aft.Utils.getDistance(nextPos, tarPos) < 10){
    //     this.changeTrackTarget();
    // }



    // aft.Logger.error("测试计算是否错误");
    // 龙测试代码

    if(!this.curUpdateDegree){
        this.curUpdateDegree = 12;
    }
    if(!this.tarObj || !this.tarObj.isAlive()){
        this.changeTrackTarget();
        return;
    }

    let curPos = this.node.getPosition();
    let tarPos = this.tarObj.getShootTarPos(0);
    let tarDegree = aft.Utils.getDegree(curPos, tarPos);

    let degree1 = this.curTrackDegree;
    let degree2 = tarDegree;
    let degreeDistance = aft.Utils.getDegreeDistance(degree1, degree2);

    let maxDifference = 3;

    // 正常判断 根据角度大小 判断方向
    if(degreeDistance == Math.abs(degree1 - degree2)){

    }
    // 说明实际夹角小 但0-359 两个数值差距比较大
    else{
        if(degree1 > 180){
            degree1 -= 360;
        }
        if(degree2 > 180){
            degree2 -= 360;
        }
    }
    if(degree1 > degree2){
        degree1 -= this.curUpdateDegree;
        if(degree1 < (degree2 - maxDifference)){
            degree1 = degree2 - maxDifference;
        }
    }else{
        degree1 += this.curUpdateDegree;
        if(degree1 > (degree2 + maxDifference)){
            degree1 = degree2 + maxDifference;
        }
    }
    this.curTrackDegree = degree1;
    if(this.curTrackDegree < 0){
        this.curTrackDegree += 360;
    }

    let isUpdateLongTarPosList = false;
    let distance = this.speed * 2 / 60;
    if(this.longBodyMoveDistance + distance >= this.longBodySectionLength ){
        distance = this.longBodySectionLength - this.longBodyMoveDistance;
        this.longBodyMoveDistance = 0;
        isUpdateLongTarPosList = true;
    }else{
        this.longBodyMoveDistance += distance;
    }

    let nodeOffset = aft.Utils.getOffsetByRotationAndDistance(this.curTrackDegree, distance / 2);
    let nextPos = cc.v2(curPos.x + nodeOffset.x, curPos.y + nodeOffset.y);
    this.node.setPosition(nextPos);

    if(aft.Utils.getDistance(nextPos, tarPos) < 10){
        this.changeTrackTarget();
    }

    let testPos = 0;
    let frontPos = this.node.convertToWorldSpaceAR(cc.v2(0,0));
    this.longBodyTarPosList[0] = frontPos;

    // aft.Logger.error("子弹根节点世界坐标" + frontPos);

    for(let i = 0; i < this.longBonePosList.length; i++){
        frontPos = this.longBodyTarPosList[i];
        let curPos = this.longBonePosList[i];

        // aft.Logger.error("计算坐标"+i);
        // aft.Logger.error("frontPos"+frontPos);
        // aft.Logger.error("curPos"+curPos);
        // aft.Logger.error("testPos"+testPos);

        curPos.x = curPos.x - nodeOffset.x;
        curPos.y = curPos.y - nodeOffset.y;

        frontPos.x = frontPos.x - nodeOffset.x;
        frontPos.y = frontPos.y - nodeOffset.y;

        let tempPos = cc.v2(curPos.x,curPos.y);

        let degree = aft.Utils.getDegree(curPos, frontPos);


        let offset = aft.Utils.getOffsetByRotationAndDistance(degree, distance);
        let nextPos = cc.v2(curPos.x + offset.x, curPos.y + offset.y);
        this.longBonePosList[i] = nextPos;


        let bone = this.longBodyBoneList[i];
        bone.x = this.node.convertToNodeSpaceAR(nextPos).x;
        bone.y = this.node.convertToNodeSpaceAR(nextPos).y;

        // aft.Logger.error(i + "计算相对坐标" + this.node.convertToNodeSpaceAR(nextPos));
        // aft.Logger.error(i + "真实相对坐标" + bone.x + "," + bone.y);
        // aft.Logger.error(i + "世界坐标" + curPos);

        // frontPos = tempPos;
        testPos = tempPos;
    }

    let newPos = this.node.convertToWorldSpaceAR(cc.v2(0,0));
    for(let i = 0; i < this.longBonePosList.length - 1; i++){
        let curPos = this.longBonePosList[i];

        let tempPos = cc.v2(curPos.x,curPos.y);

        let nextPos = this.longBonePosList[i+1];
        let degree1 = aft.Utils.getDegree(curPos, newPos);
        let degree2 = aft.Utils.getDegree(nextPos, curPos);
        let worldDegree = (degree1 + degree2) / 2  % 360 ;

        if(Math.abs(degree1 - degree2) >= 180){
            worldDegree = (worldDegree + 180) % 360;
        }

        if(i === 0){
            worldDegree = this.curTrackDegree;
        }

        let localDegree = (180 + worldDegree) % 360;

        aft.Logger.error("degree1 :"+degree1);
        aft.Logger.error("degree2 :"+degree2);
        aft.Logger.error("worldDegree :"+worldDegree);
        aft.Logger.error("localDegree :"+localDegree);

        let bone = this.longBodyBoneList[i];
        bone.rotation = localDegree;

        // aft.Logger.error("localDegree :"+localDegree);

        newPos = tempPos;
    }

    if(isUpdateLongTarPosList){
        this.longBodyTarPosList = [];
        this.longBodyTarPosList.push(null);

        for(let i = 0 ;i < this.longBonePosList.length; i++){
            let tarPos = this.longBonePosList[i];
            this.longBodyTarPosList.push(cc.v2(tarPos.x ,tarPos.y));
        }
    }

}