#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from ntpath import basename
import sys
from pathlib import Path
from core.task_manager import run_task


sys.path.insert(0, str(Path(__file__).parent))

#实例化基础workflow
def setup_workflow(workflow, input_file, ncores):
    #解析输入结构
    workflow.setup_structure(xyz_file=input_file)
    # 设置核数
    workflow.setup_calculator(ncores=ncores)

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="ORCA Workflow 主程序")
    
    # Task 类型参数
    parser.add_argument("-t", "--task", choices=['sp', 'opt', 'tddft'], required=True, help="任务类型: sp (单点计算), opt (结构优化), tddft (TDDFT计算)")

    
    parser.add_argument("-p", "--process", choices=['pre', 'post'], required=True, help="阶段类型: pre (预处理), post (后处理)")
    
    # 结构参数
    parser.add_argument("-i", "--input", required=True, help="输入文件路径")
    
    # 核数参数
    parser.add_argument("-n", "--ncores", type=int, default=32, help="设置计算所用的核数，默认为32")
    
    args = parser.parse_args(argv)
    return args 

def main(args):
    # 检查输入文件是否存在
    input_file = Path(args.input)
    if not input_file.exists():
        sys.exit(f"错误: 输入文件 '{input_file}' 不存在")

    task_type = args.task
    process_type = args.process
    #从core/task_manager.py获取action_map映射，根据任务类型和阶段类型获取对应的lambda函数
    result = run_task(args)
    

if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = parse_args()
    else:
        print("未输入参数，使用默认参数")
        default_args = ["-t", "sp", "-p", "pre", "-i", "test_water.xyz"]
        args = parse_args(default_args)
    
    main(args)