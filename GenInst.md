---
type: 产品资料
product_line: Moku
model: 
status: 有效
updated: 2026-09-01
tags:
  - moku仪器
responsible_contacts:
  - 汪工(Mark)
  - 许工(Sherry)
---

# GenInst（自定义仪器 / Custom Instrument）

Moku 自定义仪器（Custom Instrument，简称 GenInst）允许用户快速开发、编译并将数字信号处理算法部署到 Moku 的 FPGA 上，无需单独下载软件。自定义算法还能与 Moku 集成的仪器功能在并行模式下协同运行，实现系统级定制化测试与实时信号处理。结合自定义仪器，用户能够快速灵活地开发、编译和部署算法到 Moku 的 FPGA 上，实现自定义的数字信号处理，打造高度定制化测试系统。

## Moku Cloud Compile 工作流程

Moku Cloud Compile 是部署自定义仪器算法到 Moku FPGA 的云端编译服务，工作流程如下：

1. **开发算法**：用户在本地开发环境（如 Vivado、MATLAB 或 Python）中编写并验证数字信号处理算法。
2. **上传编译**：将算法上传至 Moku Cloud Compile，云端完成 FPGA 比特流的综合与实现。
3. **部署到设备**：编译生成的比特流部署到 Moku 设备的 FPGA 上，无需在本地安装完整 FPGA 工具链。
4. **并行运行**：部署后的自定义仪器可在多仪器并行模式下与标准仪器（如 [[锁相放大器]]、[[示波器]]、[[PID 控制器]]）实时协同运行。

> Moku:Pro 与 Moku:Lab 均支持 Moku Cloud Compile（MokuOS 3.0 起）。

## FPGA 开发方式

### 开发环境

- **Moku Cloud Compile**：云端编译，免本地安装完整 FPGA 工具链，适合快速部署。
- **本地 HDL 开发**：使用标准 FPGA 开发工具（如 AMD/Xilinx Vivado）编写 HDL（Verilog/VHDL），通过 Moku 提供的 IP 核与接口规范集成到 Moku 信号处理链。
- **Python 开发环境**：支持 Python 开发环境，便于算法原型验证与模型集成，无缝融入现有工作流程。

### HDL 与部署

- 自定义算法以 HDL 描述，利用 Moku 提供的 IP Cores（如 ADC/DAC 接口、时钟与触发、数据交换接口）接入 FPGA 信号处理管道。
- 编译产物为 FPGA 比特流，部署后作为虚拟仪器插槽中的一个独立仪器运行。
- 部署后可与 Moku 任何专业级仪器兼容并行，即时调整响应动态测试场景变化。

## 各型号 FPGA 资源对比

| 参数 | Moku:Go | Moku:Lab | Moku:Pro | Moku:Delta |
|------|---------|----------|----------|------------|
| FPGA 架构 | Zynq 7000 | Zynq 7000 | UltraScale+ | UltraScale+ RFSoC |
| FPGA 核心频率 | 31.25 MHz | 125 MHz | 312.5 MHz | 312.5 MHz |
| 查找表 (LUT) | 20,000 | 48,400 | 20,000 | 50,000 |
| 触发器 (FF) | 40,000 | 96,800 | 40,000 | 100,000 |
| Block RAM (36k) | 50 | 154 | 50 | 100 |
| DSP | 100 | 432 | 200 | 500 |
| 多仪器插槽 | 2 slots | 4 slots | 8 slots | 8 slots |

> 资源越充裕（尤其 DSP 与 Block RAM），可实现的自定义算法复杂度越高。Moku:Delta 与 Moku:Pro 基于 UltraScale+ 架构，提供最高的处理带宽与并行能力。

## 与多仪器并行协同

Moku 多仪器并行模式允许用户同时运行高达 8 个仪器功能。每个虚拟仪器插槽配备多个独立输入与输出接口，用户可以选择将任意模拟输入或输出信号连接到所需插槽。自定义仪器（GenInst）作为其中一个虚拟仪器插槽，可与 Moku 集成的标准仪器在并行模式下协同运行，充分释放平台潜力，实现系统级的定制化测试与实时信号处理。

- 自定义算法还能与 Moku 设备的任何专业级仪器兼容并行，即时调整响应动态测试场景变化。
- 这些自定义算法还能与 Moku 集成的仪器功能在并行模式下协同运行，实现系统级定制化测试与实时信号处理。

## 应用案例

- **自定义信号处理算法部署**：将专有测量或控制算法直接部署到 FPGA，实现低延迟实时处理。
- **FPGA 硬件加速**：利用 DSP 与 Block RAM 资源对高带宽信号进行并行处理。
- **与标准仪器组合构建定制化测试系统**：如锁相放大器 + 自定义解调 + PID 控制器组成闭环测量链。
- **快速原型验证**：通过 Moku Cloud Compile 快速迭代算法并部署到设备验证。
- **科研定制化测量方案**：针对量子光学、激光稳频、半导体表征等场景开发专用仪器。

← 返回 [[Moku]]