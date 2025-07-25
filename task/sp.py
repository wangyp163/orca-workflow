import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.base_workflow import OPIWorkflow
from opi.input.simple_keywords import *

class spWorkflow(OPIWorkflow):
    """
    专门用于结构优化的工作流类
    """
    def pre_sp(self, 
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

    def post_sp(self):
        output = self.calc.get_output()
        if not output.terminated_normally():
            print(f"ORCA calculation failed, see output file: {output.get_outfile()}")
            sys.exit(1)
        # << END OF IF

        # > Parse JSON files
        output.parse()

        # 检查SCF收敛情况
        if output.results_properties.geometries[0].single_point_data.converged:
            print("SCF已收敛")
        else:
            print("SCF未收敛")
            sys.exit(1)

        print("单点能：")
        print(output.get_final_energy())
        # > is (for this calculation) equal to
        # print(output.results_properties.geometries[0].single_point_data.finalenergy)
        # > is (for this calculation) equal to
        # print(
        #     output.results_properties.geometries[0].energy[0].totalenergy[0][0]
        #     + output.results_properties.geometries[0].vdw_correction.vdw
        # )
