from src.mcp.server import get_mcp

# 获取MCP实例
mcp = get_mcp()

if __name__ == "__main__":
    mcp.run()
    
# 命令行入口点函数
def serve_cli():
    mcp.run()