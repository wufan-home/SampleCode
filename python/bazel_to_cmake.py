#!/usr/bin/env python3

import os
import queue
import subprocess

g_workspace = "${CMAKE_CURRENT_SOURCE_DIR}"
g_current_workspace = os.getcwd()
g_generated_folder_prefix = "user_cache"
g_generated_folder_path = ""
g_dst_filename = 'CMakeLists.txt'

g_target_list = ['extentServer', 'tgtd', 'nvmf_tgt', 'spdk_nvmf_tgt']
g_targets_to_binary = {'extentServer' : '//blockstorage:extentServer',
                       'nvmf_tgt' : '//bsv2_nvmf_tgt:nvmf_tgt',
                       'spdk_nvmf_tgt' : '//spdk_nvmf_tgt:spdk_nvmf_tgt',
                       'tgtd': '//tgt:tgtd'}

g_bazel_query_outputs = {}
g_cached_lib_queue = queue.Queue()
g_included_directories = set()

def get_generated_folder_path():
    global g_generated_folder_path
    try:
        output_execroot = subprocess.run(
            ['bazel', 'info', 'execution_root'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        g_generated_folder_path = g_generated_folder_prefix + "/" + (output_execroot.stdout.strip(" ").rstrip("\n")
                                   .removeprefix(os.getenv("HOME") + "/.cache").lstrip("/")
                                   + "/bazel-out/k8-py2-fastbuild/bin")
        g_included_directories.add(g_generated_folder_path)
        print ("The generated folder is {}".format(g_generated_folder_path))
    except subprocess.CalledProcessError as e:
        print("Bazel query for working path failed: error output:\n{}".format(e.stderr))
        exit(1)

def get_file_absolute_path(filename):
    global g_generated_folder_path
    target_placed_path = filename.rstrip(" ").rstrip("\n").lstrip('/').replace(":", "/")
    try:
        output_label = subprocess.run(
            ['bazel', 'query', '--output=label_kind', filename],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        if output_label.stdout.strip(" ").startswith("generated"):
            print("the file {} is in the generated folder".format(filename))
            target_placed_path = g_generated_folder_path + "/" + target_placed_path
    except subprocess.CalledProcessError as e:
        print("Bazel query for working path failed: error {}, filename {}".format(e.stderr, filename))
        exit(1)
    return target_placed_path

def collect_src_files(target, src_file_paths):
    try:
        expr_src = "kind('generated file|source file', deps({}, 1))".format(target)
        output_src = subprocess.run(
            ['bazel', 'query', expr_src],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        g_bazel_query_outputs[target].append([])
        for filename in output_src.stdout.strip().strip("[]").split("\n"):
            if len(filename) == 0 or '+' in filename:
                continue
            path = get_file_absolute_path(filename)
            # src_file_paths.add(path.rsplit("/", 1)[0])
            g_bazel_query_outputs[target][0].append("{}".format(path))
    except subprocess.CalledProcessError as e:
        print("Bazel query for source files failed: error {}, target {}".format(e.stderr, target))
        exit(1)

def collect_dependencies(target):
    try:
        expr_lib = "kind('cc_library', deps({}, 1))".format(target)
        output_lib = subprocess.run(
            ['bazel', 'query', expr_lib],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        g_bazel_query_outputs[target].append(
            [src for src in output_lib.stdout.strip().strip("[]").split("\n") if not src.startswith("@")])
        for src in g_bazel_query_outputs[target][1]:
            g_cached_lib_queue.put(src)
    except subprocess.CalledProcessError as e:
        print("Bazel query for cc_library failed: error {}, target {}".format(e.stderr, target))
        exit(1)

def parse_dependency(target):
    src_file_paths = set()
    collect_src_files(target, src_file_paths)
    collect_dependencies(target)
    # g_bazel_query_outputs[target].append(src_file_paths)

def generate_graph(target):
    global g_bazel_query_outputs
    if target in g_bazel_query_outputs.keys():
        return
    g_bazel_query_outputs[target] = []
    parse_dependency(target)
    while g_cached_lib_queue.qsize() > 0:
        next_target = g_cached_lib_queue.get()
        print("Generate the graph for the target {}".format(next_target))
        generate_graph(next_target)

def generate_cmakelist_file(path = g_current_workspace):
    with open(os.path.join(path, 'CMakeLists.txt'), 'w') as f:
        f.write("cmake_minimum_required(VERSION 3.26)\n")
        f.write("project({})\n".format("workspace_usp"))
        f.write("set(CMAKE_CXX_STANDARD 17)\n")
        f.write("set(CMAKE_C_STANDARD 99)\n")
        f.write("set(CMAKE_EXPORT_COMPILE_COMMANDS ON)\n\n")

        # Due to the header files are included in the format #include "blockstorage/base/somefile.h"
        # i.e., the headers are using the relative path mode - relative to the root folder.
        # We only have to include the parent folder of the headers.
        # The including of headers' absolute folders would cause missing of headers.
        # This is the best practice to include header files in C++ programs.
        f.write("# Globally included directories\n")
        f.write("include_directories(\n")
        f.write("    \"{}\"\n".format(g_generated_folder_path))
        f.write("    \"{}\"\n".format(g_workspace))
        f.write("    \"{}/folly\"\n".format(g_workspace))
        f.write("    \"{}/spdk/include\"\n".format(g_workspace))
        f.write("    \"{}/spdk_nvmf_tgt/include\"\n".format(g_workspace))
        f.write("    \"third-party/capnproto/c++/src\"\n")
        f.write("    \"third-party/google-glog/generated/x86_64-linux-gnu/private_include\"\n")
        f.write("    \"third-party/google-glog/src/windows\"\n")
        f.write("    \"third-party/google-glog/generated/x86_64-linux-gnu/private_include\"\n")
        f.write("    \"third-party/google-gflags/generated/mipsisa64-octeon-elf/include\"\n")
        f.write("    \"third-party/google-gflags/generated/mipsisa64-octeon-elf/private_include\"\n")
        f.write("    \"third-party/google-gflags/generated/x86_64-linux-gnu/include\"\n")
        f.write("    \"third-party/google-gflags/generated/x86_64-linux-gnu/private_include\"\n")
        f.write("    \"third-party/google-gtest/include\"\n")
        f.write("    \"third-party/google-protobuf/src\"\n")
        f.write("    \"third-party/modular-boost/libs/icl/include\"\n")
        f.write("    \"third-party/modular-boost/libs/filesystem/include\"\n")
        f.write("    \"third-party/modular-boost/libs/uuid/include\"\n")
        f.write("    \"third-party/modular-boost/libs/unordered/include\"\n")
        f.write(")\n\n")

        f.write("# Libraries\n")
        for key, value in g_bazel_query_outputs.items():
            if key not in g_target_list:
                lib_name = key.lstrip("/").replace("/", "_").replace(":", "__")
                # Define a library with the files if refers
                f.write("add_library(\"{}\" {}\n".format(lib_name, "INTERFACE" if len(value[0]) == 0 else ""))
                for filename in value[0]:
                    f.write("    \"{}\"\n".format(filename))
                f.write(")\n")
                # Link the current lib with its dependencies.
                f.write("target_link_libraries(\"{}\" {}\n".format(lib_name, "INTERFACE" if len(value[0]) == 0 else "PUBLIC"))
                for dep_lib in value[1]:
                    dep_lib_name = dep_lib.lstrip("/").replace("/", "_").replace(":", "__")
                    if dep_lib_name == lib_name:
                        continue
                    f.write("    \"{}\"\n".format(dep_lib_name))
                f.write(")\n")
                # # Specify the path
                # f.write("target_include_directories(\"{}\" PUBLIC\n".format(lib_name))
                # for path in value[2]:
                #     f.write("    \"{}\"\n".format(path))
                # f.write(")\n")
                # Specify the language the current lib being used.
                f.write("set_target_properties(\"{}\" PROPERTIES LINKER_LANGUAGE CXX)\n".format(lib_name))
                f.write("\n")

        f.write("\n# Executable\n")
        for target in g_target_list:
            exec_name = target.lstrip("/").replace("/", "_").replace(":", "__")
            # Define an executable with specifying files
            f.write("add_executable(\"{}\" \n".format(exec_name))
            for filename in g_bazel_query_outputs[g_targets_to_binary[target]][0]:
                f.write("    \"{}\"\n".format(filename))
            f.write(")\n")
            # Link the current executable with its dependencies.
            f.write("target_link_libraries(\"{}\" PUBLIC\n".format(exec_name))
            for filename in g_bazel_query_outputs[g_targets_to_binary[target]][1]:
                f.write("    \"{}\"\n".format(filename.lstrip("/").replace("/", "_").replace(":", "__")))
            f.write(")\n")
            # # Specify the path
            # f.write("target_include_directories(\"{}\" PUBLIC\n".format(exec_name))
            # for path in g_bazel_query_outputs[g_targets_to_binary[target]][2]:
            #     f.write("    \"{}\"\n".format(path))
            # f.write(")\n")
            # Specify the language the current executable being used.
            f.write("set_target_properties(\"{}\" PROPERTIES LINKER_LANGUAGE CXX)\n".format(exec_name))

def main():
    get_generated_folder_path()
    for binary in g_target_list:
        print("Generate the graph for the binary {}".format(binary))
        generate_graph(g_targets_to_binary[binary])
        print("===================================")
    generate_cmakelist_file()

if __name__ == "__main__":
    main()
