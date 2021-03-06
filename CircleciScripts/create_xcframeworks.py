import os
import sys
import shutil

from framework_list import xcframeworks
from functions import log, run_command

IOS_DEVICE_ARCHIVE_PATH = "./xcframeworks/output/iOS/"
IOS_SIMULATOR_ARCHIVE_PATH = "./xcframeworks/output/Simulator/"
XCFRAMEWORK_PATH = "./xcframeworks/output/XCF/"

def create_archive(framework, project_file, build_for_device):
    if build_for_device:
        archive_path = f"{IOS_DEVICE_ARCHIVE_PATH}{framework}" 
        destination = "generic/platform=iOS"
    else:
        archive_path = f"{IOS_SIMULATOR_ARCHIVE_PATH}{framework}"
        destination = "generic/platform=iOS Simulator"
    cmd = [
        "xcodebuild",
        "archive",
        "-project",
        project_file,
        "-scheme",
        framework,
        "-destination",
        destination,
        "-archivePath",
        archive_path,
        "SKIP_INSTALL=NO",
        "BUILD_LIBRARY_FOR_DISTRIBUTION=YES"
    ] 
    
    (exit_code, out, err) = run_command(cmd, keepalive_interval=300, timeout=7200)
    if exit_code == 0:
        log(f"Created iOS archive {framework} {destination}")
    else:
        log(f"Could not create xcodebuild archive: {framework} output: {out}; error: {err}")
        sys.exit(exit_code)

def map_framework_to_project(framework_list):
    framework_map = {}
    cmd = [
        "xcodebuild",
        "-project",
        "AWSiOSSDKv2.xcodeproj",
        "-list",
    ] 
    (exit_code, out, err) = run_command(cmd, keepalive_interval=300, timeout=7200)
    if exit_code == 0:
        log(f"List of schema found")
    else:
        log(f"Xcodebuild list failed: output: {out}; error: {err}")
        sys.exit(exit_code)

    for framework in framework_list:
        if framework not in str(out):
            framework_map[framework] = "./AWSAuthSDK/AWSAuthSDK.xcodeproj"
        else:
            framework_map[framework] = "AWSiOSSDKv2.xcodeproj"
    return framework_map

project_dir = os.getcwd()
log(f"Creating XCFrameworks in {project_dir}")
framework_map = map_framework_to_project(xcframeworks)

# Archive all the frameworks.
for framework in xcframeworks:
    create_archive(framework=framework, project_file=framework_map[framework], build_for_device=True)
    create_archive(framework=framework, project_file=framework_map[framework], build_for_device=False)

# Create XCFramework using the archived frameworks.
for framework in xcframeworks:
    ios_device_framework = f"{IOS_DEVICE_ARCHIVE_PATH}{framework}.xcarchive/Products/Library/Frameworks/{framework}.framework"
    ios_simulator_framework = f"{IOS_SIMULATOR_ARCHIVE_PATH}{framework}.xcarchive/Products/Library/Frameworks/{framework}.framework"
    xcframework = f"{XCFRAMEWORK_PATH}{framework}.xcframework"
    cmd = [
            "xcodebuild",
            "-create-xcframework",
            "-framework",
            ios_device_framework,
             "-framework",
            ios_simulator_framework,
            "-output",
            xcframework
        ] 
    (exit_code, out, err) = run_command(cmd, keepalive_interval=300, timeout=7200)
    if exit_code == 0:
        log(f"Created XCFramework for {framework}")
    else:
        log(f"Could not create XCFramework: {framework} output: {out}; error: {err}")
        sys.exit(exit_code)
    
shutil.rmtree(IOS_DEVICE_ARCHIVE_PATH)
shutil.rmtree(IOS_SIMULATOR_ARCHIVE_PATH)
