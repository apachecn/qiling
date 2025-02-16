#!/usr/bin/env python3
# 
# Cross Platform and Multi Architecture Advanced Binary Emulation Framework
#

from functools import cached_property
from typing import Union

from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_MODE_32, UC_MODE_64
from capstone import Cs, CS_ARCH_X86, CS_MODE_16, CS_MODE_32, CS_MODE_64
from keystone import Ks, KS_ARCH_X86, KS_MODE_16, KS_MODE_32, KS_MODE_64

from unicorn.x86_const import UC_X86_REG_EFLAGS

from qiling.arch.arch import QlArch
from qiling.arch.msr import QlMsrManager
from qiling.arch.register import QlRegisterManager
from qiling.arch import x86_const
from qiling.const import QL_ARCH, QL_ENDIAN

class QlArchIntel(QlArch):
    @property
    def endian(self) -> QL_ENDIAN:
        return QL_ENDIAN.EL

    @cached_property
    def msr(self) -> QlMsrManager:
        """Model-Specific Registers.
        """

        return QlMsrManager(self.uc)

class QlArchA8086(QlArchIntel):
    type = QL_ARCH.A8086
    bits = 16

    @cached_property
    def uc(self) -> Uc:
        return Uc(UC_ARCH_X86, UC_MODE_16)

    @cached_property
    def regs(self) -> QlRegisterManager:
        regs_map = dict(
            **x86_const.reg_map_8,
            **x86_const.reg_map_16,
            **x86_const.reg_map_misc
        )

        pc_reg = 'ip'
        sp_reg = 'sp'

        return QlRegisterManager(self.uc, regs_map, pc_reg, sp_reg)

    @cached_property
    def disassembler(self) -> Cs:
        return Cs(CS_ARCH_X86, CS_MODE_16)

    @cached_property
    def assembler(self) -> Ks:
        return Ks(KS_ARCH_X86, KS_MODE_16)

class QlArchX86(QlArchIntel):
    type = QL_ARCH.X86
    bits = 32

    @cached_property
    def uc(self) -> Uc:
        return Uc(UC_ARCH_X86, UC_MODE_32)

    @cached_property
    def regs(self) -> QlRegisterManager:
        regs_map = dict(
            **x86_const.reg_map_8,
            **x86_const.reg_map_16,
            **x86_const.reg_map_32,
            **x86_const.reg_map_cr,
            **x86_const.reg_map_st,
            **x86_const.reg_map_misc
        )

        pc_reg = 'eip'
        sp_reg = 'esp'

        return QlRegisterManager(self.uc, regs_map, pc_reg, sp_reg)

    @cached_property
    def disassembler(self) -> Cs:
        return Cs(CS_ARCH_X86, CS_MODE_32)

    @cached_property
    def assembler(self) -> Ks:
        return Ks(KS_ARCH_X86, KS_MODE_32)

class QlArchX8664(QlArchIntel):
    type = QL_ARCH.X8664
    bits = 64

    @cached_property
    def uc(self) -> Uc:
        return Uc(UC_ARCH_X86, UC_MODE_64)

    @cached_property
    def regs(self) -> QlRegisterManager:
        regs_map = dict(
            **x86_const.reg_map_8,
            **x86_const.reg_map_16,
            **x86_const.reg_map_32,
            **x86_const.reg_map_64,
            **x86_const.reg_map_cr,
            **x86_const.reg_map_st,
            **x86_const.reg_map_misc,
            **x86_const.reg_map_64_b,
            **x86_const.reg_map_64_w,
            **x86_const.reg_map_64_d,
            **x86_const.reg_map_seg_base
        )

        pc_reg = 'rip'
        sp_reg = 'rsp'

        return QlRegisterManager(self.uc, regs_map, pc_reg, sp_reg)
    @cached_property
    def disassembler(self) -> Cs:
        return Cs(CS_ARCH_X86, CS_MODE_64)

    @cached_property
    def assembler(self) -> Ks:
        return Ks(KS_ARCH_X86, KS_MODE_64)

    # TODO: generalize this
    def __reg_bits(self, register: int) -> int:
        # all regs in reg_map_misc are 16 bits except of eflags
        if register == UC_X86_REG_EFLAGS:
            return 32

        regmaps = (
            (x86_const.reg_map_8, 8),
            (x86_const.reg_map_16, 16),
            (x86_const.reg_map_32, 32),
            (x86_const.reg_map_64, 64),
            (x86_const.reg_map_misc, 16),
            (x86_const.reg_map_cr, 64),         # 32 bits for x86
            (x86_const.reg_map_st, 32),
            (x86_const.reg_map_seg_base, 64),   # 32 bits for x86
        )

        return next((rsize for rmap, rsize in regmaps if register in rmap.values()), 0)

    # note: this method was not generalized for all archs since it requires a bookkeeping
    # of all registers, while it is used only by gdb and only for x86-64
    def reg_bits(self, reg: Union[str, int]) -> int:
        """Get register size in bits.
        """

        if type(reg) is str:
            reg = self.regs.register_mapping[reg]

        return self.__reg_bits(reg)
