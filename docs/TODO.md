## node agent 
### key
### value
```
{
    "service": "node-agent",
    "version": "v1.0.0",
    "md5": "1234567890",
    "download_url": "http://sasa/asas/aa.tar.gz"
}
```

## application
### key
### value
```
{
    "service": "resource-manager"
    "version": "v1.0.0",
    "md5": "1234567890",
    "download_url": "http://45.76.247.122:9000/public/resource-manager.tar.gz",
}
```


#### chmod
python os.chmod 目录时，不穿透，即不具有-r的功能

### 待测试
healthcheck的script类型，因为consul启动的时候没有指定enable_script_checks配置项，导致现在script开关没有打开，这种类型的健康检查有待测试，其他类型的健康检查已经测试完成




### 20200628
健康检查发出通知

config
1. 日常修改
配置中心修改 --> consul/etcd修改 --> 通知redis --> config进程接收redis消息 --> 刷新本地config --> 重启服务

2. 升级
把配置打到包里 --> 正常升级流程 --> 升级完成后 center agent 修改consul/etcd 



content/venv/bin/python content/main.py --type node --conf content/config --name agent-node


### 20200720
logging.TimedRotatingFileHandler 有问题，暂时关闭，不轮转

