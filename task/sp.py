from core.base_workflow import OPIWorkflow
import sys
from pathlib import Path
from opi.input.simple_keywords import *

class spWorkflow(OPIWorkflow):
    """
    专门用于结构优化的工作流类
    """
    def sp_pre(self, 
        method: str = None, basis_set: str = None) -> None:
    
        """
        设置 SP 的参数

        参数
        ----------
        method : str, optional
            优化使用的方法，默认为B3LYP
        basis_set : str, optional
            基组，默认为None
        additional_keywords : Union[str, List[str]], optional
            额外的关键字，可以是字符串或字符串列表，默认为None
        """
        if self.calc is None:
            raise ValueError("请先设置计算器")

        sk_list = [
            DispersionCorrection.D3, 
            AtomicCharge.NOPOP, 
            Scf.NOAUTOSTART, 
            Task.SP,
            BasisSet.DEF2_TZVP,
            Dft.B3LYP
        ]
        self.calc.input.add_simple_keywords(*sk_list)
        self.calc.write_input()

    def sp_post(self):
        self.calc.read_output()

if __name__ == "__main__":
    xyz_file = sys.argv[1] if len(sys.argv) > 1 else Path("test_water.xyz")
    workflow = spWorkflow(basename=f"{xyz_file.stem}", working_dir=Path("opt"))

    results = workflow.check_output()
    print(results)
