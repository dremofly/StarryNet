保存区块链应用中所需要的keys。这些keys文件的文件名为`B{数字}key.txt`。keys文件通过`relsharding-client`中的`KeyGenerator.java`来生成。例如，在`relsharding-client/dist`中运行
```
java -cp 'conf/:lib/*:apps/*' org.fisco.bcos.sdk.demo.rclient.KeyGenerator 50
```
其中50表示，生成50个private key文件。