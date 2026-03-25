"""Waver 项目测试脚本"""

import sys
import os
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """测试模块导入"""
    print("=" * 60)
    print("测试 1: 模块导入")
    print("=" * 60)
    
    try:
        print("[正在导入] waver.constants...", end=" ")
        from waver import constants
        print("✓ 成功")
        print(f"  - 版本: {constants.VERSION}")
        print(f"  - 超时: {constants.TIMEOUT_SECONDS}s")
        print(f"  - 最大输出: {constants.MAX_OUTPUT_LENGTH} 字节")
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False

    try:
        print("[正在导入] waver.config...", end=" ")
        from waver import config
        print("✓ 成功")
        print(f"  - 配置目录: {config.CONFIG_DIR}")
        print(f"  - 配置文件: {config.CONFIG_FILE}")
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False

    try:
        print("[正在导入] waver.providers...", end=" ")
        from waver import providers
        print("✓ 成功")
        provider_list = providers.list_providers()
        print(f"  - 支持的提供商: {len(provider_list)} 个")
        for name in list(provider_list.keys())[:3]:
            print(f"    • {name}")
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False

    try:
        print("[正在导入] waver.executor...", end=" ")
        from waver import executor
        print("✓ 成功")
        tools = executor.get_tools()
        print(f"  - 可用工具: {len(tools)} 个")
        for tool in tools:
            print(f"    • {tool['function']['name']}")
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False

    try:
        print("[正在导入] waver.ui...", end=" ")
        from waver import ui
        print("✓ 成功")
        print(f"  - 控制台宽度: {ui.console.width}")
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False

    print()
    return True


def test_config():
    """测试配置管理"""
    print("=" * 60)
    print("测试 2: 配置管理")
    print("=" * 60)
    
    try:
        from waver import config
        
        print("[测试] 配置目录存在...", end=" ")
        config.ensure_config_dir()
        print("✓")
        
        print("[测试] 获取默认提供商...", end=" ")
        default_provider = config.get_default_provider()
        print(f"✓ ({default_provider})")
        
        print("[测试] 获取所有密钥...", end=" ")
        all_keys = config.get_all_keys()
        print(f"✓ ({len(all_keys)} 个)")
        
        print("[测试] 配置缓存...", end=" ")
        cfg = config.load_config()
        print(f"✓ (缓存大小: {len(cfg)} 项)")
        
        print()
        return True
    except Exception as e:
        print(f"✗ 失败: {e}")
        print()
        return False


def test_providers():
    """测试提供商配置"""
    print("=" * 60)
    print("测试 3: 提供商配置")
    print("=" * 60)
    
    try:
        from waver import providers
        
        provider_list = providers.list_providers()
        
        print(f"[测试] 已注册提供商: {len(provider_list)} 个")
        for name, p in list(provider_list.items())[:3]:
            default_model = providers.get_default_model(name)
            print(f"  • {name}")
            print(f"    - 默认模型: {default_model}")
            print(f"    - 支持流式: {p.get('supports_stream', False)}")
            print(f"    - 支持工具: {p.get('supports_tools', False)}")
        
        print()
        return True
    except Exception as e:
        print(f"✗ 失败: {e}")
        print()
        return False


def test_executor():
    """测试工具执行器"""
    print("=" * 60)
    print("测试 4: 工具执行器")
    print("=" * 60)
    
    try:
        from waver import executor
        from pathlib import Path
        import tempfile
        
        tools = executor.get_tools()
        print(f"[测试] 工具列表: {len(tools)} 个工具")
        for tool in tools:
            print(f"  • {tool['function']['name']}")
        
        # 测试文件操作
        print("\n[测试] 文件操作")
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            
            print(f"  写入测试文件...", end=" ")
            result = executor.write_file_tool(str(test_file), "Hello, Waver!")
            if "File written" in result:
                print("✓")
            else:
                print(f"✗ ({result})")
            
            print(f"  读取测试文件...", end=" ")
            result = executor.read_file_tool(str(test_file))
            if "Hello, Waver!" in result:
                print("✓")
            else:
                print(f"✗ ({result})")
        
        print()
        return True
    except Exception as e:
        print(f"✗ 失败: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def test_ui():
    """测试UI显示"""
    print("=" * 60)
    print("测试 5: UI 显示")
    print("=" * 60)
    
    try:
        from waver import ui
        
        print("[测试] 显示成功消息")
        ui.show_success("这是一条成功消息")
        
        print("\n[测试] 显示信息消息")
        ui.show_info("这是一条信息消息")
        
        print("\n[测试] 显示错误消息")
        ui.show_error("这是一条错误消息")
        
        print("\n")
        return True
    except Exception as e:
        print(f"✗ 失败: {e}")
        print()
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "WAVER 项目测试套件" + " " * 24 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = []
    
    results.append(("模块导入", test_imports()))
    results.append(("配置管理", test_config()))
    results.append(("提供商配置", test_providers()))
    results.append(("工具执行器", test_executor()))
    results.append(("UI 显示", test_ui()))
    
    # 总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有测试都通过了！")
        return True
    else:
        print(f"\n⚠️  还有 {total - passed} 个测试失败")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
