import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm

required_conan_version = ">=2.0"


class OrbbecSDKConan(ConanFile):
    name = "orbbec-sdk"
    version = "2.10.6"

    description = "Orbbec Camera SDK (OrbbecSDK_v2)"
    url = "https://github.com/TUM-CONAN/conan-orbbec-sdk.git"
    homepage = "https://github.com/orbbec/OrbbecSDK_v2"
    license = "MIT"

    # The SDK only builds as a shared library (src/CMakeLists.txt: add_library(... SHARED ...)). Its API is
    # C with header-only C++ wrappers, so the binary is ABI-neutral across C++ standards.
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        # Network (GigE/PoE) devices such as the Femto Mega over Ethernet.
        "with_net": [True, False],
        "with_gmsl": [True, False],
        # Femto Bolt only: depth engine through OpenGL (needs a display).
        "bolt_opengl_compat": [True, False],
    }
    default_options = {
        "with_net": True,
        "with_gmsl": False,
        "bolt_opengl_compat": False,
    }

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.25 <4]")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["OB_BUILD_EXAMPLES"] = False
        tc.cache_variables["OB_BUILD_TESTS"] = False
        tc.cache_variables["OB_BUILD_TOOLS"] = False
        tc.cache_variables["OB_BUILD_DOCS"] = False
        tc.cache_variables["OB_INSTALL_EXAMPLES_SOURCE"] = False
        tc.cache_variables["OB_BUILD_USB_PAL"] = True
        tc.cache_variables["OB_BUILD_NET_PAL"] = bool(self.options.with_net)
        tc.cache_variables["OB_BUILD_GMSL_PAL"] = bool(self.options.with_gmsl)
        tc.cache_variables["OB_ENABLE_BOLT_OPENGL_COMPAT"] = bool(self.options.bolt_opengl_compat)
        tc.generate()
        CMakeDeps(self).generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        # Conan generates the CMake config; drop the SDK's own export files.
        rm(self, "OrbbecSDKConfig*.cmake", os.path.join(self.package_folder, "lib"))
        rm(self, "OrbbecSDKVersion.cmake", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        # Same names as the SDK's own export: find_package(OrbbecSDK) -> ob::OrbbecSDK.
        self.cpp_info.set_property("cmake_file_name", "OrbbecSDK")
        self.cpp_info.set_property("cmake_target_name", "ob::OrbbecSDK")
        self.cpp_info.libs = ["OrbbecSDK"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "dl"]
        # The SDK loads its extensions (depth engine, filters, frame processor, firmware updater) at run time
        # from <directory of libOrbbecSDK>/extensions (dladdr); they are installed to lib/extensions.
