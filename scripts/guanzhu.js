/**
 * 每次约19个金币左右
 */


// const perVideoWatchTime=8//每隔视频观看10秒
const halfDeviceHeight=device.height/2
const halfDeviceWidth=device.width/2
const videoSwipeDistance=halfDeviceHeight-100//视频下滑的长度 px

onlyRun()
//只允许本脚本时，将上行解除注释0
function onlyRun(){
    auto();
    console.show()
    log("开始抖音")

    // let totalTime=2*60*60 //刷2小时
    // run(totalTime)

    // 新写
    adolescentWindows()
    // batchScrape()
    // batchCancel()
    // searchAdd()
    searchScrape()
    // searchRepair()

}

function searchRepair(){

    // 调用
    // var res = http.get("http://192.168.11.55:18081/api/app/dy?size=10")
    var res = http.get("http://192.168.11.55:18081/api/api/account/")
    
    if (res.statusCode == 200) {
        var json = res.body.json()
        var arr = json
        log(arr.length)
    } else {
        log("请求失败")
    }

    // 启动app
    launchApp()

    var sleepTime = 5
    sleep(sleepTime * 1000);

    // 点击我的
    className("android.widget.FrameLayout").depth(9).drawingOrder(5).click()
    sleep(sleepTime * 1000);
    // 点击关注
    id("at_").findOne().click()
    sleep(sleepTime * 1000);
    // 点击关注的搜索
    id("ep").findOne().click()
    
    // 循环抖音ID列表
    for(j = 0,len=arr.length; j < len; j++) {
        if (arr[j]['aid'] == "") {
            continue
        }
            
        sleep(sleepTime * 1000);
        // 获取小搜索按钮焦点点击
        var scrollScope = id("b_j").findOne().bounds();
        click(scrollScope.left+(scrollScope.right-scrollScope.left)/2, 
            scrollScope.bottom-(scrollScope.bottom-scrollScope.top)/2)
        sleep(sleepTime * 1000);
        // 设置文字
        setText(arr[j]['aid'])
        sleep(sleepTime * 1000);
        // 点击搜索按钮
        id("com.ss.android.ugc.aweme.lite:id/dpv").text("搜索").findOne().click()
        sleep(sleepTime * 1000);

        // 截取抖音号比对
        if (id("dsn").drawingOrder(1).findOne(500)) {
            // dyText = id("dsn").drawingOrder(1).findOne().text()
            // 点击第一行
            className("android.widget.LinearLayout").depth(12).drawingOrder(1).click()
            sleep(sleepTime * 1000);

            back();
            sleep(sleepTime * 1000);
        } else {
            sleep(sleepTime * 1000);
        }

        // 点击×按钮清除文字
        if (id("qk").findOne(500)) {
            id("qk").findOne().click()
        }

        var res2 = http.get("http://192.168.11.55:18081/api/api/return?id=" + arr[j]['_id'])
    
        if (res2.statusCode == 200) {
            var json2 = res2.body.json()
        } else {
            log("请求失败")
        }

    }
}



function searchScrape(){

    // 调用
    // var res = http.get("http://192.168.11.55:18081/api/app/dy?size=10")
    var res = http.get("http://192.168.11.55:18081/api/get/app/3000/0")
    
    if (res.statusCode == 200) {
        var json = res.body.json()
        var arr = json
    } else {
        log("请求失败")
    }

    // 启动app
    launchApp()
    var sleepTime = 5
    sleep(sleepTime * 1000);

    // 点击我的
    className("android.widget.FrameLayout").depth(3).drawingOrder(19).click()
    sleep(sleepTime * 1000);
    // 点击关注
    id("ayx").findOne().click()
    sleep(sleepTime * 1000);
    // 点击关注的搜索
    id("er").findOne().click()
    
    // 循环抖音ID列表
    for(j = 0,len=arr.length; j < len; j++) {
        if (arr[j]['accountId'] == "") {
            continue
        }
            
        sleep(sleepTime * 1000);
        // 获取小搜索按钮焦点点击
        var scrollScope = id("ai1").findOne().bounds();
        click(scrollScope.left+(scrollScope.right-scrollScope.left)/2, 
            scrollScope.bottom-(scrollScope.bottom-scrollScope.top)/2)
        sleep(sleepTime * 1000);
        // 设置文字
        setText(arr[j]['accountId'])
        sleep(sleepTime * 1000);
        // 点击搜索按钮
        id("com.ss.android.ugc.aweme.lite:id/dy_").text("搜索").findOne().click()
        sleep(sleepTime * 1000);

        // 截取抖音号比对
        if (id("do0").depth(4).drawingOrder(3).findOne(500)) {
            dyText = id("do0").depth(4).drawingOrder(3).findOne().text()
            dyText = dyText.substring(4)
            if (dyText == arr[j]['accountId']) {
                // 点击第一行
                className("android.widget.LinearLayout").depth(3).drawingOrder(1).click()
                sleep(sleepTime * 1000);
                back();
                sleep(sleepTime * 1000);
                
                // // 点击商品
                // if (id("c4f").findOne(500)) {
                //     id("c4f").findOne().click();
                //     sleep(sleepTime * 1000);
                //     back();
                //     sleep(sleepTime * 1000);
                // } 

                // // 点击粉丝
                // if (id("ayt").findOne(500)) {
                //     id("ayt").findOne().click();
                //     // general_permission
                //     sleep(sleepTime * 1000);
                //     // 粉丝列表还在，没进去粉丝列表
                //     if (id("ayt").findOne(500)) {
                //         back();
                //         sleep(sleepTime * 1000);
                //     // 粉丝出现, 退俩级
                //     } else {
                //         back();
                //         sleep(sleepTime * 1000);
                //         back();
                //         sleep(sleepTime * 1000);
                //     }
                // // 粉丝按钮没出现
                // } else {
                //     back();
                //     sleep(sleepTime * 1000);
                // }
            } else {
                sleep(sleepTime * 1000);
            }

        } else {
            sleep(sleepTime * 1000);
        }

        // 点击×按钮清除文字
        if (id("qk").findOne(500)) {
            id("qk").findOne().click()
        }

        var res2 = http.get("http://192.168.11.55:18081/api/return/app?id=" + arr[j]['_id'])
    
        if (res2.statusCode == 200) {
            var json2 = res2.body.json()
        } else {
            log("请求失败")
        }

    }
}


function searchAdd(){

    // 启动app
    launchApp()

    //循环增加多少次
    for(i = 1; i < 200; i++) {

        // 点击首页观看视频
        className("android.widget.FrameLayout").depth(9).drawingOrder(1).click()
        sleep(random(3,7) * 1000);
        // 观看随机次
        for(s = 1; s < random(6, 10); s++) {
            swipeVideoIndexDirection("down")
            sleep(random(3,7) * 1000);
            likeAndfollow(25)
            sleep(random(3,7) * 1000);
        }
        
        // 点击我的开始增加
        className("android.widget.FrameLayout").depth(9).drawingOrder(5).click()
        sleep(random(3,7) * 1000);  
        // 调用接口数据
        // var res = http.get("http://192.168.11.55:18081/api/app/dy?size=10")
        var res = http.get("http://api.lolqq.xyz/api/app/dy?size=1")
        if (res.statusCode == 200) {
            var json = res.body.json()
            var arr = json.data
        } else {
            log("请求失败")
        }
        // 点击关注
        id("af0").click()
        sleep(random(5,9) * 1000);

        // 点击关注的搜索
        id("eg").click()
        sleep(random(3,7) * 1000); 

        // 循环抖音ID列表
        for(j = 0,len=arr.length; j < len; j++) {
    
            // 获取小搜索按钮焦点点击
            var scrollScope = id("aw9").findOne().bounds();
            click(scrollScope.left+(scrollScope.right-scrollScope.left)/2, 
                scrollScope.bottom-(scrollScope.bottom-scrollScope.top)/2)
            sleep(random(3,7) * 1000);
            // 设置文字
            setText(arr[j])
            sleep(random(5,9) * 1000);
            // 点击搜索按钮
            id("com.ss.android.ugc.aweme.lite:id/dd3").text("搜索").click()
            sleep(random(5,9) * 1000);
    
            // 截取抖音号比对
            if (id("d4x").drawingOrder(1).findOne(500)) {
                dyText = id("d4x").drawingOrder(1).findOne().text()
                dyText = dyText.substring(4)
                if (dyText == arr[j]) {
                    // 点击第一行
                    className("android.widget.LinearLayout").depth(12).drawingOrder(1).click()
                    sleep(random(5,9) * 1000);
                    // 点击商品
                    if (id("bgp").findOne(500)) {
                        id("bgp").findOne().click();
                        sleep(random(5,9) * 1000);
                        back();
                        sleep(random(3,7) * 1000);
                    } 
                    // 点击粉丝
                    if (id("aex").findOne(500)) {
                        id("aex").findOne().click();
                        sleep(random(5,9) * 1000);
                        // 粉丝出现, 退回点他的关注
                        if (!id("aik").findOne(500)) {
                            back();
                            sleep(random(5,9) * 1000);
                            // 点击他的关注
                            if (id("af0").findOne(500)) {
                                id("af0").findOne().click();
                                sleep(random(5,9) * 1000);
                                back();
                                sleep(random(3,7) * 1000);
                            } 
                        }
                    } 
                    // 点击关注
                    if (id("bxq").findOne(500)) {
                        gzText = id("bxq").findOne().text()
                        if (gzText == "关注") {
                            id("bxq").click()
                            sleep(random(3,7) * 1000);
                        }
                    }
                    // 回退
                    back()
                    sleep(random(3,7) * 1000);
                } 
            }
    
            // 点击×按钮清除文字
            if (id("qk").findOne(500)) {
                back()
                sleep(random(3,7) * 1000);

            }
    
        }

        isIndex = true
        while (isIndex) {
            // 回退
            back()
            sleep(random(3,7) * 1000);
            if (id("af0").findOne(500)) {
                isIndex = false
            }
        }

    }

    

}

function batchScrape(){
    // 启动app
    launchApp()
    var sleepTime = 7 + random(-2,2)
    sleep(sleepTime * 1000);
    // 点击我的
    className("android.widget.FrameLayout").depth(9).drawingOrder(5).click()
    sleep(sleepTime * 1000);
    // 记录总数点击关注
    var totalNum = id("aey").findOne().text()
    totalNum = parseInt(totalNum)
    log("发现总数"+totalNum)
    id("af0").findOne().click()
    // 记录坐标
    var scrollScope = className("android.widget.RelativeLayout").depth(11).drawingOrder(5).findOne().bounds();
    var startScroll = scrollScope.bottom
    var endScroll = scrollScope.bottom - (scrollScope.bottom - scrollScope.top) * 5

    let watchTime = 0;
    // 循环从1开始，id从0开始
    for (i = 1; i < totalNum + 1; i++) {
        var start = new Date().getTime();
        var sleepTime = 7 + random(-2,2)
        sleep(sleepTime * 1000);
        // 寻找目标并点击
        var target =  className("android.widget.RelativeLayout").depth(11).row(i - 1).findOne();
        if (target) {
            target.click()
            sleep(sleepTime * 1000);
            // 点击商品
            if (id("bgp").findOne(500)) {
                id("bgp").findOne().click();
                sleep(sleepTime * 1000);
                back();
                sleep(sleepTime * 1000);
            } 
            // 点击粉丝
            if (id("aex").findOne(500)) {
                id("aex").findOne().click();
                sleep(sleepTime * 1000);
                // 视频还在，没进去粉丝列表
                if (id("aik").findOne(500)) {
                    back();
                // 粉丝出现, 退俩级
                } else {
                    back();
                    sleep(sleepTime * 1000);
                    back();
                }
            // 粉丝按钮没出现
            } else {
                back();
            }

        }

        sleep(sleepTime * 1000);
        var end = new Date().getTime();
        waitTime = (end - start) / 1000
        singleTime = waitTime.toFixed(2);
        log("本次获取时长："+singleTime+"秒|"+"ID:"+(i-1))

        watchTime += waitTime
        sumTime = watchTime.toFixed(2);
        log("已观看："+sumTime+"秒|"+i+"次")

        // 如果是5的倍数就滑动，滑动5个
        if (i>0 && i%5==0) {
            swipe(halfDeviceWidth, startScroll, halfDeviceWidth, endScroll, 1688);
        }  
        // 如果是10的倍数就多休息会
        if (i>0 && i%10==0) {
            sleep(20 * 1000);
        }  
        
    }

}





// function batchScrape(){
//     // 启动app
//     launchApp()
//     sleep(random(3,7) * 1000);
//     // 点击我的
//     className("android.widget.FrameLayout").depth(9).drawingOrder(5).click()
//     sleep(random(3,7) * 1000);
//     // 记录总数点击关注
//     var totalNum = id("aey").findOne().text()
//     totalNum = parseInt(totalNum)
//     log("发现总数"+totalNum)
//     id("af0").findOne().click()
//     // 记录坐标
//     var scrollScope = className("android.widget.RelativeLayout").depth(11).drawingOrder(5).findOne().bounds();
//     var startScroll = scrollScope.bottom
//     var endScroll = scrollScope.bottom - (scrollScope.bottom - scrollScope.top) * 5

//     let watchTime = 0;
//     // 循环从1开始，id从0开始
//     for (i = 1; i < totalNum + 1; i++) {
//         var start = new Date().getTime();
//         sleep(random(5,9) * 1000);
//         // 寻找目标并点击
//         var target =  className("android.widget.RelativeLayout").depth(11).row(i - 1).findOne();
//         if (target) {
//             target.click()
//             sleep(random(5,9) * 1000);
//             // 点击商品
//             if (id("bgp").findOne(500)) {
//                 id("bgp").findOne().click();
//                 sleep(random(5,9) * 1000);
//                 back();
//                 sleep(random(3,7) * 1000);
//             } 
//             // 点击粉丝
//             if (id("aex").findOne(500)) {
//                 id("aex").findOne().click();
//                 sleep(random(5,9) * 1000);
//                 // 视频还在，没进去粉丝列表
//                 if (id("aik").findOne(500)) {
//                     back();
//                 // 粉丝出现, 退俩级
//                 } else {
//                     back();
//                     sleep(random(3,7) * 1000);
//                     back();
//                 }
//             // 粉丝按钮没出现
//             } else {
//                 back();
//             }


//             // // 点击粉丝
//             // if (id("aex").findOne(500)) {
//             //     id("aex").findOne().click();
//             //     sleep(random(5,9) * 1000);
//             //     // 粉丝出现, 退回点他的关注
//             //     if (!id("aik").findOne(500)) {
//             //         back();
//             //         sleep(random(3,7) * 1000);
//             //         back()
//             //         // // 点击他的关注
//             //         // if (id("af0").findOne(500)) {
//             //         //     id("af0").findOne().click();
//             //         //     sleep(random(5,9) * 1000);
//             //         //     back();
//             //         //     sleep(random(3,7) * 1000);
//             //         //     back();
//             //         // } else {
//             //         //     back();
//             //         // }
//             //     } else {
//             //         back();
//             //     }
//             // // 粉丝按钮没出现
//             // } else {
//             //     back();
//             // }

//         }

//         sleep(random(3,7) * 1000);
//         var end = new Date().getTime();
//         waitTime = (end - start) / 1000
//         singleTime = waitTime.toFixed(2);
//         log("本次获取时长："+singleTime+"秒|"+"ID:"+(i-1))

//         watchTime += waitTime
//         sumTime = watchTime.toFixed(2);
//         log("已观看："+sumTime+"秒|"+i+"次")

//         // 如果是5的倍数就滑动，滑动5个
//         if (i>0 && i%5==0) {
//             swipe(halfDeviceWidth, startScroll, halfDeviceWidth, endScroll, 1688);
//         }  
//         // // 如果是10的倍数就多休息会
//         // if (i>0 && i%10==0) {
//         //     sleep(20 * 1000);
//         // }  
        
//     }

// }

function batchCancel(){
    // 启动app
    launchApp()
    var sleepTime = 7 + random(-2,2)
    sleep(sleepTime * 1000);
    // 点击我的
    className("android.widget.FrameLayout").depth(9).drawingOrder(5).click()
    sleep(sleepTime * 1000);
    // 记录总数点击关注
    var totalNum = id("aey").findOne().text()
    totalNum = parseInt(totalNum)
    log("发现总数"+totalNum)
    id("af0").findOne().click()
    // 记录坐标
    var scrollScope = className("android.widget.RelativeLayout").depth(11).drawingOrder(5).findOne().bounds();
    var startScroll = scrollScope.bottom
    var endScroll = scrollScope.bottom - (scrollScope.bottom - scrollScope.top) * 5

    let watchTime = 0;
    // 循环从1开始，id从0开始
    for (i = 1; i < totalNum + 1; i++) {
        var start = new Date().getTime();
        var sleepTime = 10 + random(-2,2)
        sleep(sleepTime * 1000);
        // 寻找目标并点击
        var target =  className("android.widget.RelativeLayout").depth(11).row(i - 1).findOne();
        if (target) {
            target.click()
            sleep(sleepTime * 1000);
            // 点击取消
            if (id("aem").findOne()) {
                id("aem").findOne().click();
                // if (id("drp").findOne()) {
                //     log("a")
                //     id("drp").findOne().click();
                // }
                sleep(sleepTime * 1000);
            }
            back();
        }

        sleep(sleepTime * 1000);
        var end = new Date().getTime();
        waitTime = (end - start) / 1000
        singleTime = waitTime.toFixed(2);
        log(i)
        log("本次取消时长："+singleTime+"秒|"+"ID:"+(i-1))

        watchTime += waitTime
        sumTime = watchTime.toFixed(2);
        log("已取消："+sumTime+"秒|"+i+"次")

        // 如果是5的倍数就滑动，滑动5个
        if (i>0 && i%5==0) {
            swipe(halfDeviceWidth, startScroll, halfDeviceWidth, endScroll, 1688);
        }  
        // 如果是10的倍数就多休息会
        if (i>0 && i%10==0) {
            sleep(20 * 1000);
        }  
        
    }

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
        launchPackage("com.ss.android.ugc.aweme.lite")
        sleep(5000)
        // v.14.3.0
        isLauchApp=id("com.ss.android.ugc.aweme.lite:id/ed2").findOnce()
    }
    let mesbox=id("com.ss.android.ugc.aweme.lite:id/al3").findOnce()
    if(mesbox){
        mesbox.click()
    }
    log("已启动")

}
//swipeCount，累计尝试滑动视频的次数
function swipeVideo(swipeCount){
    if(swipeCount%3==0){
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

/**
 * 青少年窗口
 */
function adolescentWindows() {
    if (text("我知道了").exists()) {
        text("我知道了").findOnce().click();
    }
    if (text("知道了").exists()) {
        text("知道了").findOnce().click();
    }
}






