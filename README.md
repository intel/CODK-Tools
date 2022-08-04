DISCONTINUATION OF PROJECT.

This project will no longer be maintained by Intel.

Intel has ceased development and contributions including, but not limited to, maintenance, bug fixes, new releases, or updates, to this project. 

Intel no longer accepts patches to this project.

If you have an ongoing need to use this project, are interested in independently developing it, or would like to maintain patches for the open source software community, please create your own fork of this project. 
# CODK-Tools

### One Time Programming

The OTP (One Time Programming) is responsible for storing product and OEM data into the Curie SoC. The process to save data on OTP is executed in two stages:

•	OTP Stage 1 (initial address is 0xffffe000): The first stage is performed during Curie manufacturing. Here, some data like Intel MAC address, Curie Hardware ID and Curie ESN are stored. This area should be left alone! Modifying this area can potentially lock the OTP area and disable flashing.

•	OTP Stage 2 (initial address 0xffffe200): At this stage, data specific to your product is stored. This includes product name, vendor name, serial number, etc.

### Download CODK-Tools:

```
git clone https://github.com/01org/CODK-Tools.git
```

### Generate .bin containing customer/product data
```
cd CODK-Tools
cd otp_provisioning
```

##### Run ./generate_factory_bin_product.py

```
./generate_factory_bin_product.py --help
```

##### For example:

```
./generate_factory_bin_product.py -s 123456789 -w 01 -n "Arduino 101" -m Intel -v 8087 -p 0AB6
```

##### This will generate a file called factory_data_product.bin

##### Note: If you don’t want to store the product VID/PID into the OTP just give both parameters the value of FFFF

### Flashing the customer data section of the OTP area

Before proceeding with this step, if you are using an Arduino 101 board and want to be able to recover it to its factory state, it is highly recommended to back-up the current content of the OTP

```
./flash_otp.sh
```

##### Once flashing is successful it your board will now have your product data stored in the OTP. 
##### If you flash the firmware from https://github.com/01org/CODK-M-X86 the customer/data stored in the OTP will be used for the USB device descriptors

