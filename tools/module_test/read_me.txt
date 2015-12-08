测试方法：
1.填写module_test.conf配置文件中平台信息
  ps：测试ds、cs模块时，test_service_type项可以为同类型模块以外外任意类型，测试其余模块该项需填control_server类型
  
2.执行命令：./module_test -t xxxx.conf

*详细使用方法请见doc/test/下《自动化测试框架使用说明》

测试脚本：
各模块的是脚本位于该文件同级的各个子目录下，目录名为模块名





