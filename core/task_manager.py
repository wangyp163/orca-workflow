"""
简洁的任务管理器 - 负责创建和执行计算任务工作流
"""
import sys
import importlib
from pathlib import Path
from typing import Any, Optional

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_task(args: Any) -> Optional[Any]:
    """执行指定任务"""
    try:
        workflow = create_workflow(args.task, args.input, args.ncores)
        method = getattr(workflow, f"{args.process}_{args.task}")
        return method()
    except Exception as e:
        print(f"任务执行失败: {e}")
        return None

def create_workflow(task_type: str, input_file: str, ncores: int = 1) -> Any:
    """创建工作流实例
    
    命名规则说明：
    - task目录下的.py文件必须命名为对应的任务类型（如sp.py、opt.py）
    - 每个.py文件中必须包含一个名为"{任务类型}Workflow"的类
    - 例如：sp.py中必须定义spWorkflow类，opt.py中必须定义optWorkflow类
    """
    module = importlib.import_module(f"task.{task_type}")
    workflow_class = getattr(module, f"{task_type}Workflow")
    
    workflow = workflow_class(
        basename=Path(input_file).stem,
        working_dir=Path(task_type)
    )
    
    workflow.setup_structure(xyz_file=input_file)
    workflow.setup_calculator(ncores=ncores)
    
    return workflow

def get_workflow(task_type: str, input_file: str, ncores: int = 1) -> Any:
    """获取工作流实例（兼容接口）"""
    return create_workflow(task_type, input_file, ncores)
