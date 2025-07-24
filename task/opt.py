from core.base_workflow import OPIWorkflow
import sys
from pathlib import Path

from opi.input.simple_keywords import *


class OptWorkflow(OPIWorkflow):
    """
    专门用于结构优化的工作流类
    """
    def _setup_optimization_parameters(self, 
        method: str = None, basis_set: str = None) -> None:
    
        """
        设置优化的参数

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
            Task.OPT,
            BasisSet.DEF2_TZVP,
            Dft.B3LYP
        ]
        self.calc.input.add_simple_keywords(*sk_list)
 
    def optimize_structure(self, 
        method: str = None, basis_set: str = None) -> None:
        
        self._setup_optimization_parameters(method, basis_set)
        self.calc.write_input()

if __name__ == "__main__":
    xyz_file = sys.argv[1] if len(sys.argv) > 1 else Path("test_water.xyz")
    workflow = OptWorkflow(basename=f"{xyz_file.stem}", working_dir=Path("opt"))
    # workflow.setup_structure(xyz_file=xyz_file)
    # workflow.setup_calculator(ncores=32)
    # workflow.optimize_structure()
    
    results = workflow.check_output()
    print(results)
