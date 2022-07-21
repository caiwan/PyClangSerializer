# Tests if all requirements are installed properly

import sys


def main():
    try:
        import clang.cindex

        s = """
        int fac(int n) {
            return (n>1) ? n*fac(n-1) : 1;
        }
        """

        if len(sys.argv) > 1:
            clang.cindex.Config.set_library_path(sys.argv[1])

        idx = clang.cindex.Index.create()
        tu = idx.parse("tmp.cpp", args=["-std=c++11"], unsaved_files=[("tmp.cpp", s)], options=0)
        assert tu.get_tokens(extent=tu.cursor.extent) is not None

    except ModuleNotFoundError:
        print("Requirements are not installed properly.")
        sys.exit(-1)

    except OSError:
        print("Clang is not installed or not found.")
        sys.exit(-2)

    except clang.cindex.LibclangError as e:
        print("Clang error: " + str(e))
        sys.exit(-3)

    except Exception:
        print(sys.exc_info())
        sys.exit(-4)

    sys.exit(0)


if __name__ == "__main__":
    main()
