# Living Manual 2022 In Shanghai
![python >= 3.7](https://img.shields.io/badge/python-%3E%3D%203.7-brightgreen)
![sqlite](https://img.shields.io/badge/-sqlite-brightgreen)
![selenium](https://img.shields.io/badge/-selenium-brightgreen)
![jupyter lab](https://img.shields.io/badge/jupyter-lab-brightgreen)
![scrapy](https://img.shields.io/badge/-scrapy-brightgreen)

## 初始化

- 安装**python**库依赖
```shell
pip install -r requirmetns.txt
```

- 初始化数据路
```shell
python service.py scheme update -p '{"db":"living_vendor"}'
python service.py scheme update -p '{"db":"living_map"}'
```

## 生成页面

- 采集居住地链接
```shell
scrapy crawl resident-link-spider
```

- 采集居住地信息
```shell
scrapy crawl resident-spider
```

- 采集居住地地理坐标
```shell
scrapy crawl resident-coordinate-spider
```

- 生成**html**页面
```shell
python main.py
```

