"""确保仓库根目录在 sys.path 中，使 pytest 能导入 agents 包。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
