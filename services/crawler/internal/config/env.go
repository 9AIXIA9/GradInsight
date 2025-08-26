package config

import (
	"github.com/joho/godotenv"
	"github.com/zeromicro/go-zero/core/logx"
)

func LoadEnv(fileName string) {
	//加载根目录的 .env
	if err := godotenv.Overload(fileName); err != nil {
		logx.Severef("加载 .env 失败，错误: %v", err)
	}
	logx.Infof("成功加载%s环境文件", fileName)
}
