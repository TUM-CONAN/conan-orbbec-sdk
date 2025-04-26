from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import update_conandata, copy, chdir, mkdir, collect_libs, get, rename, unzip, replace_in_file
from conan.tools.env import Environment
from conan.tools.env import VirtualRunEnv
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.system.package_manager import Apt

import re
import glob
import shutil

import os, sys
import sysconfig
from io import StringIO

class OrbbecSDKConan(ConanFile):
    name = "orbbec-sdk"
    version = "2.3.5"

    description = "Orbbec Camera SDK"
    url = "https://github.com/TUM-CAMP-NARVIS/conan-orbbec-sdk.git"
    license = "GPL"

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def system_requirements(self):
        if self.settings.os == "Linux":
            pack_names = []
            #pack_names.append("libacl1-dev")

            Apt(self).install(pack_names)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        pass

    def build_requirements(self):
        self.tool_requires("cmake/3.25.3")

    def validate(self):
        compiler = self.settings.compiler
        version = str(self.settings.compiler.version)

        if compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)

        def add_cmake_option(option, value):
            var_name = "{}".format(option).upper()
            value_str = "{}".format(value)
            var_value = "ON" if value_str == 'True' else "OFF" if value_str == 'False' else value_str
            tc.variables[var_name] = var_value

        for option, value in self.options.items():
            add_cmake_option(option, value)

        tc.cache_variables["OB_BUILD_EXAMPLES"]= "OFF"

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def layout(self):
        cmake_layout(self)

    def build(self):
        # self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
 
    def package_info(self):
        self.cpp_info.libs = ["OrbbecSDK"]
