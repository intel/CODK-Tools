#!/bin/sh
bin/openocd -f scripts/interface/ftdi/flyswatter2.cfg -f scripts/board/quark_se.cfg -f scripts/flash-otp.cfg
if [ $? -ne 0 ]; then
  echo
  echo "***ERROR***"
else
  echo
  echo "!!!SUCCESS!!!"
fi
