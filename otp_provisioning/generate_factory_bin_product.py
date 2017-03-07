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

SERIAL_MAX = 16
STRING_MAX = 32
HWVER_MAX = 8
VIDPID_MAX = 4

base_addr = hex(0xffffe000 + 0x200)

GENUINO = "Genuino 101"
ARDUINO = "Arduino 101"
VENDOR = "Intel"
# version of this OTP block, so that it can be extended or changed in the future.
VERSIONHI = 2
VERSIONLO = 0
KEYSTART = 0xA5A5A5A5
KEYEND = 0x5A5A5A5A

description = ("This script generates a binary file containing various product "
"provisioning info for Intel Curie-based products, such as product serial "
"number, USB Vendor/Product IDs and string descriptors. The resulting binary "
"file can be programmed onto a Curie device by connecting a Flyswatter2 JTAG "
"programmer, and running the provided 'flash_otp.sh' script.")

def main():
# Parse input arguments
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-s', '--serial', dest='product_sn', help="Product "
            "serial number, up to %d ASCII characters" % SERIAL_MAX,
            required=True)
    parser.add_argument('-w', '--hw-version', dest='product_hw_ver',
            help="Product hardware version, up to %d hexadecimal "
            "characters" % HWVER_MAX, required=True)
    parser.add_argument('-n', '--product-name', dest='product_board_name',
            help="A human-readable string representing the product name. Up "
            "to %d ASCII characters" % STRING_MAX, required=True)
    parser.add_argument('-m', '--vendor-name', dest='product_vendor_name',
            help="A human-readable string representing the product name. Up "
            "to %d ASCII characters" % STRING_MAX, required=True)
    parser.add_argument('-v', '--vid', dest='product_VID', help="the Vendor "
            "ID. Up to %d hexadecimal characters" % VIDPID_MAX, required=True)
    parser.add_argument('-p', '--pid', dest='product_PID', help="the Product "
            "ID. Up to %d hexadecimal characters" % VIDPID_MAX, required=True)
    args = parser.parse_args()


# Create instance of customer data struct
    product_data = factory_data.CustomerData()

    # Add the product serial number
    ############
    assert len(args.product_sn) <= SERIAL_MAX

    product_sn_padded = args.product_sn.ljust(SERIAL_MAX, '\0')
    product_data.product_sn = (ctypes.c_ubyte * SERIAL_MAX).from_buffer_copy(bytearray(product_sn_padded))

    # Add the product hardware id
    ############
    assert len(args.product_hw_ver) <= HWVER_MAX

    product_hw_ver_padded = args.product_hw_ver.rjust(HWVER_MAX, '0')
    product_data.product_hw_ver = (ctypes.c_ubyte * (HWVER_MAX / 2)).from_buffer_copy(binascii.unhexlify(product_hw_ver_padded))
    
    #pad the spaces
    paddingBytes = bytearray().ljust(len( product_data.padding), binascii.unhexlify("FF") )
    product_data.padding = type( product_data.padding ).from_buffer_copy(paddingBytes)
    
    # insert the board name
    assert len(args.product_board_name) <= STRING_MAX
    board_name_padded = args.product_board_name.ljust(STRING_MAX, '\0')
    product_data.board_name = (ctypes.c_ubyte * STRING_MAX).from_buffer_copy(bytearray(board_name_padded))

    #insert the vendor name
    assert len(args.product_vendor_name) <= STRING_MAX
    vendor_name_padded = args.product_vendor_name.ljust(STRING_MAX, '\0')
    product_data.vendor_name = (ctypes.c_ubyte * STRING_MAX).from_buffer_copy(bytearray(vendor_name_padded))

    #insert VID
    assert len(args.product_VID) <= VIDPID_MAX
    product_data.product_vid = int(args.product_VID, 16);

    #insert PID
    assert len(args.product_PID) <= VIDPID_MAX
    product_data.product_pid = int(args.product_PID, 16);

    print "Product S/N    : " + product_sn_padded
    print "Product HW VER : " + product_hw_ver_padded
    print "Board Name     : " + board_name_padded
    print "Vendor Name    : " + vendor_name_padded
    print "Vendor ID      : " + hex(product_data.product_vid)
    print "Product ID     : " + hex(product_data.product_pid)

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
