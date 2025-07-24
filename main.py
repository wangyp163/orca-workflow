#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from ntpath import basename
import sys
from pathlib import Path

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
    parser.add_argument("--task", choices=['sp', 'opt', 'tddft'], required=True, help="任务类型: sp (单点计算), opt (结构优化), tddft (TDDFT计算)")
    
    # Phase 类型参数
    parser.add_argument("--phase", choices=['pre', 'post'], required=True, help="阶段类型: pre (预处理), post (后处理)")
    
    # 结构参数
    parser.add_argument("-i", "--input", required=True, help="输入文件路径")
    
    # 核数参数
    parser.add_argument("--ncores", type=int, default=32, help="设置计算所用的核数，默认为32")
    
    args = parser.parse_args(argv)
    return args 

import importlib

class WorkflowFactory:
    @staticmethod
    def get_workflow(task_type, args):
        try:
            # 动态导入模块
            module = importlib.import_module(f"task.{task_type}")
            # 根据约定获取类名，例如 'SpWorkflow' 或 'OptWorkflow'
            class_name = f"{task_type}Workflow"
            workflow_class = getattr(module, class_name)
            
            # 实例化工作流类
            # basename 应该从 input_file 中获取，并传递给工作流的构造函数
            # working_dir 可以根据 task_type 设置
            workflow_instance = workflow_class(basename=Path(args.input).stem, working_dir=Path(task_type))
            
            # 在实例上调用 setup_structure 和 setup_calculator
            workflow_instance.setup_structure(xyz_file=args.input)
            workflow_instance.setup_calculator(ncores=args.ncores)
            
            return workflow_instance
        except (ImportError, AttributeError) as e:
            print(f"Error loading workflow for task type {task_type}: {e}")
            return None

def main(args):

    input_file = Path(args.input)
    if not input_file.exists():
        sys.exit(f"错误: 输入文件 '{input_file}' 不存在")

    task_type = args.task
    phase_type = args.phase
    
    # 精简命令映射
    action_map = {
        ('sp', 'pre'): lambda: WorkflowFactory.get_workflow('sp', args).sp_pre(),
        ('opt', 'pre'): lambda: WorkflowFactory.get_workflow('opt', args).optimize_structure(),
        ('sp', 'post'): lambda: print(f"执行 SP 后处理: {input_file}"),
        ('opt', 'post'): lambda: (WorkflowFactory.get_workflow('opt', args).check_output(), print("执行结构优化后处理")),
        ('tddft', 'pre'): lambda: (setup_workflow(WorkflowFactory.get_workflow('tddft', args), input_file, args.ncores), print(f"执行 TDDFT 前处理: {input_file}")),
        ('tddft', 'post'): lambda: print(f"执行 TDDFT 后处理: {input_file}")
    }

    action_map[(task_type, phase_type)]()

    print("程序执行完毕")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = parse_args()
    else:
        print("未输入参数，使用默认参数")
        default_args = ["--task", "sp", "--phase", "pre", "-i", "test_water.xyz"]
        args = parse_args(default_args)
    
    main(args)