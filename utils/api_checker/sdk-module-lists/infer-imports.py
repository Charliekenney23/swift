#!/usr/bin/env python -u

import os
import sys

blacklist = ["Kernel", "Ruby", "Tk"]


def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def get_frameworks(sdk_path):
    frameworks_path = sdk_path + "/System/Library/Frameworks"
    names = []
    for frame in os.listdir(frameworks_path):
        if frame.endswith(".framework"):
            header_dir_path = frameworks_path + '/' + frame + '/Headers'
            module_dir_path = frameworks_path + '/' + frame + '/Modules'
            old_modulemap_path = frameworks_path + '/' + frame + '/module.map'
            old_modulemap_private_path = frameworks_path + '/' + frame + \
                '/module_private.map'
            if not os.path.exists(header_dir_path):
                if os.path.exists(module_dir_path):
                    print >>sys.stderr, header_dir_path, \
                        " non-existent while 'Modules' exists"
                if os.path.exists(old_modulemap_path):
                    print >>sys.stderr, header_dir_path, \
                        " non-existent while 'module.map' exists"
                if os.path.exists(old_modulemap_private_path):
                    print >>sys.stderr, header_dir_path, \
                        " non-existent while 'module_private.map' exists"
                continue

            if should_exclude_framework(frameworks_path + '/' + frame):
                continue

            name = frame[:-len(".framework")]
            if name in blacklist:
                continue
            names.append(name)
    return names


def should_exclude_framework(frame_path):
    module_map_path = frame_path + '/Modules/module.modulemap'
    if not os.path.exists(module_map_path):
        return False
    contents = open(module_map_path).read()
    if "requires !swift" in contents:
        return True
    if "requires unavailable" in contents:
        return True

    return False


def print_clang_imports(frames, use_hash):
    for name in frames:
        if use_hash:
            print "#import <" + name + "/" + name + ".h>"
        else:
            print "@import " + name + ";"


def print_swift_imports(frames):
    for name in frames:
        print "import " + name


def main():
    global opts
    from optparse import OptionParser
    parser = OptionParser("""%prog [options] command

%prog outputs imports

  $ %prog -s <sdk-path> -o <output-mode> [--hash]

""")
    parser.add_option("-s", "--sdk", help="sdk path",
                      type=str, dest="sdk", default=None)
    parser.add_option("-o", "--output", help="output mode",
                      type=str, dest="out_mode", default="list")
    parser.add_option("--hash", action="store_true", dest="use_hash")

    (opts, cmd) = parser.parse_args()

    if not opts.sdk:
        parser.error("sdk not specified")

    if not opts.out_mode:
        parser.error(
            "output mode not specified: 'clang-import'/'swift-import'/'list'")

    frames = get_frameworks(opts.sdk)
    if opts.out_mode == "clang-import":
        print_clang_imports(frames, opts.use_hash)
    elif opts.out_mode == "swift-import":
        print_swift_imports(frames)
    elif opts.out_mode == "list":
        for name in frames:
            print name
    else:
        parser.error(
            "output mode not found: 'clang-import'/'swift-import'/'list'")


if __name__ == '__main__':
    main()
