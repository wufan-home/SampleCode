#!/usr/bin/env python3

import argparse
import os
import queue
import subprocess

g_cur_workspace = os.getcwd()
g_cur_cmake_workspace = "${CMAKE_CURRENT_SOURCE_DIR}"
g_dst_filename = 'CMakeLists.txt'
g_target_list = ['nvmf_tgt', 'extentServer', 'ipsec_udp', 'tgtd']
g_targets_to_binary = {'nvmf_tgt' : '//bsv2_nvmf_tgt:nvmf_tgt',
                     'extentServer' : '//blockstorage:extentServer',
                     'ipsec_udp' : '//tgt:ipsec_udp',
                     'tgtd': '//tgt:tgtd'}
g_bazel_query_outputs = {}
g_cached_lib_queue = queue.Queue()
g_dir_set = set()

def get_dependency(binary):
    relative_path = ""
    try:
        # print("\nBinary = {}".format(binary))

        output_path = subprocess.run(
            ['bazel', 'query', '--output=package', binary],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        g_dir_set.add(output_path.stdout.strip())

        relative_path = output_path.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("Bazel query for working path failed: error output:\n{}".format(e.stderr))
        exit(1)

    try:
        expr_src = "kind('source file', deps({}, 1))".format(binary)
        output_src = subprocess.run(
            ['bazel', 'query', expr_src],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        # for filename in output.stdout.strip().strip("[]").split("\n"):
        #     if len(filename.split(":")) <= 1:
        #         print("Exceptional filename {}".format(filename))
        g_bazel_query_outputs[binary].append(
            [relative_path + "/" + src.split(":")[1]
             for src in output_src.stdout.strip().strip("[]").split("\n") if len(src.split(":")) > 1])
    except subprocess.CalledProcessError as e:
        print("Bazel query for source files failed: error output:\n{}".format(e.stderr))
        exit(1)

    try:
        expr_lib = "kind('cc_library', deps({}, 1))".format(binary)
        output_lib = subprocess.run(
            ['bazel', 'query', expr_lib],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        g_bazel_query_outputs[binary].append(
            [src for src in output_lib.stdout.strip().strip("[]").split("\n") if not src.startswith("@")])
        for src in g_bazel_query_outputs[binary][1]:
            g_cached_lib_queue.put(src)
    except subprocess.CalledProcessError as e:
        print("Bazel query for cc_library failed: error output:\n{}".format(e.stderr))
        exit(1)

    g_bazel_query_outputs[binary].append(relative_path)

def generate_graph(binary):
    global g_bazel_query_outputs
    if binary in g_bazel_query_outputs.keys():
        return
    g_bazel_query_outputs[binary] = []
    get_dependency(binary)
    while g_cached_lib_queue.qsize() > 0:
        cur = g_cached_lib_queue.get()
        print("Generate the graph for the binary {}".format(cur))
        generate_graph(cur)

def generate_cmake_files(binary, path):
    with open(os.path.join(path, 'CMakeLists.txt'), 'w') as f:
        f.write("cmake_minimum_required(VERSION 3.26)\n")
        f.write("project({})\n".format(binary))
        f.write("set(CMAKE_CXX_STANDARD 17)\n")
        f.write("set(CMAKE_C_STANDARD 99)\n\n")

        f.write("\n# Libraries\n")
        for key, value in g_bazel_query_outputs.items():
            if key is not binary:
                lib_name = key.lstrip("/").replace("/", "_").replace(":", "_")
                # Define a library with specifying files
                f.write("add_library(\"{}\"\n".format(lib_name))
                for filename in value[0]:
                    f.write("    \"{}\"\n".format(filename))
                f.write(")\n")
                # Link the current lib with its dependencies.
                f.write("target_link_libraries(\"{}\"\n".format(lib_name))
                for dep_lib in value[1]:
                    dep_lib_name = dep_lib.lstrip("/").replace("/", "_").replace(":", "_")
                    if dep_lib_name == lib_name:
                        continue
                    f.write("    \"{}\"\n".format(dep_lib_name))
                f.write(")\n")
                # Specify the path
                f.write("file(GLOB_RECURSE SUB_DIRS RELATIVE {} \"{}\")\n".format(g_cur_cmake_workspace, value[2]))
                f.write("set(INCLUDE_SUB_DIRS \"\")\n")
                f.write("foreach(sub_dir ${SUB_DIRS})\n")
                f.write("    if (IS_DIRECTORY \"{}/{}\")\n".format(g_cur_cmake_workspace, "${sub_dir}"))
                f.write("        list(APPEND INCLUDE_SUB_DIRS \"{}/{}\")\n".format(g_cur_cmake_workspace, "${sub_dir}"))
                f.write("    endif()\n")
                f.write("endforeach()\n")
                f.write("target_include_directories(\"{}\" PUBLIC\n".format(lib_name))
                f.write("    \"INCLUDE_SUB_DIRS\"\n")
                f.write(")\n")
                # Specify the language the current lib being used.
                f.write("set_target_properties(\"{}\" PROPERTIES LINKER_LANGUAGE CXX)\n".format(lib_name))
                f.write("\n")

        f.write("\n# Executable\n")
        exec_name = binary.lstrip("/").replace("/", "_").replace(":", "_")
        # Define an executable with specifying files
        f.write("add_executable(\"{}\" \n".format(exec_name))
        for filename in g_bazel_query_outputs[binary][0]:
            f.write("    \"{}\"\n".format(filename))
        f.write(")\n")
        # Link the current executable with its dependencies.
        f.write("target_link_libraries(\"{}\"\n".format(exec_name))
        for filename in g_bazel_query_outputs[binary][1]:
            f.write("    \"{}\"\n".format(filename.lstrip("/").replace("/", "_").replace(":", "_")))
        f.write(")\n")
        # Specify the path
        f.write("file(GLOB_RECURSE SUB_DIRS RELATIVE {} \"{}\")\n".format(g_cur_cmake_workspace, g_bazel_query_outputs[binary][2]))
        f.write("set(INCLUDE_SUB_DIRS \"\")\n")
        f.write("foreach(sub_dir ${SUB_DIRS})\n")
        f.write("    if (IS_DIRECTORY \"{}/{}\")\n".format(g_cur_cmake_workspace, "${sub_dir}"))
        f.write("        list(APPEND INCLUDE_SUB_DIRS \"{}/{}\")\n".format(g_cur_cmake_workspace, "${sub_dir}"))
        f.write("    endif()\n")
        f.write("endforeach()\n")
        f.write("target_include_directories(\"{}\" PUBLIC\n".format(exec_name))
        f.write("    \"INCLUDE_SUB_DIRS\"\n")
        f.write(")\n")
        # Specify the language the current executable being used.
        f.write("set_target_properties(\"{}\" PROPERTIES LINKER_LANGUAGE CXX)\n".format(exec_name))

def main(args):
    generate_graph(g_targets_to_binary[args.target])
    generate_cmake_files(g_targets_to_binary[args.target], args.dst)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", dest="dst", required=True,
                        help="The path to store the CMakeLists.txt.")
    parser.add_argument("-t", dest="target", required=True, choices=g_target_list,
                        help="The bazel build target to generate CMakeLists.txt.")
    ARGS = parser.parse_args()

    if ARGS.dst is None or ARGS.dst == "":
        print("Please specify the bazel build target to generate CMakeLists.txt.")
        ARGS.dst = g_cur_workspace

    main(ARGS)
