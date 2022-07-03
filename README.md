# Dingtalk_Notify
HomeAssistant 钉钉应用消息推送

## 官方文档

批量发送单聊消息（前期配置步骤） \
https://open.dingtalk.com/document/group/chatbots-send-one-on-one-chat-messages-in-batches


调试模式下，提示机器人不存在，发布后才能正常发送消息。


## 安装

* 将 custom_component 文件夹中的内容拷贝至自己的相应目录

或者
* 将此 repo ([https://github.com/dscao/dingtalk_notify](https://github.com/dscao/dingtalk_notify)) 添加到 [HACS](https://hacs.xyz/)，然后添加“Dingtalk Notify”

## 配置
```yaml
notify:
  - platform: dingtalk_notify
    name: dingtalk        # 实体ID  比如这个出来就是notify.dingtalk
    appkey:               # 这个是钉钉应用里面新建应用的应用AppKey
    appsecret:            # 这个是钉钉应用里面新建应用的应用AppSecret
    touser: 'userid1'     # 默认接收者，用户的userid，每次最多传20个。： 如：userid1|userid2|userid3，在钉钉管理后台——内部通讯录管理——成员详情的最上显示“员工UserID”。
    https_proxies: username:password@XXX.XXX.XXX.XXX:8080   #支持https的代理服务器地址（可选项）初步测试公共代理可以使用
    resource: http://XXX.XXX.XXX.XXX:1880/endpoint   #选配服务器中转地址（可选项），默认为： https://api.dingtalk.com ,可设置为 http:xxx.xxx.com:1880/endpoint 或 http:xxx.xxx.com:1880（具体根据node-red的设置）
    resource_username: username  #选配服务器中转基本认证用户 如 node-red中的http_node username （可选项）
    resource_password: password  #选配服务器中转地址认证密码 如 node-red中的http_node password （可选项）
```

## 使用
```yaml
service: notify.dingtalk  #调用服务
data:
  message: 消息内容
  target: 接收者userid1|接收者userid2|接收者userid3

service: notify.dingtalk  #调用服务
data:
  message: 消息内容
  target:
    - 接收者ID1
    - 接收者ID2
    - 接收者ID3


service: notify.dingtalk
data:
  message: 发送纯文本消息，当前时间：{{now().strftime('%Y-%m-%d %H:%M:%S')}}


service: notify.dingtalk
data:
  message: 发送带标题和分隔线的纯文本消息
  title: 这是标题


service: notify.dingtalk
data:
  message: 发送带内容的链接卡片
  title: 这是标题
  data:
    type: sampleActionCard
    url: 'http://www.sogou.com'
   
   
service: notify.dingtalk
data:
  message: "#### 杭州天气 @150XXXXXXXX \n > 9度，西北风1级，空气良89，相对温度73%\n > ![screenshot](https://img.alicdn.com/tfs/TB1NwmBEL9TBuNjy1zbXXXpepXa-2400-1218.png)\n > ###### 10点20分发布 [天气](https://www.dingtalk.com) \n"
  title: 这是标题
  data:
    type: sampleMarkdown   
   
service: notify.dingtalk
data:
  message: 发送图片
  title: 这是标题
  data:
    type: sampleImageMsg
    picurl: 'https://bbs.hassbian.com/static/image/common/logo.png'


service: notify.dingtalk
data:
  message: 发送带标题、内容和缩略图的链接卡片，上传本地图片（代理及中转模式下不支持）。
  title: 这是标题
  data:
    type: sampleLink
    url: 'http://www.sogou.com'
    imagepath: /config/www/1.jpg

```

## 示例：

```yaml
service: notify.dingtalk
data:
  title: 小汽车当前位置：{{states('sensor.mycar_loc')}}
  message: >-
    小汽车当前位置：{{states('sensor.mycar_loc')}} {{"\n\n"}}
    状态刷新时间：{{"\n\n"}}{{state_attr('device_tracker.gddr_gooddriver',
    'querytime')}} {{"\n\n"}}
    车辆状态：{{state_attr('device_tracker.gddr_gooddriver', 'status')}} {{"\n\n"}}
    到达位置时间：{{"\n\n"}}{{state_attr('device_tracker.gddr_gooddriver',
    'updatetime')}}
    {{"\n\n"}}停车时长：{{state_attr('device_tracker.gddr_gooddriver',
    'parking_time')}}{{"\n\n"}}当前速度：{{state_attr('device_tracker.gddr_gooddriver',
    'speed') |round(1)
    }}km/h{{"\n\n"}}[查看地图](https://uri.amap.com/marker?position={{state_attr('device_tracker.gddr_gooddriver',
    'longitude')+0.00555}},{{state_attr('device_tracker.gddr_gooddriver',
    'latitude')-0.00240}})![https://restapi.amap.com/v3/staticmap?zoom=14&size=1024*512&markers=large,,A:{{state_attr('device_tracker.gddr_gooddriver',
    'longitude')+0.00555}},{{state_attr('device_tracker.gddr_gooddriver',
    'latitude')-0.00240}}&key=819cxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx](https://restapi.amap.com/v3/staticmap?zoom=14&size=1024*512&markers=large,,A:{{state_attr('device_tracker.gddr_gooddriver',
    'longitude')+0.00555}},{{state_attr('device_tracker.gddr_gooddriver',
    'latitude')-0.00240}}&key=819cxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
  data:
    type: sampleMarkdown
```
