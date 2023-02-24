<h1 align="center">
Court Scan
</h1>
<p>&nbsp;</p>

## Overview

This was one of my first major projects. As an avid badminton player, I wanted a quick way to check the availability of courts around me and it quickly became rather tedious to look through the many schools and sport halls in my area to check for available courts. Hence I built this script where one simply enters the location where you would like to book courts such as `yishun` for example, and the script searches through all the schools and sport halls located in Yishun.

Note that this script only works during off peak hours as ActiveSG uses a _quick booking_ feature during peak hours (7am-7.30am daily) which changes the entire booking process.  
ActiveSG also warns users **not** to use any scripts to book courts and although this script does not techically book any courts, it simply adds it to your cart, it is a very fine grey area that this script is threading. Personally I have not used this script to book any courts so fair warning if you do decide to use it.

### Setup

1. Change the `USERNAME` and `PASSWORD` variables to your own credentials in `auth.py`
2. Run `pip install req.txt` to install the required Python modules
3. Run `main.py` and input the location and timings you would like to search when prompted
4. Let the script work it's magic

### Things to improve

- Figure out how to search for courts even during the _quick booking_ timings
