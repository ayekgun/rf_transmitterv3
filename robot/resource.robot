*** Settings ***
Documentation     A resource file with reusable keywords and variables.
...
...               The system specific keywords created here form our own
...               domain specific language. They utilize keywords provided
...               by the imported Selenium2Library.
# Library         SeleniumLibrary     implicit_wait=20
Library         Process
Library         OperatingSystem
Library         String
Library         Collections
Library         ../py/Transmitter.py
Resource        keyword.robot
