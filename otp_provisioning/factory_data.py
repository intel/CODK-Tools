#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, Intel Corporation. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import ctypes

MAGIC = "$FA!"
VERSION = 0x01

class HardwareInfo(ctypes.Structure):
    """Hardware info, see declaration in infra/factory_data.h, size: 16 bytes """
    _pack_ = 1
    _fields_ = [
        ("hardware_name", ctypes.c_ubyte),
        ("hardware_type", ctypes.c_ubyte),
        ("hardware_revision", ctypes.c_ubyte),
        ("reserved", ctypes.c_ubyte),
        ("hardware_variant", ctypes.c_uint*3)
    ]

class OEMData(ctypes.Structure):
    """OEM data, see declaration in infra/factory_data.h, size: 512 bytes """
    _pack_ = 1
    _fields_ = [
        ("header", ctypes.c_ubyte * 4),
        ("magic", ctypes.c_ubyte * 4),
        ("version", ctypes.c_ubyte),
        ("production_mode_oem", ctypes.c_ubyte),
        ("production_mode_customer", ctypes.c_ubyte),
        ("reserved0", ctypes.c_ubyte),
        ("hardware_info", HardwareInfo),
        ("uuid", ctypes.c_ubyte * 16),
        ("factory_sn", ctypes.c_ubyte * 32),
        ("hardware_id", ctypes.c_ubyte * 32),
        ("project_data", ctypes.c_ubyte * 84),
        ("security", ctypes.c_ubyte * 320)
    ]

class CustomerData(ctypes.Structure):
    """Customer data, see declaration in infra/factory_data.h, size: 512 bytes """
    _pack_ = 1
    _fields_ = [
        ("product_sn", ctypes.c_ubyte * 16),
        ("product_hw_ver", ctypes.c_ubyte * 4),
        ("padding", ctypes.c_ubyte * 12),
        ("board_name", ctypes.c_ubyte * 32),
        ("vendor_name", ctypes.c_ubyte * 32),
        ("sn_length", ctypes.c_uint),
        ("board_name_length", ctypes.c_uint),
        ("vendor_name_length", ctypes.c_uint),
	("product_vid", ctypes.c_uint16),
	("product_pid", ctypes.c_uint16),
        ("reserved", ctypes.c_ubyte * 384),
        ("patternKeyStart", ctypes.c_uint),
        ("blockVersionHi", ctypes.c_uint),
        ("blockVersionLo", ctypes.c_uint),
        ("patternKeyEnd", ctypes.c_uint)
    ]

class FactoryData(ctypes.Structure):
    """Factory data, see declaration in infra/factory_data.h """
    _pack_ = 1
    _fields_ = [
        ("oem_data", OEMData),
        ("customer_data", CustomerData)
    ]

def init_oem_base_fields(oem_fdata):
    oem_fdata.header[0] = 0xFF
    oem_fdata.header[1] = 0xFF
    oem_fdata.header[2] = 0xFF
    oem_fdata.header[3] = 0xFF
    oem_fdata.magic = (ctypes.c_ubyte * 4).from_buffer_copy(MAGIC)
    oem_fdata.version = VERSION
    oem_fdata.production_mode_oem = 0xFF
    oem_fdata.production_mode_customer = 0xFF
