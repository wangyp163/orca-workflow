from .utils import *
# OPI imports
from opi.core import Calculator
from opi.output.core import Output
from opi.input.simple_keywords import *
from opi.input.structures.structure import Structure
from opi.input.arbitrary_string import ArbitraryString, ArbitraryStringPos


class OPIWorkflow:
    """
    模块化的OPI工作流类，用于执行量子化学计算，包括结构优化和光谱计算等。
    """
    def __init__(self, basename: str, working_dir: Optional[Path] = None):
        """
        初始化工作流

        参数
        ----------
        basename : str
            计算的基本名称
        working_dir : Optional[Path], optional
            工作目录，默认为None
        """
        self.basename = basename
        self.working_dir = working_dir or Path.cwd()
        self.calc = None
        self.output = None
        self.structure = None

        # 确保工作目录存在
        self.working_dir.mkdir(parents=True, exist_ok=True)

    def setup_structure(self, xyz_file: Path) -> None:
        """
        设置分子结构

        参数
        ----------
        xyz_file : Path
            XYZ格式的分子结构文件路径
        """
        self.structure = Structure.from_xyz(xyz_file)

    def setup_calculator(self, ncores: int = 1) -> None:
        """
        设置计算器

        参数
        ----------
        ncores : int, optional
            计算使用的CPU核心数，默认为1
        """
        if self.structure is None:
            raise ValueError("请先设置分子结构")

        self.calc = Calculator(basename=self.basename, working_dir=self.working_dir)
        self.calc.structure = self.structure
        self.calc.input.ncores = ncores

    def _check_output(self) -> None:
        """
        检查计算输出是否正常终止和收敛
        """
        if not self.output.terminated_normally():
            raise RuntimeError(f"ORCA计算 '{self.basename}' 未正常终止")

        self.output.parse()

        # 检查SCF收敛
        if hasattr(self.output.results_properties, 'geometries') and self.output.results_properties.geometries:
            if hasattr(self.output.results_properties.geometries[0], 'single_point_data'):
                if not self.output.results_properties.geometries[0].single_point_data.converged:
                    raise RuntimeError(f"ORCA计算 '{self.basename}' 的SCF未收敛")
                print("SCF计算已收敛")

        # 检查优化收敛
        if hasattr(self.output.results_properties, 'optimization'):
            if not self.output.results_properties.optimization.converged:
                raise RuntimeError(f"结构优化 '{self.basename}' 未收敛")
            print("结构优化已收敛")

    def set_custom_parameters(self, parameters: str) -> None:
        """
        设置自定义参数

        参数
        ----------
        parameters : str
            要设置的参数，以空格分隔
        """
        if self.calc is None:
            raise ValueError("请先设置计算器")

        for param in parameters.split():
            self.calc.input.add_arbitrary_string(
                ArbitraryString(f"!{param}", pos=ArbitraryStringPos.TOP)
            )
    def check_output(self):

        from opi.output.grepper import recipes
        # > Check for proper termination of ORCA
        output = Output(basename=self.basename, working_dir=self.working_dir)
        status = output.terminated_normally()        
        if not status:
            # > ORCA did not terminate normally
            raise RuntimeError(f"ORCA计算 '{self.basename}' 未正常终止")
        else:
            # > ORCA did terminate normally so we can parse the output
            print(f"ORCA计算 '{self.basename}' 已正常终止")


        # if output.results_properties.geometries[0].single_point_data.converged:
        #     print("SCF CONVERGED")
        # else:
        #     raise RuntimeError("SCF DID NOT CONVERGE")
        
  
