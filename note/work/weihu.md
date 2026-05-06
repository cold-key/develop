1. 切换到db_client
    su db_client
    pwd: beavergame

2. 切换到发布窗口
   ta deploy

3. 使用vim打开client_config目录下的对应配置文件进行修改，一般在右边窗格进行操作

    vim client_config_native.py
    vim client_config_native_new_encrypt.py

    修改入口开启
    isMain
    True  为入口关闭状态
    False 为入口开启状态

    查看diff
    git diff client_config_native.py
    git diff client_config_native_new_encrypt.py

4. 生成配置
    python gen_config.py dbpro
    python gen_config.py dbpro -isNewEncrypt

5. 查看当前修改是否生成成功

   查看diff
   git diff output/config/dbpro/db_10022/config.json   #只看一个渠道就行了

6. 把对应的配置同步到cdn

    ./rsync_config.sh
    ./rsync_new_encrypt_config.sh

7. 开入口时同时修改版本号和开入口


