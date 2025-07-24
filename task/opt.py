from os import PRIO_USER
import sys
from pathlib import Path

from opi.output.models.json.property.properties import energy
# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.base_workflow import OPIWorkflow
from opi.input.simple_keywords import *


class optWorkflow(OPIWorkflow):
    """
    专门用于结构优化的工作流类
    """
    def pre_opt(self, method: str = None, basis_set: str = None) -> None:
        """
        准备结构优化计算
        
        设置优化参数并写入输入文件
        
        参数
        ----------
        method : str, optional
            优化使用的方法，默认为B3LYP
        basis_set : str, optional
            基组，默认为None
        """
        if self.calc is None:
            raise ValueError("请先设置计算器")

        # 设置优化参数
        sk_list = [
            DispersionCorrection.D3, 
            AtomicCharge.NOPOP, 
            Scf.NOAUTOSTART, 
            Task.OPT,
            BasisSet.DEF2_TZVP,
            Dft.B3LYP
        ]
        self.calc.input.add_simple_keywords(*sk_list)
        
        # 写入输入文件
        self.calc.write_input()

    def post_opt(self) -> None:
        """
        后处理：检查优化计算输出是否正常终止和收敛
        
        包括：
        - 检查计算是否正常完成
        - 验证SCF收敛
        - 验证几何优化收敛
        - 输出轨迹信息
        - 保存最终优化结构
        """
        output = self.calc.get_output()
        if not output.terminated_normally():
            print(f"ORCA计算失败，请查看输出文件: {output.get_outfile()}")
            sys.exit(1)
        # << 结束条件判断

        # > 解析JSON文件
        output.parse()

        # > 验证SCF收敛
        if not output.scf_converged():
            print(f"ORCA SCF未能收敛，请查看输出文件: {output.get_outfile()}")
            sys.exit(1)

        # > 验证几何优化收敛
        if not output.geometry_optimization_converged():
            print(f"ORCA几何优化未能收敛，请查看输出文件: {output.get_outfile()}")
            sys.exit(1)

        ngeoms = len(output.results_properties.geometries)
        print("构型数量")
        print(ngeoms)
        print("最终单点能")
        print(output.results_properties.geometries[-1].single_point_data.finalenergy)
        print("构型优化过程的SCF能量")
        # > 几何构型索引从1到*ngeom*
        for igeom in range(0, ngeoms):
            print(
                f"{igeom})", output.results_properties.geometries[igeom].single_point_data.finalenergy
            )
        print("轨迹上的Mulliken电荷")
        # > 几何构型索引从1到*ngeom*
        for igeom in range(0, ngeoms):
            try:
                charges = (
                    output.results_properties.geometries[igeom]
                    .mulliken_population_analysis[0]
                    .atomiccharges
                )
            except TypeError:
                charges = "无数据，未计算Mulliken电荷"
            print(f"{igeom})", charges)

        # > 现在输出最终优化结构为xyz文件格式
        optimized = output.get_structure()
        print("最终优化结构:")
        print(optimized.to_xyz_block())
        
        # > 绘制能量轨迹图
        self._plot_energy_trajectory(output)
    
    def _plot_energy_trajectory(self, output):
        """Plot energy trajectory"""
        try:
            import matplotlib.pyplot as plt
            
            energy_data = []
            ngeoms = len(output.results_properties.geometries)
            
            for igeom in range(ngeoms):
                energy = output.results_properties.geometries[igeom].single_point_data.finalenergy
                energy_data.append(energy)
            
            if energy_data:
                # Create figure
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Plot energy trajectory
                x_indices = list(range(len(energy_data)))
                ax.plot(x_indices, energy_data, 'b-o', linewidth=2, markersize=4, label='SCF Energy')
                
                # Mark final energy
                final_energy = energy_data[-1]
                ax.axhline(y=final_energy, color='r', linestyle='--', alpha=0.7, 
                           label=f'Final Energy: {final_energy:.6f} Hartree')
                
                # Add title and labels
                ax.set_title('Geometry Optimization Energy Trajectory', fontsize=14, fontweight='bold')
                ax.set_xlabel('Geometry Index', fontsize=12)
                ax.set_ylabel('Energy (Hartree)', fontsize=12)
                
                # Add grid and legend
                ax.grid(True, alpha=0.3)
                ax.legend()
                
                # Save plot
                plt.tight_layout()
                plt.savefig('energy_trajectory.png', dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"Energy trajectory plot saved: energy_trajectory.png")
                print(f"Number of geometries: {len(energy_data)}")
                print(f"Initial energy: {energy_data[0]:.6f} Hartree")
                print(f"Final energy: {energy_data[-1]:.6f} Hartree")
                print(f"Energy reduction: {energy_data[0] - energy_data[-1]:.6f} Hartree")
                
        except ImportError:
            print("Warning: matplotlib not installed, cannot plot energy trajectory")
            print("Install with: pip install matplotlib")
        except Exception as e:
            print(f"Failed to plot energy trajectory: {e}")