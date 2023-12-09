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

    def build(self):
        dl_url = None
        folder_name = None
        sub_version = None
        if self.settings.os == "Macos":
            sub_version = "1.8.1"
            dl_url = f"https://dl.orbbec3d.com/dist/orbbecsdk/{sub_version}/OrbbecSDK_{sub_version}_macOS.zip"
            folder_name = "OrbbecSDK_1.8.1_macOS"
            sub_archive_match = "OrbbecSDK_C_C++_v*_macos_arm64_release.zip"
        elif self.settings.os == "Linux":
            sub_version = "1.8.3"
            dl_url = f"https://dl.orbbec3d.com/dist/orbbecsdk/{sub_version}/OrbbecSDK_{sub_version}_Linux.zip"
            folder_name = "OrbbecSDK_1.8.3_Linux"
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
        get(self, dl_url, destination=self.source_folder)

        files = glob.glob(os.path.join(self.source_folder, folder_name, sub_archive_match))
        if len(files) != 1:
            raise ValueError("Missing Archive.")

        unzip(self, files[0], os.path.join(self.source_folder, "OrbbecSDK"))
        shutil.move(os.path.join(self.source_folder, "OrbbecSDK", f"OrbbecSDK_v{sub_version}"),
            os.path.join(self.build_folder, "dist"))


    def package(self):

        sdk_root = os.path.join(self.build_folder, "dist", "SDK")
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
            raise NotImplementedError()
        elif self.settings.os == "Windows":
            copy(self, "*.dll", 
                os.path.join(sdk_root, "lib"), 
                os.path.join(self.package_folder, "bin"))
            copy(self, "*.lib", 
                os.path.join(sdk_root, "lib"), 
                os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["OrbbecSDK"]