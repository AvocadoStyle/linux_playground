import os
import inspect

cwd_path = os.getcwd()

package_cwd_path = os.path.join(cwd_path, "linux_playground")
python_playground_path = os.path.join(package_cwd_path, "python_playground")
package_reports_path = os.path.join(package_cwd_path, "reports")

def relative_path(path: str):
    return os.path.normpath(os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe().f_back)), path))


if __name__ == '__main__':
    print("\n")
    print(f"The __file__ output: {__file__}\n")
    print(f"The os.path.dirname(__file__) output: {os.path.dirname(__file__)}\n")
    print(f"The os.path.abspath(__file__) output: {os.path.abspath(__file__)}\n")
    print(f"inspect.getfile(os) output: {inspect.getfile(os)}")
    print(f"inspect.getfile(inspect.currentframe()) output: {inspect.getfile(inspect.currentframe())}")

