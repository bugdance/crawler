/**
 * 每次约19个金币左右
 */

// const perVideoWatchTime=8//每隔视频观看10秒
const halfDeviceHeight=device.height/2
const halfDeviceWidth=device.width/2
const videoSwipeDistance=halfDeviceHeight-100//视频下滑的长度 px
// test()
onlyRun()
//只允许本脚本时，将上行解除注释0
function onlyRun(){
    auto();
    console.show()
    log("开始抖音极速版")
    let totalTime=2*60*60 //刷2小时
    run(totalTime)
}

var douyin = {};
douyin.main = function (totalTime) {    
    run(totalTime)
  };

function test(){
    auto();
    console.show()
    launchApp()
    watchAd()
    exit();

} 
function run(totalTime){
    launchApp()
    let watchTime = 0;
    let watchCount = 0;
    while(totalTime > watchTime) {
    
        var start = new Date().getTime();
        var sleepTime = 7 + random(-2,2)
        

        sleep(sleepTime * 1000);
        // 点击头像
        if (id("awr").findOne(500)) {    
            id("awr").click();

            sleep(sleepTime * 1000);
            // 等待视频出现
            if (id("jw").findOne(500)) {
                // 点击粉丝
                if (text("粉丝").findOne(500)) {
                    text("粉丝").click();
                    // id("a_q").click();

                    sleep(sleepTime * 1000);
                    // 视频还在，没进去粉丝列表
                    if (id("jw").findOne(500)) {
                        back();
                    // 粉丝出现, 退俩级
                    } else {
                        back();
                        sleep(2000);
                        back();
                    }
                // 粉丝按钮没出现
                } else {
                    back();
                }

            // 视频没出现
            } else {
                back();
            }
        }

        sleep(1000);
        likeAndfollow(15)
        sleep(3000);

        var end = new Date().getTime();
        waitTime = (end - start) / 1000
        singleTime = waitTime.toFixed(2);
        log("本条视频观看时长"+singleTime+"秒")

        watchTime += waitTime
        sumTime = watchTime.toFixed(2);
        watchCount++
        log("已观看："+sumTime+"秒|"+watchCount+"次")
        swipeVideo(watchCount)
    }
}

function launchApp(){
    let isLauchApp=false
    while(!isLauchApp){
        log("尝试启动")
        // launchPackage("com.ss.android.ugc.aweme.lite")
        launchPackage("com.ss.android.ugc.aweme")
        sleep(5000)
        isLauchApp=id("com.ss.android.ugc.aweme:id/awr").findOnce()
    }
    let mesbox=id("com.ss.android.ugc.aweme:id/al3").findOnce()
    if(mesbox){
        mesbox.click()
    }
    log("已启动")

}
//swipeCount，累计尝试滑动视频的次数
function swipeVideo(swipeCount){
    if(swipeCount%23==0){
        //  23的倍数上滑
    swipeVideoIndexDirection("up")
    }else {
        //下滑
    swipeVideoIndexDirection("down")
    }

   
}
/**
 * 指定概率（%），根据概率是否执行双击喜欢操作，
 * 输入的数据不包含…%，如输入30表示30%
 * */
function likeAndfollow(chance){
    let isLike=random(0,100)
    if(isLike<=chance){
        click(halfDeviceWidth,halfDeviceHeight)
        sleep(50)
        click(halfDeviceWidth,halfDeviceHeight)
        log("双击喜欢")
    }

}

function runOver(){
    home()
}

function swipeVideoIndexDirection(direction,swipeDelay){
    let offset=random(0,100)
    if(!swipeDelay){swipeDelay=30}
    if(direction=="up"){
        swipe(halfDeviceWidth+random(0,100), halfDeviceHeight-offset, 
        halfDeviceWidth+random(-50,50), halfDeviceHeight+offset+(videoSwipeDistance/2), swipeDelay);
    }else if(direction=="down"){
        swipe(halfDeviceWidth-random(0,100), halfDeviceHeight+offset+(videoSwipeDistance/2), 
        halfDeviceWidth+random(-50,50), halfDeviceHeight-offset-(videoSwipeDistance/2), swipeDelay);
    }
}