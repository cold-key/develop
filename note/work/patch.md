1. 切换到db_client
    su db_client
    pwd: beavergame

2. 切换到发布窗口
   ta deploy

3. 选定分支更新（大推服 dbpro , 海外服 dbglobal）
   ./rsync_patch_dbpro.sh
   ./rsync_new_encrypt_patch_dbpro.sh

   选择分支对应数字

   选择版本号，默认第一个，等待生成

4. 使用vim打开client_config目录下的对应配置文件进行修改，一般在右边窗格进行操作

    只修改版本号，默认加一
    vim client_config_native.py
    vim client_config_native_new_encrypt.py

    查看diff
    git diff client_config_native.py
    git diff client_config_native_new_encrypt.py

5. 生成配置
    python gen_config.py dbpro
    python gen_config.py dbpro -isNewEncrypt

6. 查看当前修改是否生成成功
   
   查看配置生成状态
   ./patch_new_encrypt_stats.sh
   ./patch_stats.sh

   查看diff
   git diff output/config/dbpro/db_10022/config.json   #只看一个渠道就行了
   
   添加至暂存区
   git add client_config/client_config_native.py output/config/dbpro/
   git add client_config/client_config_native_new_encrypt.py output/config_new_encrypt/dbpro/

   查看状态
   git status

   提交
   git commit -m "do"

   git push

7. 把对应的配置同步到cdn

    ./rsync_config.sh
    ./rsync_new_encrypt_config.sh


