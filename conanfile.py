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
    version = "1.9.4"

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
        get(self, f"https://github.com/orbbec/OrbbecSDK/archive/refs/tags/v{self.version}.tar.gz", destination=self.source_folder)


    def package(self):
        sdk_root = os.path.join(self.source_folder, f"OrbbecSDK-{self.version}")
        copy(self, "*.h*", 
            os.path.join(sdk_root, "include"), 
            os.path.join(self.package_folder, "include"))

        copy(self, "OrbbecSDKConfig_*.xml", 
            os.path.join(sdk_root, "misc", "config"), 
            os.path.join(self.package_folder, "config"))

        if self.settings.os == "Macos":
            copy(self, "*.dylib", 
                os.path.join(sdk_root, "lib", "MacOS"), 
                os.path.join(self.package_folder, "lib"))
            copy(self, "*.a", 
                os.path.join(sdk_root, "lib", "MacOS"), 
                os.path.join(self.package_folder, "lib"))

        elif self.settings.os == "Linux":
            if self.settings.arch == "x86_64":
                copy(self, "*.so*", 
                    os.path.join(sdk_root, "lib", "linux_x64"), 
                    os.path.join(self.package_folder, "lib"))
            elif self.settings.arch == "armv8":
                copy(self, "*.so*", 
                    os.path.join(sdk_root, "lib", "arm64"), 
                    os.path.join(self.package_folder, "lib"))

        elif self.settings.os == "Windows":
            if self.settings.arch == "x86_64":
                copy(self, "*.dll", 
                    os.path.join(sdk_root, "lib", "win_x64"), 
                    os.path.join(self.package_folder, "bin"))
                copy(self, "*.lib", 
                    os.path.join(sdk_root, "lib", "win_x64"), 
                    os.path.join(self.package_folder, "lib"))
            elif self.settings.arch == "x86":
                copy(self, "*.dll", 
                    os.path.join(sdk_root, "lib", "win_x32"), 
                    os.path.join(self.package_folder, "bin"))
                copy(self, "*.lib", 
                    os.path.join(sdk_root, "lib", "win_x32"), 
                    os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["OrbbecSDK"]
