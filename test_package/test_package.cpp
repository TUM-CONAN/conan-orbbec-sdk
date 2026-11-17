#include <libobsensor/ObSensor.hpp>

#include <iostream>

int main() {
    std::cout << "OrbbecSDK " << ob::Version::getMajor() << "." << ob::Version::getMinor() << "."
              << ob::Version::getPatch() << std::endl;
    // No device access: creating a context only loads the SDK (and its config).
    ob::Context::setLoggerSeverity(OB_LOG_SEVERITY_WARN);
    ob::Context ctx;
    return 0;
}
