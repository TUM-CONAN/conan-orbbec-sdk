from conan import ConanFile
from conan.tools.files import update_conandata, copy, chdir, mkdir, collect_libs, get, rename, unzip
from conan.tools.layout import basic_layout
from conan.tools.env import Environment
from conan.tools.env import VirtualRunEnv
import re
import glob
import shutil

import os, sys
import sysconfig
from io import StringIO

class OrbbecSDKConan(ConanFile):
    name = "orbbec-sdk"
    version = "1.8"

    description = "Orbbec Camera SDK"
    url = "https://github.com/TUM-CAMP-NARVIS/conan-orbbec-sdk.git"
    license = "GPL"
    settings = "os", "arch"

    def generate(self):
        env = Environment()
        return env

    def layout(self):
        basic_layout(self)

    def _package_description(self):
        dl_url = None
        folder_name = None
        sub_version = None
        sub_archive_match = None
        if self.settings.os == "Macos":
            sub_version = "1.8.1"
            dl_url = f"https://dl.orbbec3d.com/dist/orbbecsdk/{sub_version}/OrbbecSDK_{sub_version}_macOS.zip"
            folder_name = "OrbbecSDK_1.8.1_macOS"
            sub_archive_match = "OrbbecSDK_C_C++_v*_macos_arm64_release.zip"
        elif self.settings.os == "Linux":
            sub_version = "1.8.3"
            dl_url = f"https://dl.orbbec3d.com/dist/orbbecsdk/{sub_version}/OrbbecSDK_{sub_version}_Linux.zip"
            folder_name = "OrbbecSDK_1.8.3_Linux"
            if self.settings.arch == "x86_64":
                sub_archive_match = "OrbbecSDK_C_C++_v*_linux_x64_release.zip"
            elif self.settings.arch == "armv8":
                sub_archive_match = "OrbbecSDK_C_C++_v*_linux_arm64_release.zip"
            else:
                raise EnvironmentError("Unsupported OS")
        elif self.settings.os == "Windows":
            sub_version = "1.8.3"
            dl_url = f"https://dl.orbbec3d.com/dist/orbbecsdk/{sub_version}/OrbbecSDK_{sub_version}_Windows.zip"
            folder_name = "OrbbecSDK_1.8.3_Windows"
            if self.settings.arch == "x86":
                sub_archive_match = "OrbbecSDK_C_C++_v*_win_x86_release.zip"
            elif self.settings.arch == "x86_64":
                sub_archive_match = "OrbbecSDK_C_C++_v*_win_x64_release.zip"
            else:
                raise EnvironmentError("Unsupported OS")


        if dl_url is None:
            raise EnvironmentError("Unsupported OS")
        return (dl_url, folder_name, sub_version, sub_archive_match)        

    def build(self):
        (dl_url, folder_name, sub_version, sub_archive_match) = self._package_description()
        get(self, dl_url, destination=self.source_folder)

        files = glob.glob(os.path.join(self.source_folder, folder_name, sub_archive_match))
        if len(files) != 1:
            raise ValueError("Missing Archive.")

        # this does now work correctly with symlinks on osx and maybe linux
        if self.settings.os == "Macos" or self.settings == "Linux":
            # python zipfile does not correctly extract the symlinks for the dylib
            self.run("unzip {} -d {}".format(files[0], os.path.join(self.source_folder, "OrbbecSDK")))
        else:
            unzip(self, files[0], os.path.join(self.source_folder, "OrbbecSDK"))


    def package(self):
        (dl_url, folder_name, sub_version, sub_archive_match) = self._package_description()

        sdk_root = os.path.join(self.source_folder, "OrbbecSDK", f"OrbbecSDK_v{sub_version}", "SDK")
        copy(self, "*.h*", 
            os.path.join(sdk_root, "include"), 
            os.path.join(self.package_folder, "include"))

        copy(self, "OrbbecSDKConfig_*.xml", 
            os.path.join(sdk_root, "config"), 
            os.path.join(self.package_folder, "config"))

        if self.settings.os == "Macos":
            copy(self, "*.dylib", 
                os.path.join(sdk_root, "lib"), 
                os.path.join(self.package_folder, "lib"))
            copy(self, "*.a", 
                os.path.join(sdk_root, "lib"), 
                os.path.join(self.package_folder, "lib"))

        elif self.settings.os == "Linux":
            copy(self, "*.so*", 
                os.path.join(sdk_root, "lib"), 
                os.path.join(self.package_folder, "lib"))
        elif self.settings.os == "Windows":
            copy(self, "*.dll", 
                os.path.join(sdk_root, "lib"), 
                os.path.join(self.package_folder, "bin"))
            copy(self, "*.lib", 
                os.path.join(sdk_root, "lib"), 
                os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["OrbbecSDK"]
