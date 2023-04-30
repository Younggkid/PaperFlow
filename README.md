# PaperFlow
A useful tool to get conference papers and manage them in your computer.

## 如何使用？

下载：

```
git clone git@github.com:Younggkid/PaperFlow.git
```

安装所需环境依赖：

```
sudo pip3 install -r requirements.txt
```

建议python>=3.7

运行：

```
cd PaperFlow && python main.py
```

## 添加你的PDF阅读器

目前只支持福昕阅读器

设置->edit->修改目录为福昕阅读器.exe文件的路径->save

## 批量爬取会议论文

目前只支持每次爬取1年1个会议的论文，会议目前支持：{ccs,uss,sp,ndss,dsn,raid,imc,asiaccs,acsac,sigcomm}，年份支持2001-2022

自动导入->填写会议和年份->爬取

