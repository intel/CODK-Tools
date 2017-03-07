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

import sys
import argparse
import ctypes
import binascii

import factory_data

base_addr = hex(0xffffe000 + 0x200)

GENUINO = "Genuino 101"
ARDUINO = "Arduino 101"
VENDOR = "Intel"
# version of this OTP block, so that it can be extended or changed in the future.
VERSIONHI = 2
VERSIONLO = 0
KEYSTART = 0xA5A5A5A5
KEYEND = 0x5A5A5A5A

def main():
# Parse input arguments
    parser = argparse.ArgumentParser(description="Generate a binary file containing"
        "various provisioning product info such as product serial number.")
    parser.add_argument('--product_sn', help="the product serial number, up to 16 ASCII characters", required=True)
    parser.add_argument('--product_hw_ver', help="the product hardware version, up to 4 bytes in hexadecimal", required=True)
    parser.add_argument('--product_board_name', help="the product board name", required=True)
    parser.add_argument('--product_vendor_name', help="the product vendor name", required=True)
    parser.add_argument('--product_VID', help="the product VID", required=True)
    parser.add_argument('--product_PID', help="the product PID", required=True)
    args = parser.parse_args()


# Create instance of customer data struct
    product_data = factory_data.CustomerData()

    # Add the product serial number
    ############
    assert len(args.product_sn) <= 16

    product_sn_padded = args.product_sn.ljust(16, '\0')
    product_data.product_sn = (ctypes.c_ubyte * 16).from_buffer_copy(bytearray(product_sn_padded))

    print "Product S/N     : " + product_sn_padded

    # Add the product hardware id
    ############
    assert len(args.product_hw_ver) <= 8

    product_hw_ver_padded = args.product_hw_ver.rjust(8, '0')
    product_data.product_hw_ver = (ctypes.c_ubyte * 4).from_buffer_copy(binascii.unhexlify(product_hw_ver_padded))

    print "Product HW VER  : " + product_hw_ver_padded
    
    #pad the spaces
    paddingBytes = bytearray().ljust(len( product_data.padding), binascii.unhexlify("FF") )
    product_data.padding = type( product_data.padding ).from_buffer_copy(paddingBytes)
    
    # insert the board name
    assert len(args.product_board_name) <= 32
    board_name_padded = args.product_board_name.ljust(32, '\0')
    product_data.board_name = (ctypes.c_ubyte * 32).from_buffer_copy(bytearray(board_name_padded))
       
    print "Board Name     :" + board_name_padded

    #insert the vendor name
    assert len(args.product_vendor_name) <= 32
    vendor_name_padded = args.product_vendor_name.ljust(32, '\0')
    product_data.vendor_name = (ctypes.c_ubyte * 32).from_buffer_copy(bytearray(vendor_name_padded))
    
    print "Vendor Name     :" + vendor_name_padded

    #insert VID
    assert len(args.product_VID) <= 4
    product_data.product_vid = int(args.product_VID, 16);

    print "Vendor ID     :" + hex(product_data.product_vid)

    #insert PID
    assert len(args.product_PID) <= 4
    product_data.product_pid = int(args.product_PID, 16);

    print "Product ID     :" + hex(product_data.product_pid)

    #put in the length of the serial number string and the name string, not counting trailing nulls. 
    product_data.sn_length = len(args.product_sn)
    product_data.board_name_length = len(args.product_board_name)
    product_data.vendor_name_length = len(args.product_vendor_name)
     # Pad with 0xFF to fit project_data size
    ############
    product_data_padded = bytearray().ljust(len(product_data.reserved), binascii.unhexlify("FF"))
    product_data.reserved = type(product_data.reserved).from_buffer_copy(product_data_padded)
    
    #put the ending block pattern keys and version numbers
    product_data.patternKeyStart = KEYSTART
    product_data.blockVersionHi = VERSIONHI
    product_data.blockVersionLo = VERSIONLO
    product_data.patternKeyEnd = KEYEND

# Save the .bin file
    arr = bytearray(product_data)
    assert len(arr) == 512, "ERROR: product data struct size error"
    out_file = open("factory_data_product.bin", "wb")
    out_file.write(arr)
    out_file.close()


# Creates the OpenOCD flash script
    flash_script = """### Generated script, please do not edit
### Flash product provisining data in OTP
load_image factory_data_product.bin %s
verify_image factory_data_product.bin %s
""" % (base_addr, base_addr)
    f = open('factory_data_product.cmd', 'w')
    f.write(flash_script)
    f.close()


if __name__ == "__main__":
    sys.exit(main())
