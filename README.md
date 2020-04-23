<font color=red>重要提醒：最新的部署文档请至`企业微信`-`腾讯乐享`-`知识库`查看。</font>

鉴于存在较大数据集的情况，仓库新增了部分文件，目前，仓库主要的文件结构如下：

```markdown
.
|-- Dockerfile
|-- deploy
|   |-- bigdataset
|   |   `-- deploy.yaml  
|   `-- normal
|       `-- deploy.yaml
`-- mnist
    |-- dataset
    |   `-- mnist.npz
    |-- mnist.py
    `-- requirements.txt
```

## 数据集较小

如果您的数据集较小（小于100M），可以直接push到代码仓库，那么，您可以在使用kubesphere构建流水线时，在流水线的最后一步，使用`deploy/normal/deploy.yaml`部署文件。

注意：此时mnist.py文件中读取数数据集是使用的相对目录：

```python
def load_mnist():
    #文件路径，相对路径
    path = r'dataset/mnist.npz'
    f = np.load(path)
    x_train, y_train = f['x_train'],f['y_train']
    x_test, y_test = f['x_test'],f['y_test']
    f.close()
    return (x_train, y_train), (x_test, y_test)
```

## 数据集较大

如果您的数据集较大，那么是不能push到代码仓库去的，当然，将数据集存放到云盘，让代码在容器中运行时在线下载数据集这种方式也是不可取的。

那么，可以解决此问题的一种方案是：**将数据集也制作成一个docker镜像**。

我们假设：现在代码仓库的数据集`dataset/mnist.npz`非常大，不能上传到仓库。那么我们可以在本地将其制作成一个镜像，然后，将其上传到私有镜像仓库harbor。操作示例如下：

**前提：**您有一台装有docker的服务器，如果没有，去阿里云或者腾讯云买一台就行了，学生很便宜，每月10元。

1. 将您的数据集上传到您自己的服务器上去

   ```markdown
   .
   ├── Dockerfile
   └── dataset
       └── mnist.npz
   ```

2. 制作镜像需要写一个Dockerfile

   ```markdown
   # 基础镜像
   FROM busybox:1.31
   # 将Dockerfile同级目录下的dataset复制到容器的/dataset目录下
   COPY ./dataset /dataset
   CMD ["sh"]
   
   ```

   > 说明：这个Dockerfile非常简单，就是将Dockerfile同级目录的数据集复制到容器的/dataset目录下。为了尽可能减少您的修改内容，降低可能发生错误的概率。我们在这里做一个约定：
   >
   > 1. Dockerfile中的第二步，将您的数据集复制到容器中的目录/dataset目录，容器目录`/dataset`请不要修改。而且您的代码读取数据集的目录也要修改。例如，我这里是这样的：
   >
   >    ```python
   >    def load_mnist():
   >        #文件路径，这里是容器中的绝对路径
   >        path = r'/dataset/mnist.npz'
   >        f = np.load(path)
   >        x_train, y_train = f['x_train'],f['y_train']
   >        x_test, y_test = f['x_test'],f['y_test']
   >        f.close()
   >        return (x_train, y_train), (x_test, y_test)
   >    ```

3. 制作镜像

   - 服务器上，在Dockerfile所在路径构建镜像

     ```markdown
     docker build -t hub.data.wust.edu.cn:30880/<1>/<2> .
     ```

     > 其中：
     >  - <1> ：是您的私有仓库名字
     >  - <2> ：您的数据集镜像的名字
     >  例如：我这里是这样的：
     >  `docker build -t hub.data.wust.edu.cn:30880/ygtao/ygtao-mnist-dataset:v1.0 .`

   - 登录harbor私有镜像仓库

     ```markdown
     docker login hub.data.wust.edu.cn:30880
     ```

     > 回车，按提示输入您的仓库的用户名和密码，如果登录成功，您会看到类似如下的信息：
     >
     > Username: ygtao-admin
     > Password: 
     > WARNING! Your password will be stored unencrypted in /root/.docker/config.json.
     > Configure a credential helper to remove this warning. See
     > https://docs.docker.com/engine/reference/commandline/login/#credentials-store
     >
     > Login Succeeded

   - 将您的镜像推送到harbor仓库

     ```markdown
     docker push hub.data.wust.edu.cn:30880/<1>/<2>
     ```

     > <1> <2>同上
     >
     > 例如：`docker push hub.data.wust.edu.cn:30880/ygtao/ygtao-mnist-dataset:v1.0`

   在`kubesphere`平台部署时，我们需要在`Devops`工程中，`添加参数`位置，添加 一个新的参数`DATASET_IMAGE`，值就是你在这里构建的镜像的名字，例如：我这里的值是`hub.data.wust.eud.cn:30880/ygtao/ygtao-mnist-dataset:v1.0`

   。此外，在流水线最后一步部署的时候，配置文件选择`deploy/bigdataset/deploy.yaml`文件。

   其他内容请参考企业微信群的部署文档。