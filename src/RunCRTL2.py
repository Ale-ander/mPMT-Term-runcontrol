#!/usr/bin/env python3
# coding=utf-8

import sys
import time
import mmap
from datetime import datetime, timezone

# ---------------------
class RunControl:
    def __init__(self):
        try:
            self.fid = open('/dev/uio0', 'r+b', 0)
        except FileNotFoundError:
            print("E: UIO device /dev/uio0 not found")
            sys.exit(-1)

        self.regs = mmap.mmap(self.fid.fileno(), 0x10000)

        # Variables
        self.EnablePulser = "Disabled"
        self.EnableTrigger = "Disabled"
        self.HFFIFO = "Empty"
        self.RSTFIFO = "Free"
        self.PLLlocked = "Locked"
        self.Tr32_na = 'Tr32 NOT Aligned'
        self.Tr32_nr = 'Tr32 NOT Received'
        self.Clk_extint = "Internal"
        self.Clk_1_2 = 1
        self.Clk_extint_state = "Internal"
        self.Clk1_2_state = 1
        self.Clk_ok_1 = "OK"
        self.Clk_ok_2 = "OK"
        self.Clk_lost_1 = "CLK NOT lost"
        self.Clk_lost_2 = "CLK NOT lost"
        self.Clk_found_1 = "CLK found"
        self.Clk_found_2 = "CLK found"
        self.Td_nr = "Td NOT Received"
        self.Td_na = "Td NOT Aligned"
        self.Td_par_err = 'Td parity error'
        self.Tr32enCH = "Disabled"
        self.Rst_MCH = "Free"
        self.CalibADC = "No"
        self.Timeout = 2555
        self.counterTr32 = 0
        self.Runc_Val_Tag0 = 1
        self.Pulser = 0
        self.Pulservalue = 0
        self.Window = 0
        self.WindowValue = 0
        self.FIFOnumber = 0
        self.Ratemeter = 0
        self.Deadtime = 0

        # Local variables
        self.PowerEnable = 0x00000000
        self.AcqEnable = 0x00000000
        self.Overcurrent = 0x00000000
        self.MiscRO = 0x00000000
        self.MiscRW = 0x00000000

        # Address locations
        self.addrElenco = { "EnAcq": 0,
                            "PowEn": 1,
                            "OVC": 2,
                            "AllpurposeRO": 3,
                            "AllpurposeRW": 4,
                            "UnixTime": 5,
                            "RunCValTag0": 6,
                            "Pulser": 7,
                            "Ratemeter CH1": 8,
                            "Deadtime": 27,
                            "DatainFIFO" : 43,
                            "TriggerWindow" : 44,
                            "PPSCounter": 45
                            }

        self.Info()

    def LoopRead(self) -> None:
        for name, regAddr in self.addrElenco.items():
            dati = int.from_bytes(self.regs[regAddr * 4:(regAddr * 4) + 4], byteorder='little')
            self.EstrazioneParametri(regAddr, dati)

    def Info(self) -> None:
        self.LoopRead() #Lettura di tutti i parametri
        print(f"\n\
------ Run Control mPMT  ------\n\
* 1)  Reset Fifo                 {self.RSTFIFO!s}\n\
* 2)  CLK externel/internal      {self.Clk_extint!s}\n\
* 3)  CLK cable 1/2              {self.Clk_1_2}\n\
* 4)  Tr32 channel               {self.Tr32enCH!s}\n\
* 5)  Reset multichannel         {self.Rst_MCH!s}\n\
* 6)  Calibration ADC            {self.CalibADC!s}\n\
* 7)  Timeout FAZIA (ns)         {self.Timeout}\n\
* 8)  RuncValTag0                {self.Runc_Val_Tag0}\n\
* 9)  Pulser period (Hz)         {self.Pulservalue}\n\
* 10) Trigger Window             {self.WindowValue}\n\
* 11) Enable Trigger             {self.EnableTrigger!s}\n\
* 12) Enable Pulser              {self.EnablePulser!s}\n\
------ Run Control all channels ------\n\
* 20) Turn ON Channel -> Channel turned ON {bin(self.PowerEnable)}\n\
* 21) Turn OFF Channel\n\
* 22) Enable Channel  -> Channel enabled   {bin(self.AcqEnable)}\n\
* 23) Disable Channel \n\
* 30) Print Ratemeters \n\
------ Read only values ------\n\
* Overcurrent                    {self.Overcurrent}\n\
* Td aligned                     {self.Td_na!s}\n\
* Td reception                   {self.Td_nr!s}\n\
* Td parity                      {self.Td_par_err}\n\
* Tr32 counted                   {self.counterTr32!s} \n\
* Tr32 reception                 {self.Tr32_nr!s}\n\
* Tr32 aligned                   {self.Tr32_na!s}\n\
* Fifo Full                      {self.HFFIFO!s} \n\
* FIFO data                      {self.FIFOnumber}\n\
* PLL 250MHz                     {self.PLLlocked!s} and {self.PLL_stable}\n\
* Deadtime                       {self.Deadtime}%\n\
* CLK cable used                 {self.Clk1_2_state}\n\
* CLK source used                {self.Clk_extint_state!s}\n\
* CLK ok 1                       {self.Clk_ok_1!s}\n\
* CLK lost 1                     {self.Clk_lost_1!s}\n\
* CLK found 1                    {self.Clk_found_1!s}\n\
* CLK ok 2                       {self.Clk_ok_2!s}\n\
* CLK lost 2                     {self.Clk_lost_2!s}\n\
* CLK found 2                    {self.Clk_found_2!s}\n\
* [R] Read a register\n\
")

    def LoopRunControll(self) -> None:
        key = ""
        doinfo = True
        while key != "q":
            key = input("\n> ")

            if key == '1':
                print("Reset FIFO Reset = R, Free = F")
                dato = input("> ").upper()
                if dato == 'R':
                    self.MiscRW = self.MiscRW | 0x00000200
                elif dato == 'F':
                    self.MiscRW = self.MiscRW & 0xFFFFFDFF
                self.regs[4*4:(4*4)+4] = int.to_bytes(self.MiscRW, 4, byteorder='little')

            elif key == '2':
                print("Clock source External = E, Internal = I")
                dato = input("> ").upper()
                if dato == 'E':
                    self.MiscRW = self.MiscRW | 0x00000400
                elif dato == 'I':
                    self.MiscRW = self.MiscRW & 0xFFFFFBFF
                self.regs[4*4:(4*4)+4] = int.to_bytes(self.MiscRW, 4, byteorder='little')

            elif key == '3':
                print("Clock cable source 1/2 = ")
                dato = input("> ").upper()
                if dato == '2':
                    self.MiscRW = self.MiscRW | 0x00000800
                elif dato == '1':
                    self.MiscRW = self.MiscRW & 0xFFFFF7FF
                self.regs[4*4:(4*4)+4] = int.to_bytes(self.MiscRW, 4, byteorder='little')
            
            elif key == '4':
                print("Enable PPS channel E = Enable, D = Disable")
                dato = input("> ").upper()
                if dato == 'E':
                    self.MiscRW = self.MiscRW | 0x00004000
                elif dato == 'D':
                    self.MiscRW = self.MiscRW & 0xFFFFBFFF
                self.regs[4*4:(4*4)+4] = int.to_bytes(self.MiscRW, 4, byteorder='little')

            elif key == '5':
                print("Reset multichannel R = Reset, F = Free")
                dato = input("> ").upper()
                if dato == 'R':
                    self.MiscRW = self.MiscRW | 0x00008000
                elif dato == 'F':
                    self.MiscRW = self.MiscRW & 0xFFFF7FFF
                self.regs[4*4:(4*4)+4] = int.to_bytes(self.MiscRW, 4, byteorder='little')

            elif key == '6':
                print("Calibration ADC Y = Yes, N = No")
                dato = input("> ").upper()
                if dato == 'Y':
                    self.MiscRW = self.MiscRW | 0x00010000
                    self.regs[4*4:(4*4)+4] = int.to_bytes(self.MiscRW, 4, byteorder='little')
                    time.sleep(0.5)
                    self.MiscRW = self.MiscRW & 0xFFFEFFFF
                elif dato == 'N':
                    self.MiscRW = self.MiscRW
                self.regs[4*4:(4*4)+4] = int.to_bytes(self.MiscRW, 4, byteorder='little')
                
            elif key == '7':
                print("Timeout ns (max 2555)")
                dato = input("> ")
                try:
                  idato = int(dato)
                except ValueError:
                  print("Immettere valore intero")
                  idato = 2555
                if idato <= 2555 and idato != 0: 
                  self.MiscRW = int(idato/5) + (self.MiscRW & 0xFFFFFE00)
                elif idato == 0:
                  self.MiscRW = self.MiscRW
                else:
                  print("Value Error")
                self.regs[4*4:(4*4)+4] = int.to_bytes(self.MiscRW, 4, byteorder='little')

            elif key == '8':
                print("RunC_Val_Tag0 (min 1)")
                dato = input("> ")
                try:
                  idato = int(dato)
                except ValueError:
                  print("Immettere valore intero")
                  idato = 1
                if idato != 0:
                  self.Runc_Val_Tag0 = idato
                elif idato == 0:
                  self.Runc_Val_Tag0 = 1
                else:
                  print("Value Error")
                self.regs[6*4:(6*4)+4] = int.to_bytes(self.Runc_Val_Tag0, 4, byteorder='little')
                
            elif key == '9':
                print("Ratemeter period Hz (0 = OFF)")
                dato = input("> ")
                try:
                  idato = int(dato)
                  self.Pulservalue = idato
                except ValueError:
                  print("Immettere valore intero")
                  idato = 0
                if idato <= 1000000 and idato != 0:
                  self.Pulser = 1000000/idato
                elif idato == 0:
                  self.Pulser = 0
                else:
                  print("Value Error")
                self.regs[7*4:(7*4)+4] = int.to_bytes(int(self.Pulser), 4, byteorder='little') 
                 
            elif key == '10':
                print("Set Trigger Window in ns (min = 5 ns, 0 = OFF)")
                dato = input("> ")
                try:
                  idato = round(int(dato)/5)
                  self.WindowValue = dato
                except ValueError:
                  print("Immettere valore intero")
                  idato = 0
                self.Window = idato
                self.regs[44*4:(44*4)+4] = int.to_bytes(int(self.Window), 4, byteorder='little') 
            
            elif key == '11':
                print("Enable Trigger E = Enable, D = Disable")
                dato = input("> ").upper()
                if dato == "E":
                   self.MiscRW = self.MiscRW | 0x00002000
                elif dato == "D":
                   self.MiscRW = self.MiscRW & 0xFFFFDFFF
                self.regs[4*4:(4*4)+4] = int.to_bytes(self.MiscRW, 4, byteorder='little')
            
            elif key == '12':
                print("Enable Pulser E = Enable, D = Disable")
                dato = input("> ").upper()
                if dato == "E":
                   self.MiscRW = self.MiscRW | 0x00001000
                elif dato == "D":
                   self.MiscRW = self.MiscRW & 0xFFFFEFFF
                self.regs[4*4:(4*4)+4] = int.to_bytes(self.MiscRW, 4, byteorder='little')
          
            elif key == '20':
                print("Turn ON which channel? (1 to 19)")
                dato = int(input("> "))
                if 0 < dato < 20:
                    self.PowerEnable = 2**(dato-1) | self.PowerEnable
                    self.regs[1*4:(1*4)+4] = int.to_bytes(int(self.PowerEnable), 4, byteorder='little')
                else:
                    print("Address not valid!")
            
            elif key == '21':
                print("Turn OFF which channel? (1 to 19)")
                dato = int(input("> "))
                if 2**(dato-1) > self.PowerEnable:
                    print('Channel already OFF')
                else:
                   dtosend = self.PowerEnable - 2**(dato-1)
                   self.regs[1*4:(1*4)+4] = int.to_bytes(dtosend, 4, byteorder='little')
            
            elif key == '22':
                print("Enable which channel? (1 to 19)")
                dato = int(input("> "))
                if 0 < dato < 20:
                    self.AcqEnable = 2**(dato-1) | self.AcqEnable
                    self.regs[0*4:(0*4)+4] = int.to_bytes(self.AcqEnable, 4, byteorder='little')
                else:
                    print("Address not valid!")
            
            elif key == '23':
                print("Disable which channel? (1 to 19)")
                dato = int(input("> "))
                if 2**(dato-1) > self.AcqEnable:
                   print('Channel already disabled')
                else:
                   dtosend = self.AcqEnable - 2**(dato-1)
                   self.regs[0*4:(0*4)+4] = int.to_bytes(dtosend, 4, byteorder='little')

            elif key == 'r' or key == 'R':
               print("Which register? (0 to 45)")
               dato = int(input("> "))
               print(f'0x{int.from_bytes(self.regs[dato * 4:(dato * 4) + 4], byteorder="little"):08x}')
               doinfo = False

            elif key == '30':
               self.print_ratemeters()
               doinfo = False
            else:
               doinfo = True
            if doinfo:
                self.Info()

    def EstrazioneParametri(self, Cmd: int, Valore: int) -> None:
         if Cmd == list(self.addrElenco.values())[0]:
            self.AcqEnable = Valore

         elif Cmd == list(self.addrElenco.values())[1]:
            self.PowerEnable = Valore

         elif Cmd == list(self.addrElenco.values())[2]:
            self.Overcurrent = Valore

         elif Cmd == list(self.addrElenco.values())[3]:
            binNum = '{0:032b}'.format(Valore)
            self.MiscRO = Valore
            self.HFFIFO = 'Full' if binNum[31] == '1' else 'Free'
            self.PLLlocked = 'Locked' if binNum[30] == '1' else 'NOT locked'
            self.Clk_found_2 = 'CLK found' if binNum[29] == '1' else 'CLK NOT found'
            self.Clk_lost_2 = 'CLK lost' if binNum[28] == '1' else 'CLK NOT lost'
            self.Clk_ok_2 = 'CLK OK' if binNum[27] == '1' else 'CLK NOT OK'
            self.Clk_found_1 = 'CLK found' if binNum[26] == '1' else 'CLK NOT found'
            self.Clk_lost_1 = 'CLK lost' if binNum[25] == '1' else 'CLK NOT lost'
            self.Clk_ok_1 = 'CLK OK' if binNum[24] == '1' else 'CLK NOT OK'
            self.Clk1_2_state = '2' if binNum[23] == '1' else '1'
            self.Clk_extint_state = 'Internal' if binNum[22] == '1' else 'External'
            self.Tr32_na = 'Tr32 NOT Aligned' if binNum[21] == '1' else 'Tr32 Aligned'
            self.Tr32_nr = 'Tr32 NOT Received' if binNum[20] == '1' else 'Tr32 Received'
            self.Td_na = 'Td NOT Aligned' if binNum[21] == '1' else 'Td Aligned'
            self.Td_nr = 'Td NOT Received' if binNum[20] == '1' else 'Td Received'
            self.Td_par_err = 'Td parity error' if binNum[19] == '1' else 'Td parity OK'
            self.PLL_stable = 'Stable' if binNum[18] == '1' else 'Unstable'
            
         elif Cmd == list(self.addrElenco.values())[4]:
            binNum = '{0:032b}'.format(Valore)
            self.MiscRW = Valore
            self.Timeout = int(binNum[23:], 2) * 5
            self.RSTFIFO = 'Resetted' if binNum[22] == '1' else 'Free'
            self.Clk_extint = 'External' if binNum[21] == '1' else 'Internal'
            self.Clk_1_2 = 2 if binNum[20] == '1' else 1
            self.EnablePulser = "Enabled" if binNum[19] == '1' else "Disabled"
            self.EnableTrigger = "Enabled" if binNum[18] == '1' else "Disabled"
            self.PPSenCH = 'Enabled' if binNum[17] == '1' else 'Disabled'
            self.Rst_MCH = 'Resetted' if binNum[16] == '1' else 'Free'
            self.CalibADC = 'In calibration' if binNum[15] == '1' else 'Not calibrated'

         elif Cmd == list(self.addrElenco.values())[5]:
            self.TdValue = Valore
         elif Cmd == list(self.addrElenco.values())[6]:
            self.Runc_Val_Tag0 = Valore
         elif Cmd == list(self.addrElenco.values())[7]:
            if Valore == 0:
               self.Pulservalue = 0
            else: 
               self.Pulservalue = 1000000/Valore
         elif Cmd == list(self.addrElenco.values())[8]:
             self.Ratemeter = Valore
         elif Cmd == list(self.addrElenco.values())[9]:
             self.Deadtime = int(100*(1-Valore/48826))
         elif Cmd == list(self.addrElenco.values())[10]:
             self.FIFOnumber = Valore
         elif Cmd == list(self.addrElenco.values())[11]:
             self.WindowValue = Valore * 5
         elif Cmd == list(self.addrElenco.values())[12]:
             self.counterTr32 = Valore
         else:
            pass

    def print_ratemeters(self):
        for index in range(8, 27):
            print(f'Rate CH {index-7}: {int.from_bytes(self.regs[index * 4:(index * 4) + 4], byteorder="little")}')
        Valore = int.from_bytes(self.regs[27 * 4:(27 * 4) + 4], byteorder='little')
        self.Deadtime = int(100 * (1 - Valore / 48826))
        print(f'Deadtime: {self.Deadtime}%')

if __name__ == '__main__':
   RC = RunControl()
   RC.Info()
   RC.LoopRunControll()
